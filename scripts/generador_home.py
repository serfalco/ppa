"""
PPA — generador_home.py v3
Genera la home portal (/) con:
  - Franja de datos vivos (ticker)
  - Línea de edición: "Edición Desayuno 🧉 · Miércoles 28/05/2026 06:42"
  - Menú achicado, alineado izquierda, separado con |
  - 5 tarjetas Infobae clickeables
  - Bloques: Lo que se dice / Columnas / Stream
  - Encuesta lateral (desactivada por defecto)

Lee la edición de variables de entorno: PPA_EDICION_NOMBRE, PPA_EDICION_ICONO
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA, DIR_SITE

TZ_AR = timezone(timedelta(hours=-3))
MESES = ["enero","febrero","marzo","abril","mayo","junio",
         "julio","agosto","septiembre","octubre","noviembre","diciembre"]
DIAS_SEMANA = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

JSON_PORTADA       = os.path.join(DIR_DATA, "portada.json")
JSON_NOTAS_PROPIAS = os.path.join(DIR_DATA, "notas_propias.json")
DIR_STREAM_NOTAS   = os.path.join(DIR_SITE, "stream", "notas")


def escapar(s):
    if not s: return ""
    return (str(s).replace("&","&amp;").replace("<","&lt;")
            .replace(">","&gt;").replace('"',"&quot;"))

def fecha_legible(dt):
    return f"{DIAS_SEMANA[dt.weekday()]} {dt.day} de {MESES[dt.month-1]} de {dt.year}"

def fecha_edicion(dt):
    """Formato para la línea de edición: Miércoles 28/05/2026 06:42"""
    return f"{DIAS_SEMANA[dt.weekday()]} {dt.strftime('%d/%m/%Y %H:%M')}"


# =============================================================
# CARGAR DATOS
# =============================================================

def cargar_institucional():
    if not os.path.exists(JSON_PORTADA): return []
    try:
        with open(JSON_PORTADA,'r',encoding='utf-8') as f:
            data = json.load(f)
        return data.get("destacados",[])[:4]
    except: return []

def cargar_columnas():
    if not os.path.exists(JSON_NOTAS_PROPIAS): return []
    try:
        with open(JSON_NOTAS_PROPIAS,'r',encoding='utf-8') as f:
            data = json.load(f)
        columnas = data.get("notas",[])
        columnas.sort(key=lambda c: c.get("fecha_publicacion",""), reverse=True)
        return columnas[:4]
    except: return []

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
# BLOQUES HTML
# =============================================================

def bloque_institucional(notas):
    if not notas:
        return """
    <section class="bloque-home">
      <header class="bloque-header">
        <span class="bloque-kicker">Lo que se dice</span>
        <h2><a href="/institucional/">La Data del día</a></h2>
      </header>
      <p class="bloque-vacio">Cargando contenido...</p>
    </section>"""

    items_html = []
    for n in notas:
        items_html.append(f"""
      <article class="bloque-item">
        <span class="item-cat">{escapar(n.get('categoria',''))}</span>
        <h3><a href="{escapar(n['link'])}" target="_blank" rel="noopener">{escapar(n['titulo'])}</a></h3>
        <p class="item-fuente">{escapar(n['fuente_nombre'])}</p>
      </article>""")

    return f"""
    <section class="bloque-home bloque-institucional">
      <header class="bloque-header">
        <span class="bloque-kicker">Lo que se dice</span>
        <h2><a href="/institucional/">La Data del día</a></h2>
        <p class="bloque-sub">Lo más destacado de las instituciones, consultoras y centros de estudio</p>
      </header>
      <div class="bloque-items">
        {''.join(items_html)}
      </div>
      <a href="/institucional/" class="bloque-link">Ver edición completa →</a>
    </section>"""


def bloque_columnas(columnas):
    if not columnas: return ""
    principal = columnas[0]
    otras = columnas[1:4]
    otras_html = ""
    if otras:
        items = [f'<li><a href="/columnas/{escapar(c.get("slug",""))}.html">{escapar(c["titulo"])}</a></li>' for c in otras]
        otras_html = f'<ul class="bloque-otras">{"".join(items)}</ul>'
    return f"""
    <section class="bloque-home bloque-columnas">
      <header class="bloque-header">
        <span class="bloque-kicker">Columnas</span>
        <h2><a href="/columnas/">Análisis y miradas</a></h2>
        <p class="bloque-sub">Análisis y miradas estructurales de la economía argentina</p>
      </header>
      <article class="bloque-destacado">
        <h3><a href="/columnas/{escapar(principal.get('slug',''))}.html">{escapar(principal['titulo'])}</a></h3>
        <p>{escapar(principal.get('bajada',''))}</p>
      </article>
      {otras_html}
      <a href="/columnas/" class="bloque-link">Todas las columnas →</a>
    </section>"""


def bloque_stream(notas):
    if not notas: return ""
    items_html = []
    for n in notas:
        items_html.append(f"""
      <article class="bloque-item">
        <span class="item-cat">{escapar(n.get('categoria','General'))}</span>
        <h3><a href="/stream/notas/{escapar(n['slug'])}.html">{escapar(n['titulo'])}</a></h3>
        <p class="item-fuente">{escapar(n.get('bajada',''))[:120]}</p>
      </article>""")
    return f"""
    <section class="bloque-home bloque-stream">
      <header class="bloque-header">
        <span class="bloque-kicker">Stream</span>
        <h2><a href="/stream/">Opiniones personales</a></h2>
        <p class="bloque-sub">Miradas personales sobre participaciones en programas de streaming</p>
      </header>
      <div class="bloque-items">
        {''.join(items_html)}
      </div>
      <a href="/stream/" class="bloque-link">Todas las notas →</a>
    </section>"""


def tarjetas_infobae():
    """5 tarjetas clickeables que llevan al Tablero PPA."""
    tarjetas = [
        ("tarjeta-dolar-oficial", "DÓLAR OFICIAL",  "/tablero/#dolares"),
        ("tarjeta-dolar-mep",     "DÓLAR MEP",      "/tablero/#dolares"),
        ("tarjeta-riesgo",        "RIESGO PAÍS",    "/tablero/#mercado"),
        ("tarjeta-merval",        "MERVAL",          "/tablero/#mercado"),
        ("tarjeta-reservas",      "RESERVAS BCRA",  "/tablero/#macro"),
    ]
    cards_html = []
    for id_, titulo, href in tarjetas:
        cards_html.append(f"""
      <a href="{href}" class="tarjeta-dato" id="{id_}" title="Ver en Tablero PPA">
        <span class="tarjeta-titulo">{titulo}</span>
        <span class="tarjeta-valor">—</span>
        <span class="tarjeta-var"></span>
        <span class="tarjeta-hora"></span>
      </a>""")
    return f"""
<section class="franja-tarjetas">
  <div class="contenedor tarjetas-grid">
    {''.join(cards_html)}
  </div>
</section>"""


# =============================================================
# GENERAR HOME
# =============================================================

def generar_home():
    ahora_ar = datetime.now(TZ_AR)

    # Edición: lee variable de entorno o detecta por hora
    edicion_nombre = os.environ.get("PPA_EDICION_NOMBRE", "")
    edicion_icono  = os.environ.get("PPA_EDICION_ICONO", "")
    if not edicion_nombre:
        edicion_nombre = "Desayuno" if ahora_ar.hour < 14 else "Merienda"
        edicion_icono  = "🧉" if edicion_nombre == "Desayuno" else "☕"

    linea_edicion = f"Edición {edicion_nombre} {edicion_icono} · {fecha_edicion(ahora_ar)}"

    institucional = cargar_institucional()
    columnas      = cargar_columnas()
    stream        = cargar_stream()

    html = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PPA · Pulso Productivo Argentino</title>
<meta name="description" content="Publicación económica argentina: lo que dicen las instituciones, las expectativas del mercado, columnas editoriales y comentarios sobre streaming.">
<meta property="og:title" content="PPA · Pulso Productivo Argentino">
<meta property="og:description" content="Publicación económica argentina.">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,900&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/ppa.css">
<link rel="stylesheet" href="/assets/home.css">
<link rel="stylesheet" href="/assets/tarjetas-infobae.css">
</head>
<body class="body-home">

<!-- FRANJA SUPERIOR: datos vivos -->
<div class="franja-datos">
  <div class="contenedor franja-flex">
    <span class="fecha-mini">{escapar(fecha_legible(ahora_ar))}</span>
    <span class="dato-mini" id="clima-widget"></span>
    <span class="dato-mini">USD <span id="dolar-oficial">…</span></span>
    <span class="dato-mini">MEP <span id="dolar-mep">…</span></span>
    <span class="dato-mini">Merval <span id="merval">…</span></span>
    <span class="dato-mini">Riesgo <span id="riesgo-pais">…</span></span>
  </div>
</div>

<!-- MARQUESINA FULBITO -->
<div class="marquesina-fulbito" id="fulbito-bar" style="display:none">
  <div class="contenedor">
    <span class="fulbito-label">⚽ Fulbito hoy</span>
    <div class="fulbito-scroll" id="fulbito-partidos"></div>
  </div>
</div>

<!-- MASTHEAD -->
<header class="cabecera-home">
  <div class="contenedor">
    <h1 class="titulo-home">Pulso · Productivo · Argentino</h1>
    <p class="linea-edicion">{escapar(linea_edicion)}</p>
  </div>
</header>

<!-- WIDGET CIERRE DE MERCADO -->
<section class="widget-cierre" id="widget-cierre" style="display:none">
  <div class="contenedor">
    <div class="cierre-header">CIERRE DE MERCADO</div>
    <div class="cierre-body" id="cierre-body"></div>
  </div>
</section>

<!-- NAVEGACIÓN PRINCIPAL -->
<nav class="nav-principal">
  <div class="contenedor nav-flex">
    <div class="nav-menu">
      <a href="/" class="activo">Portada</a> |
      <a href="/institucional/">Lo que se dice</a> |
      <a href="/expectativas/">Expectativas</a> |
      <a href="/documentos/">Documentos</a> |
      <a href="/columnas/">Columnas</a> |
      <a href="/stream/">Stream</a> |
      <a href="/tablero/">Tablero</a>
    </div>
    <div class="nav-cats">
      <span class="nav-cats-label">Categorías:</span>
      <a href="/institucional/#macro">Macro</a> |
      <a href="/institucional/#politica">Política</a> |
      <a href="/institucional/#energia">Energía</a> |
      <a href="/institucional/#agro">Agro</a> |
      <a href="/institucional/#mineria">Minería</a> |
      <a href="/institucional/#comex">Comex</a> |
      <a href="/institucional/#automotor">Automotor</a> |
      <a href="/institucional/#logistica">Logística</a> |
      <a href="/institucional/#internacional">Internacional</a>
    </div>
  </div>
</nav>

<!-- 5 TARJETAS INFOBAE -->
{tarjetas_infobae()}

<!-- CONTENIDO PRINCIPAL + ENCUESTA -->
<main class="home-main">
  <div class="contenedor home-layout">

    <!-- BLOQUES EDITORIALES -->
    <div class="home-grid">
      {bloque_institucional(institucional)}
      {bloque_columnas(columnas)}
      {bloque_stream(stream)}
    </div>

    <!-- ENCUESTA LATERAL (desactivada por defecto) -->
    <!-- ENCUESTA_PLACEHOLDER -->

  </div>
</main>

<!-- PIE -->
<footer class="pie">
  <div class="contenedor">
    <strong>PPA · Pulso Productivo Argentino</strong><br>
    <span class="pie-bajada">Publicación económica · pulsoproductivo.com.ar</span>
    <div class="pie-meta">
      <a href="/institucional/">Lo que se dice</a> ·
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

    out = os.path.join(DIR_SITE, "index.html")
    os.makedirs(DIR_SITE, exist_ok=True)
    with open(out,'w',encoding='utf-8') as f:
        f.write(html)
    print(f"[PPA Home v3] Generada: {out} — Edición {edicion_nombre} {edicion_icono}")


def main():
    print(f"[PPA Home v3] Inicio: {datetime.now(timezone.utc).isoformat()}")
    generar_home()
    print(f"[PPA Home v3] Fin")

if __name__ == "__main__":
    main()
