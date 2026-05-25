"""
PPA — fetcher.py
Lee todos los RSS de las fuentes activas, filtra notas válidas,
deduplica y guarda en notas.json

Reglas:
- Solo notas de las últimas HORAS_VENTANA horas (24h por defecto)
- Sin retweets, sin replies (no aplica en RSS web, pero sí en filtros de título)
- Deduplicación por título normalizado
- Las fuentes marcadas como activas=False se saltean
- Las fuentes que fallan no rompen el proceso, se registran en fuentes_runtime.json

Cómo se corre:
    python scripts/fetcher.py
"""

import json
import os
import sys
import re
import hashlib
import unicodedata
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse

# feedparser parsea cualquier feed RSS/Atom
# requests para hacer requests HTTP con timeout
import feedparser
import requests

# Cargo configuración
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import (
    FUENTES, HORAS_VENTANA, JSON_NOTAS, JSON_FUENTES_RUNTIME,
    JSON_BORRADOS, DIR_DATA
)


# =============================================================
# HELPERS
# =============================================================

def normalizar(texto):
    """Normaliza un texto para comparaciones: sin acentos, minúsculas, sin espacios extra."""
    if not texto:
        return ""
    # quitar acentos
    texto = unicodedata.normalize('NFKD', texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    # minúsculas y limpiar
    texto = texto.lower().strip()
    # colapsar espacios múltiples
    texto = re.sub(r'\s+', ' ', texto)
    return texto


def hash_nota(titulo, fuente_id):
    """Genera un ID único para una nota: fuente + título normalizado."""
    base = f"{fuente_id}:{normalizar(titulo)}"
    return hashlib.md5(base.encode()).hexdigest()[:12]


def es_reply_o_rt(titulo):
    """Detecta titulares que son respuestas o retweets (en feeds que los mezclan)."""
    if not titulo:
        return True
    t = titulo.strip().lower()
    if t.startswith("rt @") or t.startswith("rt:"):
        return True
    if t.startswith("@"):
        return True
    return False


def fecha_de_entry(entry):
    """Saca la fecha de publicación de un entry de feedparser. Devuelve datetime con tz."""
    for campo in ("published_parsed", "updated_parsed", "created_parsed"):
        v = getattr(entry, campo, None) or entry.get(campo) if hasattr(entry, 'get') else None
        if v:
            try:
                return datetime(*v[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    # si no hay fecha, asumir ahora (para no perder la nota)
    return datetime.now(timezone.utc)


def limpiar_html(texto):
    """Quita tags HTML de un string para usar como bajada."""
    if not texto:
        return ""
    # quitar tags HTML
    texto = re.sub(r'<[^>]+>', ' ', texto)
    # decodificar entidades comunes
    texto = texto.replace('&nbsp;', ' ').replace('&amp;', '&')
    texto = texto.replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
    # colapsar espacios
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto


def bajada_corta(texto, max_chars=240):
    """Recorta una bajada a ~240 caracteres terminando en palabra completa."""
    texto = limpiar_html(texto)
    if len(texto) <= max_chars:
        return texto
    cortado = texto[:max_chars]
    # cortar en último espacio para no partir palabra
    ult_espacio = cortado.rfind(' ')
    if ult_espacio > max_chars * 0.7:
        cortado = cortado[:ult_espacio]
    return cortado.rstrip(',.;:') + '…'


def cargar_borrados():
    """Carga el set de IDs de notas marcadas como basura por el panel admin."""
    if not os.path.exists(JSON_BORRADOS):
        return set()
    try:
        with open(JSON_BORRADOS, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return set(data.get('ids', []))
    except Exception:
        return set()


# =============================================================
# LECTURA DE UNA FUENTE
# =============================================================

def leer_fuente(fuente):
    """
    Lee el RSS de una fuente y devuelve dict con:
      - notas: lista de notas válidas
      - estado: "ok" / "sin_datos" / "error"
      - error: mensaje si hubo error
      - ultima_publicacion: timestamp de la nota más reciente
    """
    resultado = {
        "id": fuente["id"],
        "notas": [],
        "estado": "ok",
        "error": None,
        "ultima_publicacion": None,
    }

    if not fuente.get("activa", True):
        resultado["estado"] = "suspendida"
        return resultado

    try:
        # Pedimos el feed con timeout para no colgar todo el proceso
        # User-Agent ayuda con sitios que filtran bots básicos
        r = requests.get(
            fuente["rss"],
            timeout=15,
            headers={"User-Agent": "PPA-Bot/1.0 (Pulso Productivo Argentino)"}
        )
        r.raise_for_status()
        feed = feedparser.parse(r.content)
    except requests.exceptions.RequestException as e:
        resultado["estado"] = "error"
        resultado["error"] = f"HTTP: {str(e)[:80]}"
        return resultado
    except Exception as e:
        resultado["estado"] = "error"
        resultado["error"] = f"Parser: {str(e)[:80]}"
        return resultado

    if not feed.entries:
        resultado["estado"] = "sin_datos"
        resultado["error"] = "Feed vacío o malformado"
        return resultado

    # Ventana de tiempo: solo notas más nuevas que esto
    limite = datetime.now(timezone.utc) - timedelta(hours=HORAS_VENTANA)

    notas_validas = []
    ultima_pub = None

    for entry in feed.entries:
        titulo = (entry.get("title") or "").strip()
        if not titulo:
            continue

        # Filtros básicos
        if es_reply_o_rt(titulo):
            continue

        fecha = fecha_de_entry(entry)
        if ultima_pub is None or fecha > ultima_pub:
            ultima_pub = fecha

        # Solo notas dentro de la ventana
        if fecha < limite:
            continue

        # Armamos la nota normalizada
        link = (entry.get("link") or "").strip()
        descripcion = entry.get("summary") or entry.get("description") or ""

        nota = {
            "id": hash_nota(titulo, fuente["id"]),
            "fuente_id": fuente["id"],
            "fuente_nombre": fuente["nombre"],
            "categoria": fuente["categoria"],
            "tier": fuente["tier"],
            "titulo": titulo,
            "bajada": bajada_corta(descripcion),
            "link": link,
            "fecha_publicacion": fecha.isoformat(),
            "fecha_lectura": datetime.now(timezone.utc).isoformat(),
        }
        notas_validas.append(nota)

    resultado["notas"] = notas_validas
    resultado["ultima_publicacion"] = ultima_pub.isoformat() if ultima_pub else None

    if not notas_validas and feed.entries:
        # tiene entradas pero ninguna entró por la ventana de 24h
        # eso no es error, solo significa que no publicaron hoy
        pass

    return resultado


# =============================================================
# DEDUPLICACIÓN
# =============================================================

def deduplicar(notas):
    """
    Quita notas duplicadas basándose en similitud de título normalizado.
    Si dos notas tienen título muy parecido, se queda la del tier más alto (más bajo).
    """
    if not notas:
        return []

    # Agrupamos por título normalizado
    grupos = {}
    for nota in notas:
        clave = normalizar(nota["titulo"])[:80]  # primeros 80 caracteres normalizados
        if clave not in grupos:
            grupos[clave] = []
        grupos[clave].append(nota)

    # De cada grupo nos quedamos con la mejor (tier más bajo = más prioritaria)
    resultado = []
    for clave, lista in grupos.items():
        lista.sort(key=lambda n: (n["tier"], n["fecha_publicacion"]), reverse=False)
        resultado.append(lista[0])

    return resultado


# =============================================================
# PROCESO PRINCIPAL
# =============================================================

def main():
    print(f"[PPA Fetcher] Inicio: {datetime.now(timezone.utc).isoformat()}")
    print(f"[PPA Fetcher] Procesando {len(FUENTES)} fuentes")
    print()

    # Aseguramos que existe el directorio data/
    os.makedirs(DIR_DATA, exist_ok=True)

    # Cargamos notas borradas por el panel
    borrados = cargar_borrados()
    print(f"[PPA Fetcher] {len(borrados)} notas marcadas como basura (se filtran)")

    todas_las_notas = []
    estado_fuentes = {}

    for i, fuente in enumerate(FUENTES, 1):
        print(f"[{i:2d}/{len(FUENTES)}] {fuente['nombre']:<35s}", end=" ", flush=True)
        res = leer_fuente(fuente)

        estado_fuentes[fuente["id"]] = {
            "nombre": fuente["nombre"],
            "estado": res["estado"],
            "error": res["error"],
            "ultima_publicacion": res["ultima_publicacion"],
            "notas_obtenidas": len(res["notas"]),
            "ultima_lectura": datetime.now(timezone.utc).isoformat(),
        }

        if res["estado"] == "ok":
            print(f"✓ {len(res['notas']):2d} notas")
            todas_las_notas.extend(res["notas"])
        elif res["estado"] == "suspendida":
            print(f"⏸  suspendida")
        elif res["estado"] == "sin_datos":
            print(f"⚠  sin datos hoy")
        else:
            print(f"✗ ERROR: {res['error']}")

    print()
    print(f"[PPA Fetcher] Total notas crudas: {len(todas_las_notas)}")

    # Filtrar las borradas por el panel
    todas_las_notas = [n for n in todas_las_notas if n["id"] not in borrados]
    print(f"[PPA Fetcher] Después de quitar borradas: {len(todas_las_notas)}")

    # Deduplicar
    todas_las_notas = deduplicar(todas_las_notas)
    print(f"[PPA Fetcher] Después de deduplicar: {len(todas_las_notas)}")

    # Ordenar por fecha de publicación, más nuevas primero
    todas_las_notas.sort(key=lambda n: n["fecha_publicacion"], reverse=True)

    # Guardar notas.json
    salida = {
        "generado_en": datetime.now(timezone.utc).isoformat(),
        "total_notas": len(todas_las_notas),
        "ventana_horas": HORAS_VENTANA,
        "notas": todas_las_notas,
    }
    with open(JSON_NOTAS, 'w', encoding='utf-8') as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)
    print(f"[PPA Fetcher] Guardado: {JSON_NOTAS}")

    # Guardar fuentes_runtime.json (estado de salud)
    salida_fuentes = {
        "generado_en": datetime.now(timezone.utc).isoformat(),
        "fuentes": estado_fuentes,
    }
    with open(JSON_FUENTES_RUNTIME, 'w', encoding='utf-8') as f:
        json.dump(salida_fuentes, f, ensure_ascii=False, indent=2)
    print(f"[PPA Fetcher] Guardado: {JSON_FUENTES_RUNTIME}")

    # Resumen final por categoría
    print()
    print("[PPA Fetcher] Resumen por categoría:")
    cats = {}
    for n in todas_las_notas:
        cats[n["categoria"]] = cats.get(n["categoria"], 0) + 1
    for cat, cnt in sorted(cats.items(), key=lambda x: -x[1]):
        print(f"   {cat:<22s} {cnt:3d} notas")

    print()
    print(f"[PPA Fetcher] Fin: {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
