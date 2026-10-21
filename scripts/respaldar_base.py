#!/usr/bin/env python3
"""Genera un respaldo fechado de la base PostgreSQL local de TesisMCP."""

from __future__ import annotations

import argparse
import hashlib
import subprocess
from datetime import datetime
from pathlib import Path


RAIZ = Path(__file__).resolve().parents[1]
DIRECTORIO_PREDETERMINADO = RAIZ / "respaldos"


def ejecutar(*argumentos: str, capturar: bool = False) -> None:
    subprocess.run(
        argumentos,
        check=True,
        stdout=subprocess.DEVNULL if capturar else None,
    )


def obtener_argumentos() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--contenedor", default="tesismcp-pg")
    parser.add_argument("--base", default="tesismcp")
    parser.add_argument("--usuario", default="tesismcp")
    parser.add_argument("--directorio", type=Path, default=DIRECTORIO_PREDETERMINADO)
    return parser.parse_args()


def main() -> int:
    opciones = obtener_argumentos()
    marca_temporal = datetime.now().astimezone().strftime("%Y-%m-%d_%H%M%S")
    nombre = f"{opciones.base}_respaldo_{marca_temporal}.dump"
    ruta_destino = opciones.directorio.resolve() / nombre
    ruta_contenedor = f"/tmp/{nombre}"

    opciones.directorio.mkdir(parents=True, exist_ok=True)
    if ruta_destino.exists():
        raise FileExistsError(f"El respaldo ya existe: {ruta_destino}")

    ejecutar(
        "podman", "exec", opciones.contenedor,
        "pg_dump", "-U", opciones.usuario, "-d", opciones.base,
        "-Fc", "-f", ruta_contenedor,
    )
    ejecutar(
        "podman", "exec", opciones.contenedor,
        "pg_restore", "-l", ruta_contenedor,
        capturar=True,
    )
    ejecutar("podman", "cp", f"{opciones.contenedor}:{ruta_contenedor}", str(ruta_destino))

    suma = hashlib.sha256(ruta_destino.read_bytes()).hexdigest()
    ruta_suma = ruta_destino.with_suffix(f"{ruta_destino.suffix}.sha256")
    ruta_suma.write_text(f"{suma}  {ruta_destino.name}\n", encoding="utf-8")

    print(f"Respaldo creado: {ruta_destino}")
    print(f"SHA-256: {suma}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
