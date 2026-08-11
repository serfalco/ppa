"""
PPA — resumidor.py v2
Genera resúmenes con Gemini en batch (8 títulos por llamada).
Una sola llamada API en vez de 8 separadas.
Solo procesa notas sin resumen previo.
"""

import json
import os
import re
import sys
import time
import requests
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA

JSON_PORTADA = os.path.join(DIR_DATA, "portada.json")

API_BASE = "https://generativelanguage.googleapis.com/v1beta"

# Cadena de modelos, igual criterio que la cadena de fuentes de riesgo país:
# se prueba en orden y gana el primero que responda. Google va retirando
# modelos sin aviso —gemini-1.5-flash ya murió así, y el sucesor que quedó
# configurado devolvía 404 en todas las corridas— y un solo nombre fijo deja
# la publicación sin resúmenes en silencio.
# GEMINI_MODEL fuerza uno solo y saltea la cadena.
MODELOS_CANDIDATOS = [
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash-lite",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-flash-latest",
]

_forzado = os.environ.get("GEMINI_MODEL", "").strip()
MODELOS = [_forzado] if _forzado else list(MODELOS_CANDIDATOS)

# 4 y no 8: cuantos más resúmenes se piden en una sola respuesta, más chance
# de que se corte a mitad y se pierda el resto del batch. Son más llamadas,
# pero cada una rinde entera.
BATCH_SIZE   = 4
MAX_NOTAS    = 16

# Modelo que respondió en esta corrida; se fija en el primer éxito.
MODELO_ACTIVO = None


def url_modelo(modelo):
    return f"{API_BASE}/models/{modelo}:generateContent"


def modelos_disponibles(api_key):
    """Pregunta a la API qué modelos hay. Solo para diagnóstico: si la cadena
    entera falla, el log dice qué se podía usar en vez de dejarnos adivinar."""
    try:
        r = requests.get(f"{API_BASE}/models?key={api_key}", timeout=15)
        r.raise_for_status()
        nombres = []
        for m in r.json().get("models", []):
            if "generateContent" in (m.get("supportedGenerationMethods") or []):
                nombres.append((m.get("name") or "").replace("models/", ""))
        return nombres
    except Exception as e:
        return [f"(no pude listar modelos: {str(e)[:60]})"]


def _parsear_respuesta(texto, cantidad):
    """Extrae los resúmenes de la respuesta "1. ... 2. ...".

    Descarta los índices fuera del batch: si el modelo numera de más, un
    índice suelto reventaba el llamador con IndexError.
    """
    resultados = {}
    for linea in texto.strip().split("\n"):
        m = re.match(r'^(\d+)\.\s+(.+)', linea.strip())
        if not m:
            continue
        idx = int(m.group(1)) - 1
        if not (0 <= idx < cantidad):
            continue
        resumen = m.group(2).strip().replace('"', '')
        if 10 < len(resumen) < 300:
            resultados[idx] = resumen
    return resultados


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
        # MAX_TOKENS holgado: los modelos nuevos de la familia razonan antes de
        # responder y ese razonamiento come del mismo presupuesto. Con 600 la
        # respuesta salía cortada y de 16 notas se rescataba una sola.
        "generationConfig": {"maxOutputTokens": 4096, "temperature": 0.2},
    }

    global MODELO_ACTIVO

    # Si ya hay un modelo que funcionó en esta corrida, no se reintentan los
    # que fallaron: se prueba ese solo.
    candidatos = [MODELO_ACTIVO] if MODELO_ACTIVO else MODELOS

    ultimo_error = None
    for modelo in candidatos:
        try:
            r = requests.post(f"{url_modelo(modelo)}?key={api_key}",
                              json=payload, timeout=40)
            r.raise_for_status()
            cuerpo = r.json()
            texto = cuerpo["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            ultimo_error = f"{modelo}: {str(e)[:70]}"
            print(f"   ⚠ {ultimo_error}")
            continue

        if MODELO_ACTIVO != modelo:
            print(f"   ✓ modelo en uso: {modelo}")
            MODELO_ACTIVO = modelo

        resultados = _parsear_respuesta(texto, len(notas_sin_resumen))

        # Un batch que devuelve menos resúmenes que notas es una falla parcial
        # silenciosa: la portada sale incompleta y nada lo dice. Se registra el
        # motivo de corte que informa la API para saber si fue truncado.
        if len(resultados) < len(notas_sin_resumen):
            razon = ""
            try:
                razon = cuerpo["candidates"][0].get("finishReason") or ""
            except Exception:
                pass
            print(f"   ⚠ batch parcial: {len(resultados)}/{len(notas_sin_resumen)} "
                  f"resúmenes" + (f" · finishReason={razon}" if razon else ""))
            if razon == "MAX_TOKENS":
                print("     (la respuesta se cortó por presupuesto de tokens)")

        return resultados

    print(f"   ✗ ningún modelo respondió (último: {ultimo_error})")
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
        print(f"[Resumidor] {total} resúmenes generados y guardados "
              f"(modelo: {MODELO_ACTIVO})")
    else:
        # Cero resúmenes con notas para resumir es una falla, no un "sin
        # novedades": la portada sale sin resúmenes. Dejamos en el log qué
        # modelos aceptaba la API para no tener que adivinar el nombre.
        print("[Resumidor] ✗ NINGÚN resumen generado — la portada sale sin resúmenes")
        print(f"[Resumidor]   modelos probados: {', '.join(MODELOS)}")
        disponibles = modelos_disponibles(api_key)
        print(f"[Resumidor]   modelos que acepta la API ({len(disponibles)}):")
        for n in disponibles[:25]:
            print(f"[Resumidor]     · {n}")
        print("[Resumidor]   → si hay uno servible, setealo en GEMINI_MODEL "
              "o agregalo a MODELOS_CANDIDATOS")


if __name__ == "__main__":
    print(f"[Resumidor] Inicio: {datetime.now(timezone.utc).isoformat()}")
    main()
    print(f"[Resumidor] Fin")
