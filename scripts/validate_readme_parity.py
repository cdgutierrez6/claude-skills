#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Falla si los dos bloques de idioma del README se han desincronizado.

Por que existe: el README es bilingue y cada cambio hay que aplicarlo dos veces.
Ya paso una vez -- el comando local de validacion se actualizo en un idioma y no
en el otro, y nada lo detecto. Es duplicacion deliberada (un lector no deberia
tener que saltar entre idiomas), pero la duplicacion sin verificacion deriva.

Que se exige identico:
  - la secuencia de bloques de codigo (mismo numero y mismo lenguaje, en orden)
  - el contenido EXACTO de los bloques `bash` y `powershell`: son comandos que
    la gente copia y pega, y no se traducen
  - los destinos de los enlaces markdown
  - el numero de subsecciones `###`

Que NO se exige identico, a proposito:
  - los bloques `mermaid` (las etiquetas de los nodos si se traducen)
  - los bloques sin lenguaje (ejemplos de prosa: "use X to review this PR")
  - el texto, obviamente

Los bloques se identifican por su orden en el documento (`<details>`): el
primero es el idioma principal y el segundo su espejo. No se busca el nombre del
idioma para no meter emoji ni acentos en este script.

Uso:
    python scripts/validate_readme_parity.py

Salida: 0 si los dos bloques estan sincronizados, 1 si han derivado.
"""

from __future__ import annotations

import io
import os
import re
import sys

README = "README.md"

RX_DETAILS = re.compile(r"<details[^>]*>(.*?)</details>", re.S)
RX_FENCE = re.compile(r"```([a-z]*)\n(.*?)```", re.S)
RX_LINK = re.compile(r"\]\(([^)]+)\)")
RX_SUBHEADING = re.compile(r"^###\s", re.M)

# Bloques cuyo contenido se copia y pega tal cual: no se traducen nunca.
EXECUTABLE = ("bash", "powershell", "sh", "console")


def main() -> int:
    if not os.path.isfile(README):
        print("ERROR: no encuentro %s (corre esto desde la raiz del repo)." % README)
        return 1

    with io.open(README, encoding="utf-8") as handle:
        text = handle.read()

    blocks = RX_DETAILS.findall(text)
    if len(blocks) != 2:
        print("ERROR: esperaba 2 bloques <details> (un idioma cada uno), encontre %d." % len(blocks))
        print("       Si has anadido o quitado un idioma, actualiza este validador.")
        return 1

    primary, mirror = blocks
    problems: list[str] = []

    fences_primary = RX_FENCE.findall(primary)
    fences_mirror = RX_FENCE.findall(mirror)

    kinds_primary = [kind or "(sin-lenguaje)" for kind, _ in fences_primary]
    kinds_mirror = [kind or "(sin-lenguaje)" for kind, _ in fences_mirror]

    if kinds_primary != kinds_mirror:
        problems.append(
            "la secuencia de bloques de codigo difiere:\n"
            "      idioma 1: %s\n"
            "      idioma 2: %s" % (kinds_primary, kinds_mirror)
        )
    else:
        # Solo tiene sentido comparar contenidos si la secuencia cuadra.
        for index, ((kind, body_primary), (_, body_mirror)) in enumerate(
            zip(fences_primary, fences_mirror)
        ):
            if kind in EXECUTABLE and body_primary.strip() != body_mirror.strip():
                problems.append(
                    "el bloque `%s` numero %d no es identico en los dos idiomas:\n"
                    "      idioma 1: %s\n"
                    "      idioma 2: %s"
                    % (
                        kind,
                        index + 1,
                        body_primary.strip().replace("\n", " ; ")[:120],
                        body_mirror.strip().replace("\n", " ; ")[:120],
                    )
                )

    links_primary = set(RX_LINK.findall(primary))
    links_mirror = set(RX_LINK.findall(mirror))
    only_primary = sorted(links_primary - links_mirror)
    only_mirror = sorted(links_mirror - links_primary)
    if only_primary:
        problems.append("enlaces presentes solo en el idioma 1: %s" % ", ".join(only_primary))
    if only_mirror:
        problems.append("enlaces presentes solo en el idioma 2: %s" % ", ".join(only_mirror))

    headings_primary = len(RX_SUBHEADING.findall(primary))
    headings_mirror = len(RX_SUBHEADING.findall(mirror))
    if headings_primary != headings_mirror:
        problems.append(
            "distinto numero de subsecciones `###`: idioma 1 tiene %d, idioma 2 tiene %d "
            "(se anadio una seccion en un solo idioma)" % (headings_primary, headings_mirror)
        )

    print("Bloques de codigo por idioma: %d y %d" % (len(fences_primary), len(fences_mirror)))
    print("Subsecciones por idioma:      %d y %d" % (headings_primary, headings_mirror))

    if not problems:
        print("OK: los dos bloques de idioma estan sincronizados.")
        return 0

    print("")
    print("DESINCRONIZADOS (%d):" % len(problems))
    for problem in problems:
        print("  - %s" % problem)
    print("")
    print("Aplica el cambio en AMBOS idiomas. El README es bilingue a proposito:")
    print("nadie deberia tener que saltar al otro idioma para encontrar un comando.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
