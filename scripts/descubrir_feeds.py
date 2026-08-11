"""
PPA — descubrir_feeds.py
Herramienta de diagnóstico (como descubrir_bcra.py, NO corre en producción).

Busca el feed RSS/Atom vigente de una institución sin adivinar URLs:

  1. Autodiscovery: baja el HTML del sitio y lee los <link rel="alternate">
     que el propio sitio declara. Es el mecanismo estándar y es el que
     encuentra la URL real cuando cambió de lugar.
  2. Rutas habituales: si el sitio no declara nada, prueba /feed/, /rss.xml
     y compañía.
  3. Valida cada candidato: lo parsea, cuenta entradas y mira la fecha de la
     más reciente. Un feed que responde 200 pero está vacío no sirve.

Todo con User-Agent de navegador: varias de las fuentes caídas daban 403,
no 404 — el feed existe y rechaza al lector. Ese es justamente el caso que
un UA de navegador destraba.

Cómo se corre (donde haya internet — tu compu o el workflow):
    python scripts/descubrir_feeds.py                 # todas las candidatas
    python scripts/descubrir_feeds.py bcra indec      # solo algunas

La salida incluye la línea lista para pegar en FUENTES.py.
"""

import sys
import re
from urllib.parse import urljoin, urlparse

import requests

try:
    import feedparser
except ImportError:
    print("Falta feedparser — pip install feedparser")
    sys.exit(1)


# Navegador real: las fuentes que daban 403 rechazan agentes que no lo parecen.
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
HDRS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
}
TIMEOUT = 20

# Rutas que usan la mayoría de los CMS, por si el sitio no declara su feed.
RUTAS = [
    "/feed/", "/rss", "/rss.xml", "/feed.xml", "/atom.xml", "/index.xml",
    "/es/rss", "/es/feed/", "/noticias/feed/", "/novedades/feed/",
    "/blog/feed/", "/?feed=rss2",
]

# Instituciones que Documentos necesita y hoy no tiene.
# El id es el que va a FUENTES.py; la home es desde donde arranca la búsqueda.
CANDIDATAS = [
    ("bcra",         "BCRA",                  "https://www.bcra.gob.ar",        "Macro", 3),
    ("indec",        "INDEC",                 "https://www.indec.gob.ar",       "Macro", 3),
    ("bcr",          "Bolsa de Comercio de Rosario", "https://www.bcr.com.ar",  "Agro", 3),
    ("fiel",         "FIEL",                  "https://www.fiel.org",           "Análisis Consultoras", 3),
    ("ieral",        "IERAL",                 "https://www.ieral.org",          "Análisis Consultoras", 3),
    ("cepal",        "CEPAL",                 "https://www.cepal.org",          "Internacional", 3),
    ("fmi",          "FMI",                   "https://www.imf.org/es",         "Internacional", 3),
    ("bancomundial", "Banco Mundial",         "https://www.bancomundial.org",   "Internacional", 3),
    ("ocde",         "OCDE",                  "https://www.oecd.org",           "Internacional", 3),
    ("magyp",        "MAGyP",                 "https://www.argentina.gob.ar/economia/agricultura", "Agro", 3),
    ("acara",        "ACARA",                 "https://www.acara.org.ar",       "Automotor", 3),
    ("adefa",        "ADEFA",                 "https://www.adefa.org.ar",       "Automotor", 3),
    ("cedol",        "CEDOL",                 "https://www.cedol.org.ar",       "Logística", 3),
    ("caem",         "CAEM",                  "https://caem.com.ar",            "Energía y Minería", 3),
    ("cari",         "CARI",                  "https://www.cari.org.ar",        "Comex", 3),
]


def bajar(url):
    """Devuelve (status, texto) o (None, motivo del fallo)."""
    try:
        r = requests.get(url, headers=HDRS, timeout=TIMEOUT, allow_redirects=True)
        return r.status_code, r.text
    except Exception as e:
        return None, str(e)[:80]


def links_declarados(html, base):
    """Extrae los feeds que el propio HTML declara con <link rel=alternate>."""
    encontrados = []
    for tag in re.findall(r"<link\b[^>]*>", html or "", re.I):
        if not re.search(r'rel\s*=\s*["\']?alternate', tag, re.I):
            continue
        if not re.search(r'type\s*=\s*["\']?application/(rss|atom)\+xml', tag, re.I):
            continue
        m = re.search(r'href\s*=\s*["\']([^"\']+)["\']', tag, re.I)
        if m:
            encontrados.append(urljoin(base, m.group(1).strip()))
    return encontrados


def evaluar(url):
    """Parsea un candidato. Devuelve dict con el veredicto."""
    estado, cuerpo = bajar(url)
    if estado is None:
        return {"url": url, "ok": False, "motivo": f"conexión: {cuerpo}"}
    if estado >= 400:
        return {"url": url, "ok": False, "motivo": f"HTTP {estado}"}

    feed = feedparser.parse(cuerpo)
    n = len(feed.entries)
    if n == 0:
        detalle = "sin entradas"
        if getattr(feed, "bozo", 0):
            detalle = f"no es XML válido ({str(getattr(feed,'bozo_exception',''))[:40]})"
        return {"url": url, "ok": False, "motivo": detalle}

    ultima = ""
    for e in feed.entries:
        f = e.get("published") or e.get("updated") or ""
        if f > ultima:
            ultima = f
    titulo = (feed.entries[0].get("title") or "")[:60]
    return {"url": url, "ok": True, "entradas": n, "ultima": ultima[:31],
            "muestra": titulo}


def candidatos_de(home):
    """Feeds a probar: los que el sitio declara, después las rutas típicas."""
    estado, cuerpo = bajar(home)
    declarados = []
    if estado and estado < 400:
        declarados = links_declarados(cuerpo, home)

    raiz = f"{urlparse(home).scheme}://{urlparse(home).netloc}"
    porRuta = [urljoin(home.rstrip("/") + "/", r.lstrip("/")) for r in RUTAS]
    porRuta += [raiz + r for r in RUTAS]

    vistos, orden = set(), []
    for u in declarados + porRuta:
        if u not in vistos:
            vistos.add(u)
            orden.append(u)
    return declarados, orden


def main():
    filtro = {a.lower() for a in sys.argv[1:]}
    # "todas" es explícito: pasar argumentos que no matchean ningún id dejaba
    # la lista vacía y el script terminaba con un "0 y 0" que parecía un
    # resultado real en vez de un filtro mal escrito.
    if "todas" in filtro:
        filtro = set()
    objetivo = [c for c in CANDIDATAS if not filtro or c[0] in filtro]

    if not objetivo:
        conocidos = ", ".join(c[0] for c in CANDIDATAS)
        print(f"Ningún id coincide con {sorted(filtro)}.")
        print(f"Ids disponibles: {conocidos}")
        print("Usá 'todas' para probarlas todas.")
        sys.exit(1)

    hallazgos, sin_suerte = [], []

    for fid, nombre, home, categoria, tier in objetivo:
        print(f"\n=== {nombre} ({fid}) — {home}")
        declarados, candidatos = candidatos_de(home)
        if declarados:
            print(f"    el sitio declara {len(declarados)} feed(s)")
        else:
            print("    no declara feed; pruebo rutas habituales")

        ganador = None
        for url in candidatos:
            r = evaluar(url)
            if r["ok"]:
                print(f"    ✓ {url}")
                print(f"      {r['entradas']} entradas · última: {r['ultima']}")
                print(f"      ej: {r['muestra']}")
                ganador = r
                break

        if ganador:
            hallazgos.append((fid, nombre, ganador["url"], categoria, tier))
        else:
            print("    ✗ ningún candidato sirvió")
            sin_suerte.append((fid, nombre))

    print("\n" + "=" * 70)
    print(f"RESULTADO: {len(hallazgos)} con feed vivo · {len(sin_suerte)} sin encontrar")

    if hallazgos:
        print("\nLíneas para FUENTES.py:\n")
        for fid, nombre, url, cat, tier in hallazgos:
            print(f'    {{"id":"{fid}", "nombre":"{nombre}", "web":"{url}", '
                  f'"categoria":"{cat}", "tier":{tier}, "activa":True}},')
        print("\nIds para la lista blanca de generador_documentos.py:")
        print("    " + ", ".join(f'"{f[0]}"' for f in hallazgos))

    if sin_suerte:
        print("\nSin feed detectable (habrá que mirarlas a mano o descartarlas):")
        for fid, nombre in sin_suerte:
            print(f"    · {nombre} ({fid})")


if __name__ == "__main__":
    main()
