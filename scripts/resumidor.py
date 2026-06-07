"""
PPA — resumidor.py
Lee portada.json, genera un resumen de 1-2 líneas para cada nota
usando la API de Gemini (gratuita), y lo guarda de vuelta en portada.json.

Corre DESPUÉS del selector.py y ANTES del generador_home.py.
Solo genera resumen para notas que no tienen uno todavía.
Si la API falla, la nota queda sin resumen (no rompe nada).

Variable de entorno requerida: GEMINI_API_KEY
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
GEMINI_URL   = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
MAX_NOTAS    = 12   # máximo de notas a resumir por corrida
ESPERA_SEG   = 1    # pausa entre llamadas para no exceder rate limit


def gemini_resumir(titulo, descripcion, api_key):
    """Llama a Gemini para generar un resumen de 1-2 líneas."""
    texto_entrada = titulo
    if descripcion and len(descripcion) > 20:
        texto_entrada += f"\n\n{descripcion[:500]}"

    prompt = (
        "Sos un editor de una publicación económica argentina. "
        "En base al siguiente título y descripción de una noticia, "
        "escribí un resumen de exactamente 1 o 2 oraciones en español rioplatense, "
        "informativo, directo, sin adornos. "
        "No uses comillas. No repitas el título. Solo el resumen.\n\n"
        f"{texto_entrada}"
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 120,
            "temperature": 0.3,
        }
    }

    try:
        r = requests.post(
            f"{GEMINI_URL}?key={api_key}",
            json=payload,
            timeout=15
        )
        r.raise_for_status()
        data = r.json()
        texto = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        # Limpiar posibles comillas o saltos
        texto = texto.replace('"', '').replace('\n', ' ').strip()
        return texto if len(texto) > 15 else None
    except Exception as e:
        print(f"   ⚠ Gemini error: {str(e)[:60]}")
        return None


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

    destacados = portada.get("destacados", [])
    secciones  = portada.get("secciones", {})

    # Juntar todas las notas para procesar
    todas = []
    for n in destacados:
        todas.append(("destacados", None, n))
    for cat, notas in secciones.items():
        for n in notas:
            todas.append(("seccion", cat, n))

    procesadas = 0
    for origen, cat, nota in todas:
        if procesadas >= MAX_NOTAS:
            break
        # Solo si no tiene resumen todavía
        if nota.get("resumen"):
            continue

        titulo = nota.get("titulo", "")
        desc   = nota.get("descripcion", nota.get("bajada", ""))
        if not titulo:
            continue

        print(f"   → Resumiendo: {titulo[:60]}...")
        resumen = gemini_resumir(titulo, desc, api_key)
        if resumen:
            nota["resumen"] = resumen
            procesadas += 1
            print(f"   ✓ {resumen[:80]}")
        else:
            print(f"   ✗ Sin resumen")

        if procesadas < MAX_NOTAS:
            time.sleep(ESPERA_SEG)

    if procesadas > 0:
        with open(JSON_PORTADA, 'w', encoding='utf-8') as f:
            json.dump(portada, f, ensure_ascii=False, indent=2)
        print(f"[Resumidor] {procesadas} resúmenes generados y guardados")
    else:
        print("[Resumidor] Sin notas nuevas para resumir")


if __name__ == "__main__":
    print(f"[Resumidor] Inicio: {datetime.now(timezone.utc).isoformat()}")
    main()
    print(f"[Resumidor] Fin")
