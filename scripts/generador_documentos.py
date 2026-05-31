"""
PPA — generador_documentos.py
Genera la sección "Documentos en circulación": hemeroteca de informes
institucionales de los últimos 30 días.

Lee:  data/notas.json (todas las notas leídas por el fetcher)
Filtra: solo las notas de fuentes institucionales puras (lista blanca abajo)
       que estén dentro de la ventana de 30 días.
Genera: site/documentos/index.html (índice de la sección)

Cómo se corre:
    python scripts/generador_documentos.py
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA, DIR_SITE
import componentes as comp
try:
    from config import VENTANA_DOCUMENTOS_HORAS
except ImportError:
    VENTANA_DOCUMENTOS_HORAS = 72  # default: ventana de 72hs

JSON_NOTAS = os.path.join(DIR_DATA, "notas.json")
DIR_DOCUMENTOS = os.path.join(DIR_SITE, "documentos")

TZ_AR = timezone(timedelta(hours=-3))
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


# =============================================================
# LISTA BLANCA: fuentes que alimentan Documentos en circulación
# =============================================================
# Solo instituciones puras: organismos públicos, think tanks, universidades,
# cámaras oficiales y organismos multilaterales.
# Los medios y consultoras-firma NO van acá (alimentan otras secciones).
FUENTES_INSTITUCIONALES = {
    # Macro institucional
    "bcra", "indec", "iaraf", "fiel", "fundar", "ieral", "cedlas",
    # Política
    "cippec",
    # Comercio Exterior
    "cari", "cei",
    # Automotor (cámaras oficiales)
    "acara", "adefa",
    # Logística (cámaras oficiales)
    "cedol", "fadeeac",
    # Minería
    "caem",
    # Agro institucional
    "bcr", "magyp", "rosgan",
    # Internacional
    "fmi", "cepal", "bancomundial", "bid", "ocde",
    # Universidad / observatorios
    "miradoruca",
}


# =============================================================
# HELPERS
# =============================================================

def escapar(s):
    if not s:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def fecha_legible(dt):
    return f"{dt.day} de {MESES[dt.month - 1]} de {dt.year}"


def hora_corta(fecha_iso):
    try:
        dt = datetime.fromisoformat(fecha_iso.replace('Z', '+00:00'))
        return dt.astimezone(TZ_AR).strftime("%H:%M")
    except Exception:
        return ""


# =============================================================
# CARGA Y FILTRADO
# =============================================================

def cargar_documentos():
    """Carga las notas y filtra solo las institucionales dentro de 30 días."""
    if not os.path.exists(JSON_NOTAS):
        return []

    try:
        with open(JSON_NOTAS, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return []

    notas = data.get("notas", [])
    if not notas:
        return []

    # Filtrar: solo de fuentes institucionales y dentro de la ventana
    limite = datetime.now(timezone.utc) - timedelta(hours=VENTANA_DOCUMENTOS_HORAS)
    documentos = []

    for nota in notas:
        if nota.get("fuente_id") not in FUENTES_INSTITUCIONALES:
            continue
        try:
            fecha = datetime.fromisoformat(nota["fecha_publicacion"].replace('Z', '+00:00'))
            if fecha < limite:
                continue
        except Exception:
            continue
        documentos.append(nota)

    # Ordenar por fecha, más nuevos primero
    documentos.sort(key=lambda d: d.get("fecha_publicacion", ""), reverse=True)
    return documentos


def agrupar_por_categoria(documentos):
    """Agrupa los documentos por categoría manteniendo orden cronológico."""
    grupos = {}
    for doc in documentos:
        cat = doc.get("categoria", "Sin categoría")
        grupos.setdefault(cat, []).append(doc)
    return grupos


# =============================================================
# HTML
# =============================================================

def html_documento(doc):
    """Genera el HTML de un documento individual en el listado."""
    # Fecha legible
    f_leg = ""
    try:
        dt = datetime.fromisoformat(doc["fecha_publicacion"].replace('Z', '+00:00'))
        f_leg = fecha_legible(dt.astimezone(TZ_AR))
    except Exception:
        f_leg = ""

    return f"""
    <article class="doc-item">
      <span class="doc-sello">★ INFORME INSTITUCIONAL</span>
      <h3>
        <a href="{escapar(doc['link'])}" target="_blank" rel="noopener">{escapar(doc['titulo'])}</a>
      </h3>
      <p class="doc-bajada">{escapar(doc.get('bajada', ''))}</p>
      <div class="doc-meta">
        <span class="doc-fuente">{escapar(doc['fuente_nombre'])}</span>
        <span class="doc-fecha">{escapar(f_leg)}</span>
      </div>
    </article>"""


def generar_indice(documentos):
    """Genera site/documentos/index.html"""

    ahora_ar = datetime.now(TZ_AR)
    actualizado = ahora_ar.strftime("%d/%m/%Y %H:%M")

    # Agrupar por categoría
    grupos = agrupar_por_categoria(documentos)

    # Render del cuerpo
    if not documentos:
        cuerpo = """
        <div class="doc-vacio">
          <p>Sin documentos en circulación en los últimos 30 días.</p>
          <p class="vacio-sub">Esta sección reúne informes, papers y publicaciones
          de organismos públicos, think tanks, universidades y cámaras institucionales.</p>
        </div>"""
    else:
        secciones = []
        for cat, items in grupos.items():
            secciones.append(f"""
        <section class="doc-categoria">
          <h2>{escapar(cat)}</h2>
          <div class="doc-grid">
            {''.join([html_documento(d) for d in items])}
          </div>
        </section>""")
        cuerpo = "".join(secciones)

    html = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Documentos en circulación — PPA</title>
<meta name="description" content="Informes y publicaciones de organismos, think tanks y universidades. Hemeroteca de los últimos 30 días.">
<meta property="og:title" content="Documentos en circulación — PPA">
<meta property="og:description" content="Hemeroteca de informes institucionales de los últimos 30 días.">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,900&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/ppa.css">
<link rel="stylesheet" href="/assets/documentos.css">
</head>
<body class="body-documentos">

<!-- BARRA SUPERIOR -->
{comp.franja_datos()}

<!-- HEADER -->
<header class="documentos-header">
  <div class="contenedor">
    <div class="documentos-kicker">Documentos en circulación</div>
    <h1>Informes y publicaciones</h1>
    <p class="documentos-intro">
      Informes, papers y publicaciones de organismos públicos, think tanks,
      universidades y cámaras institucionales. Hemeroteca de los últimos 30 días.
    </p>
    <p class="documentos-actualizado">Actualizado: {escapar(actualizado)}</p>
  </div>
</header>

<!-- NAVEGACIÓN -->
{comp.nav_principal("Documentos")}

<!-- CUERPO -->
<main class="documentos-main">
  <div class="contenedor">
    {cuerpo}
  </div>
</main>

<!-- PIE -->
{comp.pie()}

</body>
</html>"""

    os.makedirs(DIR_DOCUMENTOS, exist_ok=True)
    out = os.path.join(DIR_DOCUMENTOS, "index.html")
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[PPA Documentos] Índice: {out}")
    print(f"[PPA Documentos] Total documentos: {len(documentos)} de {len(FUENTES_INSTITUCIONALES)} fuentes institucionales")


def main():
    print(f"[PPA Documentos] Inicio: {datetime.now(timezone.utc).isoformat()}")
    documentos = cargar_documentos()
    generar_indice(documentos)
    print(f"[PPA Documentos] Fin")


if __name__ == "__main__":
    main()
