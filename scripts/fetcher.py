"""
PPA — fetcher.py v2
Baja los feeds RSS respetando cache por tier:
  Tier 1 → cache 6hs  (medios generales)
  Tier 2 → cache 24hs (sectoriales)
  Tier 3 → cache 48hs (institucionales)

Características:
  - Timeout 8s por fuente (si no responde, la saltea)
  - Deduplicación por título normalizado
  - Lista negra de títulos SEO basura
  - Cap de 3 noticias por fuente por edición
  - Guarda todo en data/notas_raw.json
"""

import json
import os
import sys
import re
import time
import hashlib
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA
from FUENTES import FUENTES, CACHE_HORAS, TITULOS_BASURA

try:
    import feedparser
except ImportError:
    print("[Fetcher] feedparser no instalado — pip install feedparser")
    sys.exit(1)

DIR_CACHE    = os.path.join(DIR_DATA, "feeds_cache")
JSON_RAW     = os.path.join(DIR_DATA, "notas_raw.json")
JSON_SALUD   = os.path.join(DIR_DATA, "fuentes_runtime.json")
MAX_POR_FUENTE = 3
TZ_AR = timezone(timedelta(hours=-3))

# ==============================================================
# SALUD DE FUENTES (Fase A del documento rector)
# Estados: ok · sin_novedades · degradada · suspendida · recuperandose
# Reglas:  3 fallos seguidos -> degradada
#          7 días sin éxito  -> suspendida (se reintenta 1 vez por día)
#          3 éxitos seguidos -> ok (si venía degradada/suspendida pasa
#          por "recuperandose" en el primer éxito)
#          feed válido pero sin contenido nuevo (>7 días) -> sin_novedades
# ==============================================================

def cargar_salud():
    if not os.path.exists(JSON_SALUD):
        return {}
    try:
        with open(JSON_SALUD, "r", encoding="utf-8") as f:
            return json.load(f).get("fuentes", {})
    except Exception:
        return {}


def guardar_salud(registro):
    with open(JSON_SALUD, "w", encoding="utf-8") as f:
        json.dump({
            "generado_en": datetime.now(timezone.utc).isoformat(),
            "fuentes": registro,
        }, f, ensure_ascii=False, indent=2)


def _dias_desde(iso):
    if not iso:
        return 9999
    try:
        t = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        return (datetime.now(timezone.utc) - t).total_seconds() / 86400
    except Exception:
        return 9999


def saltear_suspendida(salud_fuente):
    """Una fuente suspendida se reintenta solo una vez por día."""
    if not salud_fuente or salud_fuente.get("estado") != "suspendida":
        return False
    return _dias_desde(salud_fuente.get("ultima_lectura")) < 1.0


def actualizar_salud(registro, fuente, resultado, notas, ultima_pub, error_msg):
    """Actualiza el registro de salud de UNA fuente tras intentar leerla.
    resultado: "ok" | "vacio" | "error" | "cache" """
    fid = fuente["id"]
    r = registro.get(fid, {})
    r["nombre"] = fuente["nombre"]
    if resultado == "cache":
        # Cache fresco: no hay información nueva sobre la salud real.
        registro[fid] = r
        return
    ahora = datetime.now(timezone.utc).isoformat()
    r["ultima_lectura"] = ahora

    if resultado == "ok":
        r["fallos_consecutivos"] = 0
        r["exitos_consecutivos"] = r.get("exitos_consecutivos", 0) + 1
        r["ultima_ok"] = ahora
        r["error"] = None
        r["notas_obtenidas"] = len(notas)
        if ultima_pub:
            r["ultima_publicacion"] = ultima_pub
        estado_previo = r.get("estado")
        if estado_previo in ("degradada", "suspendida"):
            r["estado"] = "recuperandose"
        elif estado_previo == "recuperandose" and r["exitos_consecutivos"] < 3:
            r["estado"] = "recuperandose"
        elif _dias_desde(r.get("ultima_publicacion")) > 7:
            r["estado"] = "sin_novedades"  # responde, pero no publica nada nuevo
        else:
            r["estado"] = "ok"
    else:  # "error" o "vacio"
        r["exitos_consecutivos"] = 0
        r["fallos_consecutivos"] = r.get("fallos_consecutivos", 0) + 1
        r["error"] = error_msg
        r["notas_obtenidas"] = 0
        if r.get("ultima_ok") and _dias_desde(r.get("ultima_ok")) > 7:
            r["estado"] = "suspendida"
        elif r["fallos_consecutivos"] >= 14:
            # fuente que nunca funcionó: ~7 días de intentos fallidos
            r["estado"] = "suspendida"
        elif r["fallos_consecutivos"] >= 3:
            r["estado"] = "degradada"
        else:
            r["estado"] = "error"
    registro[fid] = r


def _cache_path(fuente_id):
    return os.path.join(DIR_CACHE, f"{fuente_id}.json")


FORZAR = "--forzar" in sys.argv  # si viene este flag, ignora el cache

def _cache_fresco(fuente_id, horas):
    if FORZAR:
        return None  # ignorar cache, bajar siempre
    path = _cache_path(fuente_id)
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            cache = json.load(f)
        ts = datetime.fromisoformat(cache.get("descargado_en", "2000-01-01"))
        if (datetime.now(timezone.utc) - ts).total_seconds() < horas * 3600:
            return cache.get("notas", [])
    except Exception:
        pass
    return None


def _guardar_cache(fuente_id, notas):
    os.makedirs(DIR_CACHE, exist_ok=True)
    path = _cache_path(fuente_id)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump({
            "descargado_en": datetime.now(timezone.utc).isoformat(),
            "notas": notas
        }, f, ensure_ascii=False)


# Patrones de URLs a descartar (antes de procesar el entry)
URLS_BLOQUEADAS = [
    "cronista.com/espana/",
    "cronista.com/lifestyle/",
    "cronista.com/deportes/",
]

# Palabras que delatan títulos en inglés
PALABRAS_INGLES = [
    " the ", " and ", " for ", " with ", " this ", " that ",
    " will ", " have ", " from ", " about ", " official",
    "prohibit", "cancel", "government ", " benefits ",
]

def _url_bloqueada(url):
    url = (url or "").lower()
    return any(p in url for p in URLS_BLOQUEADAS)

def _es_ingles(titulo):
    t = " " + titulo.lower() + " "
    matches = sum(1 for p in PALABRAS_INGLES if p in t)
    return matches >= 2  # 2 o más palabras inglesas = descartado

def _es_basura(titulo):
    t = titulo.lower()
    if any(patron in t for patron in TITULOS_BASURA):
        return True
    if _es_ingles(titulo):
        return True
    return False


def _normalizar(titulo):
    """Clave de deduplicación: solo letras y números, minúsculas."""
    return re.sub(r'[^a-z0-9]', '', titulo.lower())[:80]


def _fecha_iso(entry):
    """Intenta extraer una fecha ISO del entry."""
    for campo in ('published_parsed', 'updated_parsed'):
        t = getattr(entry, campo, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc).isoformat()
            except Exception:
                pass
    return datetime.now(timezone.utc).isoformat()


def bajar_fuente(fuente):
    """Baja una fuente respetando cache.
    Devuelve (notas, resultado, error_msg) donde resultado es
    "ok" | "vacio" | "error" | "cache"."""
    fid   = fuente["id"]
    url   = fuente["web"]
    tier  = fuente.get("tier", 1)
    horas = CACHE_HORAS.get(tier, 6)

    # Chequear cache
    cached = _cache_fresco(fid, horas)
    if cached is not None:
        print(f"   ↩ {fid}: cache fresco ({len(cached)} notas)")
        return cached, "cache", None

    print(f"   ↓ {fid}: bajando {url[:60]}...")
    try:
        import socket
        socket.setdefaulttimeout(8)
        feed = feedparser.parse(url, request_headers={
            "User-Agent": "PPA/2.0 RSS Reader",
            "Accept": "application/rss+xml, application/xml, text/xml"
        })
    except Exception as e:
        print(f"   ✗ {fid}: {str(e)[:50]}")
        return [], "error", str(e)[:120]

    if not feed.entries:
        print(f"   ✗ {fid}: sin entries")
        _guardar_cache(fid, [])
        return [], "vacio", "Feed vacío o malformado"

    notas = []
    for entry in feed.entries[:MAX_POR_FUENTE * 2]:  # tomar más para filtrar
        titulo = (entry.get('title') or '').strip()
        link   = entry.get('link') or entry.get('id') or ''

        if not titulo or len(titulo) < 20:
            continue
        if _url_bloqueada(link):
            continue
        if _es_basura(titulo):
            continue
        desc = entry.get('summary') or entry.get('description') or ''
        # Limpiar HTML de la descripción
        desc = re.sub(r'<[^>]+>', ' ', desc)
        desc = re.sub(r'\s{2,}', ' ', desc).strip()[:500]

        notas.append({
            "id":           hashlib.md5(link.encode()).hexdigest()[:12],
            "titulo":       titulo,
            "link":         link,
            "descripcion":  desc,
            "fecha_publicacion": _fecha_iso(entry),
            "fuente_id":    fid,
            "fuente_nombre": fuente["nombre"],
            "categoria":    fuente["categoria"],
        })
        if len(notas) >= MAX_POR_FUENTE:
            break

    _guardar_cache(fid, notas)
    print(f"   ✓ {fid}: {len(notas)} notas")
    return notas, "ok", None


# Fuentes Nitter — solo van a EconoTuits, no a notas_raw
FUENTES_NITTER = {"bcra", "indec", "mecon"}

def main():
    print(f"[Fetcher] Inicio: {datetime.now(TZ_AR).strftime('%Y-%m-%d %H:%M')} ARG")
    os.makedirs(DIR_CACHE, exist_ok=True)

    todas_notas = []
    titulos_vistos = set()
    fuentes_activas = [f for f in FUENTES if f.get("activa", True)]
    salud = cargar_salud()

    print(f"[Fetcher] {len(fuentes_activas)} fuentes activas")

    for fuente in fuentes_activas:
        # Fuente suspendida: un solo reintento por día para no gastar tiempo
        if saltear_suspendida(salud.get(fuente["id"])) and not FORZAR:
            print(f"   ⏭ {fuente['id']}: suspendida (reintento diario ya usado)")
            continue
        notas, resultado, error_msg = bajar_fuente(fuente)
        ultima_pub = max((n.get("fecha_publicacion") or "" for n in notas), default=None) or None
        actualizar_salud(salud, fuente, resultado, notas, ultima_pub, error_msg)
        for nota in notas:
            # Fuentes Nitter solo van a EconoTuits, no a notas_raw
            if nota.get("fuente_id","") in FUENTES_NITTER:
                continue
            clave = _normalizar(nota["titulo"])
            if clave in titulos_vistos:
                continue  # deduplicar
            titulos_vistos.add(clave)
            todas_notas.append(nota)

    # Ordenar por fecha desc
    todas_notas.sort(key=lambda n: n.get("fecha_publicacion", ""), reverse=True)

    with open(JSON_RAW, 'w', encoding='utf-8') as f:
        json.dump({
            "generado_en": datetime.now(timezone.utc).isoformat(),
            "total":       len(todas_notas),
            "notas":       todas_notas
        }, f, ensure_ascii=False, indent=2)

    guardar_salud(salud)
    degradadas = [fid for fid, s in salud.items()
                  if s.get("estado") in ("degradada", "suspendida")]
    print(f"[Fetcher] {len(todas_notas)} notas únicas guardadas en notas_raw.json")
    print(f"[Fetcher] Salud: {len(salud)} fuentes registradas · "
          f"{len(degradadas)} degradadas/suspendidas")
    if degradadas:
        print(f"[Fetcher]   → {', '.join(degradadas[:15])}"
              + (" …" if len(degradadas) > 15 else ""))
    print(f"[Fetcher] Fin")


if __name__ == "__main__":
    main()
