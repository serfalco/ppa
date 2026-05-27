"""
PPA — selector.py
Selecciona los 5 destacados de tapa automáticamente.

Algoritmo "Tier 1 + Reciente":
  Cada nota recibe un score basado en:
    - Tier de la fuente (peso 60%): tier 1 vale 100, tier 2 vale 50, tier 3 vale 20
    - Recencia (peso 40%): cuanto más reciente, más puntos (decae linealmente en 24h)
  
  Los 5 con mayor score van a la tapa.
  Restricción: no puede haber más de 2 destacados de la misma fuente.
  Restricción: tratamos de tener al menos 3 categorías distintas representadas.

Cómo se corre:
    python scripts/selector.py
    
Lee:  data/notas.json
Genera: data/portada.json (estructura final con destacados + secciones + último momento)
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    JSON_NOTAS, DIR_DATA, CATEGORIAS,
    DESTACADOS_CANT, NOTAS_POR_CATEGORIA, ULTIMO_MOMENTO_CANT,
    VENTANA_HORAS_POR_TIER,
)

JSON_PORTADA = os.path.join(DIR_DATA, "portada.json")
JSON_NOTAS_PROPIAS = os.path.join(DIR_DATA, "notas_propias.json")


# =============================================================
# SCORING
# =============================================================

def score_por_tier(tier):
    """Tier 1 = 100, Tier 2 = 50, Tier 3 = 20."""
    return {1: 100, 2: 50, 3: 20}.get(tier, 10)


def score_por_recencia(fecha_iso, tier):
    """
    Decae linealmente de 100 (recién publicada) a 0 (al final de la ventana del tier).
    Tier 1: 7 días, Tier 2: 3 días, Tier 3: 24h.
    Si la nota es más vieja que la ventana, score 0.
    """
    try:
        fecha = datetime.fromisoformat(fecha_iso.replace('Z', '+00:00'))
    except Exception:
        return 0

    ahora = datetime.now(timezone.utc)
    diff_horas = (ahora - fecha).total_seconds() / 3600

    if diff_horas < 0:
        return 100  # fecha futura (raro pero pasa)

    horas_ventana = VENTANA_HORAS_POR_TIER.get(tier, 24)
    if diff_horas >= horas_ventana:
        return 0
    return 100 * (1 - diff_horas / horas_ventana)


def calcular_score(nota):
    """Score combinado: 60% tier + 40% recencia (con ventana variable por tier)."""
    s_tier = score_por_tier(nota["tier"])
    s_rec = score_por_recencia(nota["fecha_publicacion"], nota["tier"])
    return round(s_tier * 0.6 + s_rec * 0.4, 2)


# =============================================================
# SELECCIÓN DE DESTACADOS
# =============================================================

def seleccionar_destacados(notas):
    """
    Devuelve los DESTACADOS_CANT mejores tweets aplicando restricciones:
      - Máximo 2 notas de la misma fuente
      - Tratar de incluir al menos 3 categorías distintas
    """
    if not notas:
        return []

    # Ordenar por score descendente
    ordenadas = sorted(notas, key=lambda n: -n["score"])

    destacados = []
    fuentes_usadas = {}    # fuente_id -> cantidad
    categorias_usadas = set()

    # Primer pase: maximizar diversidad
    for nota in ordenadas:
        if len(destacados) >= DESTACADOS_CANT:
            break
        # límite de 2 por fuente
        if fuentes_usadas.get(nota["fuente_id"], 0) >= 2:
            continue
        # si ya tenemos 3 categorías cubiertas, no nos preocupamos más por diversidad
        if len(categorias_usadas) < 3:
            # si la categoría ya está cubierta y hay otras sin cubrir, esperamos
            if nota["categoria"] in categorias_usadas:
                # solo agregamos si en el resto de notas hay categorías nuevas
                hay_nuevas = any(
                    n["categoria"] not in categorias_usadas
                    for n in ordenadas
                    if n not in destacados and fuentes_usadas.get(n["fuente_id"], 0) < 2
                )
                if hay_nuevas:
                    continue
        destacados.append(nota)
        fuentes_usadas[nota["fuente_id"]] = fuentes_usadas.get(nota["fuente_id"], 0) + 1
        categorias_usadas.add(nota["categoria"])

    # Segundo pase: rellenar si quedó incompleto
    if len(destacados) < DESTACADOS_CANT:
        for nota in ordenadas:
            if len(destacados) >= DESTACADOS_CANT:
                break
            if nota in destacados:
                continue
            if fuentes_usadas.get(nota["fuente_id"], 0) >= 2:
                continue
            destacados.append(nota)
            fuentes_usadas[nota["fuente_id"]] = fuentes_usadas.get(nota["fuente_id"], 0) + 1

    return destacados


# =============================================================
# ORGANIZACIÓN POR CATEGORÍA
# =============================================================

def organizar_por_categoria(notas, ya_destacadas_ids):
    """
    Agrupa notas por categoría, excluyendo las que ya están en destacados.
    Devuelve dict {categoria: [notas...]} con máximo NOTAS_POR_CATEGORIA por categoría.
    """
    secciones = {cat: [] for cat in CATEGORIAS}

    for nota in notas:
        if nota["id"] in ya_destacadas_ids:
            continue
        cat = nota["categoria"]
        if cat in secciones and len(secciones[cat]) < NOTAS_POR_CATEGORIA:
            secciones[cat].append(nota)

    # Quitamos categorías vacías
    return {cat: lista for cat, lista in secciones.items() if lista}


# =============================================================
# ÚLTIMO MOMENTO
# =============================================================

def ultimo_momento(notas, ya_destacadas_ids):
    """Las N notas más recientes, sin importar fuente ni categoría."""
    candidatas = [n for n in notas if n["id"] not in ya_destacadas_ids]
    candidatas.sort(key=lambda n: n["fecha_publicacion"], reverse=True)
    return candidatas[:ULTIMO_MOMENTO_CANT]


# =============================================================
# NOTAS PROPIAS (columna de Sergio Falco)
# =============================================================

def cargar_nota_propia_activa():
    """
    Si existe una columna semanal publicada en los últimos 7 días, la devuelve.
    Si no, devuelve None.
    """
    if not os.path.exists(JSON_NOTAS_PROPIAS):
        return None
    try:
        with open(JSON_NOTAS_PROPIAS, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return None

    notas = data.get("notas", [])
    if not notas:
        return None

    # La más reciente publicada
    notas.sort(key=lambda n: n.get("fecha_publicacion", ""), reverse=True)
    mas_reciente = notas[0]

    # Verificamos que sea de los últimos 7 días
    try:
        fecha = datetime.fromisoformat(mas_reciente["fecha_publicacion"].replace('Z', '+00:00'))
    except Exception:
        return None

    ahora = datetime.now(timezone.utc)
    if (ahora - fecha).days > 7:
        return None

    return mas_reciente


# =============================================================
# PROCESO PRINCIPAL
# =============================================================

def main():
    print(f"[PPA Selector] Inicio: {datetime.now(timezone.utc).isoformat()}")

    # Cargar notas
    if not os.path.exists(JSON_NOTAS):
        print(f"ERROR: no existe {JSON_NOTAS}. Corré primero scripts/fetcher.py")
        sys.exit(1)

    with open(JSON_NOTAS, 'r', encoding='utf-8') as f:
        data_notas = json.load(f)
    notas = data_notas.get("notas", [])
    print(f"[PPA Selector] Notas disponibles: {len(notas)}")

    if not notas:
        print("[PPA Selector] No hay notas para procesar. Saliendo.")
        return

    # Calcular score de cada nota
    for nota in notas:
        nota["score"] = calcular_score(nota)

    # Seleccionar destacados
    destacados = seleccionar_destacados(notas)
    print(f"[PPA Selector] {len(destacados)} destacados seleccionados:")
    for i, d in enumerate(destacados, 1):
        print(f"   {i}. [{d['categoria']:<18s}] {d['fuente_nombre']:<22s} score={d['score']:5.1f}")
        print(f"      {d['titulo'][:80]}")

    destacados_ids = {d["id"] for d in destacados}

    # Organizar por categorías
    secciones = organizar_por_categoria(notas, destacados_ids)
    print(f"[PPA Selector] {len(secciones)} categorías con contenido")

    # Último momento
    ult_mom = ultimo_momento(notas, destacados_ids)
    print(f"[PPA Selector] {len(ult_mom)} notas en último momento")

    # Cargar nota propia activa (columna semanal de Sergio)
    nota_propia = cargar_nota_propia_activa()
    if nota_propia:
        print(f"[PPA Selector] Columna activa: '{nota_propia['titulo']}'")
    else:
        print(f"[PPA Selector] Sin columna activa esta semana")

    # Armar portada.json
    portada = {
        "generado_en": datetime.now(timezone.utc).isoformat(),
        "destacados": destacados,
        "secciones": secciones,
        "ultimo_momento": ult_mom,
        "nota_propia": nota_propia,
        "stats": {
            "total_notas": len(notas),
            "destacados": len(destacados),
            "categorias_con_contenido": len(secciones),
            "ultimo_momento": len(ult_mom),
        }
    }

    with open(JSON_PORTADA, 'w', encoding='utf-8') as f:
        json.dump(portada, f, ensure_ascii=False, indent=2)
    print(f"[PPA Selector] Guardado: {JSON_PORTADA}")

    print(f"[PPA Selector] Fin: {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
