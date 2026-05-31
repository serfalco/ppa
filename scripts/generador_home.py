"""
PPA — generador_home.py v4
HOME DENSA: columna principal con muchos títulos por bloques temáticos + sidebar columnas/stream.
El clic en la home va a la sección interna de PPA (no directo a la fuente) → +1 página vista.
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


def limpiar_url(texto):
    if not texto: return texto
    t = re.sub(r'https?://\S+', '', str(texto))
    t = re.sub(r'\b(Acced[eé]|Disponible|Ver|Leer|Más|Link|Enlace)[^.:]*[:]\\s*$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s{2,}', ' ', t)
    t = re.sub(r'[\s·\-–—:]+$', '', t)
    return t.strip()

TZ_AR = timezone(timedelta(hours=-3))
MESES = ["enero","febrero","marzo","abril","mayo","junio",
         "julio","agosto","septiembre","octubre","noviembre","diciembre"]
DIAS_SEMANA = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

JSON_PORTADA        = os.path.join(DIR_DATA, "portada.json")
JSON_NOTAS_PROPIAS  = os.path.join(DIR_DATA, "notas_propias.json")
JSON_COLUMNAS_PANEL = os.path.join(DIR_DATA, "columnas_manual.json")
DIR_STREAM_NOTAS    = os.path.join(DIR_SITE, "stream", "notas")

# Orden canónico de categorías en la home densa
CATEGORIAS_HOME = [
    "Macro", "Política", "Mercados", "Finanzas",
    "Energía", "Agro", "Minería", "Comex",
    "Laboral", "Automotor", "Logística", "Internacional",
]

# Iconos por categoría (usa los disponibles en iconos.py)
ICONO_CAT = {
    "Macro":         "macro",
    "Política":      "politica",
    "Mercados":      "mercado",
    "Finanzas":      "finanzas",
    "Energía":       "energia",
    "Agro":          "agro",
    "Minería":       "mineria",
    "Comex":         "comex",
    "Laboral":       "laboral",
    "Automotor":     "automotor",
    "Logística":     "logistica",
    "Internacional": "internacional",
}


def escapar(s):
    if not s: return ""
    return (str(s).replace("&","&amp;").replace("<","&lt;")
            .replace(">","&gt;").replace('"',"&quot;"))

def fecha_legible(dt):
    return f"{DIAS_SEMANA[dt.weekday()]} {dt.day} de {MESES[dt.month-1]} de {dt.year}"


# =============================================================
# CARGAR DATOS
# =============================================================

def cargar_institucional():
    """Devuelve dict con 'destacados' (lista) y 'secciones' (dict cat → lista notas)."""
    if not os.path.exists(JSON_PORTADA):
        return {"destacados": [], "secciones": {}}
    try:
        with open(JSON_PORTADA,'r',encoding='utf-8') as f:
            data = json.load(f)
        return {
            "destacados": data.get("destacados", [])[:5],
            "secciones":  data.get("secciones", {}),
        }
    except:
        return {"destacados": [], "secciones": {}}

def cargar_columnas():
    """Combina columnas del panel y de notas_propias. Devuelve las 4 más recientes."""
    columnas = []
    # Panel primero
    if os.path.exists(JSON_COLUMNAS_PANEL):
        try:
            with open(JSON_COLUMNAS_PANEL,'r',encoding='utf-8') as f:
                data = json.load(f)
            columnas += data.get("columnas", [])
        except: pass
    # Respaldo notas_propias
    if os.path.exists(JSON_NOTAS_PROPIAS):
        try:
            with open(JSON_NOTAS_PROPIAS,'r',encoding='utf-8') as f:
                data = json.load(f)
            respaldo = data.get("notas", data.get("columnas", []))
            slugs = {c.get("slug") for c in columnas}
            for c in respaldo:
                if c.get("slug") not in slugs:
                    columnas.append(c)
        except: pass
    columnas.sort(key=lambda c: c.get("fecha_publicacion",""), reverse=True)
    return columnas[:4]


class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}; self.titulo = ""; self.en_title = False
    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "meta":
            name = d.get("name") or d.get("property")
            if name: self.meta[name] = d.get("content","")
        elif tag == "title": self.en_title = True
    def handle_endtag(self, tag):
        if tag == "title": self.en_title = False
    def handle_data(self, data):
        if self.en_title: self.titulo += data

def cargar_stream():
    if not os.path.exists(DIR_STREAM_NOTAS): return []
    notas = []
    for archivo in sorted(os.listdir(DIR_STREAM_NOTAS)):
        if not archivo.endswith('.html'): continue
        path = os.path.join(DIR_STREAM_NOTAS, archivo)
        try:
            with open(path,'r',encoding='utf-8') as f: html = f.read()
            p = MetaParser(); p.feed(html)
            notas.append({
                "slug": archivo.replace('.html',''),
                "titulo": p.titulo.replace(" — PPA Stream","").strip(),
                "bajada": p.meta.get("description",""),
                "categoria": p.meta.get("article:section","General"),
                "fecha": p.meta.get("article:published_time",""),
            })
        except: continue
    notas.sort(key=lambda n: n.get("fecha",""), reverse=True)
    return notas[:4]


# =============================================================
# CARRUSEL DE DATOS
# =============================================================

def carrusel_datos():
    tarjetas = [
        ("tarjeta-riesgo",        "RIESGO PAÍS",   "/tablero/#mercado",  True),
        ("tarjeta-dolar-oficial", "DÓLAR OFICIAL", "/tablero/#dolares",  False),
        ("tarjeta-dolar-mep",     "DÓLAR MEP",     "/tablero/#dolares",  False),
        ("tarjeta-dolar-ccl",     "DÓLAR CCL",     "/tablero/#dolares",  False),
        ("tarjeta-dolar-blue",    "DÓLAR BLUE",    "/tablero/#dolares",  False),
        ("tarjeta-merval",        "MERVAL",         "/tablero/#mercado",  False),
        ("tarjeta-reservas",      "RESERVAS BCRA", "/tablero/#mercado",  False),
        ("tarjeta-brecha",        "BRECHA MEP",    "/tablero/#dolares",  False),
        ("tarjeta-ipc",           "IPC MENSUAL",   "/tablero/#macro",    False),
        ("tarjeta-emae",          "EMAE",           "/tablero/#macro",    False),
    ]
    cards_html = []
    for id_, titulo, href, destacada in tarjetas:
        clase = "tarjeta-dato" + (" tarjeta-destacada" if destacada else "")
        cards_html.append(f"""
      <a href="{href}" class="{clase}" id="{id_}" title="Ver en Tablero PPA">
        <span class="tarjeta-titulo">{titulo}</span>
        <span class="tarjeta-valor">…</span>
        <span class="tarjeta-var"></span>
        <span class="tarjeta-hora"></span>
      </a>""")
    tarjeta_banda = f"""
      <a href="/tablero/#dolares" class="tarjeta-dato tarjeta-banda" id="tarjeta-banda" title="Banda cambiaria">
        <span class="tarjeta-titulo">{ICONO['banda']}Banda cambiaria</span>
        <div class="banda-term">
          <div class="banda-barra"><div class="banda-marcador" id="banda-marcador"></div></div>
          <div class="banda-pies">
            <span class="banda-piso" id="banda-piso">…</span>
            <span class="banda-actual" id="banda-actual"></span>
            <span class="banda-techo" id="banda-techo">…</span>
          </div>
        </div>
      </a>"""
    cards_html.append(tarjeta_banda)
    return f"""
<section class="franja-tarjetas">
  <div class="carrusel-datos" id="carrusel-datos">
    <div class="carrusel-pista" id="carrusel-pista">
    {''.join(cards_html)}
    </div>
  </div>
</section>"""


# =============================================================
# HOME DENSA — bloques temáticos
# =============================================================

def bloque_destacados(notas):
    """Los 3-5 destacados del día: título grande + fuente. Van arriba del todo."""
    if not notas: return ""
    items = []
    for i, n in enumerate(notas):
        titulo = escapar(limpiar_url(n.get("titulo","")))
        fuente = escapar(n.get("fuente_nombre",""))
        cat    = escapar(n.get("categoria",""))
        link_interno = f"/institucional/"
        clase = "dest-principal" if i == 0 else "dest-secundario"
        items.append(f"""
      <article class="dest-item {clase}">
        <span class="dest-cat">{cat}</span>
        <h2 class="dest-titulo"><a href="{link_interno}">{titulo}</a></h2>
        <span class="dest-fuente">{fuente}</span>
      </article>""")
    return f"""
<div class="home-destacados">
  <div class="dest-label">LO MÁS IMPORTANTE</div>
  <div class="dest-lista">
    {''.join(items)}
  </div>
</div>"""


def bloque_categoria(cat, notas, max_notas=6):
    """Un bloque temático: título de sección + lista de títulos."""
    if not notas: return ""
    icono_key = ICONO_CAT.get(cat, "")
    icono_html = ICONO.get(icono_key, "") if icono_key else ""
    cat_slug = cat.lower().replace(" ", "-").replace("é","e").replace("í","i").replace("ó","o")
    link_seccion = f"/institucional/#{cat_slug}"

    items = []
    for n in notas[:max_notas]:
        titulo = escapar(limpiar_url(n.get("titulo","")))
        fuente = escapar(n.get("fuente_nombre",""))
        # El clic va a la sección interna, no directo a la fuente
        items.append(f"""
        <li class="cat-item">
          <a href="{link_seccion}" class="cat-titulo">{titulo}</a>
          <span class="cat-fuente">{fuente}</span>
        </li>""")

    return f"""
<div class="home-bloque-cat">
  <div class="cat-header">
    <span class="cat-icono">{icono_html}</span>
    <a href="{link_seccion}" class="cat-nombre">{escapar(cat)}</a>
  </div>
  <ul class="cat-lista">
    {''.join(items)}
  </ul>
</div>"""


def columna_principal(institucional):
    """La columna gruesa: destacados + grilla de bloques por categoría."""
    destacados = institucional.get("destacados", [])
    secciones  = institucional.get("secciones", {})

    bloques_cats = []
    for cat in CATEGORIAS_HOME:
        notas = secciones.get(cat, [])
        if notas:
            bloques_cats.append(bloque_categoria(cat, notas))

    # Si no hay ninguna categoría del orden canónico, mostrar lo que haya
    if not bloques_cats:
        for cat, notas in secciones.items():
            if cat not in CATEGORIAS_HOME and notas:
                bloques_cats.append(bloque_categoria(cat, notas))

    bloques_html = "".join(bloques_cats) if bloques_cats else """
<div class="home-vacio">
  <p>Cargando la edición…</p>
</div>"""

    return f"""
<div class="home-col-principal">
  <div class="col-header">
    <span class="col-kicker">LA DATA DEL DÍA</span>
    <a href="/institucional/" class="col-ver-todo">Edición completa →</a>
  </div>
  {bloque_destacados(destacados)}
  <div class="home-cats-grid">
    {bloques_html}
  </div>
</div>"""


def sidebar_columnas(columnas):
    if not columnas: return ""
    items = []
    for c in columnas:
        titulo = escapar(c.get("titulo",""))
        bajada = escapar(c.get("bajada",""))
        slug   = escapar(c.get("slug",""))
        autor  = escapar(c.get("autor",""))
        items.append(f"""
    <article class="sb-item">
      <h3 class="sb-titulo"><a href="/columnas/{slug}.html">{titulo}</a></h3>
      {f'<p class="sb-bajada">{bajada}</p>' if bajada else ''}
      {f'<span class="sb-fuente">{autor}</span>' if autor else ''}
    </article>""")
    return f"""
<div class="sidebar-bloque sidebar-columnas">
  <div class="sb-header">
    <span class="sb-kicker">Columnas</span>
    <a href="/columnas/" class="sb-link">Ver todas →</a>
  </div>
  {''.join(items)}
</div>"""


def sidebar_stream(notas):
    if not notas: return ""
    items = []
    for n in notas:
        titulo = escapar(n.get("titulo",""))
        slug   = escapar(n.get("slug",""))
        cat    = escapar(n.get("categoria",""))
        items.append(f"""
    <article class="sb-item">
      <span class="sb-cat">{cat}</span>
      <h3 class="sb-titulo"><a href="/stream/notas/{slug}.html">{titulo}</a></h3>
    </article>""")
    return f"""
<div class="sidebar-bloque sidebar-stream">
  <div class="sb-header">
    <span class="sb-kicker">Stream</span>
    <a href="/stream/" class="sb-link">Ver todo →</a>
  </div>
  {''.join(items)}
</div>"""


# =============================================================
# GENERAR HOME
# =============================================================

def generar_home():
    ahora_ar = datetime.now(TZ_AR)

    edicion_nombre = os.environ.get("PPA_EDICION_NOMBRE", "")
    edicion_icono  = os.environ.get("PPA_EDICION_ICONO", "")
    if not edicion_nombre:
        edicion_nombre = "Desayuno" if ahora_ar.hour < 14 else "Merienda"
        edicion_icono  = "🧉" if edicion_nombre == "Desayuno" else "☕"

    linea_edicion = f"Edición {edicion_nombre} {edicion_icono}"

    institucional = cargar_institucional()
    columnas      = cargar_columnas()
    stream        = cargar_stream()

    html = (
        comp.head_comun(
            "PPA · Pulso Productivo Argentino",
            "Publicación económica argentina: análisis, datos de mercado, columnas y más.",
            css_extra='<link rel="stylesheet" href="/assets/home.css">\n<link rel="stylesheet" href="/assets/carrusel-datos.css">'
        ) + f"""
<body class="body-home">

{comp.cabecera("Portada", edicion_nombre, edicion_icono)}

<!-- CARRUSEL DE DATOS -->
{carrusel_datos()}

<!-- CONTENIDO: columna principal + sidebar -->
<main class="home-main">
  <div class="contenedor home-layout-densa">

    {columna_principal(institucional)}

    <aside class="home-sidebar">
      {sidebar_columnas(columnas)}
      {sidebar_stream(stream)}
    </aside>

  </div>
</main>

<!-- CINTA DE CATEGORÍAS -->
<nav class="nav-cats-cinta">
  <div class="contenedor nav-cats-scroll">
    <a href="/institucional/#macro">{ICONO['macro']}<span>Macro</span></a>
    <a href="/institucional/#politica">{ICONO['politica']}<span>Política</span></a>
    <a href="/institucional/#energia">{ICONO['energia']}<span>Energía</span></a>
    <a href="/institucional/#agro">{ICONO['agro']}<span>Agro</span></a>
    <a href="/institucional/#mineria">{ICONO['mineria']}<span>Minería</span></a>
    <a href="/institucional/#comex">{ICONO['comex']}<span>Comex</span></a>
    <a href="/institucional/#automotor">{ICONO['automotor']}<span>Automotor</span></a>
    <a href="/institucional/#logistica">{ICONO['logistica']}<span>Logística</span></a>
    <a href="/institucional/#internacional">{ICONO['internacional']}<span>Internacional</span></a>
  </div>
</nav>

<!-- PIE -->
<footer class="pie">
  <div class="contenedor">
    <strong>PPA · Pulso Productivo Argentino</strong><br>
    <span class="pie-bajada">Publicación económica · pulsoproductivo.com.ar</span>
    <div class="pie-meta">
      <a href="/institucional/">Institucional</a> ·
      <a href="/expectativas/">Expectativas de mercado</a> ·
      <a href="/documentos/">Documentos</a> ·
      <a href="/columnas/">Columnas</a> ·
      <a href="/stream/">Stream</a> ·
      <a href="/tablero/">Tablero</a> ·
      <a href="/como-trabajamos.html">Cómo trabajamos</a> ·
      <a href="/acerca.html">Acerca de</a>
    </div>
    <div class="pie-legal">Editor responsable: Sergio Falco</div>
  </div>
</footer>

<script src="/assets/ppa.js"></script>

</body>
</html>"""
    )

    out = os.path.join(DIR_SITE, "index.html")
    os.makedirs(DIR_SITE, exist_ok=True)
    with open(out,'w',encoding='utf-8') as f:
        f.write(html)
    print(f"[PPA Home v4] Generada: {out} — Edición {edicion_nombre} {edicion_icono}")


def main():
    print(f"[PPA Home v4] Inicio: {datetime.now(timezone.utc).isoformat()}")
    generar_home()
    print(f"[PPA Home v4] Fin")

if __name__ == "__main__":
    main()
