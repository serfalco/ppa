"""
PPA — generador_columnas.py
Genera el HTML de cada columna semanal de Sergio Falco y el índice de todas.

Lee:  data/notas_propias.json (todas las columnas publicadas)
Genera:
  - site/columnas/{slug}.html (una página por columna)
  - site/columnas/index.html (índice de todas las columnas)

Cómo se corre:
    python scripts/generador_columnas.py
"""

import json
import os
import sys
import re
import unicodedata
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA, DIR_SITE

JSON_NOTAS_PROPIAS = os.path.join(DIR_DATA, "notas_propias.json")
DIR_COLUMNAS = os.path.join(DIR_SITE, "columnas")

TZ_AR = timezone(timedelta(hours=-3))
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]


def slugify(texto):
    """Convierte un título en slug URL-friendly."""
    texto = unicodedata.normalize('NFKD', texto)
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    texto = texto.lower()
    texto = re.sub(r'[^a-z0-9\s-]', '', texto)
    texto = re.sub(r'\s+', '-', texto)
    texto = re.sub(r'-+', '-', texto)
    return texto.strip('-')[:80]


def fecha_legible(dt):
    return f"{dt.day} de {MESES[dt.month - 1]} de {dt.year}"


def escapar(s):
    if not s:
        return ""
    return (str(s)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;"))


def parrafos_html(texto):
    """Convierte texto plano con saltos de línea en párrafos HTML."""
    if not texto:
        return ""
    parrafos = [p.strip() for p in texto.split('\n\n') if p.strip()]
    return "\n".join([f"<p>{escapar(p)}</p>" for p in parrafos])


def html_head_columna(titulo, bajada):
    desc = bajada[:160] if bajada else "Columna semanal de PPA"
    return f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escapar(titulo)} — PPA</title>
<meta name="description" content="{escapar(desc)}">
<meta property="og:title" content="{escapar(titulo)}">
<meta property="og:description" content="{escapar(desc)}">
<meta property="og:type" content="article">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,900&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/ppa.css">
<style>
  /* Estilos específicos de columna */
  .columna-page {{ max-width: 720px; margin: 0 auto; padding: 0 32px; }}
  .columna-volver {{
    display: inline-block; margin: 24px 0;
    font-family: 'IBM Plex Sans', sans-serif; font-size: 12px;
    letter-spacing: 0.1em; text-transform: uppercase; color: var(--gris);
  }}
  .columna-volver:hover {{ color: var(--rojo); }}
  .columna-header {{
    border-bottom: 1px solid var(--linea);
    padding-bottom: 24px;
    margin-bottom: 32px;
  }}
  .columna-kicker {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 11px;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--rojo);
    margin-bottom: 12px;
  }}
  .columna-page h1 {{
    font-family: 'Playfair Display', serif;
    font-size: clamp(32px, 4.5vw, 48px);
    font-weight: 700;
    line-height: 1.1;
    margin-bottom: 16px;
    color: var(--tinta);
  }}
  .columna-page .bajada-art {{
    font-family: 'Source Serif 4', serif;
    font-style: italic;
    font-size: 19px;
    color: var(--gris);
    line-height: 1.5;
    margin-bottom: 20px;
  }}
  .columna-page .firma-art {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 13px;
    color: var(--gris);
    letter-spacing: 0.05em;
  }}
  .columna-page .firma-art strong {{ color: var(--tinta); font-weight: 600; }}
  .columna-cuerpo p {{
    font-family: 'Source Serif 4', serif;
    font-size: 18px;
    line-height: 1.7;
    margin-bottom: 22px;
    color: var(--tinta);
  }}
  .columna-cuerpo p:first-of-type::first-letter {{
    font-family: 'Playfair Display', serif;
    font-size: 64px;
    float: left;
    line-height: 0.9;
    padding-right: 8px;
    padding-top: 6px;
    color: var(--rojo);
    font-weight: 900;
  }}
  .columna-fin {{
    text-align: center;
    font-family: 'IBM Plex Sans', sans-serif;
    color: var(--gris-claro);
    margin: 32px 0;
    font-size: 18px;
    letter-spacing: 0.5em;
  }}
  .columna-otras {{
    margin-top: 48px;
    padding-top: 32px;
    border-top: 1px solid var(--linea);
  }}
  .columna-otras h3 {{
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: 22px;
    margin-bottom: 16px;
  }}
  .columna-otras ul {{ list-style: none; padding: 0; }}
  .columna-otras li {{
    padding: 8px 0;
    border-bottom: 1px dotted var(--linea);
  }}
  .columna-otras a {{ color: var(--tinta); }}
  .columna-otras .fecha-mini {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 11px;
    color: var(--gris);
    letter-spacing: 0.05em;
    text-transform: uppercase;
  }}
</style>
</head>
<body>"""


def html_cuerpo_columna(col, otras_columnas):
    """Genera el HTML del cuerpo de una columna individual."""
    fecha = ""
    try:
        dt = datetime.fromisoformat(col["fecha_publicacion"].replace('Z', '+00:00'))
        fecha = fecha_legible(dt.astimezone(TZ_AR))
    except Exception:
        pass

    # Botones de compartir
    url_completa = f"https://pulsoproductivo.com.ar/columnas/{col['slug']}.html"
    url_enc = url_completa.replace(' ', '%20')
    txt_enc = (col['titulo'] + ' — por Sergio Falco en PPA').replace(' ', '%20').replace('"', '%22')

    # Lista de otras columnas (excluyendo la actual)
    otras_html = ""
    if otras_columnas:
        items = []
        for o in otras_columnas[:5]:
            f_otra = ""
            try:
                d = datetime.fromisoformat(o["fecha_publicacion"].replace('Z', '+00:00'))
                f_otra = fecha_legible(d.astimezone(TZ_AR))
            except Exception:
                pass
            items.append(f"""
      <li>
        <a href="/columnas/{escapar(o['slug'])}.html">{escapar(o['titulo'])}</a>
        <span class="fecha-mini"> · {escapar(f_otra)}</span>
      </li>""")
        otras_html = f"""
  <section class="columna-otras">
    <h3>Otras columnas</h3>
    <ul>{''.join(items)}</ul>
  </section>"""

    return f"""
<div class="barra-superior">
  <div class="contenedor">
    <span class="fecha-barra">PPA · Pulso Productivo Argentino</span>
    <span><a href="/" style="color:inherit">Volver a la portada →</a></span>
  </div>
</div>

<article class="columna-page">
  <a href="/columnas/" class="columna-volver">← Todas las columnas</a>

  <header class="columna-header">
    <div class="columna-kicker">Columna</div>
    <h1>{escapar(col['titulo'])}</h1>
    {f'<p class="bajada-art">{escapar(col.get("bajada", ""))}</p>' if col.get("bajada") else ''}
    <div class="firma-art">
      <strong>Sergio Falco</strong> · {escapar(fecha)}
    </div>
  </header>

  <div class="columna-cuerpo">
    {parrafos_html(col.get('cuerpo', ''))}
  </div>

  <div class="columna-fin">· · ·</div>

  <div class="compartir" style="justify-content:center">
    <a class="comp-btn" href="https://wa.me/?text={txt_enc}%20{url_enc}" target="_blank" rel="noopener">WhatsApp</a>
    <a class="comp-btn" href="https://twitter.com/intent/tweet?text={txt_enc}&url={url_enc}" target="_blank" rel="noopener">X</a>
    <a class="comp-btn" href="https://www.linkedin.com/sharing/share-offsite/?url={url_enc}" target="_blank" rel="noopener">LinkedIn</a>
    <button class="comp-btn" onclick="navigator.clipboard.writeText('{escapar(url_completa)}'); this.textContent='Copiado'">Copiar enlace</button>
  </div>

  {otras_html}
</article>

<footer class="pie" style="margin-top:48px">
  <div class="contenedor">
    <strong>PPA · Pulso Productivo Argentino</strong><br>
    <span class="pie-bajada">Publicación económica</span>
    <div class="pie-meta">
      <a href="/">Portada</a> ·
      <a href="/institucional/">Lo que se dice</a> ·
      <a href="/expectativas/">Expectativas de mercado</a> ·
      <a href="/documentos/">Documentos</a> ·
      <a href="/columnas/">Columnas</a> ·
      <a href="/stream/">Stream</a> ·
      <a href="/como-trabajamos.html">Cómo trabajamos</a>
    </div>
  </div>
</footer>
</body>
</html>"""


def html_indice_columnas(columnas):
    """Genera el índice de todas las columnas."""
    items_html = []
    for col in columnas:
        fecha = ""
        try:
            dt = datetime.fromisoformat(col["fecha_publicacion"].replace('Z', '+00:00'))
            fecha = fecha_legible(dt.astimezone(TZ_AR))
        except Exception:
            pass
        items_html.append(f"""
    <article class="indice-item">
      <div class="indice-fecha">{escapar(fecha)}</div>
      <h2><a href="/columnas/{escapar(col['slug'])}.html">{escapar(col['titulo'])}</a></h2>
      <p>{escapar(col.get('bajada', ''))}</p>
    </article>""")

    return f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Columnas — PPA</title>
<meta name="description" content="Columnas semanales de Sergio Falco en PPA. Análisis estructural de la economía argentina.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,900&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/ppa.css">
<style>
  .columnas-page {{ max-width: 800px; margin: 0 auto; padding: 0 32px; }}
  .columnas-titulo {{
    border-bottom: 3px double var(--tinta);
    padding: 32px 0 20px;
    text-align: center;
    margin-bottom: 32px;
  }}
  .columnas-titulo h1 {{
    font-family: 'Playfair Display', serif;
    font-style: italic;
    font-size: clamp(40px, 6vw, 64px);
    font-weight: 900;
  }}
  .columnas-titulo p {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 12px;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--gris);
    margin-top: 8px;
  }}
  .indice-item {{
    padding: 24px 0;
    border-bottom: 1px solid var(--linea);
  }}
  .indice-fecha {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 11px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--rojo);
    margin-bottom: 6px;
  }}
  .indice-item h2 {{
    font-family: 'Playfair Display', serif;
    font-size: 24px;
    font-weight: 700;
    line-height: 1.2;
    margin-bottom: 6px;
  }}
  .indice-item h2 a {{ color: var(--tinta); }}
  .indice-item p {{
    font-family: 'Source Serif 4', serif;
    font-size: 15px;
    color: var(--gris);
    line-height: 1.5;
  }}
  .vacio {{
    text-align: center;
    padding: 80px 20px;
    color: var(--gris);
    font-style: italic;
  }}
</style>
</head>
<body>

<div class="barra-superior">
  <div class="contenedor">
    <span class="fecha-barra">PPA · Pulso Productivo Argentino</span>
    <span><a href="/" style="color:inherit">Volver a la portada →</a></span>
  </div>
</div>

<div class="columnas-page">
  <header class="columnas-titulo">
    <h1>Columnas</h1>
    <p>Análisis y miradas estructurales de la economía argentina</p>
  </header>

  {"".join(items_html) if items_html else '<div class="vacio">Aún no hay columnas publicadas.</div>'}
</div>

<footer class="pie" style="margin-top:48px">
  <div class="contenedor">
    <strong>PPA · Pulso Productivo Argentino</strong><br>
    <span class="pie-bajada">Publicación económica</span>
    <div class="pie-meta">
      <a href="/">Portada</a> ·
      <a href="/institucional/">Lo que se dice</a> ·
      <a href="/expectativas/">Expectativas de mercado</a> ·
      <a href="/documentos/">Documentos</a> ·
      <a href="/columnas/">Columnas</a> ·
      <a href="/stream/">Stream</a> ·
      <a href="/como-trabajamos.html">Cómo trabajamos</a>
    </div>
  </div>
</footer>

</body>
</html>"""


def cargar_columnas():
    """Carga todas las columnas publicadas y les genera slug si no tienen."""
    if not os.path.exists(JSON_NOTAS_PROPIAS):
        return []
    try:
        with open(JSON_NOTAS_PROPIAS, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return []
    columnas = data.get("notas", [])
    # Asegurar que cada columna tenga slug
    for c in columnas:
        if not c.get("slug"):
            c["slug"] = slugify(c.get("titulo", "columna"))
    # Ordenar por fecha descendente
    columnas.sort(key=lambda c: c.get("fecha_publicacion", ""), reverse=True)
    return columnas


def main():
    print(f"[PPA Columnas] Inicio: {datetime.now(timezone.utc).isoformat()}")
    os.makedirs(DIR_COLUMNAS, exist_ok=True)

    columnas = cargar_columnas()
    print(f"[PPA Columnas] {len(columnas)} columnas cargadas")

    # Generar cada columna individual
    for i, col in enumerate(columnas):
        otras = [c for c in columnas if c["slug"] != col["slug"]]
        html = html_head_columna(col["titulo"], col.get("bajada", ""))
        html += html_cuerpo_columna(col, otras)
        path = os.path.join(DIR_COLUMNAS, f"{col['slug']}.html")
        with open(path, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"   [{i+1}] {col['slug']}.html")

    # Generar índice
    indice_path = os.path.join(DIR_COLUMNAS, "index.html")
    with open(indice_path, 'w', encoding='utf-8') as f:
        f.write(html_indice_columnas(columnas))
    print(f"[PPA Columnas] Índice generado: {indice_path}")

    print(f"[PPA Columnas] Fin: {datetime.now(timezone.utc).isoformat()}")


if __name__ == "__main__":
    main()
