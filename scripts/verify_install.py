#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Comprueba que el pack quedo REALMENTE instalado en esta maquina.

"Las copie" no es una verificacion. Un `cp` puede fallar a medias, dejar una
carpeta sin su SKILL.md, o copiar el arbol un nivel mas abajo del que toca --
y en ese caso las skills simplemente no aparecen, sin ningun error visible.

Este script compara el contenido del repo (la lista de lo que DEBERIA haber)
contra el directorio de skills instalado, y ademas valida que cada copia
instalada sea cargable, no solo que exista la carpeta.

Uso (desde el repo clonado):
    python scripts/verify_install.py
    python scripts/verify_install.py --target /ruta/a/.claude/skills

Salida: 0 si el pack esta completo y sano, 1 si falta o esta roto algo.
"""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate_skills import validate_skill  # noqa: E402  (misma logica, una sola fuente)

REPO_SKILLS = "skills"
REPO_TEMPLATES = "templates"


def listdirs(path: str) -> set:
    if not os.path.isdir(path):
        return set()
    return {n for n in os.listdir(path) if os.path.isdir(os.path.join(path, n)) and not n.startswith(".")}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        default=os.path.expanduser(os.path.join("~", ".claude", "skills")),
        help="directorio de skills instalado (por defecto ~/.claude/skills)",
    )
    parser.add_argument(
        "--templates-target",
        default=os.path.expanduser(os.path.join("~", ".claude", "templates")),
        help="directorio de templates instalado (por defecto ~/.claude/templates)",
    )
    args = parser.parse_args()

    if not os.path.isdir(REPO_SKILLS):
        print("ERROR: corre esto desde la raiz del repo clonado (no encuentro ./skills).")
        return 1

    expected = listdirs(REPO_SKILLS)
    installed = listdirs(args.target)

    if not installed:
        print("ERROR: no hay ninguna skill en %s" % args.target)
        print("       Revisa que la copia apuntara ahi y no a una subcarpeta.")
        return 1

    missing = sorted(expected - installed)
    # Lo "de mas" no es un error: puede tener skills propias o de terceros.
    extra = sorted(installed - expected)

    # Que la carpeta exista no basta: se valida cada copia instalada.
    broken: dict[str, list[str]] = {}
    for name in sorted(expected & installed):
        errors = validate_skill(args.target, name)
        if errors:
            broken[name] = errors

    print("Destino:   %s" % args.target)
    # ASCII puro: la consola por defecto de Windows usa cp1252 y convierte
    # cualquier caracter no-ASCII en un rombo negro ilegible.
    print("Esperadas: %d  |  Instaladas del pack: %d  |  Otras presentes: %d"
          % (len(expected), len(expected & installed), len(extra)))

    # Los templates son parte del pack: sin ellos los skills de marketing
    # funcionan a ciegas (pierden su esquema de intake y la metrica).
    templates_ok = True
    if os.path.isdir(REPO_TEMPLATES):
        expected_templates = []
        for dirpath, _, filenames in os.walk(REPO_TEMPLATES):
            for filename in filenames:
                rel = os.path.relpath(os.path.join(dirpath, filename), REPO_TEMPLATES)
                expected_templates.append(rel)
        missing_templates = [
            rel for rel in expected_templates
            if not os.path.isfile(os.path.join(args.templates_target, rel))
        ]
        if missing_templates:
            templates_ok = False
            print("Templates: FALTAN %d de %d en %s"
                  % (len(missing_templates), len(expected_templates), args.templates_target))
            for rel in sorted(missing_templates):
                print("    - %s" % rel.replace(os.sep, "/"))
        else:
            print("Templates: %d/%d presentes" % (len(expected_templates), len(expected_templates)))

    if missing:
        print("")
        print("FALTAN %d skills del pack:" % len(missing))
        for name in missing:
            print("    - %s" % name)

    if broken:
        print("")
        print("INSTALADAS PERO ROTAS (%d) -- se copiaron mal o quedaron incompletas:" % len(broken))
        for name in sorted(broken):
            for error in broken[name]:
                print("    - %s: %s" % (name, error))

    if missing or broken or not templates_ok:
        print("")
        print("El pack NO esta completo. Vuelve a copiar y ejecuta esto otra vez.")
        return 1

    print("")
    print("OK: las %d skills del pack estan instaladas y cargables." % len(expected))
    print("Reinicia Claude Code para que las lea.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
