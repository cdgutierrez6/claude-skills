#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Falla si una skill documenta el VALOR de una credencial en vez de su nombre.

Por que existe, y por que asi: este repo publico llego a contener una API key
real -- `WAHA_KEY=<valor>` -- durante horas. Tres escaneos previos dijeron
"0 secretos" y los tres se equivocaron, porque buscaban PATRONES CONOCIDOS:
comillas alrededor del valor, o prefijos tipo `sk-` / `ghp_` / `AKIA`. Una
asignacion pelada, con un valor que no se parece a nada famoso, paso por debajo
de todos.

De ahi el diseno: **default-deny**. No se busca "lo que parece un secreto"; se
exige que el valor de toda variable con nombre de credencial sea un placeholder
RECONOCIBLE. Si no se reconoce, falla. Un falso positivo se resuelve escribiendo
un placeholder de verdad, que es lo que deberia haber ahi de todas formas; un
falso negativo se resuelve rotando una clave en produccion.

Cubre tres formas de escribir lo mismo:
    NOMBRE=valor            (shell / .env / bloque de texto)
    "NOMBRE": "valor"       (JSON)
    NOMBRE: valor           (YAML)
y las cadenas de conexion con credenciales embebidas (`scheme://user:pass@host`).

Uso:
    python scripts/validate_no_secrets.py

Salida: 0 si no hay valores reales, 1 si alguno no es un placeholder reconocible.
"""

from __future__ import annotations

import io
import os
import re
import sys

SCAN_DIRS = ("skills", "templates")

# Nombres que denotan una credencial. Deliberadamente amplio.
CREDENTIAL_NAME = re.compile(
    r"(?:^|[^A-Za-z0-9_])"
    r"([A-Za-z][A-Za-z0-9_]*"
    r"(?:KEY|SECRET|TOKEN|PASSWORD|PASSWD|PASS|CREDENTIAL|JWT|APIKEY)"
    r"[A-Za-z0-9_]*)",
    re.IGNORECASE,
)

ASSIGNMENTS = (
    re.compile(r"^\s*([A-Za-z][A-Za-z0-9_]*)\s*=\s*(\S.*?)\s*$"),          # NOMBRE=valor
    re.compile(r'"([A-Za-z][A-Za-z0-9_]*)"\s*:\s*"([^"]*)"'),               # "NOMBRE": "valor"
    re.compile(r"^\s*-?\s*([A-Za-z][A-Za-z0-9_]*)\s*:\s+(\S.*?)\s*$"),      # NOMBRE: valor (YAML)
)

# Cadena de conexion con usuario:clave embebidos.
CONNECTION = re.compile(r"[a-z][a-z0-9+.-]*://([^/\s:@]+):([^/\s@]+)@", re.IGNORECASE)

# Marcas que hacen a un valor reconociblemente falso. En minusculas.
PLACEHOLDER_MARKS = (
    "xxx", "yyy", "zzz", "...", "***", "____",
    "example", "ejemplo", "placeholder", "sample", "dummy", "fake",
    "your", "your-", "tu-", "tu_", "mi-", "changeme", "cambiame",
    "redacted", "rotar", "vacio", "empty", "none", "null", "todo",
    "abc123", "secret123", "clave", "password",
)


def es_placeholder(value: str) -> bool:
    """True si el valor es reconociblemente falso."""
    v = value.strip().strip(",;").strip()
    if not v or v in ('""', "''"):
        return True

    # Interpolaciones: el valor real vive fuera del fichero, que es lo correcto.
    if "${" in v or "{{" in v or "$env" in v or "os.environ" in v or "process.env" in v:
        return True
    # Marcadores angulares: <clave>, <vacio aqui>, <ROTAR - ...>
    if "<" in v and ">" in v:
        return True

    low = v.lower()
    if any(mark in low for mark in PLACEHOLDER_MARKS):
        return True

    # Un valor muy corto no es una credencial util.
    if len(v) < 8:
        return True

    return False


def scan_file(path: str) -> list[tuple[int, str, str]]:
    hallazgos: list[tuple[int, str, str]] = []
    with io.open(path, encoding="utf-8") as handle:
        for lineno, line in enumerate(handle, start=1):
            if len(line) > 400:      # tablas y bloques largos: no son asignaciones
                continue

            for rx in ASSIGNMENTS:
                for match in rx.finditer(line):
                    name, value = match.group(1), match.group(2)
                    if not CREDENTIAL_NAME.search(name):
                        continue
                    # Un comentario tras el valor no forma parte del valor.
                    value = re.split(r"\s+(?:#|//|<-|←)", value)[0].strip()
                    if not es_placeholder(value):
                        hallazgos.append((lineno, name, value))

            for match in CONNECTION.finditer(line):
                usuario, clave = match.group(1), match.group(2)
                if not es_placeholder(clave):
                    hallazgos.append((lineno, "cadena de conexion (%s:...)" % usuario, clave))

    return hallazgos


def main() -> int:
    total = 0
    fallos: list[str] = []

    for base in SCAN_DIRS:
        if not os.path.isdir(base):
            continue
        for dirpath, _, filenames in os.walk(base):
            for filename in filenames:
                if not filename.endswith((".md", ".json", ".yml", ".yaml", ".env", ".tmpl")):
                    continue
                path = os.path.join(dirpath, filename)
                total += 1
                for lineno, name, value in scan_file(path):
                    fallos.append("  - %s:%d  %s = %s"
                                  % (path.replace(os.sep, "/"), lineno, name, value))

    print("Ficheros revisados: %d" % total)
    if not fallos:
        print("OK: ninguna credencial con valor real.")
        return 0

    print("")
    print("VALORES QUE NO PARECEN PLACEHOLDER (%d):" % len(fallos))
    for f in fallos:
        print(f)
    print("")
    print("Documenta el NOMBRE de la variable, nunca su valor. Si es un ejemplo,")
    print("escribe un placeholder reconocible: <valor>, xxx, ${VAR} o vacio.")
    print("Si es una credencial real: quitala Y ROTALA -- el historial de git la")
    print("conserva aunque la borres del fichero.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
