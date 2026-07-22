"""
PPA — historico.py
Memoria acumulativa del sistema (Fase A del documento rector).

Lee data/datos.json (el estado actual que arma datos_economicos.py) y
apendea una observación por indicador y por día en:

    data/historico/{clave}.jsonl

Formato de cada línea (JSONL, una observación por línea):

    {"fecha": "2026-07-22", "valor": 419, "unidad": "pb",
     "fuente": "argentinadatos.com", "capturado_en": "..."}

Reglas:
  - Solo registra valores FRESCOS (stale=False). Un valor conservado
    pertenece a un día anterior y ya está en el histórico.
  - Una observación por día y por indicador: si el script corre varias
    veces el mismo día (cron horario de mercado), REEMPLAZA la última
    línea del día con el valor más reciente. El histórico queda con el
    valor de cierre de cada jornada.
  - Nunca rompe la edición: cualquier error se reporta y sigue.
  - Los valores compuestos (dólares compra/venta, banda) se guardan
    tal cual: el que grafica decide qué campo usar.

Este archivo es la base de: rachas, máximos/mínimos, récords, La Data
del Día narrada, detección de anomalías y auditoría.

Cómo se corre:
    python scripts/historico.py
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA

TZ_AR = timezone(timedelta(hours=-3))
JSON_DATOS = os.path.join(DIR_DATA, "datos.json")
DIR_HISTORICO = os.path.join(DIR_DATA, "historico")


def fecha_de_captura(salida):
    """Fecha (AR) a la que pertenece la observación. Sale del generado_en
    del datos.json — no del reloj — para que una corrida sobre datos
    viejos no invente observaciones de hoy."""
    try:
        t = datetime.fromisoformat(salida["generado_en"].replace("Z", "+00:00"))
        return t.astimezone(TZ_AR).strftime("%Y-%m-%d")
    except Exception:
        return datetime.now(TZ_AR).strftime("%Y-%m-%d")


def leer_jsonl(ruta):
    """Lee un JSONL completo. Lista vacía si no existe o está roto."""
    if not os.path.exists(ruta):
        return []
    filas = []
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    filas.append(json.loads(linea))
                except json.JSONDecodeError:
                    continue  # línea corrupta: se ignora, no se rompe
    except Exception:
        return []
    return filas


def escribir_jsonl(ruta, filas):
    tmp = ruta + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for fila in filas:
            f.write(json.dumps(fila, ensure_ascii=False) + "\n")
    os.replace(tmp, ruta)  # escritura atómica: nunca queda a medias


def registrar(clave, item, fecha_hoy):
    """Registra (o actualiza) la observación de hoy para un indicador."""
    ruta = os.path.join(DIR_HISTORICO, f"{clave}.jsonl")
    filas = leer_jsonl(ruta)

    obs = {
        "fecha": fecha_hoy,
        "valor": item.get("valor"),
        "unidad": item.get("unidad"),
        "fuente": item.get("fuente"),
        "capturado_en": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    # Si el dato trae su propia fecha de período (series mensuales),
    # la conservamos: sirve para saber a qué período pertenece el valor.
    if item.get("fecha"):
        obs["fecha_dato"] = item["fecha"]
    if item.get("variacion") is not None:
        obs["variacion"] = item["variacion"]

    if filas and filas[-1].get("fecha") == fecha_hoy:
        # Ya hay observación de hoy: reemplazar por la más reciente
        if filas[-1].get("valor") == obs["valor"]:
            return "sin_cambio"
        filas[-1] = obs
        escribir_jsonl(ruta, filas)
        return "actualizado"

    # Día nuevo: apendear (rápido, sin reescribir todo)
    with open(ruta, "a", encoding="utf-8") as f:
        f.write(json.dumps(obs, ensure_ascii=False) + "\n")
    return "nuevo"


def main():
    print(f"[Histórico] Inicio: {datetime.now(TZ_AR).strftime('%Y-%m-%d %H:%M')} ARG")

    if not os.path.exists(JSON_DATOS):
        print("[Histórico] No existe data/datos.json — nada que registrar.")
        return

    try:
        with open(JSON_DATOS, "r", encoding="utf-8") as f:
            salida = json.load(f)
        datos = salida.get("datos", {})
    except Exception as e:
        print(f"[Histórico] ⚠ No pude leer datos.json: {e}")
        return

    os.makedirs(DIR_HISTORICO, exist_ok=True)
    fecha_hoy = fecha_de_captura(salida)
    print(f"[Histórico] Observaciones con fecha {fecha_hoy}")
    contadores = {"nuevo": 0, "actualizado": 0, "sin_cambio": 0, "stale": 0, "error": 0}

    for clave, item in datos.items():
        if not isinstance(item, dict) or item.get("valor") is None:
            continue
        if item.get("stale"):
            contadores["stale"] += 1
            continue  # valor conservado: pertenece a un día anterior
        try:
            resultado = registrar(clave, item, fecha_hoy)
            contadores[resultado] += 1
        except Exception as e:
            contadores["error"] += 1
            print(f"   ⚠ {clave}: {str(e)[:60]}")

    print(f"[Histórico] {contadores['nuevo']} nuevos · "
          f"{contadores['actualizado']} actualizados · "
          f"{contadores['sin_cambio']} sin cambio · "
          f"{contadores['stale']} stale (omitidos) · "
          f"{contadores['error']} errores")
    print(f"[Histórico] Guardado en {DIR_HISTORICO}/")


if __name__ == "__main__":
    main()
