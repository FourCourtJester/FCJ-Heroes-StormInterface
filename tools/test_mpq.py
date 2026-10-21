"""
Tests for tools/mpq.py: archives written raw and compressed read back byte for byte,
and compression stores each file the way the game is known to load (Spazzo's v40).

    python tools/test_mpq.py
"""

import os
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import mpq  # noqa: E402

FILES = {
    "Base.StormData/UI/Layout/A.StormLayout": b"<Desc>" + b"<Frame/>" * 3000 + b"</Desc>",
    "_Assets/Textures/B.dds": bytes(70000),                      # compresses to almost nothing
    "_Assets/Textures/C.dds": os.urandom(9000),                  # doesn't compress: stays raw
    "_Assets/Textures/D.dds": bytes(4096) + os.urandom(4096) + bytes(100),   # mixed sectors
    "Empty.txt": b"",
}


class MpqTests(unittest.TestCase):
    def roundtrip(self, compress):
        archive = mpq.MpqArchive(mpq.write_mpq(FILES, compress=compress))
        for name, data in FILES.items():
            self.assertEqual(archive.read(name), data, name)
        return archive

    def test_raw(self):
        archive = self.roundtrip(False)
        for name in FILES:
            self.assertFalse(archive._find(name)[3] & mpq.FILE_COMPRESS, name)

    def test_compressed(self):
        archive = self.roundtrip(True)
        self.assertEqual(archive.format_version, 0)
        self.assertEqual(archive.sector_size, 4096)
        flags = {name: archive._find(name)[3] for name in FILES}
        for name in ("Base.StormData/UI/Layout/A.StormLayout", "_Assets/Textures/B.dds",
                     "_Assets/Textures/D.dds"):
            self.assertEqual(flags[name], mpq.FILE_EXISTS | mpq.FILE_COMPRESS, name)
        for name in ("_Assets/Textures/C.dds", "Empty.txt"):
            self.assertEqual(flags[name], mpq.FILE_EXISTS, name)

    def test_sector_masks(self):
        # every compressed sector zlib (0x02); D's random sector stored raw, shorter by none
        archive = mpq.MpqArchive(mpq.write_mpq(FILES, compress=True))
        pos, csize, fsize, _ = archive._find("_Assets/Textures/D.dds")
        offsets = struct.unpack_from("<4I", archive.data, pos)
        sizes = [offsets[i + 1] - offsets[i] for i in range(3)]
        self.assertEqual(archive.data[pos + offsets[0]], 0x02)
        self.assertEqual(sizes[1], 4096)
        self.assertEqual(archive.data[pos + offsets[2]], 0x02)
        self.assertEqual(offsets[3], csize)


if __name__ == "__main__":
    unittest.main()
