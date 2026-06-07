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
MAX_POR_FUENTE = 3
TZ_AR = timezone(timedelta(hours=-3))


def _cache_path(fuente_id):
    return os.path.join(DIR_CACHE, f"{fuente_id}.json")


def _cache_fresco(fuente_id, horas):
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


def _es_basura(titulo):
    t = titulo.lower()
    return any(patron in t for patron in TITULOS_BASURA)


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
    """Baja una fuente respetando cache. Devuelve lista de notas."""
    fid   = fuente["id"]
    url   = fuente["web"]
    tier  = fuente.get("tier", 1)
    horas = CACHE_HORAS.get(tier, 6)

    # Chequear cache
    cached = _cache_fresco(fid, horas)
    if cached is not None:
        print(f"   ↩ {fid}: cache fresco ({len(cached)} notas)")
        return cached

    print(f"   ↓ {fid}: bajando {url[:60]}...")
    try:
        feed = feedparser.parse(url, request_headers={
            "User-Agent": "PPA/2.0 RSS Reader",
            "Accept": "application/rss+xml, application/xml, text/xml"
        }, timeout=8)
    except Exception as e:
        print(f"   ✗ {fid}: {str(e)[:50]}")
        return []

    if not feed.entries:
        print(f"   ✗ {fid}: sin entries")
        _guardar_cache(fid, [])
        return []

    notas = []
    for entry in feed.entries[:MAX_POR_FUENTE * 2]:  # tomar más para filtrar
        titulo = (entry.get('title') or '').strip()
        if not titulo or len(titulo) < 20:
            continue
        if _es_basura(titulo):
            continue

        link = entry.get('link') or entry.get('id') or ''
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
    return notas


def main():
    print(f"[Fetcher] Inicio: {datetime.now(TZ_AR).strftime('%Y-%m-%d %H:%M')} ARG")
    os.makedirs(DIR_CACHE, exist_ok=True)

    todas_notas = []
    titulos_vistos = set()
    fuentes_activas = [f for f in FUENTES if f.get("activa", True)]

    print(f"[Fetcher] {len(fuentes_activas)} fuentes activas")

    for fuente in fuentes_activas:
        notas = bajar_fuente(fuente)
        for nota in notas:
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

    print(f"[Fetcher] {len(todas_notas)} notas únicas guardadas en notas_raw.json")
    print(f"[Fetcher] Fin")


if __name__ == "__main__":
    main()
