"""
Minimal MPQ archive reader/writer for .StormInterface files.

A .StormInterface is an MPQ archive. The Java builder writes format version 3
(the 208-byte "MPQ v4" header); this writes the original format version 0
("MPQ v1"): a 32-byte header, the files stored raw, then the hash and block
tables, each encrypted with a fixed key.

Writing is uncompressed only. Reading also handles zlib/bzip2 sectors, enough
to open archives made by other tools for comparison.

CLI:
    python tools/mpq.py list    <archive>
    python tools/mpq.py extract <archive> <dest-folder>
"""

import bz2
import struct
import sys
import zlib
from pathlib import Path

MASK = 0xFFFFFFFF

HASH_OFFSET, HASH_NAME_A, HASH_NAME_B, HASH_FILE_KEY = 0, 1, 2, 3

FILE_IMPLODE     = 0x00000100
FILE_COMPRESS    = 0x00000200
FILE_ENCRYPTED   = 0x00010000
FILE_SINGLE_UNIT = 0x01000000
FILE_SECTOR_CRC  = 0x04000000
FILE_EXISTS      = 0x80000000

HASH_EMPTY   = 0xFFFFFFFF
HASH_DELETED = 0xFFFFFFFE

LISTFILE = "(listfile)"


def _build_crypt_table():
    table = [0] * 0x500
    seed = 0x00100001
    for i in range(0x100):
        idx = i
        for _ in range(5):
            seed = (seed * 125 + 3) % 0x2AAAAB
            hi = (seed & 0xFFFF) << 16
            seed = (seed * 125 + 3) % 0x2AAAAB
            lo = seed & 0xFFFF
            table[idx] = hi | lo
            idx += 0x100
    return table


CRYPT = _build_crypt_table()


def hash_string(name, hash_type):
    """Blizzard's string hash. Case-insensitive, and / is treated as \\."""
    seed1, seed2 = 0x7FED7FED, 0xEEEEEEEE
    for c in name.replace("/", "\\").encode("utf-8"):
        if 0x61 <= c <= 0x7A:
            c -= 0x20
        seed1 = CRYPT[(hash_type << 8) + c] ^ ((seed1 + seed2) & MASK)
        seed2 = (c + seed1 + seed2 + (seed2 << 5) + 3) & MASK
    return seed1


def _crypt(data, key, decrypt):
    count = len(data) // 4
    words = struct.unpack(f"<{count}I", data[: count * 4])
    out = []
    seed1, seed2 = key, 0xEEEEEEEE
    for w in words:
        seed2 = (seed2 + CRYPT[0x400 + (seed1 & 0xFF)]) & MASK
        x = (w ^ (seed1 + seed2)) & MASK
        plain = x if decrypt else w
        out.append(x)
        seed1 = (((~seed1 << 21) + 0x11111111) | (seed1 >> 11)) & MASK
        seed2 = (plain + seed2 + (seed2 << 5) + 3) & MASK
    return struct.pack(f"<{count}I", *out)


def encrypt(data, key):
    return _crypt(data, key, decrypt=False)


def decrypt(data, key):
    return _crypt(data, key, decrypt=True)


HASH_TABLE_KEY  = hash_string("(hash table)", HASH_FILE_KEY)
BLOCK_TABLE_KEY = hash_string("(block table)", HASH_FILE_KEY)


# ------------------------------------------------------------------ writing

def write_mpq(files, sector_shift=3, listfile=True):
    """Build an MPQ v1 archive from {archive path: bytes}. Returns the archive bytes.

    Paths use backslashes inside the archive; forward slashes are converted.
    Files are stored uncompressed and unencrypted, so no sector offset table
    is needed - the data is simply contiguous.
    """
    entries = {name.replace("/", "\\"): data for name, data in files.items()}
    if listfile:
        names = sorted(entries)
        entries[LISTFILE] = ("\r\n".join(names) + "\r\n").encode("utf-8")

    hash_size = 16
    while hash_size < len(entries) * 2:
        hash_size *= 2

    body = bytearray()
    header_size = 32
    blocks = []
    for name, data in entries.items():
        blocks.append((header_size + len(body), len(data), len(data), FILE_EXISTS))
        body += data

    hash_table = [(HASH_EMPTY, HASH_EMPTY, 0xFFFF, 0xFFFF, HASH_EMPTY)] * hash_size
    for block_index, name in enumerate(entries):
        slot = hash_string(name, HASH_OFFSET) & (hash_size - 1)
        while hash_table[slot][4] != HASH_EMPTY:
            slot = (slot + 1) & (hash_size - 1)
        hash_table[slot] = (
            hash_string(name, HASH_NAME_A),
            hash_string(name, HASH_NAME_B),
            0,  # locale: neutral
            0,  # platform
            block_index,
        )

    hash_bytes = encrypt(b"".join(struct.pack("<IIHHI", *e) for e in hash_table), HASH_TABLE_KEY)
    block_bytes = encrypt(b"".join(struct.pack("<IIII", *b) for b in blocks), BLOCK_TABLE_KEY)

    hash_pos = header_size + len(body)
    block_pos = hash_pos + len(hash_bytes)
    archive_size = block_pos + len(block_bytes)

    header = struct.pack(
        "<4sIIHHIIII",
        b"MPQ\x1a",
        header_size,
        archive_size,
        0,  # format version 0 = MPQ v1
        sector_shift,
        hash_pos,
        block_pos,
        hash_size,
        len(blocks),
    )
    return header + bytes(body) + hash_bytes + block_bytes


# ------------------------------------------------------------------ reading

class MpqArchive:
    def __init__(self, data):
        self.data = data
        magic, header_size, _, version, shift, hash_pos, block_pos, hash_n, block_n = \
            struct.unpack_from("<4sIIHHIIII", data, 0)
        if magic != b"MPQ\x1a":
            raise ValueError("not an MPQ archive (no MPQ\\x1A header)")
        self.header_size = header_size
        self.format_version = version
        self.sector_size = 512 << shift
        if version >= 1:
            # v2+ carries the high 16 bits of each table position after the v1 header.
            _, hash_hi, block_hi = struct.unpack_from("<QHH", data, 32)
            hash_pos |= hash_hi << 32
            block_pos |= block_hi << 32

        raw = decrypt(data[hash_pos : hash_pos + hash_n * 16], HASH_TABLE_KEY)
        self.hash_table = [struct.unpack_from("<IIHHI", raw, i * 16) for i in range(hash_n)]
        raw = decrypt(data[block_pos : block_pos + block_n * 16], BLOCK_TABLE_KEY)
        self.block_table = [struct.unpack_from("<IIII", raw, i * 16) for i in range(block_n)]

    def _find(self, name):
        n = len(self.hash_table)
        a, b = hash_string(name, HASH_NAME_A), hash_string(name, HASH_NAME_B)
        slot = hash_string(name, HASH_OFFSET) & (n - 1)
        for _ in range(n):
            ha, hb, _, _, block = self.hash_table[slot]
            if block == HASH_EMPTY:
                return None
            if ha == a and hb == b and block != HASH_DELETED:
                return self.block_table[block]
            slot = (slot + 1) & (n - 1)
        return None

    def has(self, name):
        return self._find(name) is not None

    def read(self, name):
        block = self._find(name)
        if block is None:
            raise KeyError(name)
        pos, csize, fsize, flags = block
        if flags & FILE_ENCRYPTED:
            raise NotImplementedError(f"{name}: encrypted files are not supported")
        raw = self.data[pos : pos + csize]
        if not flags & (FILE_COMPRESS | FILE_IMPLODE):
            return raw[:fsize]
        if flags & FILE_SINGLE_UNIT:
            return _decompress(raw, fsize) if csize < fsize else raw[:fsize]

        sectors = (fsize + self.sector_size - 1) // self.sector_size
        count = sectors + 1 + (1 if flags & FILE_SECTOR_CRC else 0)
        offsets = struct.unpack_from(f"<{count}I", raw, 0)
        out = bytearray()
        for i in range(sectors):
            chunk = raw[offsets[i] : offsets[i + 1]]
            expected = min(self.sector_size, fsize - i * self.sector_size)
            out += _decompress(chunk, expected) if len(chunk) < expected else chunk
        return bytes(out)

    def names(self):
        if not self.has(LISTFILE):
            raise KeyError("archive has no (listfile); names cannot be recovered")
        text = self.read(LISTFILE).decode("utf-8", "replace")
        return [n for n in (line.strip() for line in text.splitlines()) if n]


def _decompress(chunk, expected):
    mask, payload = chunk[0], chunk[1:]
    if mask == 0x02:
        return zlib.decompress(payload)
    if mask == 0x10:
        return bz2.decompress(payload)
    raise NotImplementedError(f"compression mask 0x{mask:02x} is not supported")


def read_mpq(path):
    return MpqArchive(Path(path).read_bytes())


# ------------------------------------------------------------------ CLI

def _main(argv):
    if len(argv) < 2 or argv[0] not in ("list", "extract"):
        print(__doc__.strip().split("CLI:")[1])
        return 2
    archive = read_mpq(argv[1])
    print(f"format version {archive.format_version}, header {archive.header_size} bytes, "
          f"{len(archive.block_table)} blocks")
    for name in archive.names():
        pos, csize, fsize, flags = archive._find(name)
        if argv[0] == "list":
            print(f"  {fsize:>8}  {csize:>8}  0x{flags:08x}  {name}")
        else:
            dest = Path(argv[2]) / name.replace("\\", "/")
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(archive.read(name))
            print(f"  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(_main(sys.argv[1:]))
