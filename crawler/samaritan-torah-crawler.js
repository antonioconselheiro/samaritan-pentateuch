const booksNames = {
  'gn': 'GEN',
  'ex': 'EXO',
  'lv': 'LEV',
  'nm': 'NUM',
  'dt': 'DEU'
};

const booksContent = {
  GEN: {chapters:[]},
  EXO: {chapters:[]},
  LEV: {chapters:[]},
  NUM: {chapters:[]},
  DEU: {chapters:[]}
};

const Books = {
  gn: 50,
  ex: 40,
  lv: 27,
  nm: 36,
  dt: 34
};

const VersesPerChapter = {
  gn: [31, 25, 24, 26, 32, 22, 24, 22, 29, 32, 32, 20, 18, 24, 21, 16, 27, 33, 38, 18, 34, 24, 20, 67, 34, 35, 46, 22, 35, 43, 55, 33, 20, 31, 29, 43, 36, 30, 23, 23, 57, 38, 34, 34, 28, 34, 31, 22, 33, 26],
  ex: [22, 25, 22, 31, 23, 30, 25, 32, 35, 29, 10, 51, 22, 31, 27, 36, 16, 27, 25, 26, 37, 30, 33, 18, 40, 37, 21, 43, 46, 38, 18, 35, 23, 35, 35, 38, 29, 31, 43, 38],
  lv: [17, 16, 17, 35, 26, 23, 38, 36, 24, 20, 47, 8, 59, 57, 33, 34, 16, 30, 37, 27, 24, 33, 44, 23, 55, 46, 34],
  nm: [54, 34, 51, 49, 31, 27, 89, 26, 23, 36, 35, 16, 33, 45, 41, 35, 28, 32, 22, 29, 35, 41, 30, 25, 18, 65, 23, 31, 40, 16, 54, 42, 56, 29, 34, 13],
  dt: [46, 37, 29, 49, 33, 25, 26, 20, 29, 22, 32, 31, 19, 29, 23, 22, 20, 22, 21, 20, 23, 29, 26, 22, 19, 19, 26, 69, 29, 20, 30, 52, 29, 12]
};

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function fetchVerse(book, chapter, verse) {
  const url = `https://samaritantorah.com/${book}${chapter}-${verse}`;
  let attempts = 0;
  while (attempts < Infinity) {
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP error: ${res.status}`);
      const text = await res.text();
      console.log(`✅ Fetched verse ${book}, ${chapter}:${verse}`);
      const parser = new DOMParser();
      return parser.parseFromString(text, "text/html");
    } catch (err) {
      attempts++;
      console.error(err);

      if (/HTTP error: 404/.test(err.message)) {
        return null;
      } else {
        console.warn(`⚠️ Retry ${attempts} for verse ${book}, ${chapter}:${verse}`);
      }

      // VM1631:42  GET https://samaritantorah.com/gn31-55 404 (Not Found)
      await sleep(3000);
    }
  }
}

function getNextVerse(book, chapter, verse) {
  const bookOrder = Object.keys(Books);

  // Livro inválido
  if (!VersesPerChapter[book]) {
    return null;
  }

  const chapters = VersesPerChapter[book];
  const versesInChapter = chapters[chapter - 1];

  // Capítulo inválido
  if (!versesInChapter) {
    return null;
  }

  // Próximo versículo no mesmo capítulo
  if (verse < versesInChapter) {
    return [book, chapter, verse + 1];
  }

  // Primeiro versículo do próximo capítulo
  if (chapter < chapters.length) {
    return [book, chapter + 1, 1];
  }

  // Primeiro versículo do próximo livro
  const currentBookIndex = bookOrder.indexOf(book);

  if (currentBookIndex === -1 || currentBookIndex === bookOrder.length - 1) {
    return null; // Não existe próximo livro
  }

  const nextBook = bookOrder[currentBookIndex + 1];
  return [nextBook, 1, 1];
}

function getSamaritanText(html) {
    const entry = html.querySelector(".entry-content");
    if (!entry) return null;

    const SAMARITAN_CHAR = /[\u0800-\u0815]/u;
    const VALID_TEXT = /^[\u0800-\u0815\s\p{P}\p{S}\p{Pd}]+$/u;

    const marker = [...entry.querySelectorAll("p")]
        .find(p => /Samaritan Pentateuch/i.test(p.textContent));

    // Tenta obter o elemento imediatamente anterior ao marcador
    let candidate = marker?.previousElementSibling;

    // Fallback
    if (!candidate) {
        candidate = entry.querySelector("h2, h3");
    }

    if (!candidate) {
        console.warn("Nenhum candidato ao texto samaritano foi encontrado.");
        return null;
    }

    const text = candidate.textContent.trim();

    if (!SAMARITAN_CHAR.test(text)) {
        console.warn(
            "O texto candidato não contém nenhum caractere do bloco Unicode Samaritano.",
            text
        );
        return null;
    }

    if (!VALID_TEXT.test(text)) {
        console.warn(
            "O texto candidato contém caracteres fora do esperado.",
            text
        );
        return null;
    }

    return text;
}

async function loadRecusively() {
  const booksKeys = Object.keys(booksNames);
  let html, book = 'gn', chapter = 1, verse = 1;
  let hasNext;
  
  do {
    await sleep(5);
    console.info('⚡️ Fetching: ', book, chapter, verse);
    html = await fetchVerse(book, chapter, verse);
    let text = null;
    if (html) {
      text = getSamaritanText(html);
    }

    hasNext = getNextVerse(book, chapter, verse);
    booksContent[booksNames[book]].chapters[chapter - 1] = booksContent[booksNames[book]].chapters[chapter - 1] || [];

    if (!text) {
      console.warn(`⚠️ No Samaritan text found for ${book}, ${chapter}:${verse}`);
      booksContent[booksNames[book]].chapters[chapter - 1][verse - 1] = {
        verse, text: null
      };
      await sleep(3000);
    } else {
      booksContent[booksNames[book]].chapters[chapter - 1][verse - 1] = {
        verse, text
      };
    }

    if (hasNext) {
      [book, chapter, verse] = hasNext;
    }
  } while (hasNext);
  
  console.info(JSON.stringify(booksContent));
}

loadRecusively();
