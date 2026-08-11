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
    python scripts/descubrir_feeds.py fundar          # una fuente de FUENTES.py
    python scripts/descubrir_feeds.py https://x.ar/blog/feed/   # una URL puntual

Cualquier id del catálogo sirve como argumento para diagnosticar una fuente
caída, sin agregarla a CANDIDATAS: prueba primero la URL configurada — así
el log dice por qué dejó de andar — y después busca reemplazo. Si las rutas
habituales no dan con nada, pasar una URL directa prueba esa sola y, cuando
no es un feed, lista los feeds que esa página declara o enlaza.

La salida incluye la línea lista para pegar en FUENTES.py.
"""

import sys
import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin, urlparse

import requests

from FUENTES import FUENTES_POR_ID

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
# 8s y no 20: un sitio que tarda más que eso en dar un feed tampoco sirve
# para el fetcher, que usa el mismo criterio. Con 15 instituciones × varias
# rutas cada una, la diferencia es entre terminar y comerse el timeout del job.
TIMEOUT = 8

# Rutas que usan la mayoría de los CMS, por si el sitio no declara su feed.
# Lista corta a propósito: cada una es un pedido más por institución.
RUTAS = [
    "/feed/", "/rss.xml", "/rss", "/index.xml", "/es/rss", "/noticias/feed/",
]

# Cuántas instituciones se prueban a la vez. El trabajo es puro esperar red,
# así que el paralelismo es lo que hace que esto termine en un minuto.
PARALELAS = 8

# Instituciones que Documentos necesita.
# El id es el que va a FUENTES.py; la home es desde donde arranca la búsqueda.
#
# Resultado de la corrida del 11/08/2026 (15 probadas, 3 con feed vivo):
#
#   ✓ CEDOL  https://www.cedol.org.ar/logistica/feed/   declarado por el sitio
#   ✓ CAEM   https://caem.com.ar/feed/                  por ruta habitual
#   ✗ MAGyP  el único candidato que respondió fue https://www.argentina.gob.ar/rss.xml,
#            que es el feed de TODO el portal del Estado, no el de Agricultura.
#            Rotularlo "MAGyP" sería atribuir mal la fuente, así que se descarta.
#   ✗ BCRA, INDEC, BCR, FIEL, IERAL, CEPAL, FMI, Banco Mundial, OCDE, ACARA,
#     ADEFA, CARI — sin feed detectable: 404, 403 aun con User-Agent de
#     navegador (OCDE), o HTML donde debería haber XML (ACARA).
#
# Que no aparezcan no es un problema de búsqueda. Según §13 del documento
# integral estas instituciones no son fuentes de RSS: BCRA, INDEC y FMI son
# Capa 1 (APIs estructuradas) y sus informes son Capa 2 (PDFs, boletines,
# calendarios). El RSS es Capa 3 y es periodístico. La vía correcta para
# traerlas es la Fase C, no seguir buscándoles feed.
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


def candidatos_de(home, actual=None):
    """Feeds a probar: el que ya está configurado (si lo hay), después los
    que el sitio declara, después las rutas típicas.

    El configurado va primero a propósito: cuando la fuente ya existe en el
    catálogo, lo primero que hay que saber es por qué la URL que tenemos
    dejó de servir — 404, bloqueo o XML vacío. Eso sale en el log aunque
    después se encuentre un reemplazo.
    """
    estado, cuerpo = bajar(home)
    declarados = []
    if estado and estado < 400:
        declarados = links_declarados(cuerpo, home)

    raiz = f"{urlparse(home).scheme}://{urlparse(home).netloc}"
    porRuta = [urljoin(home.rstrip("/") + "/", r.lstrip("/")) for r in RUTAS]
    porRuta += [raiz + r for r in RUTAS]

    vistos, orden = set(), []
    for u in ([actual] if actual else []) + declarados + porRuta:
        if u not in vistos:
            vistos.add(u)
            orden.append(u)
    return declarados, orden


def desde_catalogo(fid):
    """Arma una candidata a partir de una fuente que ya está en FUENTES.py.

    Sirve para diagnosticar las fuentes que el fetcher reporta caídas: no
    hay que agregarlas a mano a CANDIDATAS, alcanza con pasar su id. La
    búsqueda arranca desde la raíz del sitio, que es donde vive el
    autodiscovery, y prueba primero la URL que hoy tiene el catálogo.
    """
    f = FUENTES_POR_ID.get(fid)
    if not f:
        return None
    partes = urlparse(f["web"])
    return {
        "id": fid,
        "nombre": f["nombre"],
        "home": f"{partes.scheme}://{partes.netloc}",
        "categoria": f["categoria"],
        "tier": f["tier"],
        "actual": f["web"],
    }


def enlaces_a_feeds(html, base):
    """Enlaces de la página que parecen feeds, más allá del <link alternate>.

    Varios sitios no declaran nada pero tienen una página índice que lista
    sus canales. Ahí el feed está en un <a href>, no en el <head>.
    """
    encontrados = []
    for href in re.findall(r'<a\b[^>]*href\s*=\s*["\']([^"\']+)["\']',
                           html or "", re.I):
        if re.search(r"(rss|feed|\.xml)", href, re.I):
            encontrados.append(urljoin(base, href.strip()))
    vistos, orden = set(), []
    for u in encontrados:
        if u not in vistos:
            vistos.add(u)
            orden.append(u)
    return orden


def probar_urls(urls):
    """Evalúa URLs sueltas y, si no son feeds, dice qué feeds ofrece la página.

    Es el segundo paso del diagnóstico: cuando las rutas habituales fallan,
    uno ya tiene una sospecha concreta (otra categoría, otro post type, la
    página que lista los canales) y quiere probarla sin tocar el catálogo.
    """
    for url in urls:
        print(f"=== {url}")
        r = evaluar(url)
        if r["ok"]:
            print(f"    ✓ {r['entradas']} entradas · última: {r['ultima']}")
            print(f"      ej: {r['muestra']}")
            print()
            continue

        print(f"    ✗ {r['motivo']}")
        estado, cuerpo = bajar(url)
        if estado and estado < 400:
            declarados = links_declarados(cuerpo, url)
            enlazados = [u for u in enlaces_a_feeds(cuerpo, url)
                         if u not in declarados and u != url]
            for u in declarados:
                print(f"      declara: {u}")
            for u in enlazados[:12]:
                print(f"      enlaza:  {u}")
            if not declarados and not enlazados:
                print("      la página no ofrece ningún feed")
        print()


def main():
    argumentos = sys.argv[1:]

    # Una URL como argumento se prueba tal cual. Los ids buscan; una URL ya
    # es la sospecha concreta y lo único que falta es el veredicto.
    urls = [a for a in argumentos if a.lower().startswith("http")]
    if urls:
        probar_urls(urls)
        if len(urls) == len(argumentos):
            return

    filtro = {a.lower() for a in argumentos if a not in urls}
    # "todas" es explícito: pasar argumentos que no matchean ningún id dejaba
    # la lista vacía y el script terminaba con un "0 y 0" que parecía un
    # resultado real en vez de un filtro mal escrito.
    if "todas" in filtro:
        filtro = set()
    objetivo = [
        {"id": c[0], "nombre": c[1], "home": c[2], "categoria": c[3],
         "tier": c[4], "actual": None}
        for c in CANDIDATAS if not filtro or c[0] in filtro
    ]

    # Un id que no está entre las institucionales puede ser una fuente que ya
    # vive en FUENTES.py y el fetcher reporta caída. Ese es el caso de uso
    # frecuente: el registro de salud dice "fundar, microjuris_laboral,
    # noticiasnet_energia" y uno quiere saber qué les pasó sin editar nada.
    ya_estan = {c["id"] for c in objetivo}
    for fid in sorted(filtro - ya_estan):
        del_catalogo = desde_catalogo(fid)
        if del_catalogo:
            objetivo.append(del_catalogo)

    if not objetivo:
        conocidos = ", ".join(c[0] for c in CANDIDATAS)
        print(f"Ningún id coincide con {sorted(filtro)}.")
        print(f"Institucionales: {conocidos}")
        print("También sirve cualquier id de FUENTES.py "
              "(ej: fundar, microjuris_laboral).")
        print("Usá 'todas' para probar todas las institucionales.")
        sys.exit(1)

    plural = "fuente" if len(objetivo) == 1 else "fuentes"
    print(f"Probando {len(objetivo)} {plural} "
          f"({PARALELAS} en paralelo, {TIMEOUT}s por pedido)…\n")

    def procesar(candidata):
        """Busca el feed de UNA institución. Devuelve (líneas, hallazgo)."""
        fid, nombre = candidata["id"], candidata["nombre"]
        home, actual = candidata["home"], candidata["actual"]
        categoria, tier = candidata["categoria"], candidata["tier"]
        log = [f"=== {nombre} ({fid}) — {home}"]
        if actual:
            log.append(f"    en catálogo: {actual}")

        declarados, candidatos = candidatos_de(home, actual)
        log.append(f"    el sitio declara {len(declarados)} feed(s)"
                   if declarados else
                   "    no declara feed; pruebo rutas habituales")

        for url in candidatos:
            r = evaluar(url)
            if r["ok"]:
                log.append(f"    ✓ {url}")
                if url == actual:
                    log.append("      es la URL que ya tiene el catálogo: "
                               "la caída fue pasajera, no hay que cambiar nada")
                log.append(f"      {r['entradas']} entradas · última: {r['ultima']}")
                log.append(f"      ej: {r['muestra']}")
                return log, (fid, nombre, r["url"], categoria, tier)
            log.append(f"      · {url[:70]} → {r['motivo'][:45]}")

        log.append("    ✗ ningún candidato sirvió")
        return log, None

    hallazgos, sin_suerte = [], []
    with ThreadPoolExecutor(max_workers=PARALELAS) as pool:
        for candidata, (log, hallazgo) in zip(
                objetivo, pool.map(procesar, objetivo)):
            print("\n".join(log) + "\n", flush=True)
            if hallazgo:
                hallazgos.append(hallazgo)
            else:
                sin_suerte.append((candidata["id"], candidata["nombre"]))

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
