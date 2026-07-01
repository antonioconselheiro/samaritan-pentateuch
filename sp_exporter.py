#!/usr/bin/env python3

import json
import os

from tf.app import use

# ---------------------------------------------------------
# Carrega o corpus da Torá Samaritana
# ---------------------------------------------------------

A = use("DT-UCPH/sp", silent=True)
api = A.api

F = api.F
L = api.L
T = api.T

# ---------------------------------------------------------
# Nomes desejados para os arquivos
# ---------------------------------------------------------

BOOKS = {
    "Genesis": "GEN.json",
    "Exodus": "EXO.json",
    "Leviticus": "LEV.json",
    "Numbers": "NUM.json",
    "Deuteronomy": "DEU.json",
}

# ---------------------------------------------------------
# Estrutura inicial
# ---------------------------------------------------------

books = {}

for book in BOOKS:
    books[book] = []

# ---------------------------------------------------------
# Percorre todos os versículos
# ---------------------------------------------------------

current_book = None
current_chapter = None

for verse_node in F.otype.s("verse"):

    book, chapter, verse = T.sectionFromNode(verse_node)

    # monta o texto do versículo

    words = []

    for word in L.d(verse_node, otype="word"):

        w = F.g_cons_utf8.v(word)

        trailer = F.trailer.v(word) or ""

        words.append(w + trailer)

    text = "".join(words).strip()

    # mudou de livro

    if current_book != book:

        current_book = book
        current_chapter = None

    # mudou de capítulo

    if current_chapter != chapter:

        books[book].append([])

        current_chapter = chapter

    books[book][-1].append(
        {
            "verse": str(verse),
            "text": text,
        }
    )

# ---------------------------------------------------------
# Exporta
# ---------------------------------------------------------

for book, filename in BOOKS.items():

    data = {
        "chapters": books[book]
    }

    with open(
        filename,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"✓ {filename}")