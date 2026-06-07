"""
PPA — generador_tuits.py
Genera el bloque de tuits institucionales (/tuits/ y fragmento embebible).

Fuentes: cuentas fijas vía RSS de Nitter (nitter.net/{usuario}/rss)
  - BCRA        (@BancoCentral_AR)
  - INDEC       (@INDECArgentina)
  - Mecon       (@MinEconomiaAR)
  - Milei       (@JMilei)  ← opcional, se puede desactivar

Comportamiento ante caída de Nitter:
  - Si el feed responde: actualiza y guarda en data/tuits_cache.json
  - Si el feed falla: usa el cache (congela con lo último conocido)
  - Cada tuit tiene: usuario, texto limpio, fecha, link original a Twitter

El HTML generado va como sección en la home (fragmento) y como página propia.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA, DIR_SITE
import componentes as comp

TZ_AR      = timezone(timedelta(hours=-3))
JSON_TUITS = os.path.join(DIR_DATA, "tuits_cache.json")
DIR_TUITS  = os.path.join(DIR_SITE, "tuits")

# Cuentas a monitorear — orden = orden de aparición
CUENTAS = [
    {"id": "bcra",   "usuario": "BancoCentral_AR",  "nombre": "BCRA",                 "activa": True},
    {"id": "indec",  "usuario": "INDECArgentina",    "nombre": "INDEC",                "activa": True},
    {"id": "mecon",    "usuario": "MinEconomiaAR",    "nombre": "Ministerio de Economía",  "activa": True},
    {"id": "hacienda",  "usuario": "SecHacienda",       "nombre": "Secretaría de Hacienda",   "activa": True},
    {"id": "finanzas",  "usuario": "SecFinanzasAR",     "nombre": "Secretaría de Finanzas",   "activa": True},
    {"id": "energia",   "usuario": "EnergiaAR",         "nombre": "Secretaría de Energía",    "activa": True},
    {"id": "magyp",     "usuario": "magyp_ar",          "nombre": "Ministerio de Agricultura","activa": True},
    {"id": "comercio",  "usuario": "SecComercioAR",     "nombre": "Secretaría de Comercio",   "activa": True},
    {"id": "afip",      "usuario": "AFIP_Argentina",    "nombre": "AFIP",                     "activa": True},
    {"id": "cnv",       "usuario": "CNV_Argentina",     "nombre": "CNV",                      "activa": True},
    {"id": "canciller", "usuario": "CancilleriaARG",    "nombre": "Cancillería",              "activa": True},
    {"id": "opublica",  "usuario": "ObraPublicaAR",     "nombre": "Obras Públicas",           "activa": True},
    # ── Institucionales ──
    {"id":"fiel",       "usuario":"FIEL_arg",         "nombre":"FIEL",                   "activa":True},
    {"id":"ieral",      "usuario":"ieralprovincia",   "nombre":"IERAL",                  "activa":True},
    {"id":"fundar",     "usuario":"FundAr",           "nombre":"Fundar",                 "activa":True},
    {"id":"cippec",     "usuario":"CIPPEC",           "nombre":"CIPPEC",                 "activa":True},
    {"id":"cedlas",     "usuario":"CEDLAS_UNLP",      "nombre":"CEDLAS",                 "activa":True},
    {"id":"econviews",  "usuario":"econviews",        "nombre":"Econviews",              "activa":True},
    {"id":"acde",       "usuario":"ACDEArgentina",    "nombre":"ACDE",                   "activa":True},
    {"id":"abeceb",     "usuario":"AbecebConsult",    "nombre":"Abeceb",                 "activa":True},
    {"id":"pxq",        "usuario":"pxqconsultora",    "nombre":"PxQ",                    "activa":True},
    # ── Personales ──
    {"id":"vitelli",    "usuario":"SalvadorVitell1",  "nombre":"Salvador Vitelli",       "activa":True},
    {"id":"kiguel",     "usuario":"KiguelMiguel",     "nombre":"Miguel Kiguel",          "activa":True},
    {"id":"laspina",    "usuario":"laspina",          "nombre":"Luciano Laspina",        "activa":True},
    {"id":"spotorno",   "usuario":"fspotorno",        "nombre":"Fausto Spotorno",        "activa":True},
    {"id":"sica",       "usuario":"DanteSica",        "nombre":"Dante Sica",             "activa":True},
    {"id":"melconian",  "usuario":"mcarlosmelconian", "nombre":"Carlos Melconian",       "activa":True},
    {"id":"dalpoggetto","usuario":"DalPoggettoM",     "nombre":"Marina Dal Poggetto",    "activa":True},
]

# Clasificación por tipo
OFICIALES       = {"bcra","indec","mecon","hacienda","finanzas","energia","magyp","comercio","afip","cnv","canciller","opublica"}
INSTITUCIONALES = {"fiel","ieral","fundar","cippec","cedlas","econviews","acde","abeceb","pxq"}

TUITS_POR_CUENTA = 3   # máx tuits a mostrar por cuenta


# ================================================================
# RSS PARSING
# ================================================================

class RSSParser(HTMLParser):
    """Parser minimal de RSS/Atom — extrae items con title, link, pubDate, description."""
    def __init__(self):
        super().__init__()
        self.items = []
        self._item = None
        self._campo = None
        self._buf = ""

    def handle_starttag(self, tag, attrs):
        if tag == "item":
            self._item = {}
        elif tag in ("title", "link", "pubdate", "description") and self._item is not None:
            self._campo = tag
            self._buf = ""

    def handle_endtag(self, tag):
        if tag == "item" and self._item is not None:
            self.items.append(self._item)
            self._item = None
            self._campo = None
        elif tag == self._campo and self._item is not None:
            self._item[self._campo] = self._buf.strip()
            self._campo = None
            self._buf = ""

    def handle_data(self, data):
        if self._campo:
            self._buf += data

    def handle_entityref(self, name):
        if self._campo:
            self._buf += f"&{name};"

    def handle_charref(self, name):
        if self._campo:
            self._buf += f"&#{name};"


def _limpiar_texto(texto):
    """Elimina HTML, URLs y basura del texto del tuit."""
    if not texto: return ""
    # Decodificar entidades básicas
    t = texto.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"')
    # Quitar tags HTML
    t = re.sub(r"<[^>]+>", " ", t)
    # Quitar URLs
    t = re.sub(r"https?://\S+", "", t)
    # Quitar "RT @usuario:" al principio
    t = re.sub(r"^RT @\w+:\s*", "", t.strip())
    # Limpiar espacios
    t = re.sub(r"\s{2,}", " ", t)
    return t.strip()


def _fecha_iso(pubdate_str):
    """Convierte fecha RSS a ISO. Ej: 'Tue, 27 May 2026 14:30:00 +0000'"""
    if not pubdate_str: return ""
    meses = {"Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
             "Jul":7,"Aug":8,"Sep":9,"Oct":10,"Nov":11,"Dec":12}
    try:
        parts = pubdate_str.split()
        d, mes, y, hora = int(parts[1]), meses.get(parts[2], 1), int(parts[3]), parts[4]
        h, m, s = [int(x) for x in hora.split(":")]
        dt = datetime(y, mes, d, h, m, s, tzinfo=timezone.utc)
        return dt.isoformat()
    except Exception:
        return pubdate_str


def fetch_tuits_cuenta(cuenta):
    """Baja el RSS de Nitter para una cuenta. Devuelve lista de tuits o None si falla."""
    import requests, urllib3
    urllib3.disable_warnings()
    usuario = cuenta["usuario"]
    url = f"https://nitter.net/{usuario}/rss"
    try:
        r = requests.get(url, timeout=12, verify=False,
                         headers={"User-Agent": "PPA/4.0 RSS Reader"})
        if r.status_code != 200:
            print(f"   ⚠  {usuario}: HTTP {r.status_code}")
            return None
        p = RSSParser()
        p.feed(r.text)
        tuits = []
        for item in p.items[:TUITS_POR_CUENTA]:
            texto = _limpiar_texto(item.get("description") or item.get("title", ""))
            if not texto or len(texto) < 10:
                continue
            # Link: nitter → twitter
            link_nitter = item.get("link", "")
            link_twitter = link_nitter.replace("nitter.net", "twitter.com")
            tuits.append({
                "usuario":  usuario,
                "nombre":   cuenta["nombre"],
                "texto":    texto[:400],
                "fecha":    _fecha_iso(item.get("pubdate", "")),
                "link":     link_twitter,
            })
        print(f"   ✓  {usuario}: {len(tuits)} tuits")
        return tuits
    except Exception as e:
        print(f"   ⚠  {usuario}: {str(e)[:60]}")
        return None


# ================================================================
# CACHE
# ================================================================

def cargar_cache():
    if not os.path.exists(JSON_TUITS):
        return {}
    try:
        with open(JSON_TUITS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def guardar_cache(cache):
    os.makedirs(DIR_DATA, exist_ok=True)
    with open(JSON_TUITS, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def _leer_config_panel():
    """Lee la config de cuentas activas desde el panel69."""
    config_path = os.path.join(DIR_DATA, "econotuits_config.json")
    if not os.path.exists(config_path):
        return {}
    try:
        with open(config_path,'r',encoding='utf-8') as f:
            data = json.load(f)
        return data.get("config", {})
    except:
        return {}


def obtener_todos_los_tuits():
    """Para cada cuenta activa: intenta Nitter, si falla usa cache."""
    print("· EconoTuits (Nitter)")
    cache = cargar_cache()
    config_panel = _leer_config_panel()
    resultado = {}
    for cuenta in CUENTAS:
        cid = cuenta["id"]
        # Config del panel tiene prioridad sobre el default de CUENTAS
        activa = config_panel.get(cid, cuenta.get("activa", True))
        if not activa:
            continue
        cid = cuenta["id"]
        tuits = fetch_tuits_cuenta(cuenta)
        if tuits:
            resultado[cid] = {
                "nombre":       cuenta["nombre"],
                "usuario":      cuenta["usuario"],
                "tuits":        tuits,
                "actualizado":  datetime.now(timezone.utc).isoformat(),
                "fuente":       "nitter",
            }
        elif cid in cache:
            resultado[cid] = cache[cid]
            resultado[cid]["fuente"] = "cache"
            print(f"   ↩  {cuenta['usuario']}: usando cache")
        else:
            resultado[cid] = {
                "nombre":   cuenta["nombre"],
                "usuario":  cuenta["usuario"],
                "tuits":    [],
                "fuente":   "sin_datos",
            }
    guardar_cache(resultado)
    return resultado


# ================================================================
# HTML
# ================================================================

def escapar(s):
    if not s: return ""
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")


def _hora_legible(fecha_iso):
    if not fecha_iso: return ""
    try:
        dt = datetime.fromisoformat(fecha_iso.replace("Z", "+00:00")).astimezone(TZ_AR)
        hoy = datetime.now(TZ_AR).date()
        if dt.date() == hoy:
            return dt.strftime("%H:%M")
        return dt.strftime("%d/%m %H:%M")
    except Exception:
        return ""


def html_tuits(tuits_por_cuenta):
    """Genera el fragmento HTML del bloque de tuits (para embeber en otras páginas o standalone)."""
    bloques = []
    for cid, data in tuits_por_cuenta.items():
        tuits = data.get("tuits", [])
        if not tuits:
            continue
        usuario  = escapar(data.get("usuario", ""))
        nombre   = escapar(data.get("nombre", ""))
        fuente   = data.get("fuente", "")
        stale    = fuente == "cache"

        items_html = []
        for t in tuits:
            hora = _hora_legible(t.get("fecha", ""))
            items_html.append(f"""
        <article class="tuit-item{'  tuit-stale' if stale else ''}">
          <p class="tuit-texto">{escapar(t.get('texto',''))}</p>
          <div class="tuit-meta">
            <span class="tuit-hora">{escapar(hora)}</span>
            <a href="{escapar(t.get('link',''))}" target="_blank" rel="noopener" class="tuit-link">Ver en X →</a>
          </div>
        </article>""")

        stale_aviso = ' <span class="tuit-stale-aviso">· último conocido</span>' if stale else ''
        bloques.append(f"""
    <div class="tuits-cuenta">
      <div class="tuits-cuenta-header">
        <span class="tuits-nombre">{nombre}</span>
        <a href="https://twitter.com/{usuario}" target="_blank" rel="noopener" class="tuits-perfil">@{usuario}</a>
        {stale_aviso}
      </div>
      {''.join(items_html)}
    </div>""")

    if not bloques:
        return '<div class="tuits-vacio">Sin datos disponibles</div>'
    return f'<div class="tuits-grid">{"".join(bloques)}</div>'


def generar_pagina_tuits(tuits_por_cuenta):
    """Genera /tuits/index.html."""
    cuerpo = html_tuits(tuits_por_cuenta)
    total = sum(len(d.get("tuits", [])) for d in tuits_por_cuenta.values())

    html = f"""{comp.head_comun(
        "EconoTuits — PPA",
        "Lo último de BCRA, INDEC y Ministerio de Economía en X/Twitter.",
        css_extra='<link rel="stylesheet" href="/assets/ppa.css"><link rel="stylesheet" href="/assets/interior.css"><link rel="stylesheet" href="/assets/tuits.css">'
    )}
<body>

{comp.franja_datos()}
{comp.cabecera()}
{comp.nav_principal()}

<main class="tuits-main">
  <div class="contenedor">
    <div class="tuits-header">
      <h1 class="tuits-titulo">EconoTuits</h1>
      <p class="tuits-sub">Lo último de BCRA, INDEC y Ministerio de Economía en X/Twitter.
      Se actualiza con cada edición. Si Nitter no responde, muestra el último valor conocido.</p>
    </div>
    {cuerpo}
  </div>
</main>

{comp.pie()}
</body>
</html>"""

    os.makedirs(DIR_TUITS, exist_ok=True)
    out = os.path.join(DIR_TUITS, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[Tuits] Generado: {out} ({total} tuits)")
    return out


def generar_fragmento_tuits(tuits_por_cuenta):
    """Guarda el HTML del bloque para embeber en la home si se quiere."""
    fragmento = html_tuits(tuits_por_cuenta)
    out = os.path.join(DIR_DATA, "tuits_fragmento.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(fragmento)
    return out


def main():
    print(f"[Tuits] Inicio: {datetime.now(timezone.utc).isoformat()}")
    tuits = obtener_todos_los_tuits()
    generar_pagina_tuits(tuits)
    generar_fragmento_tuits(tuits)
    print(f"[Tuits] Fin")


if __name__ == "__main__":
    main()
