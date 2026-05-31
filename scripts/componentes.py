"""
PPA — componentes.py v4.1
Cabecera sticky, menú hamburguesa, pie compacto.
Paleta tresempanadas.
"""

import os
import re
from datetime import datetime, timezone, timedelta

TZ_AR = timezone(timedelta(hours=-3))
MESES = ["enero","febrero","marzo","abril","mayo","junio",
         "julio","agosto","septiembre","octubre","noviembre","diciembre"]
DIAS_SEMANA = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

def fecha_legible(dt=None):
    if dt is None:
        dt = datetime.now(TZ_AR)
    return f"{DIAS_SEMANA[dt.weekday()]} {dt.day} de {MESES[dt.month-1]} de {dt.year}"

def fecha_corta(dt=None):
    if dt is None:
        dt = datetime.now(TZ_AR)
    return f"{DIAS_SEMANA[dt.weekday()][:3].upper()} {dt.day}/{dt.month:02d}/{dt.year}"


_SECCIONES = [
    ("Portada",     "/"),
    ("Análisis",    "/analisis/"),
    ("EconoTuits",  "/tuits/"),
    ("REM",         "/rem/"),
    ("Tablero",     "/tablero/"),
    ("Documentos",  "/documentos/"),
    ("Columnas",    "/columnas/"),
    ("Stream",      "/stream/"),
]


def cabecera(activo="", edicion_nombre="", edicion_icono=""):
    if not edicion_nombre:
        ahora = datetime.now(TZ_AR)
        edicion_nombre = "Desayuno" if ahora.hour < 14 else "Merienda"
        edicion_icono  = "🧉" if edicion_nombre == "Desayuno" else "☕"
    fecha = fecha_corta()

    _partes = []
    for nombre, href in _SECCIONES:
        clase = ' class="activo"' if nombre == activo else ''
        _partes.append(f'<a href="{href}"{clase}>{nombre}</a>')
    items = '\n    '.join(_partes)
    return f"""
<div id="cabecera-wrap">
<header class="cabecera-ppa expandida" id="cabecera-ppa">
  <!-- Fila superior: fecha · clima · edición -->
  <div class="cab-top">
    <div class="cab-top-izq">
      <span class="cab-fecha">{fecha}</span>
      <span class="cab-clima" id="cab-clima"></span>
    </div>
    <span class="cab-edicion">Edición {edicion_nombre} {edicion_icono}</span>
  </div>
  <!-- Fila logo + datos + hamburguesa -->
  <div class="cab-logo-fila">
    <div>
      <a href="/" class="cab-logo">PPA</a>
      <div class="cab-tagline">Pulso Productivo Argentino</div>
    </div>
    <div class="cab-datos-expandidos">
      <div class="cab-dato">
        <span class="cab-dato-label">Oficial</span>
        <span class="cab-dato-valor" id="dolar-oficial">…</span>
      </div>
      <div class="cab-dato">
        <span class="cab-dato-label">MEP</span>
        <span class="cab-dato-valor" id="dolar-mep">…</span>
      </div>
      <div class="cab-dato hide-mobile">
        <span class="cab-dato-label">Blue</span>
        <span class="cab-dato-valor" id="dolar-blue-cab">…</span>
      </div>
      <div class="cab-dato">
        <span class="cab-dato-label">Riesgo</span>
        <span class="cab-dato-valor" id="riesgo-pais">…</span>
      </div>
      <button class="cab-hamburguesa" id="btn-menu" aria-label="Menú">
        <span></span><span></span><span></span>
      </button>
    </div>
  </div>
</header>
<div class="cab-spacer" id="cab-spacer"></div>
</div>

<!-- DRAWER MENÚ -->
<div class="menu-overlay" id="menu-overlay"></div>
<nav class="menu-drawer" id="menu-drawer">
  <div class="menu-drawer-header">
    <span class="menu-drawer-logo">PPA</span>
    <button class="menu-cerrar" id="btn-menu-cerrar">✕</button>
  </div>
  <div class="menu-nav">
    {items}
  </div>
  <div class="menu-datos">
    <div class="menu-dato">
      <span class="menu-dato-label">USD Oficial</span>
      <span class="menu-dato-valor" id="m-dolar-oficial">…</span>
    </div>
    <div class="menu-dato">
      <span class="menu-dato-label">MEP</span>
      <span class="menu-dato-valor" id="m-dolar-mep">…</span>
    </div>
    <div class="menu-dato">
      <span class="menu-dato-label">Blue</span>
      <span class="menu-dato-valor" id="m-dolar-blue">…</span>
    </div>
    <div class="menu-dato">
      <span class="menu-dato-label">Riesgo</span>
      <span class="menu-dato-valor" id="m-riesgo">…</span>
    </div>
  </div>
</nav>"""


def nav_principal(activo=""):
    """Compatibilidad — el nav real está en el drawer. Devuelve vacío."""
    return ""


def franja_datos(dt=None):
    """Compatibilidad — los datos están en la cabecera. Devuelve vacío."""
    return ""


def pie():
    return """
<footer class="pie">
  <div class="contenedor">
    <span class="pie-logo">PPA</span>
    <span class="pie-bajada">Pulso Productivo Argentino · pulsoproductivo.com.ar</span>
    <div class="pie-meta">
      <a href="/analisis/">Análisis</a>
      <a href="/tuits/">EconoTuits</a>
      <a href="/rem/">REM</a>
      <a href="/tablero/">Tablero</a>
      <a href="/documentos/">Documentos</a>
      <a href="/columnas/">Columnas</a>
      <a href="/stream/">Stream</a>
      <a href="/como-trabajamos.html">Cómo trabajamos</a>
    </div>
    <span class="pie-legal">Editor responsable: Sergio Falco</span>
  </div>
</footer>"""


def head_comun(titulo, descripcion="Publicación económica argentina.", css_extra=""):
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
    if not texto: return texto
    t = re.sub(r'https?://\S+', '', str(texto))
    t = re.sub(r'\b(Acced[eé]|Disponible|Ver|Leer|Más|Link|Enlace)[^.:]*[:]\\s*$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s{2,}', ' ', t)
    t = re.sub(r'[\s·\-–—:]+$', '', t)
    return t.strip()
