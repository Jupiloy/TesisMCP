#!/usr/bin/env python3
"""
scripts/verify_project.py - Barrera Automática Determinista de Finalización (DoD Gate)
para TesisMCP (Edición Avance Capítulos 1 al 3: P01 a P12).

Comprobaciones ejecutadas:
1. Integridad del Sistema Django: manage.py check sin errores.
2. Integridad de Migraciones: manage.py makemigrations --check --dry-run sin discrepancias.
3. Esquema físico español en PostgreSQL: 17 tablas propias (15 modelos + 2 intermedias) y sus
   columnas, restricciones, índices, funciones y disparadores con nombres españoles.
4. Suite de Pruebas Automatizadas: pytest --reuse-db -q (100% verde).
5. Higiene de Repositorio: sin archivos sobredimensionados ni temporales.
6. Consistencia Código vs. Documentación:
   - Modelos Django exactos (15)
   - Migraciones activas (2)
   - Pasos metodológicos P01-P12 (12, Capítulos 1 al 3)
   - Herramientas MCP (17) y Prompts MCP (15)
   - Enlaces internos en Markdown 100% válidos (0 rotos)
7. Auditoría Adversaria de Contratos:
   - Validación estricta de esquemas Pydantic (SalidaEstricta, extra="forbid")
   - Cero mocks residuales en servicios de producción.
"""

import os
import re
import subprocess
import sys
import time
import urllib.parse
from pathlib import Path

SCRIPT_PATH = Path(__file__).resolve()
ROOT_DIR = SCRIPT_PATH.parent.parent
os.chdir(ROOT_DIR)

VENV_DIR = ROOT_DIR / ".venv"
if not VENV_DIR.exists():
    VENV_DIR = (ROOT_DIR.parent / ".venv").resolve()

VENV_PYTHON = VENV_DIR / "bin" / "python"
if VENV_PYTHON.exists() and sys.executable != str(VENV_PYTHON):
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(SCRIPT_PATH), *sys.argv[1:]])

sys.path.insert(0, str(ROOT_DIR / "backend"))
sys.path.insert(0, str(ROOT_DIR))

os.environ["DJANGO_DEBUG"] = "1"
os.environ["DJANGO_SETTINGS_MODULE"] = "config.settings"

ENV = os.environ.copy()
pythonpath = ENV.get("PYTHONPATH", "")
ENV["PYTHONPATH"] = f"{ROOT_DIR / 'backend'}:{ROOT_DIR}:{pythonpath}" if pythonpath else f"{ROOT_DIR / 'backend'}:{ROOT_DIR}"

VENV_PYTEST = VENV_DIR / "bin" / "pytest"
PYTEST_EXEC = str(VENV_PYTEST) if VENV_PYTEST.exists() else "pytest"
PYTHON_EXEC = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


class SuiteVerificacion:
    def __init__(self):
        self.results = []
        self.start_time = time.time()

    def registrar_resultado(self, category: str, test_name: str, passed: bool, details: str, duration: float):
        self.results.append({
            "category": category,
            "name": test_name,
            "passed": passed,
            "details": details,
            "duration": duration,
        })
        icon = f"{GREEN}✅ PASÓ{RESET}" if passed else f"{RED}❌ FALLÓ{RESET}"
        print(f"[{icon}] {CYAN}{category}{RESET} -> {BOLD}{test_name}{RESET} ({duration:.2f}s)")
        if not passed or "advertencia" in details.lower():
            color = RED if not passed else YELLOW
            print(f"       {color}↳ Detalle: {details}{RESET}")

    def ejecutar_comando(self, cmd: list[str], timeout: int = 120) -> tuple[int, str, str, float]:
        t0 = time.time()
        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                env=ENV,
                cwd=ROOT_DIR,
                timeout=timeout,
            )
            elapsed = time.time() - t0
            return res.returncode, res.stdout, res.stderr, elapsed
        except Exception as e:
            elapsed = time.time() - t0
            return 1, "", str(e), elapsed

    def verificar_salud_django(self):
        cmd = [PYTHON_EXEC, "backend/manage.py", "check"]
        code, out, err, elapsed = self.ejecutar_comando(cmd)
        passed = code == 0 and "no issues" in (out + err).lower()
        details = "0 errores o advertencias en configuración Django" if passed else (err or out).strip()[:200]
        self.registrar_resultado("Integridad Django", "manage.py check", passed, details, elapsed)

    def verificar_migraciones_django(self):
        cmd = [PYTHON_EXEC, "backend/manage.py", "makemigrations", "--check", "--dry-run"]
        code, out, err, elapsed = self.ejecutar_comando(cmd)
        passed = code == 0 and "no changes detected" in (out + err).lower()
        details = "0 discrepancias entre modelos y archivos de migración" if passed else (err or out).strip()[:200]
        self.registrar_resultado("Integridad Django", "makemigrations --check --dry-run", passed, details, elapsed)

    def verificar_esquema_fisico_espanol(self):
        t0 = time.time()
        errors = []

        try:
            import django
            django.setup()
            from django.apps import apps
            from django.db import connection

            modelos = list(apps.get_app_config("thesis").get_models())
            tablas_modelos = {modelo._meta.db_table for modelo in modelos}
            tablas_intermedias = {"tesis_usuario_grupo", "tesis_usuario_permiso"}
            tablas_esperadas = tablas_modelos | tablas_intermedias

            if len(tablas_esperadas) != 17:
                errors.append(
                    f"Contrato ORM inesperado: {len(tablas_esperadas)} tablas, esperadas 17"
                )
            tablas_no_espanolas = sorted(
                tabla for tabla in tablas_esperadas if not tabla.startswith("tesis_")
            )
            if tablas_no_espanolas:
                errors.append(f"Tablas ORM sin prefijo español: {tablas_no_espanolas}")

            columnas_esperadas = {
                modelo._meta.db_table: {campo.column for campo in modelo._meta.local_fields}
                for modelo in modelos
            }
            columnas_esperadas["tesis_usuario_grupo"] = {"id", "usuario_id", "grupo_id"}
            columnas_esperadas["tesis_usuario_permiso"] = {"id", "usuario_id", "permiso_id"}

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT table_name, column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                      AND starts_with(table_name, 'tesis_')
                    ORDER BY table_name, ordinal_position
                    """
                )
                columnas_reales = {}
                for tabla, columna in cursor.fetchall():
                    columnas_reales.setdefault(tabla, set()).add(columna)

                tablas_reales = set(columnas_reales)
                if tablas_reales != tablas_esperadas:
                    faltantes = sorted(tablas_esperadas - tablas_reales)
                    sobrantes = sorted(tablas_reales - tablas_esperadas)
                    errors.append(
                        f"Tablas físicas discrepantes; faltantes={faltantes}, sobrantes={sobrantes}"
                    )

                for tabla, esperadas in columnas_esperadas.items():
                    reales = columnas_reales.get(tabla, set())
                    if reales != esperadas:
                        errors.append(
                            f"Columnas discrepantes en {tabla}; "
                            f"faltantes={sorted(esperadas - reales)}, "
                            f"sobrantes={sorted(reales - esperadas)}"
                        )

                cursor.execute(
                    """
                    SELECT con.conname
                    FROM pg_constraint con
                    JOIN pg_class tabla ON tabla.oid = con.conrelid
                    JOIN pg_namespace ns ON ns.oid = tabla.relnamespace
                    WHERE ns.nspname = 'public'
                      AND starts_with(tabla.relname, 'tesis_')
                      AND NOT starts_with(con.conname, 'tesis_')
                    """
                )
                restricciones_no_espanolas = [fila[0] for fila in cursor.fetchall()]
                if restricciones_no_espanolas:
                    errors.append(
                        "Restricciones propias sin nombre español: "
                        f"{restricciones_no_espanolas[:5]}"
                    )

                cursor.execute(
                    """
                    SELECT indexname
                    FROM pg_indexes
                    WHERE schemaname = 'public'
                      AND starts_with(tablename, 'tesis_')
                      AND NOT starts_with(indexname, 'tesis_')
                    """
                )
                indices_no_espanoles = [fila[0] for fila in cursor.fetchall()]
                if indices_no_espanoles:
                    errors.append(
                        f"Índices propios sin nombre español: {indices_no_espanoles[:5]}"
                    )

                cursor.execute(
                    """
                    SELECT tg.tgname, procedimiento.proname
                    FROM pg_trigger tg
                    JOIN pg_class tabla ON tabla.oid = tg.tgrelid
                    JOIN pg_namespace ns ON ns.oid = tabla.relnamespace
                    JOIN pg_proc procedimiento ON procedimiento.oid = tg.tgfoid
                    WHERE ns.nspname = 'public'
                      AND starts_with(tabla.relname, 'tesis_')
                      AND NOT tg.tgisinternal
                    """
                )
                disparadores = dict(cursor.fetchall())
                disparadores_no_espanoles = [
                    nombre for nombre in disparadores if not nombre.startswith("tesis_")
                ]
                if disparadores_no_espanoles:
                    errors.append(
                        "Disparadores propios sin nombre español: "
                        f"{disparadores_no_espanoles}"
                    )

                disparadores_esperados = {
                    "tesis_revision_capitulo_solo_anexar": "tesis_rechazar_cambio_historial",
                    "tesis_evento_revision_solo_anexar": "tesis_rechazar_cambio_historial",
                }
                if disparadores != disparadores_esperados:
                    errors.append(
                        "Disparadores de inmutabilidad discrepantes; "
                        f"encontrados={disparadores}, esperados={disparadores_esperados}"
                    )

                cursor.execute(
                    """
                    SELECT procedimiento.proname
                    FROM pg_proc procedimiento
                    JOIN pg_namespace ns ON ns.oid = procedimiento.pronamespace
                    WHERE ns.nspname = 'public'
                      AND procedimiento.proname = 'tesis_rechazar_cambio_historial'
                    """
                )
                funciones = {fila[0] for fila in cursor.fetchall()}
                if funciones != {"tesis_rechazar_cambio_historial"}:
                    errors.append(
                        "No se encontró la función PostgreSQL "
                        "tesis_rechazar_cambio_historial"
                    )

            connection.close()
        except Exception as e:
            errors.append(f"No se pudo auditar PostgreSQL: {e}")

        elapsed = time.time() - t0
        passed = len(errors) == 0
        details = (
            "17 tablas propias; columnas, restricciones, índices, funciones y "
            "disparadores físicos en español"
            if passed else "; ".join(errors)
        )
        self.registrar_resultado(
            "Esquema PostgreSQL",
            "Nombres físicos íntegramente en español",
            passed,
            details,
            elapsed,
        )

    def verificar_suite_pytest(self):
        cmd = [PYTEST_EXEC, "--reuse-db", "-q"]
        code, out, err, elapsed = self.ejecutar_comando(cmd, timeout=180)
        m = re.search(r"(\d+)\s+passed", out)
        cantidad = int(m.group(1)) if m else None
        passed = (
            code == 0
            and "failed" not in out.lower()
            and cantidad == 32
        )
        details = (
            "Suite de pruebas superada al 100% (32 pruebas en verde)"
            if passed
            else f"Se esperaban 32 pruebas aprobadas; detectadas={cantidad}; {(err or out).strip()[:160]}"
        )
        self.registrar_resultado("Pruebas Unitarias/Integración", "Pytest Suite Completa", passed, details, elapsed)

    def verificar_higiene_repositorio(self):
        t0 = time.time()
        errors = []

        gitignore = ROOT_DIR / ".gitignore"
        if not gitignore.exists():
            errors.append("No existe archivo .gitignore en la raíz")
        else:
            gi_text = gitignore.read_text(encoding="utf-8")
            required_patterns = [
                ".venv/", "__pycache__/", "*.pyc", ".pytest_cache/",
                ".env", "var/", "graphify-out/cache/",
            ]
            for pat in required_patterns:
                if pat not in gi_text:
                    errors.append(f"Falta patrón obligatorio en .gitignore: '{pat}'")

        temp_files = []
        for pat in ["*.tmp", "*.swp", "*.bak", "*.orig", "*~"]:
            for tf in ROOT_DIR.glob(f"**/{pat}"):
                if "/.venv/" not in str(tf) and "/.git/" not in str(tf):
                    temp_files.append(str(tf.relative_to(ROOT_DIR)))
        if temp_files:
            errors.append(f"Residuos temporales encontrados: {', '.join(temp_files[:3])}")

        code, tracked_out, tracked_err, _ = self.ejecutar_comando(
            ["git", "ls-files"], timeout=15,
        )
        if code != 0:
            errors.append(f"No se pudo auditar git ls-files: {tracked_err.strip()[:120]}")
        else:
            tracked = tracked_out.splitlines()
            forbidden_tracked = [
                path for path in tracked
                if "__pycache__/" in path
                or path.endswith(".pyc")
                or "/.pytest_cache/" in f"/{path}"
                or Path(path).name in {".env", ".env.local"}
            ]
            if forbidden_tracked:
                errors.append(
                    f"Cachés o secretos rastreados: {forbidden_tracked[:3]}"
                )

        excluded_parts = {".git", ".venv", "__pycache__", ".pytest_cache"}
        archivos_proyecto = [
            path for path in ROOT_DIR.rglob("*")
            if path.is_file() and not excluded_parts.intersection(path.relative_to(ROOT_DIR).parts)
        ]
        if len(archivos_proyecto) > 250:
            errors.append(
                f"Explosión potencial de archivos: {len(archivos_proyecto)} archivos (máximo 250)"
            )
        archivos_grandes = [
            str(path.relative_to(ROOT_DIR))
            for path in archivos_proyecto
            if path.stat().st_size > 500 * 1024
        ]
        if archivos_grandes:
            errors.append(
                f"Archivos de código/documentación mayores a 500 KB: {archivos_grandes[:3]}"
            )

        dockerfile = ROOT_DIR / "Dockerfile"
        if dockerfile.exists():
            fuentes_copy = []
            for linea in dockerfile.read_text(encoding="utf-8").splitlines():
                partes = linea.strip().split()
                if len(partes) >= 3 and partes[0].upper() == "COPY":
                    fuentes_copy.extend(partes[1:-1])
            fuentes_inexistentes = [
                fuente for fuente in fuentes_copy
                if fuente != "." and not (ROOT_DIR / fuente).exists()
            ]
            if fuentes_inexistentes:
                errors.append(
                    f"Dockerfile copia fuentes inexistentes: {fuentes_inexistentes}"
                )

        elapsed = time.time() - t0
        passed = len(errors) == 0
        details = "Árbol limpio: sin residuos y con .gitignore íntegro" if passed else "; ".join(errors)
        self.registrar_resultado("Higiene de Repositorio", "Auditoría de Archivos y Fugas", passed, details, elapsed)

    def verificar_consistencia_documentacion_codigo(self):
        t0 = time.time()
        errors = []

        try:
            import django
            django.setup()
            from django.apps import apps
            thesis_models = list(apps.get_app_config("thesis").get_models())
            model_count = len(thesis_models)
            if model_count != 15:
                errors.append(f"Modelos Django discrepantes: encontrados {model_count}, esperados 15")
        except Exception as e:
            errors.append(f"Error importando modelos Django: {e}")

        mig_files = list((ROOT_DIR / "backend" / "thesis" / "migrations").glob("0*.py"))
        if len(mig_files) != 2:
            errors.append(f"Migraciones discrepantes: encontradas {len(mig_files)}, esperadas 2")

        try:
            import thesis.step_catalogue as sc
            steps_count = len(sc.CATALOGO_PASOS)
            chapters = sorted({info["capitulo"] for info in sc.CATALOGO_PASOS.values()})
            if steps_count != 12 or chapters != [1, 2, 3]:
                errors.append(f"Catálogo discrepante: {steps_count} pasos en capítulos {chapters}, esperados 12 en [1, 2, 3]")
        except Exception as e:
            errors.append(f"Error importando CATALOGO_PASOS: {e}")

        try:
            import mcp_server.server as mcp_srv
            tools_count = len(mcp_srv.app._tool_manager._tools)
            prompts_count = len(mcp_srv.app._prompt_manager._prompts)
            if tools_count != 17:
                errors.append(f"Herramientas MCP discrepantes: registradas {tools_count}, esperadas 17")
            if prompts_count != 15:
                errors.append(f"Prompts MCP discrepantes: registrados {prompts_count}, esperados 15")
        except Exception as e:
            errors.append(f"Error comprobando servidor MCP: {e}")

        broken_links = []
        docs_to_check = [ROOT_DIR / "README.md", *sorted((ROOT_DIR / "docs").glob("**/*.md"))]
        for doc in docs_to_check:
            text = doc.read_text(encoding="utf-8", errors="ignore")
            for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", text):
                link = m.group(2).strip()
                if link.startswith(("http://", "https://", "#", "mailto:")):
                    continue
                path_part = link.split("#")[0].strip()
                if not path_part:
                    continue
                path_part = urllib.parse.unquote(path_part)
                target = Path(path_part[7:]) if path_part.startswith("file://") else (doc.parent / path_part).resolve()
                if not target.exists():
                    broken_links.append(f"{doc.relative_to(ROOT_DIR)} -> {link}")

        if broken_links:
            errors.append(f"Enlaces Markdown rotos ({len(broken_links)}): {broken_links[:2]}")

        textos_docs = "\n".join(
            doc.read_text(encoding="utf-8", errors="ignore") for doc in docs_to_check
        )
        afirmaciones_obsoletas = [
            texto for texto in [
                "43 tests", "43 Tests", "43 pruebas", "FastMCP",
                "STALE_VERSION", "CHAPTER_APPROVED_LOCKED",
                "start_offset", "end_offset", "quoted_text",
                "guardar_envio_paso", "validar_carga_paso",
                "renderizar_markdown_capitulo", "topic_options",
                "instantanea_estructurada", "prefijo_clave",
                "TESISMCP_TOKEN_ACCESO", "POST /api/projects",
            ]
            if texto in textos_docs
        ]
        if afirmaciones_obsoletas:
            errors.append(
                f"Documentación contiene contratos obsoletos: {afirmaciones_obsoletas}"
            )

        settings_text = (ROOT_DIR / "backend" / "config" / "settings.py").read_text(encoding="utf-8")
        compose_text = (ROOT_DIR / "compose.yaml").read_text(encoding="utf-8")
        if "127.0.0.1:5434/tesismcp_reducido_docente" not in settings_text:
            errors.append("settings.py no usa por defecto el PostgreSQL aislado del puerto 5434")
        if '"127.0.0.1:5434:5432"' not in compose_text:
            errors.append("compose.yaml no publica PostgreSQL reducido en 127.0.0.1:5434")
        for servicio in ["postgres:", "backend:", "mcp:"]:
            if servicio not in compose_text:
                errors.append(f"compose.yaml no declara el servicio {servicio.rstrip(':')}")

        elapsed = time.time() - t0
        passed = len(errors) == 0
        details = (
            "15 modelos, 2 migraciones, 12 pasos (Cap. 1-3), 17 herramientas MCP, 15 prompts, "
            f"{len(docs_to_check)} docs Markdown con 0 links rotos"
        ) if passed else "; ".join(errors)
        self.registrar_resultado("Consistencia Doc-Código", "Sincronización de Cifras y Enlaces", passed, details, elapsed)

    def verificar_contratos_adversarios(self):
        t0 = time.time()
        errors = []

        try:
            from thesis.services.step_contracts import SalidaP01
            try:
                SalidaP01.model_validate({
                    "temas_propuestos": [
                        {
                            "id": i,
                            "titulo_tentativo": f"Tema tentativo de prueba {i}",
                            "pros": ["Pro verificado"],
                            "contras": ["Contra verificada"],
                            "viabilidad_preliminar": "ALTA",
                        } for i in range(1, 6)
                    ],
                    "tema_preseleccionado_id": 1,
                    "campo_espurio_prohibido": 123,
                })
                errors.append("SalidaP01 no rechazó un campo espurio (falla extra='forbid')")
            except Exception:
                pass

            try:
                SalidaP01.model_validate({
                    "temas_propuestos": [
                        {
                            "id": 1,
                            "titulo_tentativo": "Tema tentativo de prueba 1",
                            "pros": ["Pro verificado"],
                            "contras": ["Contra verificada"],
                            "viabilidad_preliminar": "ALTA",
                        }
                    ],
                    "tema_preseleccionado_id": 1,
                })
                errors.append("SalidaP01 aceptó lista menor a 5 temas")
            except Exception:
                pass
        except Exception as e:
            errors.append(f"Fallo importando/validando contratos Pydantic: {e}")

        service_mocks = []
        marcadores_ficticios = [
            "2501.00001", "mock_data_dummy", "example.invalid",
            "paper alucinado", "autor ficticio",
        ]
        production_roots = [
            ROOT_DIR / "backend" / "thesis" / "services",
            ROOT_DIR / "backend" / "thesis" / "integrations",
            ROOT_DIR / "mcp_server",
        ]
        for production_root in production_roots:
            for pyfile in production_root.rglob("*.py"):
                relative_parts = pyfile.relative_to(ROOT_DIR).parts
                if "demo" in relative_parts or "tests" in relative_parts or pyfile.name.startswith("test_"):
                    continue
                content = pyfile.read_text(encoding="utf-8").lower()
                if any(marker in content for marker in marcadores_ficticios):
                    service_mocks.append(str(pyfile.relative_to(ROOT_DIR)))
        if service_mocks:
            errors.append(f"Mocks residuales encontrados en servicios: {', '.join(service_mocks)}")

        elapsed = time.time() - t0
        passed = len(errors) == 0
        details = "Contratos Pydantic estrictos (extra='forbid') y 0 marcadores ficticios en producción" if passed else "; ".join(errors)
        self.registrar_resultado("Auditoría Adversaria", "Validación de Contratos y Cero Mocks", passed, details, elapsed)

    def ejecutar_todo(self) -> int:
        print("=" * 80)
        print(f"{BOLD}INICIANDO PUERTA AUTOMÁTICA DE VERIFICACIÓN — AVANCE CAPÍTULOS 1 AL 3{RESET}")
        print(f"Directorio Raíz: {ROOT_DIR}")
        print(f"Intérprete Python: {PYTHON_EXEC}")
        print("=" * 80)

        self.verificar_salud_django()
        self.verificar_migraciones_django()
        self.verificar_esquema_fisico_espanol()
        self.verificar_suite_pytest()
        self.verificar_higiene_repositorio()
        self.verificar_consistencia_documentacion_codigo()
        self.verificar_contratos_adversarios()

        total_elapsed = time.time() - self.start_time
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r["passed"])
        all_passed = passed_tests == total_tests

        print("\n" + "=" * 80)
        print(f"{BOLD}RESUMEN FINAL DE LA PUERTA DE VERIFICACIÓN (DoD){RESET}")
        print("=" * 80)
        print(f"Pruebas de Verificación: {passed_tests}/{total_tests} exitosas")
        print(f"Tiempo Total de Ejecución: {total_elapsed:.2f} segundos")

        if all_passed:
            print(f"\n{GREEN}{BOLD}VEREDICTO: [APROBADO_CON_EVIDENCIA / EXIT_CODE_0]{RESET}")
            print(f"{GREEN}Todas las garantías técnicas, de esquema español, de higiene y de contratos están cumplidas al 100%.{RESET}\n")
            return 0
        else:
            print(f"\n{RED}{BOLD}VEREDICTO: [RECHAZADO_CON_HALLAZGOS / EXIT_CODE_1]{RESET}")
            print(f"{RED}Existen comprobaciones fallidas. Prohibido reportar la tarea como concluida hasta corregirlas.{RESET}\n")
            return 1


if __name__ == "__main__":
    suite = SuiteVerificacion()
    sys.exit(suite.ejecutar_todo())
