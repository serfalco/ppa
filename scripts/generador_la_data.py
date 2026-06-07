"""
PPA — generador_analisis.py
Fusión de Institucional + Expectativas → /la-data/

Genera:
  - site/la-data/index.html  (la sección principal)
  - site/institucional/index.html  (redirect 301 → /la-data/)
  - site/expectativas/index.html   (redirect 301 → /la-data/)

Lee: data/portada.json (notas institucionales) + data/portada.json secciones
     data/expectativas.json si existe (notas de consultoras con permanencia)

Criterio editorial:
  - Medios e instituciones oficiales (BCRA, INDEC, Mecon) → van a EconoTuits
  - Consultoras, institutos, universidades, ONG → van a Análisis
  - El REM del BCRA → sección propia /rem/
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA, DIR_SITE, CATEGORIAS
import componentes as comp

TZ_AR = timezone(timedelta(hours=-3))
MESES = ["enero","febrero","marzo","abril","mayo","junio",
         "julio","agosto","septiembre","octubre","noviembre","diciembre"]
DIAS_SEMANA = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

JSON_PORTADA = os.path.join(DIR_DATA, "portada.json")
DIR_ANALISIS  = os.path.join(DIR_SITE, "la-data")
DIR_INST      = os.path.join(DIR_SITE, "institucional")
DIR_EXPECT    = os.path.join(DIR_SITE, "expectativas")

ICONO = {
    "macro":        '<svg viewBox="0 0 32 32" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="27" x2="27" y2="27"/><rect x="7" y="18" width="4" height="9"/><rect x="14" y="13" width="4" height="14"/><rect x="21" y="8" width="4" height="19"/></svg>',
    "politica":     '<svg viewBox="0 0 32 32" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polyline points="6,12 16,6 26,12"/><line x1="8" y1="12" x2="8" y2="24"/><line x1="13" y1="12" x2="13" y2="24"/><line x1="19" y1="12" x2="19" y2="24"/><line x1="24" y1="12" x2="24" y2="24"/><line x1="5" y1="24" x2="27" y2="24"/></svg>',
    "energia":      '<svg viewBox="0 0 32 32" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><polygon points="18,4 8,18 15,18 14,28 24,14 17,14"/></svg>',
    "agro":         '<svg viewBox="0 0 32 32" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><line x1="16" y1="29" x2="16" y2="13"/><path d="M16 14 q-5 -1 -5 -6 q5 1 5 6"/><path d="M16 14 q5 -1 5 -6 q-5 1 -5 6"/></svg>',
    "comex":        '<svg viewBox="0 0 32 32" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 20 L27 20 L24 26 L8 26 Z"/><rect x="11" y="13" width="5" height="7"/><rect x="16" y="13" width="5" height="7"/><line x1="16" y1="8" x2="16" y2="13"/></svg>',
    "mineria":      '<svg viewBox="0 0 32 32" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 22 C 5 14, 11 9, 16 9 C 21 9, 27 14, 27 22"/><line x1="4" y1="22" x2="28" y2="22"/><rect x="14" y="6" width="4" height="5"/><circle cx="16" cy="14" r="2"/></svg>',
    "automotor":    '<svg viewBox="0 0 32 32" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><path d="M5 21 L7 14 L25 14 L27 21"/><line x1="4" y1="21" x2="28" y2="21"/><circle cx="10" cy="23" r="2.5"/><circle cx="22" cy="23" r="2.5"/></svg>',
    "logistica":    '<svg viewBox="0 0 32 32" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="11" width="13" height="10"/><path d="M17 14 L23 14 L27 18 L27 21 L17 21"/><circle cx="10" cy="23" r="2.5"/><circle cx="23" cy="23" r="2.5"/></svg>',
    "internacional":'<svg viewBox="0 0 32 32" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="16" cy="16" r="11"/><ellipse cx="16" cy="16" rx="5" ry="11"/><line x1="5" y1="16" x2="27" y2="16"/></svg>',
    "laboral":      '<svg viewBox="0 0 32 32" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><circle cx="16" cy="11" r="5"/><path d="M6 27 C 6 20, 11 18, 16 18 C 21 18, 26 20, 26 27"/></svg>',
    "fiscal":       '<svg viewBox="0 0 32 32" width="1em" height="1em" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"><rect x="7" y="5" width="18" height="22" rx="2"/><line x1="11" y1="11" x2="21" y2="11"/><line x1="11" y1="16" x2="21" y2="16"/><line x1="11" y1="21" x2="17" y2="21"/></svg>',
}

CATEGORIAS_ORDEN = [
    "Macro","Política","Mercados","Finanzas","Energía","Agro",
    "Minería","Comex","Laboral","Automotor","Logística","Internacional","Fiscal",
]

def escapar(s):
    if not s: return ""
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def hora_corta(fecha_iso):
    try:
        dt = datetime.fromisoformat(fecha_iso.replace('Z','+00:00')).astimezone(TZ_AR)
        return dt.strftime("%H:%M")
    except: return ""

def fecha_legible(dt):
    return f"{DIAS_SEMANA[dt.weekday()]} {dt.day} de {MESES[dt.month-1]} de {dt.year}"


def cargar_datos():
    if not os.path.exists(JSON_PORTADA):
        return {"destacados": [], "secciones": {}}
    try:
        with open(JSON_PORTADA,'r',encoding='utf-8') as f:
            return json.load(f)
    except:
        return {"destacados": [], "secciones": {}}


def nota_html(nota, grande=False):
    titulo = escapar(comp.limpiar_url(nota.get("titulo","")))
    fuente = escapar(nota.get("fuente_nombre",""))
    link   = escapar(nota.get("link","#"))
    cat    = escapar(nota.get("categoria",""))
    hora   = hora_corta(nota.get("fecha_publicacion",""))
    bajada = escapar(nota.get("bajada",""))

    if grande:
        return f"""
<article class="an-destacado">
  <span class="an-cat">{cat}</span>
  <h2 class="an-titulo-grande"><a href="{link}" target="_blank" rel="noopener">{titulo}</a></h2>
  {f'<p class="an-bajada">{bajada}</p>' if bajada else ''}
  <div class="an-meta"><span class="an-fuente">{fuente}</span>{f' · <span class="an-hora">{hora}</span>' if hora else ''}</div>
</article>"""
    return f"""
<article class="an-nota">
  <h3 class="an-titulo"><a href="{link}" target="_blank" rel="noopener">{titulo}</a></h3>
  <div class="an-meta"><span class="an-fuente">{fuente}</span>{f' · <span class="an-hora">{hora}</span>' if hora else ''}</div>
</article>"""


def seccion_cat_html(cat, notas):
    if not notas: return ""
    icono_key = cat.lower().replace("é","e").replace("í","i").replace("ó","o").replace("á","a")
    icono_svg = ICONO.get(icono_key, "")
    cat_id = cat.lower().replace(" ","-").replace("é","e").replace("í","i").replace("ó","o")
    items = "".join(nota_html(n) for n in notas[:8])
    return f"""
<section class="an-seccion" id="{cat_id}">
  <div class="an-seccion-header">
    <span class="an-ic">{icono_svg}</span>
    <h2 class="an-seccion-nombre">{escapar(cat)}</h2>
  </div>
  <div class="an-notas">
    {items}
  </div>
</section>"""


def nav_categorias_html(secciones):
    cats = [c for c in CATEGORIAS_ORDEN if c in secciones and secciones[c]]
    if not cats: return ""
    items = []
    for cat in cats:
        icono_key = cat.lower().replace("é","e").replace("í","i").replace("ó","o").replace("á","a")
        ic = ICONO.get(icono_key,"")
        cat_id = cat.lower().replace(" ","-").replace("é","e").replace("í","i").replace("ó","o")
        items.append(f'<a href="#{cat_id}">{ic}{escapar(cat)}</a>')
    return f"""
<nav class="an-nav-cats">
  <div class="an-nav-scroll">
    {''.join(items)}
  </div>
</nav>"""


def generar_analisis():
    ahora = datetime.now(TZ_AR)
    data = cargar_datos()
    destacados = data.get("destacados", [])
    secciones  = data.get("secciones", {})

    # Destacados
    dest_html = ""
    if destacados:
        dest_html = nota_html(destacados[0], grande=True)
        if len(destacados) > 1:
            rest = "".join(nota_html(n) for n in destacados[1:5])
            dest_html += f'<div class="an-dest-rest">{rest}</div>'

    # Secciones por categoría
    secs_html = ""
    for cat in CATEGORIAS_ORDEN:
        if cat in secciones:
            secs_html += seccion_cat_html(cat, secciones[cat])
    # Categorías que no están en el orden predefinido
    for cat, notas in secciones.items():
        if cat not in CATEGORIAS_ORDEN and notas:
            secs_html += seccion_cat_html(cat, notas)

    nav_cats = nav_categorias_html(secciones)
    total = sum(len(v) for v in secciones.values()) + len(destacados)

    css_extra = '<link rel="stylesheet" href="/assets/la-data.css">'
    html = comp.head_comun(
        f"La Data del Día — PPA · {fecha_legible(ahora)}",
        "Lo más destacado de consultoras, institutos y organismos sobre la economía argentina.",
        css_extra=css_extra
    ) + f"""
<body class="body-analisis">

{comp.cabecera("La Data del Día")}

{nav_cats}

<main class="an-main">
  <div class="contenedor">

    <div class="an-header">
      <h1 class="an-titulo-seccion">La Data del Día</h1>
      <p class="an-sub">Consultoras · Institutos · Organismos · {fecha_legible(ahora)}</p>
      <p class="an-total">{total} notas en esta edición</p>
    </div>

    {f'<div class="an-destacados">{dest_html}</div>' if dest_html else ''}

    <div class="an-cuerpo">
      {secs_html if secs_html else '<p class="an-vacio">Cargando contenido…</p>'}
    </div>

  </div>
</main>

{comp.pie()}
<script src="/assets/ppa.js"></script>
</body>
</html>"""

    os.makedirs(DIR_ANALISIS, exist_ok=True)
    out = os.path.join(DIR_ANALISIS, "index.html")
    with open(out,'w',encoding='utf-8') as f:
        f.write(html)
    print(f"[Análisis] Generado: {out} ({total} notas)")

    # Redirects 301 para URLs viejas
    _generar_redirect(DIR_INST, "/la-data/", "Institucional")
    _generar_redirect(DIR_EXPECT, "/la-data/", "Expectativas de mercado")


def _generar_redirect(dir_destino, url_nueva, nombre_viejo):
    """HTML de redirección con meta refresh + JS."""
    os.makedirs(dir_destino, exist_ok=True)
    html = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="UTF-8">
<meta http-equiv="refresh" content="0; url={url_nueva}">
<title>Redirigiendo… — PPA</title>
<link rel="canonical" href="{url_nueva}">
</head>
<body>
<p>Esta sección se fusionó con <a href="{url_nueva}">Análisis</a>.</p>
<script>window.location.replace("{url_nueva}");</script>
</body>
</html>"""
    out = os.path.join(dir_destino, "index.html")
    with open(out,'w',encoding='utf-8') as f:
        f.write(html)
    print(f"[Análisis] Redirect {nombre_viejo} → {url_nueva}: {out}")


def main():
    print(f"[Análisis] Inicio: {datetime.now(timezone.utc).isoformat()}")
    generar_analisis()
    print(f"[Análisis] Fin")

if __name__ == "__main__":
    main()
