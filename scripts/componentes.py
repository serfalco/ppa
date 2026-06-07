"""
PPA — componentes.py v5
2 fuentes (Playfair Display + IBM Plex Sans) · 5 colores
Cabecera sticky con ticker pasarela · Drawer sin datos
"""

import os
import re
from datetime import datetime, timezone, timedelta

TZ_AR = timezone(timedelta(hours=-3))
MESES = ["enero","febrero","marzo","abril","mayo","junio",
         "julio","agosto","septiembre","octubre","noviembre","diciembre"]
DIAS_SEMANA = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

def fecha_corta(dt=None):
    if dt is None:
        dt = datetime.now(TZ_AR)
    dias = ["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"]
    return f"{dias[dt.weekday()]} {dt.day}/{dt.month:02d}/{dt.year}"

# Menú definitivo — orden cerrado
_SECCIONES = [
    ("Portada",         "/"),
    ("La Data del Día", "/la-data/"),
    ("REM",             "/rem/"),
    ("Columnas",        "/columnas/"),
    ("TXT-Stream",      "/stream/"),
    ("EconoTuits",      "/tuits/"),
    ("Tablero",         "/tablero/"),
    ("Documentos",      "/documentos/"),
    ("Cómo trabajamos", "/como-trabajamos.html"),
]

# Ticker: IDs que lee el JS de ppa.js
_TICKER_ITEMS = [
    ("OFICIAL",   "dolar-oficial"),
    ("MEP",       "dolar-mep"),
    ("BLUE",      "dolar-blue-cab"),
    ("RIESGO",    "riesgo-pais"),
    ("RESERVAS",  "reservas-cab"),
    ("IPC",       "ipc-cab"),
    ("TCRM",      "tcrm-cab"),
]

def _ticker_html():
    """Genera la pista del ticker doble (para loop continuo)."""
    items = "".join(
        f'<span>{label}<b id="{id_}">…</b></span>'
        for label, id_ in _TICKER_ITEMS
    )
    # Duplicado para el loop infinito
    return items + items


def cabecera(activo="", edicion_nombre="", edicion_icono=""):
    if not edicion_nombre:
        ahora = datetime.now(TZ_AR)
        edicion_nombre = "Desayuno" if ahora.hour < 14 else "Merienda"
        edicion_icono  = "🧉" if edicion_nombre == "Desayuno" else "☕"
    fecha = fecha_corta()

    # Menú items
    _partes = []
    for nombre, href in _SECCIONES:
        clase = ' class="activo"' if nombre == activo else ''
        _partes.append(f'<a href="{href}"{clase}>{nombre}</a>')
    menu_items = "\n    ".join(_partes)

    return f"""
<div id="cabecera-wrap">
<header class="cabecera-ppa expandida" id="cabecera-ppa">

  <div class="cab-top">
    <span class="cab-fecha">{fecha}</span>
    <span class="cab-edicion">Edición {edicion_nombre} {edicion_icono}</span>
  </div>

  <div class="cab-logo-fila">
    <div>
      <a href="/" class="cab-logo">PPA</a>
      <div class="cab-tagline">Pulso Productivo Argentino</div>
    </div>
    <button class="cab-hamburguesa" id="btn-menu" aria-label="Menú">
      <span></span><span></span><span></span>
    </button>
  </div>

  <div class="cab-ticker-wrap">
    <div class="cab-ticker" id="cab-ticker">
      {_ticker_html()}
    </div>
  </div>

</header>
<div class="cab-spacer" id="cab-spacer"></div>
</div>

<div class="menu-overlay" id="menu-overlay"></div>
<nav class="menu-drawer" id="menu-drawer">
  <div class="menu-drawer-header">
    <span class="menu-drawer-logo">PPA</span>
    <button class="menu-cerrar" id="btn-menu-cerrar">✕</button>
  </div>
  <div class="menu-nav">
    {menu_items}
  </div>
</nav>"""


def nav_principal(activo=""):
    return ""  # reemplazado por el drawer


def franja_datos(dt=None):
    return ""  # reemplazado por el ticker de la cabecera


def pie():
    links = " ·\n      ".join(
        f'<a href="{href}">{nombre}</a>'
        for nombre, href in _SECCIONES
    )
    return f"""
<footer class="pie">
  <div class="contenedor">
    <span class="pie-logo">PPA</span>
    <span class="pie-bajada">Pulso Productivo Argentino · pulsoproductivo.com.ar</span>
    <div class="pie-meta">
      {links}
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
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/ppa.css">
{css_extra}
</head>"""


def limpiar_url(texto):
    """Quita URLs pegadas en títulos (frecuente en RSS de Twitter/BCRA/INDEC)."""
    if not texto: return texto
    t = re.sub(r'https?://\S+', '', str(texto))
    t = re.sub(r'\b(Acced[eé]|Disponible|Ver|Leer|Más|Link|Enlace)[^.:]*[:]\s*$', '', t, flags=re.IGNORECASE)
    t = re.sub(r'\s{2,}', ' ', t)
    t = re.sub(r'[\s·\-–—:]+$', '', t)
    return t.strip()
