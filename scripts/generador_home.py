"""
PPA — generador_home.py v5
Home completa en una página:
  1. La Data del Día (8 notas, mismo tamaño)
  2. Categorías (14, 2 columnas, icono + nombre)
  3. Tarjetas del Tablero (9 datos confiables, scroll horizontal)
  4. Columna (título + bajada + primer párrafo + degradado + ver más)
  5. TXT-Stream (4 notas)
  6. EconoTuits (Oficiales · Institucionales · Personales, 2 c/u)
  7. Footer
"""

import json
import os
import re
import sys
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA, DIR_SITE
from iconos import ICONO
import componentes as comp

TZ_AR = timezone(timedelta(hours=-3))
MESES = ["enero","febrero","marzo","abril","mayo","junio",
         "julio","agosto","septiembre","octubre","noviembre","diciembre"]
DIAS_SEMANA = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

JSON_PORTADA       = os.path.join(DIR_DATA, "portada.json")
JSON_NOTAS_PROPIAS = os.path.join(DIR_DATA, "notas_propias.json")
JSON_COLUMNAS      = os.path.join(DIR_DATA, "columnas_manual.json")
JSON_TUITS         = os.path.join(DIR_DATA, "tuits_cache.json")
DIR_STREAM_NOTAS   = os.path.join(DIR_SITE, "stream", "notas")

NOTAS_HOME    = 8
NOTAS_STREAM  = 4
TUITS_POR_COL = 2

# 14 categorías — orden de aparición en la grilla
CATEGORIAS_GRILLA = [
    "Macro", "Política", "Energía", "Agro",
    "Mercados", "Finanzas", "Comex", "Minería",
    "Laboral", "Automotor", "Logística", "Internacional",
    "Fiscal", "Fulbito",
]

ICONO_CAT = {
    "macro":         "macro",
    "politica":      "politica",
    "energia":       "energia",
    "agro":          "agro",
    "mercados":      "mercado",
    "finanzas":      "finanzas",
    "comex":         "comex",
    "mineria":       "mineria",
    "laboral":       "laboral",
    "automotor":     "automotor",
    "logistica":     "logistica",
    "internacional": "internacional",
    "fiscal":        "fiscal",
    "fulbito":       "fulbito",
}


def escapar(s):
    if not s: return ""
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def fecha_legible(dt):
    return f"{DIAS_SEMANA[dt.weekday()]} {dt.day} de {MESES[dt.month-1]} de {dt.year}"

def _norm(cat):
    return cat.lower().replace("é","e").replace("í","i").replace("ó","o").replace("á","a").replace(" ","-")


# ================================================================
# CARGAR DATOS
# ================================================================

def cargar_portada():
    if not os.path.exists(JSON_PORTADA):
        return {"destacados": [], "secciones": {}}
    try:
        with open(JSON_PORTADA,'r',encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"destacados": [], "secciones": {}}

def cargar_columna():
    """Devuelve la columna más reciente."""
    if os.path.exists(JSON_COLUMNAS):
        try:
            with open(JSON_COLUMNAS,'r',encoding='utf-8') as f:
                data = json.load(f)
            cols = data.get("columnas", [])
            if cols: return cols[0]
        except: pass
    if os.path.exists(JSON_NOTAS_PROPIAS):
        try:
            with open(JSON_NOTAS_PROPIAS,'r',encoding='utf-8') as f:
                data = json.load(f)
            cols = data.get("columnas", data.get("notas", []))
            if cols: return cols[0]
        except: pass
    return None

class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}; self.titulo = ""; self._en_title = False
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "meta":
            name = d.get("name") or d.get("property")
            if name: self.meta[name] = d.get("content","")
        elif tag == "title": self._en_title = True
    def handle_endtag(self, tag):
        if tag == "title": self._en_title = False
    def handle_data(self, data):
        if self._en_title: self.titulo += data

def cargar_stream():
    if not os.path.exists(DIR_STREAM_NOTAS): return []
    notas = []
    for archivo in sorted(os.listdir(DIR_STREAM_NOTAS), reverse=True):
        if not archivo.endswith('.html'): continue
        try:
            with open(os.path.join(DIR_STREAM_NOTAS, archivo),'r',encoding='utf-8') as f:
                html = f.read()
            p = MetaParser(); p.feed(html)
            notas.append({
                "slug":      archivo.replace('.html',''),
                "titulo":    p.titulo.replace(" — PPA Stream","").strip(),
                "categoria": p.meta.get("article:section",""),
            })
        except: continue
        if len(notas) >= NOTAS_STREAM: break
    return notas

def cargar_tuits():
    """Devuelve dict {oficiales: [], institucionales: [], personales: []}"""
    if not os.path.exists(JSON_TUITS):
        return {"oficiales": [], "institucionales": [], "personales": []}
    try:
        with open(JSON_TUITS,'r',encoding='utf-8') as f:
            cache = json.load(f)
    except:
        return {"oficiales": [], "institucionales": [], "personales": []}

    # Clasificación por tipo de cuenta
    OFICIALES      = {"bcra","indec","mecon","hacienda","finanzas","energia",
                      "magyp","comercio","afip","cnv","canciller","opublica"}
    INSTITUCIONALES = {"fiel","ieral","fundar","cedlas","cippec","iaraf","ceso"}

    resultado = {"oficiales": [], "institucionales": [], "personales": []}
    for cid, data in cache.items():
        tuits = data.get("tuits", [])[:TUITS_POR_COL]
        if not tuits: continue
        if cid in OFICIALES:
            resultado["oficiales"] += tuits
        elif cid in INSTITUCIONALES:
            resultado["institucionales"] += tuits
        else:
            resultado["personales"] += tuits

    # Limitar a TUITS_POR_COL por columna
    for k in resultado:
        resultado[k] = resultado[k][:TUITS_POR_COL]
    return resultado


# ================================================================
# HTML — LA DATA DEL DÍA (8 notas planas)
# ================================================================

def html_la_data(portada):
    destacados = portada.get("destacados", [])
    secciones  = portada.get("secciones", {})

    # Juntar todas las notas: destacados primero, después secciones por orden
    todas = list(destacados)
    for cat in CATEGORIAS_GRILLA:
        for n in secciones.get(cat, []):
            if n not in todas:
                todas.append(n)
    # Fallback: resto de secciones
    for notas in secciones.values():
        for n in notas:
            if n not in todas:
                todas.append(n)

    todas = todas[:NOTAS_HOME]
    if not todas:
        return '<p class="home-vacio">Cargando la edición…</p>'

    items = []
    for n in todas:
        titulo = escapar(comp.limpiar_url(n.get("titulo","")))
        fuente = escapar(n.get("fuente_nombre",""))
        cat    = escapar(n.get("categoria",""))
        link   = escapar(n.get("link","#"))
        resumen = escapar(comp.limpiar_url(n.get("resumen","")))
        cat_slug = cat.lower().replace(" ","-").replace("é","e").replace("í","i").replace("ó","o").replace("á","a")
        href_nota = f"/la-data/#{cat_slug}"
        items.append(f"""
      <li class="data-item">
        <span class="data-cat">{cat}</span>
        <a href="{href_nota}" class="data-titulo">{titulo}</a>
        {f'<span class="data-resumen">{resumen}</span>' if resumen else ''}
        <span class="data-fuente">{fuente}</span>
      </li>""")

    return f"""
<section class="home-la-data">
  <div class="kicker">La Data del Día</div>
  <div class="kicker-linea"></div>
  <ul class="data-lista">
    {''.join(items)}
  </ul>
</section>"""


# ================================================================
# HTML — CATEGORÍAS (14, 2 columnas)
# ================================================================

def html_categorias():
    items = []
    for cat in CATEGORIAS_GRILLA:
        key  = _norm(cat)
        ic   = ICONO.get(ICONO_CAT.get(key, ""), "")
        href = f"/la-data/#{key}"
        items.append(f"""
      <a href="{href}" class="cat-link">
        <span class="cat-ic">{ic}</span>
        <span class="cat-txt">{escapar(cat)}</span>
      </a>""")

    return f"""
<section class="home-categorias">
  <div class="cats-grid">
    {''.join(items)}
  </div>
</section>"""


# ================================================================
# HTML — TARJETAS TABLERO (scroll horizontal)
# ================================================================

def html_tarjetas_tablero():
    tarjetas = [
        ("tarjeta-dolar-oficial", "Oficial",   "/tablero/#dolares"),
        ("tarjeta-dolar-mep",     "MEP",        "/tablero/#dolares"),
        ("tarjeta-dolar-ccl",     "CCL",        "/tablero/#dolares"),
        ("tarjeta-dolar-blue",    "Blue",       "/tablero/#dolares"),
        ("tarjeta-reservas",      "Reservas",   "/tablero/#bcra"),
        ("tarjeta-brecha",        "Brecha MEP", "/tablero/#dolares"),
        ("tarjeta-banda",         "Banda",      "/tablero/#dolares"),
        ("tarjeta-ipc",           "IPC",        "/tablero/#macro"),
        ("tarjeta-tcrm",          "TCRM",       "/tcrm/"),
    ]
    cards = []
    for id_, label, href in tarjetas:
        cards.append(f"""
      <a href="{href}" class="t-card" id="{id_}">
        <span class="t-label">{label}</span>
        <span class="t-valor">…</span>
        <span class="t-var"></span>
      </a>""")

    return f"""
<section class="home-tarjetas">
  <div class="tablero-scroll">
    {''.join(cards)}
  </div>
</section>"""


# ================================================================
# HTML — COLUMNA (degradado)
# ================================================================

def html_columna(col):
    if not col:
        return ""
    titulo = escapar(col.get("titulo",""))
    bajada = escapar(col.get("bajada",""))
    slug   = escapar(col.get("slug",""))
    cuerpo = col.get("cuerpo", col.get("texto",""))
    # Primer párrafo: hasta 300 chars
    primer_parrafo = escapar(cuerpo[:300]) if cuerpo else ""

    return f"""
<section class="home-columna">
  <div class="kicker">Columnas</div>
  <div class="kicker-linea"></div>
  <h2 class="col-titulo-h">{titulo}</h2>
  {f'<p class="col-bajada-h">{bajada}</p>' if bajada else ''}
  <div class="col-texto-wrap">
    <p class="col-texto-h">{primer_parrafo}</p>
    <div class="col-fade-h"></div>
  </div>
  <a href="/columnas/{slug}.html" class="col-ver-h">Ver más →</a>
</section>"""


# ================================================================
# HTML — TXT-STREAM
# ================================================================

def html_stream(notas):
    if not notas:
        return ""
    items = []
    for n in notas:
        cat    = escapar(n.get("categoria",""))
        titulo = escapar(n.get("titulo",""))
        slug   = escapar(n.get("slug",""))
        items.append(f"""
      <li class="sb-item">
        {f'<span class="sb-cat">{cat}</span>' if cat else ''}
        <a href="/stream/notas/{slug}.html" class="sb-titulo">{titulo}</a>
      </li>""")

    return f"""
<section class="home-stream">
  <div class="kicker">TXT-Stream</div>
  <div class="kicker-linea"></div>
  <p class="stream-bajada">Versión en texto de nuestros últimos streams.</p>
  <ul class="sb-lista">
    {''.join(items)}
  </ul>
  <a href="/stream/" class="sb-ver">Ver todo →</a>
</section>"""


# ================================================================
# HTML — ECONOTUITS
# ================================================================

def html_econotuits(tuits):
    def col_html(titulo_col, lista):
        if not lista:
            return f"""
      <div class="et-col">
        <div class="et-col-titulo">{titulo_col}</div>
        <p class="et-vacio">Sin datos</p>
      </div>"""
        items = []
        for t in lista:
            usuario = escapar(t.get("usuario",""))
            texto   = escapar(t.get("texto","")[:120])
            link    = escapar(t.get("link","#"))
            items.append(f"""
          <div class="et-tuit">
            <span class="et-cuenta">@{usuario}</span>
            <p class="et-texto">{texto}</p>
            <a href="{link}" target="_blank" rel="noopener" class="et-link">Ver →</a>
          </div>""")
        return f"""
      <div class="et-col">
        <div class="et-col-titulo">{titulo_col}</div>
        {''.join(items)}
      </div>"""

    return f"""
<section class="home-econotuits">
  <div class="kicker">EconoTuits</div>
  <div class="kicker-linea"></div>
  <div class="et-grid">
    {col_html("Oficiales",       tuits.get("oficiales",      []))}
    {col_html("Institucionales", tuits.get("institucionales",[]))}
    {col_html("Personales",      tuits.get("personales",     []))}
  </div>
  <a href="/tuits/" class="sb-ver">Ver todos →</a>
</section>"""


# ================================================================
# GENERAR HOME
# ================================================================

def generar_home():
    ahora = datetime.now(TZ_AR)
    edicion_nombre = os.environ.get("PPA_EDICION_NOMBRE","")
    edicion_icono  = os.environ.get("PPA_EDICION_ICONO","")
    if not edicion_nombre:
        edicion_nombre = "Desayuno" if ahora.hour < 14 else "Merienda"
        edicion_icono  = "🧉" if edicion_nombre == "Desayuno" else "☕"

    portada = cargar_portada()
    columna = cargar_columna()
    stream  = cargar_stream()
    tuits   = cargar_tuits()

    html = (
        comp.head_comun(
            "PPA · Pulso Productivo Argentino",
            "Publicación económica argentina. La Data del Día, datos de mercado, columnas y más.",
            css_extra='<link rel="stylesheet" href="/assets/home.css">\n<link rel="stylesheet" href="/assets/carrusel-datos.css">'
        ) + f"""
<body class="body-home">

{comp.cabecera("Portada", edicion_nombre, edicion_icono)}

<main class="home-main">
<div class="contenedor">

{html_la_data(portada)}

{html_categorias()}

{html_tarjetas_tablero()}

{html_columna(columna)}

{html_stream(stream)}

{html_econotuits(tuits)}

</div>
</main>

{comp.pie()}
<script src="/assets/ppa.js"></script>
</body>
</html>"""
    )

    out = os.path.join(DIR_SITE, "index.html")
    os.makedirs(DIR_SITE, exist_ok=True)
    with open(out,'w',encoding='utf-8') as f:
        f.write(html)
    print(f"[Home v5] Generada: {out} — {edicion_nombre} {edicion_icono}")


def main():
    print(f"[Home v5] Inicio: {datetime.now(timezone.utc).isoformat()}")
    generar_home()

if __name__ == "__main__":
    main()
