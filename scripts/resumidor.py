"""
PPA — resumidor.py v2
Genera resúmenes con Gemini en batch (8 títulos por llamada).
Una sola llamada API en vez de 8 separadas.
Solo procesa notas sin resumen previo.
"""

import json
import os
import sys
import time
import requests
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA

JSON_PORTADA = os.path.join(DIR_DATA, "portada.json")
# Modelo configurable por env var (el doc rector pide poder cambiar de
# modelo sin reconstruir). gemini-1.5-flash fue discontinuado por Google;
# el default actual es gemini-2.5-flash-lite (el más barato de la familia).
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")
GEMINI_URL   = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
BATCH_SIZE   = 8
MAX_NOTAS    = 16


def gemini_batch(notas_sin_resumen, api_key):
    """Manda hasta BATCH_SIZE notas en un solo prompt. Devuelve dict {idx: resumen}."""
    if not notas_sin_resumen:
        return {}

    items = []
    for i, nota in enumerate(notas_sin_resumen):
        titulo = nota.get("titulo", "")
        desc   = nota.get("descripcion", "")[:200]
        texto  = titulo + (f" — {desc}" if desc else "")
        items.append(f"{i+1}. {texto}")

    prompt = (
        "Sos editor de una publicación económica argentina. "
        "Para cada noticia numerada, escribí UN resumen de 1-2 oraciones en español rioplatense. "
        "Directo, informativo, sin adornos, sin repetir el título. "
        "Respondé SOLO con el formato:\n"
        "1. [resumen]\n2. [resumen]\netc.\n\n"
        "Noticias:\n" + "\n".join(items)
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"maxOutputTokens": 600, "temperature": 0.2}
    }

    try:
        r = requests.post(f"{GEMINI_URL}?key={api_key}", json=payload, timeout=20)
        r.raise_for_status()
        texto = r.json()["candidates"][0]["content"]["parts"][0]["text"]

        # Parsear respuesta "1. resumen\n2. resumen..."
        resultados = {}
        for linea in texto.strip().split("\n"):
            m = __import__('re').match(r'^(\d+)\.\s+(.+)', linea.strip())
            if m:
                idx = int(m.group(1)) - 1
                resumen = m.group(2).strip().replace('"','')
                if 10 < len(resumen) < 300:
                    resultados[idx] = resumen
        return resultados
    except Exception as e:
        print(f"   ⚠ Gemini batch error: {str(e)[:60]}")
        return {}


def main():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("[Resumidor] Sin GEMINI_API_KEY — saltando")
        return

    if not os.path.exists(JSON_PORTADA):
        print("[Resumidor] Sin portada.json — saltando")
        return

    with open(JSON_PORTADA, 'r', encoding='utf-8') as f:
        portada = json.load(f)

    # Recolectar notas sin resumen
    sin_resumen = []
    refs = []  # (lista_origen, indice) para actualizar in-place

    for i, nota in enumerate(portada.get("destacados", [])):
        if not nota.get("resumen") and len(sin_resumen) < MAX_NOTAS:
            sin_resumen.append(nota)
            refs.append(("destacados", i))

    for cat, notas in portada.get("secciones", {}).items():
        for i, nota in enumerate(notas):
            if not nota.get("resumen") and len(sin_resumen) < MAX_NOTAS:
                sin_resumen.append(nota)
                refs.append(("seccion", cat, i))

    if not sin_resumen:
        print("[Resumidor] Sin notas nuevas para resumir")
        return

    print(f"[Resumidor] {len(sin_resumen)} notas para resumir en batches de {BATCH_SIZE}")

    total = 0
    for start in range(0, len(sin_resumen), BATCH_SIZE):
        batch = sin_resumen[start:start+BATCH_SIZE]
        batch_refs = refs[start:start+BATCH_SIZE]

        resultados = gemini_batch(batch, api_key)

        for idx, resumen in resultados.items():
            ref = batch_refs[idx]
            if ref[0] == "destacados":
                portada["destacados"][ref[1]]["resumen"] = resumen
            else:
                portada["secciones"][ref[1]][ref[2]]["resumen"] = resumen
            total += 1

        if start + BATCH_SIZE < len(sin_resumen):
            time.sleep(1)  # pausa entre batches

    if total > 0:
        with open(JSON_PORTADA, 'w', encoding='utf-8') as f:
            json.dump(portada, f, ensure_ascii=False, indent=2)
        print(f"[Resumidor] {total} resúmenes generados y guardados")
    else:
        print("[Resumidor] Sin resúmenes nuevos")


if __name__ == "__main__":
    print(f"[Resumidor] Inicio: {datetime.now(timezone.utc).isoformat()}")
    main()
    print(f"[Resumidor] Fin")
