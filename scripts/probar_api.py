"""
PPA — probar_api.py
Herramienta de diagnóstico: prueba endpoints y muestra qué devuelven.

Por qué existe: las APIs que alimentan los datos se caen sin avisar y sin
decir cuál es el reemplazo. Pasó con la serie del TCRM en datos.gob.ar (400),
con la variable 6 del BCRA (400) y con el Merval en argentinadatos (404). En
los tres casos lo primero que hace falta es lo mismo — pedir la URL y ver qué
contesta de verdad — y hasta ahora había que improvisarlo cada vez.

No es un test ni corre en producción: es para mirar. Muestra el código HTTP,
el tipo de contenido y, si es JSON, la forma de la respuesta: las claves de
arriba, y para las listas cuántos elementos y cómo es el primero. Con eso
alcanza para saber si un endpoint sirve y por dónde sale el valor.

Cómo se corre (donde haya internet):
    python scripts/probar_api.py https://api.ejemplo.com/v1/cosa
    python scripts/probar_api.py URL1 URL2 URL3
"""

import json
import re
import sys
from urllib.parse import urljoin

import requests

HDRS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                   "AppleWebKit/537.36 (KHTML, like Gecko) "
                   "Chrome/126.0 Safari/537.36"),
    "Accept": "application/json, text/plain, */*",
}
TIMEOUT = 20

# Cuánto se muestra de una respuesta que no es JSON. Lo justo para reconocer
# si es una página de error, un HTML de login o un XML.
CHARS_CRUDO = 300

# Documentos que interesan cuando la respuesta es una página: los organismos
# publican sus series y sus informes como archivos colgados de un índice, y
# encontrar el enlace es la mitad del trabajo. Le pasó al ITCRM y le está
# pasando al REM, que busca "rem_AAAAMM.xls" en una página que cambió.
EXT_DOCUMENTOS = (".xlsx", ".xls", ".csv", ".pdf", ".zip")
MAX_ENLACES = 25


def resumir(valor, sangria=1, max_claves=12):
    """Describe la forma de un JSON sin volcarlo entero."""
    pre = "  " * sangria
    if isinstance(valor, dict):
        claves = list(valor.keys())
        print(f"{pre}objeto con {len(claves)} claves")
        for k in claves[:max_claves]:
            v = valor[k]
            if isinstance(v, (dict, list)):
                print(f"{pre}  {k}:")
                resumir(v, sangria + 2, max_claves)
            else:
                print(f"{pre}  {k} = {str(v)[:70]}")
        if len(claves) > max_claves:
            print(f"{pre}  … y {len(claves) - max_claves} claves más")
    elif isinstance(valor, list):
        print(f"{pre}lista de {len(valor)} elementos")
        if valor:
            print(f"{pre}  primero:")
            resumir(valor[0], sangria + 2, max_claves)
            if len(valor) > 1:
                print(f"{pre}  último:")
                resumir(valor[-1], sangria + 2, max_claves)
    else:
        print(f"{pre}{str(valor)[:70]}")


def enlaces_a_documentos(html, base):
    """Enlaces de la página que apuntan a archivos descargables."""
    encontrados, vistos = [], set()
    for href in re.findall(r'href\s*=\s*["\']([^"\']+)["\']', html or "", re.I):
        limpio = href.strip()
        if not limpio.lower().split("?")[0].endswith(EXT_DOCUMENTOS):
            continue
        completo = urljoin(base, limpio)
        if completo not in vistos:
            vistos.add(completo)
            encontrados.append(completo)
    return encontrados


def probar(url):
    print(f"=== {url}")
    try:
        r = requests.get(url, headers=HDRS, timeout=TIMEOUT)
    except Exception as e:
        print(f"    ✗ no conectó: {str(e)[:90]}\n")
        return

    tipo = r.headers.get("content-type", "?").split(";")[0]
    print(f"    HTTP {r.status_code} · {tipo} · {len(r.content)} bytes")

    if r.status_code >= 400:
        # El cuerpo de un error suele decir el motivo, y a veces la ruta nueva.
        cuerpo = r.text.strip()
        if cuerpo:
            print(f"    cuerpo: {cuerpo[:CHARS_CRUDO]}")
        print()
        return

    try:
        datos = r.json()
    except Exception:
        docs = enlaces_a_documentos(r.text, url)
        if docs:
            print(f"    no es JSON; la página enlaza {len(docs)} documento(s):")
            for u in docs[:MAX_ENLACES]:
                print(f"      {u}")
            if len(docs) > MAX_ENLACES:
                print(f"      … y {len(docs) - MAX_ENLACES} más")
        else:
            print(f"    no es JSON: {r.text.strip()[:CHARS_CRUDO]}")
        print()
        return

    resumir(datos)
    print()


def main():
    urls = [a for a in sys.argv[1:] if a.lower().startswith("http")]
    if not urls:
        print("Pasá al menos una URL.")
        print("  python scripts/probar_api.py https://api.ejemplo.com/v1/cosa")
        sys.exit(1)
    for url in urls:
        probar(url)


if __name__ == "__main__":
    main()
