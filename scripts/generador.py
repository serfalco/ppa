"""
PPA — generador.py
Toma data/portada.json y genera el sitio HTML estático en site/index.html

Genera:
  - site/index.html (la portada)
  - site/archivo/YYYY/MM/DD/merienda.html (edición archivada)
  - site/archivo/YYYY/MM/index.html (calendario mensual)
  - site/archivo/YYYY/index.html (página anual)

Cómo se corre:
    python scripts/generador.py
"""

import json
import os
import sys
import shutil
from datetime import datetime, timezone, timedelta
from calendar import monthrange

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA, DIR_SITE, DIR_ARCHIVO, CATEGORIAS
import componentes as comp

JSON_PORTADA = os.path.join(DIR_DATA, "portada.json")

# Zona horaria Argentina (UTC-3)
TZ_AR = timezone(timedelta(hours=-3))

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def fecha_legible(dt):
    """Devuelve 'Sábado 24 de mayo de 2026'."""
    dia_sem = DIAS_SEMANA[dt.weekday()]
    mes = MESES[dt.month - 1]
    return f"{dia_sem} {dt.day} de {mes} de {dt.year}"


def hora_corta(fecha_iso):
    """Convierte ISO timestamp a 'HH:MM' en hora Argentina."""
    try:
        dt = datetime.fromisoformat(fecha_iso.replace('Z', '+00:00'))
        dt_ar = dt.astimezone(TZ_AR)
        return dt_ar.strftime("%H:%M")
    except Exception:
        return ""


def numero_edicion(fecha):
    """Genera un número de edición basado en días desde el 1 de enero de 2026."""
    inicio = datetime(2026, 1, 1, tzinfo=TZ_AR)
    delta = fecha - inicio
    return delta.days + 1


def escapar_html(texto):
    """Escapa caracteres HTML peligrosos en texto."""
    if not texto:
        return ""
    return (texto
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#39;"))


# =============================================================
# COMPONENTES HTML
# =============================================================

def html_head(titulo_pagina, descripcion="Publicación económica institucional"):
    """Genera el <head> común a todas las páginas."""
    return f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escapar_html(titulo_pagina)} — PPA</title>
<meta name="description" content="{escapar_html(descripcion)}">
<meta property="og:title" content="{escapar_html(titulo_pagina)}">
<meta property="og:description" content="{escapar_html(descripcion)}">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,900&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/ppa.css">
</head>
<body>"""


def html_barra_superior(fecha_str):
    """Barra superior negra con fecha y clima (clima se actualiza por JS)."""
    return f"""
<div class="barra-superior">
  <div class="contenedor">
    <span class="fecha-barra">{fecha_str} · Buenos Aires</span>
    <span class="clima" id="clima-widget">—</span>
  </div>
</div>"""


def html_marquesina_fulbito():
    """Marquesina de fútbol. Se llena por JS al cargar."""
    return """
<div class="marquesina-fulbito" id="fulbito-bar" style="display:none">
  <div class="contenedor">
    <span class="fulbito-label">⚽ Fulbito hoy</span>
    <div class="fulbito-scroll" id="fulbito-partidos"></div>
  </div>
</div>"""


def html_cabecera(num_edicion, fecha_str):
    """Masthead del diario: PPA grande con bajada."""
    return f"""
<header class="cabecera">
  <div class="contenedor">
    <div class="fecha-edicion">Edición Nº {num_edicion} · {fecha_str.upper()}</div>
    <h1 class="titulo-diario">PPA</h1>
    <div class="bajada-diario">Pulso · Productivo · Argentino</div>
  </div>
</header>"""


def html_ticker():
    """Ticker con dólar oficial y riesgo país. Se actualiza por JS."""
    return """
<div class="ticker" id="ticker-datos">
  <div class="contenedor ticker-flex">
    <div class="ticker-item">
      <span class="ticker-label">Dólar oficial</span>
      <span class="ticker-valor" id="dolar-oficial">—</span>
    </div>
    <div class="ticker-item">
      <span class="ticker-label">Riesgo país</span>
      <span class="ticker-valor" id="riesgo-pais">—</span>
    </div>
  </div>
</div>"""


def html_widget_mulc():
    """Widget de cierre MULC. Se muestra solo entre 17 y 20hs, lunes a viernes."""
    return """
<section class="widget-mulc" id="widget-mulc" style="display:none">
  <div class="contenedor">
    <div class="mulc-header">CIERRE MULC</div>
    <div class="mulc-body" id="mulc-body">
      <span class="mulc-loading">Cargando datos del cierre...</span>
    </div>
  </div>
</section>"""


def html_nav_secciones():
    """Navegación principal."""
    items = [f'<li><a href="#{cat.lower().replace(" ", "-")}">{cat}</a></li>' for cat in CATEGORIAS]
    return f"""
<nav class="nav-secciones">
  <div class="contenedor">
    <ul>
      <li><a href="/">Portada</a></li>
      <li><a href="/institucional/" class="activo">Institucional</a></li>
      <li><a href="/expectativas/">Expectativas</a></li>
      <li><a href="/documentos/">Documentos</a></li>
      <li><a href="/columnas/">Columnas</a></li>
      <li><a href="/stream/">Stream</a></li>
      <li><a href="/tablero/">Tablero</a></li>
      {''.join(items)}
    </ul>
  </div>
</nav>"""


def html_columna_propia(nota_propia):
    """Si hay columna semanal activa, se muestra arriba destacada."""
    if not nota_propia:
        return ""

    fecha_pub = ""
    try:
        dt = datetime.fromisoformat(nota_propia["fecha_publicacion"].replace('Z', '+00:00'))
        fecha_pub = fecha_legible(dt.astimezone(TZ_AR))
    except Exception:
        pass

    return f"""
<section class="columna-propia">
  <div class="contenedor">
    <div class="columna-marco">
      <div class="columna-tag">★ COLUMNA</div>
      <h2 class="columna-titulo">{escapar_html(nota_propia['titulo'])}</h2>
      <p class="columna-bajada">{escapar_html(nota_propia.get('bajada', ''))}</p>
      <div class="columna-firma">
        <strong>Por Sergio Falco</strong> · {escapar_html(fecha_pub)}
      </div>
      <a class="columna-leer" href="/columnas/{nota_propia.get('slug', '')}.html">Leer la columna completa →</a>
    </div>
  </div>
</section>"""


def html_destacado_principal(nota):
    """El destacado más grande de la tapa (primero de la lista)."""
    return f"""
<article class="destacado-principal">
  <span class="etiqueta">★ Destacado del día</span>
  <h2><a href="{escapar_html(nota['link'])}" target="_blank" rel="noopener">{escapar_html(comp.limpiar_url(nota['titulo']))}</a></h2>
  <p class="destacado-bajada">{escapar_html(nota['bajada'])}</p>
  <div class="firma">
    <span><strong>{escapar_html(nota['fuente_nombre'])}</strong> · {escapar_html(nota['categoria'])}</span>
    <span><a href="{escapar_html(nota['link'])}" target="_blank" rel="noopener" class="ver-mas">Ver en {escapar_html(nota['fuente_nombre'])} →</a></span>
  </div>
  {html_compartir(nota)}
</article>"""


def html_destacado_secundario(nota):
    """Destacados 2 a 5: más chicos, en columna lateral."""
    return f"""
<article class="destacado-secundario">
  <span class="etiqueta-sec">{escapar_html(nota['categoria'])}</span>
  <h3><a href="{escapar_html(nota['link'])}" target="_blank" rel="noopener">{escapar_html(comp.limpiar_url(nota['titulo']))}</a></h3>
  <p>{escapar_html(nota['bajada'])}</p>
  <div class="firma">
    <span><strong>{escapar_html(nota['fuente_nombre'])}</strong></span>
  </div>
  {html_compartir(nota)}
</article>"""


def html_compartir(nota):
    """Botones de compartir: WhatsApp, X, LinkedIn, copiar link."""
    url = nota.get('link', '')
    titulo = nota.get('titulo', '')
    # Encodeo simple para URLs
    url_enc = url.replace(' ', '%20').replace('"', '%22')
    txt_enc = (titulo + ' — vía PPA').replace(' ', '%20').replace('"', '%22')
    
    return f"""
<div class="compartir">
  <a class="comp-btn" href="https://wa.me/?text={txt_enc}%20{url_enc}" target="_blank" rel="noopener" title="Compartir por WhatsApp">WhatsApp</a>
  <a class="comp-btn" href="https://twitter.com/intent/tweet?text={txt_enc}&url={url_enc}" target="_blank" rel="noopener" title="Compartir en X">X</a>
  <a class="comp-btn" href="https://www.linkedin.com/sharing/share-offsite/?url={url_enc}" target="_blank" rel="noopener" title="Compartir en LinkedIn">LinkedIn</a>
  <button class="comp-btn" onclick="navigator.clipboard.writeText('{escapar_html(url)}'); this.textContent='Copiado'" title="Copiar enlace">Copiar</button>
</div>"""


def html_nota_seccion(nota):
    """Nota dentro de una sección por categoría."""
    return f"""
<article class="nota">
  <div class="fuente">{escapar_html(nota['fuente_nombre'])}</div>
  <h3><a href="{escapar_html(nota['link'])}" target="_blank" rel="noopener">{escapar_html(comp.limpiar_url(nota['titulo']))}</a></h3>
  <p>{escapar_html(nota['bajada'])}</p>
  <div class="meta">
    <span>{hora_corta(nota['fecha_publicacion'])}</span>
    <a href="{escapar_html(nota['link'])}" target="_blank" rel="noopener">Ver en {escapar_html(nota['fuente_nombre'])} →</a>
  </div>
</article>"""


def html_sidebar_ultimo_momento(notas):
    """Sidebar derecho con últimas notas."""
    items_html = []
    for n in notas:
        items_html.append(f"""
    <div class="sidebar-item">
      <span class="hora">{hora_corta(n['fecha_publicacion'])}</span>
      <div class="texto">
        <a href="{escapar_html(n['link'])}" target="_blank" rel="noopener">{escapar_html(n['titulo'])}</a>
        <span class="fuente-mini">{escapar_html(n['fuente_nombre'])}</span>
      </div>
    </div>""")

    return f"""
<aside class="sidebar">
  <h3 class="sidebar-titulo">Último momento</h3>
  {''.join(items_html)}
</aside>"""


def html_seccion_categoria(categoria, notas):
    """Sección por categoría con sus notas."""
    if not notas:
        return ""

    notas_html = "".join([html_nota_seccion(n) for n in notas])
    cat_id = categoria.lower().replace(" ", "-")

    return f"""
<section class="seccion" id="{cat_id}">
  <div class="seccion-titulo">
    <h2>{escapar_html(categoria)}</h2>
  </div>
  <div class="notas-grid">
    {notas_html}
  </div>
</section>"""


def html_pie(generado_en):
    """Pie del sitio."""
    return f"""
<footer class="pie">
  <div class="contenedor">
    <strong>PPA · Pulso Productivo Argentino</strong><br>
    <span class="pie-bajada">Publicación económica · Curaduría automática con criterio editorial</span>
    <div class="pie-meta">
      Actualizado: {generado_en} ·
      <a href="/">Portada</a> ·
      <a href="/columnas/">Columnas</a> ·
      <a href="/stream/">Stream</a> ·
      <a href="/como-trabajamos.html">Cómo trabajamos</a> ·
      <a href="/acerca.html">Acerca de</a>
    </div>
  </div>
</footer>
<script src="/assets/ppa.js"></script>
</body>
</html>"""


# =============================================================
# GENERAR PORTADA
# =============================================================

def generar_portada():
    """Genera site/index.html"""
    if not os.path.exists(JSON_PORTADA):
        print(f"ERROR: no existe {JSON_PORTADA}. Corré primero scripts/selector.py")
        sys.exit(1)

    with open(JSON_PORTADA, 'r', encoding='utf-8') as f:
        data = json.load(f)

    ahora_ar = datetime.now(TZ_AR)
    fecha_str = fecha_legible(ahora_ar)
    num_ed = numero_edicion(ahora_ar)

    destacados = data.get("destacados", [])
    secciones = data.get("secciones", {})
    ult_mom = data.get("ultimo_momento", [])
    nota_propia = data.get("nota_propia")

    # Construir HTML
    partes = []
    partes.append(comp.head_comun(
        f"PPA · Institucional — {fecha_str}",
        "Pulso Productivo Argentino: análisis económico curado de instituciones y consultoras.",
        css_extra='<link rel="stylesheet" href="/assets/home.css">'
    ) + "\n<body>")
    partes.append(comp.franja_datos(ahora_ar))
    partes.append(comp.cabecera())
    partes.append(comp.nav_principal("Institucional"))
    partes.append(html_columna_propia(nota_propia))

    # Tapa con destacados
    partes.append('<section class="tapa"><div class="contenedor"><div class="tapa-grid">')
    if destacados:
        partes.append(html_destacado_principal(destacados[0]))
        partes.append('<div class="destacados-laterales">')
        for d in destacados[1:5]:
            partes.append(html_destacado_secundario(d))
        partes.append('</div>')
    partes.append('</div></div></section>')

    # Cuerpo con secciones + sidebar
    partes.append('<div class="contenedor"><div class="layout-con-sidebar"><main>')
    for cat in CATEGORIAS:  # iteramos en orden definido en config
        if cat in secciones:
            partes.append(html_seccion_categoria(cat, secciones[cat]))
    partes.append('</main>')
    partes.append(html_sidebar_ultimo_momento(ult_mom))
    partes.append('</div></div>')

    partes.append(comp.pie())

    html = "".join(partes)

    # Escribir en /institucional/index.html
    dir_inst = os.path.join(DIR_SITE, "institucional")
    os.makedirs(dir_inst, exist_ok=True)
    out = os.path.join(dir_inst, "index.html")
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[PPA Generador] Sección institucional: {out}")
    return out


# =============================================================
# GUARDAR EDICIÓN HISTÓRICA (Merienda)
# =============================================================

def archivar_edicion():
    """Copia la portada institucional actual al archivo histórico."""
    src = os.path.join(DIR_SITE, "institucional", "index.html")
    if not os.path.exists(src):
        print("ERROR: no hay index.html para archivar")
        return

    ahora_ar = datetime.now(TZ_AR)
    dir_dia = os.path.join(DIR_ARCHIVO, str(ahora_ar.year),
                            f"{ahora_ar.month:02d}", f"{ahora_ar.day:02d}")
    os.makedirs(dir_dia, exist_ok=True)
    dst = os.path.join(dir_dia, "merienda.html")
    shutil.copy(src, dst)
    print(f"[PPA Generador] Archivada: {dst}")


# =============================================================
# PROCESO PRINCIPAL
# =============================================================

def main():
    print(f"[PPA Generador] Inicio: {datetime.now(timezone.utc).isoformat()}")
    generar_portada()
    archivar_edicion()
    print(f"[PPA Generador] Fin: {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
