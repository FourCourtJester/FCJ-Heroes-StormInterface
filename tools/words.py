"""Our own on-screen words, in every language the game has: gen.py writes them into each
language's GameStrings.txt as FCJH/<key>, and our layouts show them as @FCJH/<key>.

The English is ours, as it always was. The other languages are Blizzard's own words for the
same thing wherever the game has them (Jamie Phan's gamestrings, the key named beside each),
in capitals where the English is. Where Blizzard has no such words - the Towers town alert,
Alterac's camp alerts, the clone note - they are put together from Blizzard's names and
phrasing, by hand: those want a native speaker's eye (marked HAND below).
"""

LOCALES = ("deDE", "enUS", "esES", "esMX", "frFR", "itIT", "koKR", "plPL", "ptBR", "ruRU", "zhCN", "zhTW")


def _row(*texts):
    assert len(texts) == len(LOCALES), texts
    return dict(zip(LOCALES, texts))


def _upper(row):
    return {loc: text.upper() for loc, text in row.items()}


def _join(a, b, sep="  ·  "):
    return {loc: a[loc] + sep + b[loc] for loc in LOCALES}


# Blizzard's words (ScoreValue/Name/<score> unless said; <n/> and hyphenated breaks closed up)
HERO_DAMAGE = _row("Heldenschaden", "Hero Damage", "Daño a héroes", "Daño de héroe", "Dégâts de héros",
                   "Danni a eroi", "영웅 피해", "Obrażenia", "Dano de Herói", "Урон по героям", "英雄伤害", "英雄傷害")
SELF_HEALING = _row("Selbstheilung", "Self Healing", "Autosanación", "Autosanación", "Soins personnels",
                    "Cure su se stessi", "자신 치유", "Samoleczenie", "Autocura", "Оздоровление", "自我治疗", "治療自己")
# the halves of Healing's "Healing/Shielding" (French has one word, "Soutien": its PublishName
# Soins, and ProtectionGivenToAllies' Protections)
HEALING = _row("Heilung", "Healing", "Curación", "Sanación", "Soins", "Cure", "치유", "Leczenie", "Cura",
               "Исцеление", "治疗量", "治療")
SHIELDING = _row("Schilde", "Shielding", "Escudo", "Protección", "Protections", "Protezione", "방지", "Osłanianie",
                 "Proteção", "Щиты", "护盾吸收量", "護盾")
SIEGE = _row("Diener- und Gebäudeschaden", "Siege Damage", "Daño de asedio", "Daño de asedio", "Dégâts de siège",
             "Danni da assedio", "공성 피해", "Zniszczenia", "Dano de Cerco", "Осадный урон", "攻城伤害", "攻城傷害")
STRUCTURES = _row("Gebäudeschaden", "Structures", "Daño a estructuras", "Daño infligido a estructuras",
                  "Dégâts aux bâtiments", "Danni alle strutture", "구조물 피해", "Obrażenia budowli",
                  "Dano de Estrutura", "Урон по строениям", "建筑伤害", "建築傷害")
EXPERIENCE = _row("Erfahrung", "Experience", "Experiencia", "Experiencia", "Expérience", "Esperienza", "경험치",
                  "Doświadczenie", "Experiência", "Опыт", "经验值", "經驗值")   # UI/ScoreScreen/TotalExperience
# UI/HeroLeaderPanel/BlueTeam, RedTeam; Race/Name/Neut
BLUE_TEAM = _row("Blaues Team", "Blue Team", "Equipo azul", "Equipo azul", "Équipe bleue", "Squadra Blu", "파랑팀",
                 "Drużyna niebieskich", "Equipe Azul", "Синяя команда", "蓝队", "藍隊")
RED_TEAM = _row("Rotes Team", "Red Team", "Equipo rojo", "Equipo rojo", "Équipe rouge", "Squadra Rossa", "빨강팀",
                "Drużyna czerwonych", "Equipe Vermelha", "Красная команда", "红队", "紅隊")
# Button/Name/AbathurUltimateEvolution
ULTIMATE_EVOLUTION = _row("Ultimative Evolution", "Ultimate Evolution", "Evolución suprema", "Evolución máxima",
                          "Évolution ultime", "Evoluzione Definitiva", "최종 진화물", "Ostateczna Ewolucja",
                          "Evolução Final", "Венец эволюции", "终极进化", "終極進化")

WORDS = {
    # the inspect card's section heads (UI/HeroLeaderPanel/TalentsToggleButton, StatsToggleButton)
    "Inspect/Talents": _upper(_row("Talente", "Talents", "Talentos", "Talentos", "Talents", "Talenti", "특성",
                                   "Talenty", "Talentos", "Таланты", "天赋", "天賦")),
    "Inspect/Stats": _upper(_row("Statistiken", "Stats", "Estadísticas", "Estadísticas", "Statistiques",
                                 "Statistiche", "통계", "Statystyki", "Estatísticas", "Статистика", "统计", "統計")),
    # the inspect card's team line
    "Inspect/Blue": _upper(BLUE_TEAM),
    "Inspect/Red": _upper(RED_TEAM),
    "Inspect/Neutral": _upper(_row("Neutral", "Neutral", "Neutral", "Neutral", "Neutre", "Neutrale", "중립",
                                   "Neutralny", "Neutro", "Нейтральный", "中立", "中立")),
    # Abathur's clone, on its plate and its inspect card. HAND: Blizzard's Ultimate Evolution
    # tooltip calls it a clone, the word is ours
    "Clone": _row("KLON", "CLONE", "CLON", "CLON", "CLONE", "CLONE", "복제", "KOPIA", "CLONE", "КОПИЯ",
                  "复制体", "複製體"),
    # HAND, around Blizzard's names (Hero/Name/Abathur; Ultimate Evolution above)
    "Inspect/CloneNote": {loc: text.format(ue=ULTIMATE_EVOLUTION[loc]) for loc, text in _row(
        "Abathurs {ue}: keine Talente", "Abathur's {ue}: no talents", "{ue} de Abathur: sin talentos",
        "{ue} de Abathur: sin talentos", "{ue} d'Abathur : aucun talent", "{ue} di Abathur: nessun talento",
        "아바투르의 {ue}: 특성 없음", "{ue} Abatura: brak talentów", "{ue} de Abathur: sem talentos",
        "{ue} Абатура: нет талантов", "阿巴瑟的{ue}：无天赋", "阿巴瑟的{ue}：無天賦").items()},
    # the stats panes: titles, column heads (K/D/A kept but in Chinese and Korean, Blizzard's
    # Kills/Deaths/Assists there), the team bands (UI/TeamColor02, 01; Blizzard's team names in
    # Chinese and Korean, where the colour alone isn't a team's name)
    "Stats/KdaTitle": _join({loc: "KDA" for loc in LOCALES}, _upper(HERO_DAMAGE)),
    "Stats/HealingTitle": _join(_upper(HEALING), _upper(SHIELDING)),
    "Stats/StructuresTitle": _join(_upper(STRUCTURES), _upper(EXPERIENCE)),
    "Stats/K": _row("K", "K", "K", "K", "K", "K", "처치", "K", "K", "K", "击杀", "擊殺"),
    "Stats/D": _row("D", "D", "D", "D", "D", "D", "죽음", "D", "D", "D", "阵亡", "死亡"),
    "Stats/A": _row("A", "A", "A", "A", "A", "A", "지원", "A", "A", "A", "助攻", "助攻"),
    "Stats/HeroDamage": _upper(HERO_DAMAGE) | {"enUS": "HERO DMG"},
    "Stats/Self": _upper(SELF_HEALING) | {"enUS": "SELF"},
    "Stats/Healing": _upper(HEALING),
    "Stats/Shielding": _upper(SHIELDING),
    "Stats/Siege": _upper(SIEGE) | {"enUS": "SIEGE"},
    "Stats/Structures": _upper(STRUCTURES),
    # UI/PartyPanel/BonusExperience
    "Stats/XP": _row("EP", "XP", "EXP", "PE", "EXP", "PE", "XP", "PD", "EXP", "ОПЫТ", "XP", "經驗值"),
    "Stats/Blue": _row("BLAU", "BLUE", "AZUL", "AZUL", "BLEU", "BLU", "파랑팀", "NIEBIESKI", "AZUL", "СИНИЙ",
                       "蓝队", "藍隊"),
    "Stats/Red": _row("ROT", "RED", "ROJO", "ROJO", "ROUGE", "ROSSO", "빨강팀", "CZERWONY", "VERMELHO", "КРАСНЫЙ",
                      "红队", "紅隊"),
    # the replay panel's tab (UI/Replay_Control; French and Russian UI/Replay, the shorter;
    # the shortcut is layout.toml's)
    "Replay": {loc: text.upper() + "  Ctrl+Shift+R" for loc, text in _row(
        "Replay", "Replay", "Repetición", "Repetición", "Rejouer", "Replay", "리플레이", "Powtórka", "Replay",
        "Повтор", "观看录像", "戰鬥錄影").items()},
    # Towers of Doom: which team took a town. HAND: Blizzard's own alert is a player's ("ALLIES
    # CAPTURED", lib_MTOD_3069EA41) over its target; ours names the team, its target a fort
    # (Unit/Name/TownTownHallL2)
    "Towers/Blue": _row("Blaues Team eroberte", "Blue team captured", "El equipo azul ha capturado",
                        "El equipo azul capturó", "L'équipe bleue a capturé", "La squadra blu conquista",
                        "파랑팀 점령:", "Niebiescy zdobyli", "Equipe Azul capturou", "Синяя команда захватила",
                        "蓝队占领了", "藍隊佔領了"),
    "Towers/Red": _row("Rotes Team eroberte", "Red team captured", "El equipo rojo ha capturado",
                       "El equipo rojo capturó", "L'équipe rouge a capturé", "La squadra rossa conquista",
                       "빨강팀 점령:", "Czerwoni zdobyli", "Equipe Vermelha capturou", "Красная команда захватила",
                       "红队占领了", "紅隊佔領了"),
    "Towers/Town": _row("ein Fort", "a town", "un fuerte", "un fuerte", "un fort", "un forte", "요새", "fort",
                        "um forte", "форт", "堡垒", "堡壘"),
    # Alterac Pass's camp alerts, an observer's (blue Alliance, red Horde). HAND: from
    # Blizzard's player-facing camp alerts, with its faction names
    "Alterac/AllianceCapturing": _row(
        "Die Allianz nimmt ein Gefängnis der Horde ein", "Alliance capturing Horde camp",
        "La Alianza está capturando un campamento de la Horda", "La Alianza captura el campamento de la Horda",
        "L'Alliance capture un camp de la Horde", "L'Alleanza conquista un campo dell'Orda",
        "얼라이언스가 호드 수용소를 공격하고 있습니다", "Przymierze zajmuje więzienie Hordy",
        "Aliança capturando acampamento da Horda", "Альянс захватывает лагерь Орды", "联盟正在占领部落营地",
        "聯盟正在佔領部落營地"),
    "Alterac/HordeCapturing": _row(
        "Die Horde nimmt ein Gefängnis der Allianz ein", "Horde capturing Alliance camp",
        "La Horda está capturando un campamento de la Alianza", "La Horda captura el campamento de la Alianza",
        "La Horde capture un camp de l'Alliance", "L'Orda conquista un campo dell'Alleanza",
        "호드가 얼라이언스 수용소를 공격하고 있습니다", "Horda zajmuje więzienie Przymierza",
        "Horda capturando acampamento da Aliança", "Орда захватывает лагерь Альянса", "部落正在占领联盟营地",
        "部落正在佔領聯盟營地"),
    "Alterac/AllianceRetook": _row(
        "Die Allianz hat ihr Gefängnis zurückerobert", "Alliance retook their camp",
        "La Alianza ha recuperado su campamento", "La Alianza recapturó su campamento",
        "L'Alliance a repris son camp", "L'Alleanza ha riconquistato il suo campo", "얼라이언스가 수용소를 방어했습니다",
        "Przymierze odbiło więzienie", "A Aliança retomou seu acampamento", "Альянс отбил свой лагерь",
        "联盟夺回了营地", "聯盟已奪回營地"),
    "Alterac/HordeRetook": _row(
        "Die Horde hat ihr Gefängnis zurückerobert", "Horde retook their camp",
        "La Horda ha recuperado su campamento", "La Horda recapturó su campamento",
        "La Horde a repris son camp", "L'Orda ha riconquistato il suo campo", "호드가 수용소를 방어했습니다",
        "Horda odbiła więzienie", "A Horda retomou seu acampamento", "Орда отбила свой лагерь",
        "部落夺回了营地", "部落已奪回營地"),
}


def ref(english):
    """Our English words -> the @FCJH/<key> that shows them in the player's language."""
    keys = [key for key, row in WORDS.items() if row["enUS"] == english]
    assert len(keys) == 1, (english, keys)
    return f"@FCJH/{keys[0]}"
