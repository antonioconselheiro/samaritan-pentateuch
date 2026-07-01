#!/usr/bin/env python3

import json

from tf.app import use

# ----------------------------------------------------
# Carrega o corpus
# ----------------------------------------------------

A = use(
    "DT-UCPH/sp",
    silent=True,
)

api = A.api

F = api.F
T = api.T

# ----------------------------------------------------
# Livros
# ----------------------------------------------------

BOOKS = {
    "Genesis": "GEN.json",
    "Exodus": "EXO.json",
    "Leviticus": "LEV.json",
    "Numbers": "NUM.json",
    "Deuteronomy": "DEU.json",
}

books = {book: [] for book in BOOKS}

current_book = None
current_chapter = None

# ----------------------------------------------------
# Percorre todos os versículos
# ----------------------------------------------------

for verse_node in F.otype.s("verse"):

    book, chapter, verse = T.sectionFromNode(verse_node)

    if current_book != book:
        current_book = book
        current_chapter = None

    if current_chapter != chapter:
        books[book].append([])
        current_chapter = chapter

    # Renderização oficial do Text-Fabric
    text = T.text(verse_node).strip()

    books[book][-1].append(
        {
            "verse": str(verse),
            "text": text,
        }
    )

# ----------------------------------------------------
# Exportação
# ----------------------------------------------------

for book, filename in BOOKS.items():

    with open(
        filename,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            {
                "chapters": books[book]
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Exportado: {filename}")