"""
services/ortografia.py
----------------------
Corrección ortográfica para los textos libres del voucher (concepto y
descripciones). Usa un diccionario de español y, encima, un diccionario PROPIO
del dominio (NNA, IGSS, CONACMI, KNH, viáticos…) para no marcar como error los
términos que sí son correctos en este contexto.

Es una ayuda, no un bloqueo: devuelve palabras dudosas con sugerencias para
que la persona decida. El arreglo de fondo sigue siendo el vocabulario
controlado del catálogo (los nombres de cuenta se eligen, no se teclean).
"""

import re
from functools import lru_cache
from pathlib import Path

from spellchecker import SpellChecker

DICCIONARIO_DOMINIO = Path(__file__).resolve().parent.parent / "data" / "diccionario_dominio.txt"
RE_PALABRA = re.compile(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]{3,}")


@lru_cache(maxsize=1)
def _corrector() -> SpellChecker:
    spell = SpellChecker(language="es")
    if DICCIONARIO_DOMINIO.exists():
        palabras = [
            w.strip().lower()
            for w in DICCIONARIO_DOMINIO.read_text(encoding="utf-8").splitlines()
            if w.strip()
        ]
        spell.word_frequency.load_words(palabras)
    return spell


def revisar(texto: str, max_sugerencias: int = 3) -> list[dict]:
    """Devuelve las palabras no reconocidas con sus sugerencias.

    [{ "palabra": "consultoria", "sugerencias": ["consultoría"] }, ...]
    """
    spell = _corrector()
    tokens = RE_PALABRA.findall(texto or "")
    desconocidas = spell.unknown(t.lower() for t in tokens)

    resultado = []
    vistas = set()
    for t in tokens:
        tl = t.lower()
        if tl in desconocidas and tl not in vistas:
            vistas.add(tl)
            candidatas = spell.candidates(tl) or set()
            sugerencias = sorted(c for c in candidatas if c != tl)[:max_sugerencias]
            resultado.append({"palabra": t, "sugerencias": sugerencias})
    return resultado
