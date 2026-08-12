"""
PPA — vigia_ediciones.py
Controla que las ediciones del día hayan salido de verdad.

Por qué: la Merienda del 6 de agosto de 2026 no salió y nadie se enteró. No
falló — directamente no existe la ejecución. Los crons de GitHub Actions no
garantizan puntualidad ni ejecución bajo carga, y el paso "Alerta si falló"
del workflow de ediciones solo avisa cuando el workflow corre y algo revienta.
Una corrida que nunca arranca no dispara nada: es el punto ciego.

Este script mira las corridas del workflow de ediciones del día y dice cuáles
de las esperadas no aparecieron. Sale con código 1 si falta alguna, así el
workflow que lo llama abre el aviso con el mismo mecanismo que ya se usa.

Cuenta como cumplida cualquier corrida exitosa en la ventana, sea del cron o
a mano: lo que importa es que la edición haya salido, no cómo se disparó.

Cómo se corre a mano:
    GH_TOKEN=... python scripts/vigia_ediciones.py
    GH_TOKEN=... python scripts/vigia_ediciones.py --ahora 2026-08-06T23:00
"""

import os
import sys
from datetime import datetime, timezone, timedelta

import requests

REPO = os.environ.get("GITHUB_REPOSITORY", "serfalco/ppa")
WORKFLOW = "edicion-merienda.yml"

# Las dos ediciones y su horario de cron, en UTC. Tiene que coincidir con
# .github/workflows/edicion-merienda.yml.
EDICIONES = [
    ("Desayuno", 9, 0),    # 06:00 ARG
    ("Merienda", 20, 15),  # 17:15 ARG
]

# Cuánto se le perdona a un cron antes de considerarlo ausente. GitHub avisa
# que puede demorar bajo carga, y se lo vio arrancar 45 minutos tarde: dos
# horas es holgado sin volverse inútil.
GRACIA = timedelta(hours=2)

# Una corrida puede arrancar unos minutos antes de su horario nominal; se la
# cuenta igual para la edición que le corresponde.
ADELANTO = timedelta(minutes=20)


def _api(ruta, token, **params):
    r = requests.get(
        f"https://api.github.com/repos/{REPO}/{ruta}",
        headers={"Authorization": f"Bearer {token}",
                 "Accept": "application/vnd.github+json"},
        params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def corridas_de_hoy(token, hoy):
    """Corridas del workflow de ediciones creadas hoy (UTC)."""
    j = _api(f"actions/workflows/{WORKFLOW}/runs", token,
             created=f">={hoy.isoformat()}", per_page=50)
    return j.get("workflow_runs", [])


def horario(hoy, hh, mm):
    return datetime(hoy.year, hoy.month, hoy.day, hh, mm, tzinfo=timezone.utc)


def revisar(corridas, ahora):
    """Devuelve (cumplidas, faltantes, no_vencidas) para el día de `ahora`.

    Una edición está cumplida si hay una corrida exitosa desde poco antes de
    su horario y antes del horario de la siguiente. Ese corte importa: sin él
    la corrida del Desayuno taparía a una Merienda que nunca salió.
    """
    hoy = ahora.date()
    marcas = [(nombre, horario(hoy, hh, mm)) for nombre, hh, mm in EDICIONES]

    exitosas = []
    for c in corridas:
        if c.get("conclusion") != "success":
            continue
        try:
            t = datetime.fromisoformat(c["created_at"].replace("Z", "+00:00"))
        except Exception:
            continue
        if t.date() == hoy:
            exitosas.append(t)

    cumplidas, faltantes, no_vencidas = [], [], []
    for i, (nombre, cuando) in enumerate(marcas):
        desde = cuando - ADELANTO
        hasta = marcas[i + 1][1] if i + 1 < len(marcas) else None

        if ahora < cuando + GRACIA:
            no_vencidas.append(nombre)
            continue

        hubo = any(t >= desde and (hasta is None or t < hasta)
                   for t in exitosas)
        (cumplidas if hubo else faltantes).append(nombre)

    return cumplidas, faltantes, no_vencidas


def main():
    ahora = datetime.now(timezone.utc)
    args = sys.argv[1:]
    if "--ahora" in args:
        i = args.index("--ahora")
        if i + 1 >= len(args):
            print("--ahora necesita una fecha: --ahora 2026-08-06T23:00")
            sys.exit(2)
        try:
            ahora = datetime.fromisoformat(args[i + 1]).replace(
                tzinfo=timezone.utc)
        except ValueError:
            print(f"No entiendo la fecha {args[i + 1]!r} "
                  "(se espera 2026-08-06T23:00).")
            sys.exit(2)

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Falta GH_TOKEN.")
        sys.exit(2)

    print(f"[Vigía] {ahora.strftime('%Y-%m-%d %H:%M UTC')} · {REPO}")
    try:
        corridas = corridas_de_hoy(token, ahora.date())
    except Exception as e:
        # No poder consultar no es lo mismo que una edición faltante: avisar
        # de menos es preferible a inventar una alerta por un 500 de GitHub.
        print(f"[Vigía] no pude consultar las corridas: {str(e)[:90]}")
        sys.exit(0)

    cumplidas, faltantes, no_vencidas = revisar(corridas, ahora)

    for n in cumplidas:
        print(f"   ✓ {n}")
    for n in no_vencidas:
        print(f"   · {n}: todavía no vence")
    for n in faltantes:
        print(f"   ✗ {n}: no salió")

    if faltantes:
        # Lo lee el workflow para armar el título del aviso.
        salida = os.environ.get("GITHUB_OUTPUT")
        if salida:
            with open(salida, "a", encoding="utf-8") as f:
                f.write(f"faltantes={', '.join(faltantes)}\n")
        print(f"[Vigía] FALTAN: {', '.join(faltantes)}")
        sys.exit(1)

    print("[Vigía] todo en orden")


if __name__ == "__main__":
    main()
