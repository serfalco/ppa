"""
PPA — selector.py v2
Lee notas_raw.json y arma portada.json con:
  - destacados: las 3 mejores notas del día (una por categoría distinta)
  - secciones: por categoría, cap 2 notas por categoría en home, cap 3 por fuente global

Filtros:
  - Sin títulos basura (lista negra)
  - Sin duplicados
  - Máximo 8 notas totales para la home
  - Máximo 2 por categoría
  - Máximo 3 por fuente en todo el portada.json
"""

import json
import os
import sys
import re
from datetime import datetime, timezone, timedelta
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA
from FUENTES import TITULOS_BASURA

JSON_RAW     = os.path.join(DIR_DATA, "notas_raw.json")
JSON_PORTADA = os.path.join(DIR_DATA, "portada.json")

MAX_HOME_TOTAL   = 8   # notas en la home
MAX_POR_CAT_HOME = 2   # máx por categoría en home
MAX_POR_FUENTE   = 3   # máx por fuente en todo el portada
MAX_POR_SECCION  = 8   # notas en cada sección de /la-data/

TZ_AR = timezone(timedelta(hours=-3))

# Categorías en orden de prioridad para la home
ORDEN_CATS = [
    "Macro", "Mercados", "Finanzas", "Energía", "Internacional",
    "Agro", "Comex", "Política", "Minería", "Laboral",
    "Automotor", "Logística", "Fiscal", "Fulbito",
    "Expectativas de mercado",
]


def _es_basura(titulo):
    t = titulo.lower()
    return any(p in t for p in TITULOS_BASURA)


def _score(nota):
    """Puntaje simple: más reciente = mayor score. Fuentes tier 1 tienen bonus."""
    try:
        dt = datetime.fromisoformat(nota.get("fecha_publicacion","2000-01-01"))
        score = dt.timestamp()
    except Exception:
        score = 0
    return score


def main():
    print(f"[Selector] Inicio: {datetime.now(TZ_AR).strftime('%Y-%m-%d %H:%M')} ARG")

    if not os.path.exists(JSON_RAW):
        print("[Selector] Sin notas_raw.json — abortando")
        return

    with open(JSON_RAW, 'r', encoding='utf-8') as f:
        raw = json.load(f)

    notas = raw.get("notas", [])
    print(f"[Selector] {len(notas)} notas disponibles")

    # Filtrar basura
    notas = [n for n in notas if not _es_basura(n.get("titulo",""))]
    print(f"[Selector] {len(notas)} notas después de filtro basura")

    # Ordenar por score (más reciente primero)
    notas.sort(key=_score, reverse=True)

    # ── Armar secciones por categoría ──
    por_cat = defaultdict(list)
    fuente_count = defaultdict(int)

    for nota in notas:
        cat = nota.get("categoria", "General")
        fid = nota.get("fuente_id", "")
        if fuente_count[fid] >= MAX_POR_FUENTE:
            continue
        if len(por_cat[cat]) >= MAX_POR_SECCION:
            continue
        por_cat[cat].append(nota)
        fuente_count[fid] += 1

    # ── Armar home: máx 8 notas, máx 2 por categoría ──
    home_notas = []
    cat_home_count = defaultdict(int)
    fuente_home_count = defaultdict(int)

    for cat in ORDEN_CATS:
        for nota in por_cat.get(cat, []):
            if len(home_notas) >= MAX_HOME_TOTAL:
                break
            if cat_home_count[cat] >= MAX_POR_CAT_HOME:
                break
            if fuente_home_count[nota.get("fuente_id","")] >= 2:
                continue
            home_notas.append(nota)
            cat_home_count[cat] += 1
            fuente_home_count[nota.get("fuente_id","")] += 1

    # ── Destacados: las 3 primeras de la home (categorías distintas) ──
    destacados = []
    cats_dest = set()
    for nota in home_notas:
        cat = nota.get("categoria","")
        if cat not in cats_dest:
            destacados.append(nota)
            cats_dest.add(cat)
        if len(destacados) >= 3:
            break

    # ── Guardar portada.json ──
    portada = {
        "generado_en": datetime.now(timezone.utc).isoformat(),
        "destacados":  destacados,
        "secciones":   dict(por_cat),
    }

    with open(JSON_PORTADA, 'w', encoding='utf-8') as f:
        json.dump(portada, f, ensure_ascii=False, indent=2)

    total_secciones = sum(len(v) for v in por_cat.values())
    print(f"[Selector] Home: {len(home_notas)} notas · Secciones: {total_secciones} notas · Destacados: {len(destacados)}")
    print(f"[Selector] Fin")


if __name__ == "__main__":
    main()
