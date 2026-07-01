#!/usr/bin/env python3

import json
from tf.app import use

# --------------------------------------------------
# Carrega o corpus oficial
# --------------------------------------------------

A = use("DT-UCPH/sp", silent=True)
api = A.api

F = api.F
T = api.T

# --------------------------------------------------
# Mapeamento oficial ETCBC → Unicode Samaritano
# (baseado em make_transcriptions.py + ajuste F)
# --------------------------------------------------

ETCBC_TO_SAMARITAN = {
    ">": "ࠀ",
    "B": "ࠁ",
    "G": "ࠂ",
    "D": "ࠃ",
    "H": "ࠄ",
    "W": "ࠅ",
    "Z": "ࠆ",
    "X": "ࠇ",
    "V": "ࠈ",
    "J": "ࠉ",
    "K": "ࠊ",
    "L": "ࠋ",
    "M": "ࠌ",
    "N": "ࠍ",
    "S": "ࠎ",
    "<": "ࠏ",
    "P": "ࠐ",
    "Y": "ࠑ",
    "Q": "ࠒ",
    "R": "ࠓ",
    # Shin + Sin não distinguem no samaritano
    "C": "ࠔ",
    "F": "ࠔ",

    "T": "ࠕ",
}

def to_samaritan(latin_word: str) -> str:
    """Converte transliteração ETCBC para Unicode Samaritano"""
    return "".join(
        ETCBC_TO_SAMARITAN.get(ch, "")
        for ch in latin_word
    )

# --------------------------------------------------
# Livros de saída
# --------------------------------------------------

BOOKS = {
    "Genesis": "GEN.json",
    "Exodus": "EXO.json",
    "Leviticus": "LEV.json",
    "Numbers": "NUM.json",
    "Deuteronomy": "DEU.json",
}

data = {b: [] for b in BOOKS}

current_book = None
current_chapter = None

# --------------------------------------------------
# Percorre todos os versículos
# --------------------------------------------------

for verse in F.otype.s("verse"):

    book, chapter, verse_num = T.sectionFromNode(verse)

    if book not in BOOKS:
        continue

    if book != current_book:
        current_book = book
        current_chapter = None

    if chapter != current_chapter:
        data[book].append([])
        current_chapter = chapter

    # --------------------------------------------------
    # renderização oficial do corpus
    # --------------------------------------------------
    words = []

    for w in T.words(verse):

        latin = F.g_cons.v(w)
        sam = to_samaritan(latin)

        trailer = F.trailer.v(w) or ""

        words.append(sam + trailer)

    text = "".join(words).strip()

    data[book][-1].append({
        "verse": str(verse_num),
        "text": text
    })

# --------------------------------------------------
# Exportação final
# --------------------------------------------------

for book, filename in BOOKS.items():

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(
            {"chapters": data[book]},
            f,
            ensure_ascii=False,
            indent=2
        )

    print(f"✓ {filename}")