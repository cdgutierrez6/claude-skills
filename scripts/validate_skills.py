#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Valida que cada skill del repo sea instalable por un tercero.

Por que existe: al publicar el repo se colaron cuatro fallos que en Windows son
invisibles pero rompen la instalacion en Linux y macOS:

  1. `saas-monetization-expert/skill.md` en minuscula. En un filesystem
     case-sensitive ese archivo no es `SKILL.md` y la skill no carga.
  2. Tres skills sin frontmatter YAML. Sin `description`, Claude no tiene con
     que decidir cuando dispararlas: se instalan pero nunca se activan.
  3. Descripciones escritas como escalar plano conteniendo ": ", que es YAML
     invalido. El parser falla y la skill se cae entera.
  4. `name` del frontmatter distinto del nombre de la carpeta.

Todo esto es verificable de forma deterministica, asi que vive aqui y no en la
memoria de quien haga el proximo commit.

Uso:
    python scripts/validate_skills.py [--skills-dir skills]

Salida: 0 si todo esta sano, 1 si hay al menos un error (lo que rompe el CI).
"""

from __future__ import annotations

import argparse
import io
import os
import sys

try:
    import yaml
except ImportError:  # pragma: no cover
    sys.exit("Falta PyYAML. Instalalo con:  pip install pyyaml")

# Una descripcion mas corta que esto no le da a Claude senales suficientes para
# decidir cuando disparar la skill. No es un capricho de estilo: una skill con
# `description: "DevOps"` se instala y nunca se activa.
MIN_DESCRIPTION_CHARS = 40

SKILL_FILENAME = "SKILL.md"


def read_frontmatter(path: str) -> tuple[dict | None, str | None]:
    """Devuelve (frontmatter, error). Solo uno de los dos es no-None."""
    try:
        with io.open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError as exc:
        return None, "no se pudo leer: %s" % exc

    if not text.startswith("---"):
        return None, "no empieza con un bloque frontmatter `---`"

    # Partimos en 3: lo previo al primer ---, el frontmatter, y el cuerpo.
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, "el bloque frontmatter no esta cerrado con `---`"

    try:
        data = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        # El caso tipico: `description: Actualo con: "x"`. Un escalar plano no
        # puede contener ": ". La solucion es un bloque plegado `description: >`.
        first_line = str(exc).splitlines()[0]
        return None, "frontmatter no es YAML valido (%s). Usa `description: >` en bloque." % first_line

    if not isinstance(data, dict):
        return None, "el frontmatter no es un mapa clave/valor"

    return data, None


def validate_skill(skills_dir: str, name: str) -> list[str]:
    """Valida una skill. Devuelve la lista de errores encontrados (vacia si OK)."""
    errors: list[str] = []
    skill_dir = os.path.join(skills_dir, name)

    if not os.path.isdir(skill_dir):
        return ["`%s` no es un directorio; cada skill debe ser una carpeta" % name]

    # Comparamos contra el listado real del directorio en vez de usar
    # os.path.exists: en Windows y macOS el filesystem es case-insensitive y
    # exists("SKILL.md") devuelve True aunque el archivo sea "skill.md".
    entries = os.listdir(skill_dir)
    if SKILL_FILENAME not in entries:
        variants = [e for e in entries if e.lower() == SKILL_FILENAME.lower()]
        if variants:
            errors.append(
                "el archivo se llama `%s`; debe ser exactamente `%s` "
                "(en Linux y macOS las mayusculas importan)" % (variants[0], SKILL_FILENAME)
            )
        else:
            errors.append("falta `%s`" % SKILL_FILENAME)
        return errors

    data, error = read_frontmatter(os.path.join(skill_dir, SKILL_FILENAME))
    if error:
        return [error]
    assert data is not None

    declared = data.get("name")
    if not declared or not str(declared).strip():
        errors.append("el frontmatter no declara `name`")
    elif str(declared).strip() != name:
        errors.append(
            "`name: %s` no coincide con la carpeta `%s`; Claude resuelve la skill "
            "por el nombre de la carpeta" % (declared, name)
        )

    description = data.get("description")
    if not description or not str(description).strip():
        errors.append("el frontmatter no declara `description`")
    elif len(str(description).strip()) < MIN_DESCRIPTION_CHARS:
        errors.append(
            "`description` tiene %d caracteres (minimo %d): demasiado vaga para que "
            "Claude sepa cuando disparar la skill"
            % (len(str(description).strip()), MIN_DESCRIPTION_CHARS)
        )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skills-dir", default="skills", help="ruta a la carpeta de skills")
    args = parser.parse_args()

    skills_dir = args.skills_dir
    if not os.path.isdir(skills_dir):
        print("ERROR: no existe el directorio `%s`" % skills_dir)
        return 1

    names = sorted(n for n in os.listdir(skills_dir) if not n.startswith("."))
    if not names:
        print("ERROR: `%s` esta vacio" % skills_dir)
        return 1

    # No hace falta un chequeo de `name` duplicado: la regla "name == nombre de
    # la carpeta" ya lo garantiza, porque el filesystem no permite dos carpetas
    # hermanas con el mismo nombre. Un chequeo aparte seria codigo inalcanzable.
    failures: dict[str, list[str]] = {}
    for name in names:
        errors = validate_skill(skills_dir, name)
        if errors:
            failures[name] = errors

    print("Skills revisadas: %d" % len(names))
    if not failures:
        print("OK: todas tienen SKILL.md, frontmatter YAML valido, `name` coincidente y `description` util.")
        return 0

    print("")
    print("FALLARON %d de %d:" % (len(failures), len(names)))
    for name in sorted(failures):
        for error in failures[name]:
            print("  - %s: %s" % (name, error))
    print("")
    print("Corrige lo anterior: una skill que falla aqui se instala pero no funciona.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
