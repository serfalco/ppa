"""
PPA — generador_home.py
Genera la home portal (/) con datos vivos arriba y 3 bloques iguales:
  - Institucional (3-4 destacados del agregador)
  - Columnas (última columna de Sergio Falco)
  - Stream (últimas notas del Blog Stream)

Cómo se corre:
    python scripts/generador_home.py
"""

import json
import os
import sys
import re
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA, DIR_SITE

TZ_AR = timezone(timedelta(hours=-3))
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

JSON_PORTADA = os.path.join(DIR_DATA, "portada.json")
JSON_NOTAS_PROPIAS = os.path.join(DIR_DATA, "notas_propias.json")
DIR_STREAM_NOTAS = os.path.join(DIR_SITE, "stream", "notas")


def escapar(s):
    if not s:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def fecha_legible(dt):
    return f"{DIAS_SEMANA[dt.weekday()]} {dt.day} de {MESES[dt.month - 1]} de {dt.year}"


# =============================================================
# CARGAR DATOS DE LAS TRES SECCIONES
# =============================================================

def cargar_institucional():
    """Carga los 4 destacados de la portada institucional."""
    if not os.path.exists(JSON_PORTADA):
        return []
    try:
        with open(JSON_PORTADA, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return []
    return data.get("destacados", [])[:4]


def cargar_columnas():
    """Carga las últimas columnas de Sergio Falco."""
    if not os.path.exists(JSON_NOTAS_PROPIAS):
        return []
    try:
        with open(JSON_NOTAS_PROPIAS, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return []
    columnas = data.get("notas", [])
    columnas.sort(key=lambda c: c.get("fecha_publicacion", ""), reverse=True)
    return columnas[:4]


# Reuso el parser de stream
class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.titulo = ""
        self.en_title = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == "meta":
            name = d.get("name") or d.get("property")
            content = d.get("content", "")
            if name:
                self.meta[name] = content
        elif tag == "title":
            self.en_title = True

    def handle_endtag(self, tag):
        if tag == "title":
            self.en_title = False

    def handle_data(self, data):
        if self.en_title:
            self.titulo += data


def cargar_stream():
    """Carga las últimas notas del Blog Stream leyendo los HTML."""
    if not os.path.exists(DIR_STREAM_NOTAS):
        return []
    notas = []
    for archivo in sorted(os.listdir(DIR_STREAM_NOTAS)):
        if not archivo.endswith('.html'):
            continue
        path = os.path.join(DIR_STREAM_NOTAS, archivo)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                html = f.read()
            p = MetaParser()
            p.feed(html)
            notas.append({
                "slug": archivo.replace('.html', ''),
                "titulo": p.titulo.replace(" — PPA Stream", "").strip(),
                "bajada": p.meta.get("description", ""),
                "categoria": p.meta.get("article:section", "General"),
                "fecha": p.meta.get("article:published_time", ""),
            })
        except Exception:
            continue
    notas.sort(key=lambda n: n.get("fecha", ""), reverse=True)
    return notas[:4]


# =============================================================
# HTML BUILDERS
# =============================================================

def bloque_institucional(notas):
    if not notas:
        return """
    <section class="bloque-home">
      <header class="bloque-header">
        <span class="bloque-kicker">Institucional</span>
        <h2><a href="/institucional/">Análisis del día</a></h2>
      </header>
      <p class="bloque-vacio">Cargando contenido institucional...</p>
    </section>"""

    items_html = []
    for n in notas:
        items_html.append(f"""
      <article class="bloque-item">
        <span class="item-cat">{escapar(n.get('categoria', ''))}</span>
        <h3><a href="{escapar(n['link'])}" target="_blank" rel="noopener">{escapar(n['titulo'])}</a></h3>
        <p class="item-fuente">{escapar(n['fuente_nombre'])}</p>
      </article>""")

    return f"""
    <section class="bloque-home bloque-institucional">
      <header class="bloque-header">
        <span class="bloque-kicker">Institucional</span>
        <h2><a href="/institucional/">Análisis del día</a></h2>
        <p class="bloque-sub">Lo más destacado de las instituciones, consultoras y centros de estudio</p>
      </header>
      <div class="bloque-items">
        {''.join(items_html)}
      </div>
      <a href="/institucional/" class="bloque-link">Ver edición completa →</a>
    </section>"""


def bloque_columnas(columnas):
    if not columnas:
        return """
    <section class="bloque-home bloque-columnas">
      <header class="bloque-header">
        <span class="bloque-kicker">Columnas</span>
        <h2><a href="/columnas/">La mirada del editor</a></h2>
      </header>
      <p class="bloque-vacio">Los martes a las 18hs sale una nueva columna.</p>
    </section>"""

    principal = columnas[0]
    otras = columnas[1:4]

    otras_html = ""
    if otras:
        items = [f'<li><a href="/columnas/{escapar(c.get("slug", ""))}.html">{escapar(c["titulo"])}</a></li>' for c in otras]
        otras_html = f'<ul class="bloque-otras">{"".join(items)}</ul>'

    return f"""
    <section class="bloque-home bloque-columnas">
      <header class="bloque-header">
        <span class="bloque-kicker">Columnas</span>
        <h2><a href="/columnas/">La mirada del editor</a></h2>
        <p class="bloque-sub">Análisis estructural de la economía argentina por Sergio Falco</p>
      </header>
      <article class="bloque-destacado">
        <h3><a href="/columnas/{escapar(principal.get('slug', ''))}.html">{escapar(principal['titulo'])}</a></h3>
        <p>{escapar(principal.get('bajada', ''))}</p>
      </article>
      {otras_html}
      <a href="/columnas/" class="bloque-link">Todas las columnas →</a>
    </section>"""


def bloque_stream(notas):
    if not notas:
        return """
    <section class="bloque-home bloque-stream">
      <header class="bloque-header">
        <span class="bloque-kicker">Stream</span>
        <h2><a href="/stream/">Comentarios editoriales</a></h2>
      </header>
      <p class="bloque-vacio">Comentarios sobre programas de streaming. Próximamente.</p>
    </section>"""

    items_html = []
    for n in notas:
        items_html.append(f"""
      <article class="bloque-item">
        <span class="item-cat">{escapar(n.get('categoria', 'General'))}</span>
        <h3><a href="/stream/notas/{escapar(n['slug'])}.html">{escapar(n['titulo'])}</a></h3>
        <p class="item-fuente">{escapar(n.get('bajada', ''))[:120]}</p>
      </article>""")

    return f"""
    <section class="bloque-home bloque-stream">
      <header class="bloque-header">
        <span class="bloque-kicker">Stream</span>
        <h2><a href="/stream/">Comentarios editoriales</a></h2>
        <p class="bloque-sub">Opiniones personales sobre participaciones en programas de streaming</p>
      </header>
      <div class="bloque-items">
        {''.join(items_html)}
      </div>
      <a href="/stream/" class="bloque-link">Todas las notas →</a>
    </section>"""


# =============================================================
# GENERAR HOME
# =============================================================

def generar_home():
    ahora_ar = datetime.now(TZ_AR)
    fecha_str = fecha_legible(ahora_ar)

    institucional = cargar_institucional()
    columnas = cargar_columnas()
    stream = cargar_stream()

    html = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PPA · Pulso Productivo Argentino</title>
<meta name="description" content="Diario económico institucional argentino: análisis de las consultoras, columnas editoriales y comentarios sobre streaming. Actualización diaria.">
<meta property="og:title" content="PPA · Pulso Productivo Argentino">
<meta property="og:description" content="Diario económico institucional argentino.">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,900&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/ppa.css">
<link rel="stylesheet" href="/assets/home.css">
</head>
<body class="body-home">

<!-- FRANJA SUPERIOR CHICA con datos vivos -->
<div class="franja-datos">
  <div class="contenedor franja-flex">
    <span class="fecha-mini">{escapar(fecha_str)}</span>
    <span class="dato-mini" id="clima-widget">—</span>
    <span class="dato-mini">USD <span id="dolar-oficial">—</span></span>
    <span class="dato-mini">Riesgo <span id="riesgo-pais">—</span></span>
  </div>
</div>

<!-- Marquesina Fulbito y MULC -->
<div class="marquesina-fulbito" id="fulbito-bar" style="display:none">
  <div class="contenedor">
    <span class="fulbito-label">⚽ Fulbito hoy</span>
    <div class="fulbito-scroll" id="fulbito-partidos"></div>
  </div>
</div>
<section class="widget-mulc" id="widget-mulc" style="display:none">
  <div class="contenedor">
    <div class="mulc-header">CIERRE MULC</div>
    <div class="mulc-body" id="mulc-body"><span class="mulc-loading">Cargando...</span></div>
  </div>
</section>

<!-- MASTHEAD -->
<header class="cabecera-home">
  <div class="contenedor">
    <h1 class="titulo-home">PPA</h1>
    <p class="bajada-home">Pulso · Productivo · Argentino</p>
  </div>
</header>

<!-- NAVEGACIÓN PRINCIPAL -->
<nav class="nav-principal">
  <div class="contenedor">
    <a href="/" class="activo">Portada</a>
    <a href="/institucional/">Institucional</a>
    <a href="/columnas/">Columnas</a>
    <a href="/stream/">Stream</a>
  </div>
</nav>

<!-- TRES BLOQUES IGUALES -->
<main class="home-main">
  <div class="contenedor">
    <div class="home-grid">
      {bloque_institucional(institucional)}
      {bloque_columnas(columnas)}
      {bloque_stream(stream)}
    </div>
  </div>
</main>

<!-- PIE -->
<footer class="pie">
  <div class="contenedor">
    <strong>PPA · Pulso Productivo Argentino</strong><br>
    <span class="pie-bajada">Diario económico institucional · pulsoproductivo.com.ar</span>
    <div class="pie-meta">
      <a href="/institucional/">Institucional</a> ·
      <a href="/columnas/">Columnas</a> ·
      <a href="/stream/">Stream</a> ·
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
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[PPA Home] Generada: {out}")


def main():
    print(f"[PPA Home] Inicio: {datetime.now(timezone.utc).isoformat()}")
    generar_home()
    print(f"[PPA Home] Fin")


if __name__ == "__main__":
    main()
