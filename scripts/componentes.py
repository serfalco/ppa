"""
PPA — componentes.py
Componentes HTML compartidos entre todos los generadores (v4).
Importar con: from componentes import franja_datos, cabecera, nav_principal, pie
"""

import os
from datetime import datetime, timezone, timedelta

TZ_AR = timezone(timedelta(hours=-3))
MESES = ["enero","febrero","marzo","abril","mayo","junio",
         "julio","agosto","septiembre","octubre","noviembre","diciembre"]
DIAS_SEMANA = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

def fecha_legible(dt=None):
    if dt is None:
        dt = datetime.now(TZ_AR)
    return f"{DIAS_SEMANA[dt.weekday()]} {dt.day} de {MESES[dt.month-1]} de {dt.year}"

# IDs JS que el ppa.js ya sabe leer — no cambiar sin actualizar el JS
def franja_datos(dt=None):
    """Franja superior negra: fecha + USD + MEP + Merval + Riesgo."""
    fecha = fecha_legible(dt)
    return f"""
<div class="franja-datos">
  <div class="contenedor franja-flex">
    <span class="fecha-mini">{fecha}</span>
    <span class="dato-mini">USD <span id="dolar-oficial">…</span></span>
    <span class="dato-mini">MEP <span id="dolar-mep">…</span></span>
    <span class="dato-mini" id="merval-item">Merval <span id="merval">…</span></span>
    <span class="dato-mini">Riesgo <span id="riesgo-pais">…</span></span>
  </div>
</div>"""


def cabecera(edicion_nombre="", edicion_icono=""):
    """Masthead: PPA grande + subtítulo + línea de edición."""
    if not edicion_nombre:
        ahora = datetime.now(TZ_AR)
        edicion_nombre = "Desayuno" if ahora.hour < 14 else "Merienda"
        edicion_icono  = "🧉" if edicion_nombre == "Desayuno" else "☕"
    linea = f"Edición {edicion_nombre} {edicion_icono}"
    return f"""
<header class="cabecera-home">
  <div class="contenedor">
    <h1 class="titulo-home">PPA</h1>
    <p class="subtitulo-home">Pulso Productivo Argentino</p>
    <p class="linea-edicion">{linea}</p>
  </div>
</header>"""


# Mapa sección → href (para marcar la activa)
_SECCIONES = [
    ("Portada",        "/"),
    ("Institucional",  "/institucional/"),
    ("Expectativas",   "/expectativas/"),
    ("Documentos",     "/documentos/"),
    ("Columnas",       "/columnas/"),
    ("Stream",         "/stream/"),
    ("Tablero",        "/tablero/"),
]

def nav_principal(activo=""):
    """Nav horizontal con la sección activa marcada. activo = nombre exacto de _SECCIONES."""
    items = []
    for nombre, href in _SECCIONES:
        clase = ' class="activo"' if nombre == activo else ''
        items.append(f'<a href="{href}"{clase}>{nombre}</a>')
    return f"""
<nav class="nav-principal">
  <div class="contenedor">
    <div class="nav-menu">
      {''.join(items)}
    </div>
  </div>
</nav>"""


def pie():
    """Pie de página común."""
    return """
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
</footer>"""


def head_comun(titulo, descripcion="Publicación económica argentina.", css_extra=""):
    """<head> estándar con fuentes y CSS base. css_extra = tags <link> adicionales."""
    return f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titulo}</title>
<meta name="description" content="{descripcion}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,900&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/ppa.css">
{css_extra}
</head>"""


import re

def limpiar_url(texto):
    """Quita URLs pegadas en títulos/bajadas (frecuente en RSS de Twitter/BCRA/INDEC).
    Ej: 'Accedé al informe en: https://...' → 'Accedé al informe en'"""
    if not texto: return texto
    t = re.sub(r'https?://\S+', '', str(texto))
    t = re.sub(r'\b(Acced[eé]|Disponible|Ver|Leer|Más|Link|Enlace)[^.:]*[:]\\s*$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s{2,}', ' ', t)
    t = re.sub(r'[\s·\-–—:]+$', '', t)
    return t.strip()
