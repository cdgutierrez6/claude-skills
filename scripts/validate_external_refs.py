#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Falla si una skill cita algo externo al repo que COMPATIBILIDAD.md no explica.

Por que existe: las skills salieron de una instalacion concreta y citan comandos
(`/sdd`), reglas de un CLAUDE.md privado (`REGLA #6.0`) y notas personales
(`[[medicion]]`). Ninguna referencia rompe una skill -- Claude las lee como
prosa -- pero para quien clona el repo son huecos: lee "por REGLA #6.0 no borres
el core" y no tiene forma de saber que es eso.

COMPATIBILIDAD.md documenta cada una. El problema de un documento asi es que
envejece en silencio: se anade una skill que cita `/opsx`, nadie actualiza el
doc, y el hueco vuelve sin que salte ninguna alarma. Eso es exactamente lo que
la REGLA #9 manda convertir en test en vez de dejarlo como nota.

El registro vive en COMPATIBILIDAD.md, no en una allowlist dentro de este
script: lo que se declara "documentado" tiene que ser legible y revisable por
un humano en el PR, no estar escondido en codigo.

Uso:
    python scripts/validate_external_refs.py

Salida: 0 si toda referencia externa esta documentada, 1 si alguna no lo esta.
"""

from __future__ import annotations

import io
import os
import re
import sys

SCAN_DIRS = ("skills", "templates")
DOC = "COMPATIBILIDAD.md"

# `/algo` entre backticks. Si `algo` es una carpeta de skills/ es interno.
RX_COMMAND = re.compile(r"`(/[a-z][a-z0-9-]{2,})`")
# "REGLA #6.0" / "Regla #0". Se normaliza al numero: el doc los tabula como
# "**#6.0 - ...**", sin repetir la palabra REGLA en cada fila.
RX_RULE = re.compile(r"\bREGLA\s+(#[0-9]+(?:\.[0-9]+)?)", re.IGNORECASE)
RX_WIKILINK = re.compile(r"\[\[([a-z0-9-]+)\]\]")


def iter_markdown(root: str):
    for base in SCAN_DIRS:
        if not os.path.isdir(base):
            continue
        for dirpath, _, filenames in os.walk(base):
            for filename in filenames:
                if filename.endswith(".md"):
                    yield os.path.join(dirpath, filename)


def collect(root: str) -> tuple[dict, set, set]:
    """Devuelve (referencias -> ubicaciones, skills del repo, basenames del repo)."""
    skills = {
        name for name in os.listdir("skills")
        if os.path.isdir(os.path.join("skills", name))
    } if os.path.isdir("skills") else set()

    basenames = set()
    for path in iter_markdown(root):
        basenames.add(os.path.splitext(os.path.basename(path))[0])

    refs: dict[tuple[str, str], list[str]] = {}

    def note(kind: str, value: str, path: str, lineno: int):
        refs.setdefault((kind, value), []).append("%s:%d" % (path.replace(os.sep, "/"), lineno))

    for path in iter_markdown(root):
        with io.open(path, encoding="utf-8") as handle:
            for lineno, line in enumerate(handle, start=1):
                for match in RX_COMMAND.finditer(line):
                    command = match.group(1)
                    if command.lstrip("/") not in skills:
                        note("comando", command, path, lineno)
                for match in RX_RULE.finditer(line):
                    note("regla", match.group(1), path, lineno)
                for match in RX_WIKILINK.finditer(line):
                    target = match.group(1)
                    if target not in basenames:
                        note("nota", "[[%s]]" % target, path, lineno)

    return refs, skills, basenames


def is_documented(kind: str, value: str, doc: str) -> bool:
    if kind == "regla":
        # `#6` no debe darse por documentado solo porque exista `#6.0`.
        return re.search(re.escape(value) + r"(?![0-9.])", doc) is not None
    return value in doc


def main() -> int:
    if not os.path.isfile(DOC):
        print("ERROR: falta %s, que es donde se documentan las referencias externas." % DOC)
        return 1

    with io.open(DOC, encoding="utf-8") as handle:
        doc = handle.read()
    refs, skills, _ = collect(".")

    undocumented = {
        key: locations for key, locations in refs.items()
        if not is_documented(key[0], key[1], doc)
    }

    print("Skills en el repo: %d" % len(skills))
    print("Referencias externas encontradas: %d" % len(refs))

    if not undocumented:
        print("OK: todas estan explicadas en %s." % DOC)
        return 0

    print("")
    print("SIN DOCUMENTAR en %s (%d):" % (DOC, len(undocumented)))
    for (kind, value), locations in sorted(undocumented.items()):
        shown = ", ".join(locations[:3])
        if len(locations) > 3:
            shown += " (+%d mas)" % (len(locations) - 3)
        print("  - [%s] %s  ->  %s" % (kind, value, shown))
    print("")
    print("Anade cada una a %s explicando que era y con que sustituirla." % DOC)
    # Salida en ASCII puro a proposito: la consola por defecto de Windows usa
    # cp1252 y convierte cualquier acento en un rombo negro ilegible.
    print("Si alguna NO es una referencia real (una ruta URL dentro de un")
    print("ejemplo de codigo), declarala igual ahi: el documento es el registro.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
