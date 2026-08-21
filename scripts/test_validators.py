#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests de los validadores del repo.

Por que existe: los validadores son la unica red que impide publicar skills
rotas, y hasta ahora se habian probado a mano. Un validador que siempre pasa es
peor que no tener validador -- da una confianza que no ha ganado. Estos tests
inyectan cada modo de fallo conocido y exigen que se detecte, y ademas exigen
que un caso sano NO se marque (sin eso, un validador que siempre falla tambien
"pasaria" la mitad de la suite).

Cada modo de fallo probado aqui salio de un bug real de este repo:
  - `skill.md` en minuscula: se publico asi y en Linux no cargaba.
  - Skills sin frontmatter: se publicaron mudas, sin `description`.
  - `description` como escalar plano con ": ": YAML invalido, la skill se caia
    entera. Lo introdujo el propio arreglo del bug anterior.
  - Referencias externas sin documentar: el hueco que COMPATIBILIDAD.md cierra.
  - Instalacion a medias: carpeta copiada sin su SKILL.md, invisible con `ls`.
  - Una credencial REAL publicada: `WAHA_KEY=<valor>`. Tres escaneos previos
    dijeron "0 secretos" porque buscaban patrones conocidos.

Uso:
    python scripts/test_validators.py          # o: python -m unittest discover scripts
"""

from __future__ import annotations

import io
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from validate_skills import validate_skill  # noqa: E402

VALIDATE_REFS = os.path.join(HERE, "validate_external_refs.py")
VERIFY_INSTALL = os.path.join(HERE, "verify_install.py")
READ_PARITY = os.path.join(HERE, "validate_readme_parity.py")
NO_SECRETS = os.path.join(HERE, "validate_no_secrets.py")

# Larga a proposito: supera el minimo de caracteres, para que ningun test falle
# por un motivo distinto del que esta probando.
GOOD_DESCRIPTION = (
    "Actua como rol de prueba. Usalo para ejercitar el validador con una "
    "descripcion suficientemente larga y concreta."
)


def write(path: str, content: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Con `with`, no sin el: unittest activa los warnings por defecto y un
    # descriptor sin cerrar por cada fixture inunda la salida del CI con
    # ResourceWarning, escondiendo los fallos que si importan.
    with io.open(path, "w", encoding="utf-8", newline="") as handle:
        handle.write(content)


def make_skill(root: str, name: str, *, filename: str = "SKILL.md",
               declared: str | None = None, description: str | None = None,
               frontmatter: bool = True, raw: str | None = None) -> None:
    """Crea una skill en `root`. Los parametros permiten romperla a voluntad."""
    if raw is not None:
        write(os.path.join(root, name, filename), raw)
        return
    body = "\n# Cuerpo de la skill\n"
    if not frontmatter:
        write(os.path.join(root, name, filename), "# Titulo suelto\n" + body)
        return
    head = "---\nname: %s\ndescription: %s\n---\n" % (
        declared if declared is not None else name,
        description if description is not None else GOOD_DESCRIPTION,
    )
    write(os.path.join(root, name, filename), head + body)


def run(script: str, args: list[str], cwd: str) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, script] + args,
        cwd=cwd, capture_output=True, text=True,
    )
    return proc.returncode, proc.stdout + proc.stderr


class TestValidateSkills(unittest.TestCase):
    """validate_skill(): un error por cada forma conocida de romper una skill."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_skill_correcta_no_da_errores(self):
        # Control positivo: sin esto, un validador que siempre falla pasaria
        # todos los demas tests de esta clase.
        make_skill(self.root, "skill-buena")
        self.assertEqual(validate_skill(self.root, "skill-buena"), [])

    def test_nombre_de_archivo_en_minuscula(self):
        make_skill(self.root, "en-minuscula", filename="skill.md")
        errors = validate_skill(self.root, "en-minuscula")
        self.assertTrue(errors)
        self.assertIn("SKILL.md", errors[0])

    def test_sin_archivo_de_skill(self):
        os.makedirs(os.path.join(self.root, "vacia"))
        errors = validate_skill(self.root, "vacia")
        self.assertTrue(errors)
        self.assertIn("falta", errors[0].lower())

    def test_sin_frontmatter(self):
        make_skill(self.root, "sin-fm", frontmatter=False)
        errors = validate_skill(self.root, "sin-fm")
        self.assertTrue(errors)
        self.assertIn("frontmatter", errors[0])

    def test_yaml_invalido_por_dos_puntos_en_escalar_plano(self):
        # El bug real: `description: Activalo con: "x"`. Un escalar plano no
        # puede contener ": ". La solucion es un bloque plegado `description: >`.
        make_skill(self.root, "yaml-roto",
                   raw='---\nname: yaml-roto\ndescription: Activalo con: "algo" y rompe\n---\n')
        errors = validate_skill(self.root, "yaml-roto")
        self.assertTrue(errors)
        self.assertIn("YAML", errors[0])

    def test_bloque_plegado_si_admite_dos_puntos(self):
        # La contraparte del anterior: el formato correcto debe pasar.
        make_skill(self.root, "yaml-bien",
                   raw='---\nname: yaml-bien\ndescription: >\n  Actua como rol de prueba.\n'
                       '  Activalo con: "haz esto", "haz lo otro", y mas texto de relleno.\n---\n')
        self.assertEqual(validate_skill(self.root, "yaml-bien"), [])

    def test_name_distinto_de_la_carpeta(self):
        make_skill(self.root, "carpeta-x", declared="otro-nombre")
        errors = validate_skill(self.root, "carpeta-x")
        self.assertTrue(errors)
        self.assertIn("no coincide", errors[0])

    def test_description_demasiado_corta(self):
        make_skill(self.root, "corta", description="DevOps")
        errors = validate_skill(self.root, "corta")
        self.assertTrue(errors)
        self.assertIn("caracteres", errors[0])

    def test_description_ausente(self):
        make_skill(self.root, "sin-desc", raw="---\nname: sin-desc\n---\n")
        errors = validate_skill(self.root, "sin-desc")
        self.assertTrue(errors)
        self.assertIn("description", errors[0])


class TestValidateExternalRefs(unittest.TestCase):
    """El CI debe caerse si una referencia externa no esta en COMPATIBILIDAD.md."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        make_skill(os.path.join(self.root, "skills"), "skill-interna")
        os.makedirs(os.path.join(self.root, "templates"), exist_ok=True)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def cite(self, text: str) -> None:
        make_skill(os.path.join(self.root, "skills"), "que-cita",
                   raw="---\nname: que-cita\ndescription: %s\n---\n\n%s\n" % (GOOD_DESCRIPTION, text))

    def doc(self, text: str) -> None:
        write(os.path.join(self.root, "COMPATIBILIDAD.md"), "# Compatibilidad\n\n" + text + "\n")

    def test_todo_documentado_pasa(self):
        self.cite("Corre `/comando-externo` segun la REGLA #7.")
        self.doc("El comando `/comando-externo` se sustituye por X. La regla **#7** dice Y.")
        code, out = run(VALIDATE_REFS, [], self.root)
        self.assertEqual(code, 0, out)

    def test_comando_sin_documentar_falla(self):
        self.cite("Corre `/comando-externo` antes de nada.")
        self.doc("Aqui no se explica nada relevante.")
        code, out = run(VALIDATE_REFS, [], self.root)
        self.assertEqual(code, 1)
        self.assertIn("/comando-externo", out)

    def test_regla_sin_documentar_falla(self):
        self.cite("Aplica la REGLA #42 sin excepcion.")
        self.doc("Aqui no se explica nada relevante.")
        code, out = run(VALIDATE_REFS, [], self.root)
        self.assertEqual(code, 1)
        self.assertIn("#42", out)

    def test_wikilink_sin_destino_falla(self):
        self.cite("Ver [[nota-inexistente]] para el detalle.")
        self.doc("Aqui no se explica nada relevante.")
        code, out = run(VALIDATE_REFS, [], self.root)
        self.assertEqual(code, 1)
        self.assertIn("nota-inexistente", out)

    def test_comando_que_es_una_skill_del_repo_no_se_marca(self):
        self.cite("Invoca `/skill-interna` para esto.")
        self.doc("Nada que declarar.")
        code, out = run(VALIDATE_REFS, [], self.root)
        self.assertEqual(code, 0, out)

    def test_regla_6_no_se_da_por_documentada_por_existir_6_0(self):
        # Sin el lookahead negativo, "#6" haria match dentro de "#6.0" y una
        # regla realmente indocumentada pasaria inadvertida.
        self.cite("Aplica la REGLA #6 en cada revision.")
        self.doc("Solo se explica la regla **#6.0** sobre no borrar el core.")
        code, out = run(VALIDATE_REFS, [], self.root)
        self.assertEqual(code, 1)
        self.assertIn("#6", out)

    def test_wikilink_a_un_archivo_del_repo_no_se_marca(self):
        write(os.path.join(self.root, "templates", "medicion.md"), "# Medicion\n")
        self.cite("Ver [[medicion]] para el North Star.")
        self.doc("Nada que declarar.")
        code, out = run(VALIDATE_REFS, [], self.root)
        self.assertEqual(code, 0, out)


class TestVerifyInstall(unittest.TestCase):
    """Debe distinguir una instalacion completa de una copiada a medias."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name                       # hace de repo clonado
        self.repo_skills = os.path.join(self.root, "skills")
        for name in ("alfa", "beta", "gamma"):
            make_skill(self.repo_skills, name)
        write(os.path.join(self.root, "templates", "marketing", "medicion.md"), "# Medicion\n")

        self.target = os.path.join(self.root, "instalado", "skills")
        self.templates_target = os.path.join(self.root, "instalado", "templates")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def install(self, names, with_templates=True):
        for name in names:
            make_skill(self.target, name)
        if with_templates:
            write(os.path.join(self.templates_target, "marketing", "medicion.md"), "# Medicion\n")

    def check(self):
        return run(VERIFY_INSTALL, ["--target", self.target,
                                    "--templates-target", self.templates_target], self.root)

    def test_instalacion_completa_pasa(self):
        self.install(["alfa", "beta", "gamma"])
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_skill_faltante_falla(self):
        self.install(["alfa", "beta"])
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("gamma", out)

    def test_carpeta_copiada_sin_su_archivo_falla(self):
        # El caso invisible con `ls`: la carpeta esta, la skill no carga.
        self.install(["alfa", "beta", "gamma"])
        os.remove(os.path.join(self.target, "gamma", "SKILL.md"))
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("gamma", out)

    def test_templates_faltantes_fallan(self):
        self.install(["alfa", "beta", "gamma"], with_templates=False)
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("medicion", out)

    def test_skills_ajenas_presentes_no_son_error(self):
        # Quien instala puede tener skills propias o de terceros: sobrar no es
        # un fallo, solo faltar lo es.
        self.install(["alfa", "beta", "gamma"])
        make_skill(self.target, "skill-de-un-tercero")
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_destino_vacio_falla_con_mensaje_claro(self):
        os.makedirs(self.target, exist_ok=True)
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("ninguna skill", out)


class TestNoSecrets(unittest.TestCase):
    """Ninguna skill puede documentar el VALOR de una credencial.

    El caso historico: este repo publico contuvo `WAHA_KEY=<valor real>` durante
    horas, y tres escaneos previos dijeron "0 secretos" porque buscaban patrones
    conocidos (comillas, prefijos `sk-`/`ghp_`). El validador invierte la carga:
    el valor debe ser un placeholder RECONOCIBLE o falla.
    """

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def skill_con(self, cuerpo: str) -> None:
        write(os.path.join(self.root, "skills", "caso", "SKILL.md"),
              "---\nname: caso\ndescription: %s\n---\n\n%s\n" % (GOOD_DESCRIPTION, cuerpo))

    def check(self):
        return run(NO_SECRETS, [], self.root)

    def test_el_caso_historico_se_detecta(self):
        # La regresion exacta que motivo este validador: una variable con nombre
        # de credencial asignada a un valor con forma de <palabra><anio><palabra>,
        # sin comillas y sin ningun prefijo famoso.
        #
        # El valor de abajo es INVENTADO a proposito. La primera version de este
        # test uso el valor real, y asi el test que impide publicar la clave la
        # publicaba el. Un fixture de credencial se fabrica, nunca se copia de
        # produccion.
        self.skill_con("WAHA_KEY=marcaficticia2020palabra")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("WAHA_KEY", out)

    def test_placeholders_habituales_no_se_marcan(self):
        # Control negativo amplio: si esto falla, el validador es inusable y
        # acabaria desactivado, que es peor que no tenerlo.
        self.skill_con(
            "RESEND_API_KEY=re_xxx\n"
            "ANTHROPIC_API_KEY=sk-ant-xxx\n"
            "STRIPE_SECRET_KEY=sk_live_xxx\n"
            "INTERNAL_API_KEY=<vacio aqui>\n"
            "JWT_SECRET=${JWT_SECRET}\n"
            "DB_PASSWORD=\n"
            "WEBHOOK_SECRET=tu-clave-aqui\n"
        )
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_token_con_pinta_de_real_en_json(self):
        self.skill_con('{ "env": { "API_TOKEN": "ghp_realLookingTokenValue123456" } }')  # secreto-de-prueba
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("API_TOKEN", out)

    def test_clave_dentro_de_una_cadena_de_conexion(self):
        self.skill_con('conn = "postgresql://usuario:Cl4v3Real2026Larga@host:5432/db"')  # secreto-de-prueba
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("conexion", out)

    def test_conexion_con_clave_placeholder_no_se_marca(self):
        self.skill_con('conn = "postgresql://usuario:password@host:5432/db"')
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_variable_yaml(self):
        self.skill_con("env:\n  API_SECRET: valorRealQueNoDeberiaEstarAqui")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("API_SECRET", out)

    def test_tambien_mira_dentro_de_scripts(self):
        # La credencial real acabo en scripts/, no en skills/, cuando la copie
        # como fixture. Si el validador no se escanea a si mismo, ese es
        # exactamente el sitio donde vuelve a colarse.
        write(os.path.join(self.root, "scripts", "algo.py"),
              "WAHA_KEY=marcainventada2019palabra")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("scripts/algo.py", out.replace(os.sep, "/"))

    def test_la_marca_de_fixture_declara_la_excepcion(self):
        # Un fixture necesita una cadena con forma de credencial. La marca lo
        # declara de forma visible en el diff, en vez de esconder la excepcion
        # dentro de la logica del validador.
        write(os.path.join(self.root, "scripts", "test_algo.py"),
              "WAHA_KEY=marcainventada2019palabra  # secreto-de-prueba")
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_variable_sin_nombre_de_credencial_no_se_mira(self):
        # Solo importan las que denotan credencial; lo demas es ruido.
        self.skill_con("BASE_URL=https://ejemplo-de-un-host-cualquiera.com/api/v1")
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_comentario_tras_el_valor_no_cuenta_como_valor(self):
        self.skill_con("WAHA_KEY=<rotar>   # el valor vive en el gestor de secretos")
        code, out = self.check()
        self.assertEqual(code, 0, out)


class TestReadmeParity(unittest.TestCase):
    """Los dos bloques de idioma del README no pueden derivar en silencio."""

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def readme(self, primary: str, mirror: str) -> None:
        write(os.path.join(self.root, "README.md"),
              "# Titulo\n\n<details open>\n<summary><h2>Uno</h2></summary>\n\n%s\n\n</details>\n\n"
              "<details>\n<summary><h2>Dos</h2></summary>\n\n%s\n\n</details>\n" % (primary, mirror))

    def check(self):
        return run(READ_PARITY, [], self.root)

    def test_bloques_sincronizados_pasan(self):
        body = "### Seccion\n\n```bash\npython algo.py\n```\n\nVer [doc](COMPATIBILIDAD.md).\n"
        self.readme(body, body)
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_comando_distinto_falla(self):
        # El bug real: se actualizo el comando en un idioma y no en el otro.
        self.readme("### A\n\n```bash\npython uno.py && python dos.py\n```\n",
                    "### A\n\n```bash\npython uno.py\n```\n")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("bash", out)

    def test_secuencia_de_bloques_distinta_falla(self):
        self.readme("### A\n\n```bash\nls\n```\n\n```powershell\nGet-ChildItem\n```\n",
                    "### A\n\n```bash\nls\n```\n")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("secuencia", out)

    def test_enlace_en_un_solo_idioma_falla(self):
        self.readme("### A\n\nVer [doc](COMPATIBILIDAD.md) y [otro](scripts/x.py).\n",
                    "### A\n\nVer [doc](COMPATIBILIDAD.md).\n")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("scripts/x.py", out)

    def test_seccion_anadida_en_un_solo_idioma_falla(self):
        self.readme("### A\n\ntexto\n\n### B\n\nmas texto\n", "### A\n\ntexto\n")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("subsecciones", out)

    def test_mermaid_traducido_no_es_error(self):
        # Las etiquetas de los nodos SI se traducen: marcarlo seria un falso
        # positivo que obligaria a dejar el diagrama en un solo idioma.
        self.readme('### A\n\n```mermaid\nflowchart LR\n  A["Parallel review"]\n```\n',
                    '### A\n\n```mermaid\nflowchart LR\n  A["Revision paralela"]\n```\n')
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_bloque_sin_lenguaje_traducido_no_es_error(self):
        # Son ejemplos de prosa ("use X to review this PR"), no comandos.
        self.readme("### A\n\n```\nuse tech-lead-senior to review this PR\n```\n",
                    "### A\n\n```\nusa tech-lead-senior para revisar este PR\n```\n")
        code, out = self.check()
        self.assertEqual(code, 0, out)

    def test_numero_de_bloques_de_idioma_inesperado_falla(self):
        write(os.path.join(self.root, "README.md"),
              "# Titulo\n\n<details>\n<summary>Solo uno</summary>\n\ntexto\n\n</details>\n")
        code, out = self.check()
        self.assertEqual(code, 1)
        self.assertIn("2 bloques", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
