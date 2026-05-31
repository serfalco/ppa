"""
PPA — generador_stream.py
Genera el índice de Blog Stream y las páginas individuales si vienen como JSON.

Hay dos formas de cargar notas al Blog Stream:

  Modo 1 - HTML directo (recomendado, lo que va a hacer Gemini):
    Las notas vienen como archivos HTML ya armados en site/stream/notas/{slug}.html
    Este script las lista, lee sus metadatos (de <meta> tags) y arma el índice.

  Modo 2 - JSON estructurado:
    Si hay notas en data/stream_notas.json, las convierte a HTML usando el template.

Cómo se corre:
    python scripts/generador_stream.py
"""

import json
import os
import sys
import re
import unicodedata
from datetime import datetime, timezone, timedelta
from html.parser import HTMLParser

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA, DIR_SITE
import componentes as comp

DIR_STREAM = os.path.join(DIR_SITE, "stream")
DIR_STREAM_NOTAS = os.path.join(DIR_STREAM, "notas")
JSON_STREAM = os.path.join(DIR_DATA, "stream_notas.json")

TZ_AR = timezone(timedelta(hours=-3))
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]

# Categorías propias del Blog Stream
CATEGORIAS_STREAM = [
    "Economía",
    "Tecnología",
    "Política",
    "Sociedad",
    "Comunicación",
    "Cultura",
    "Internacional",
    "General",
]


def slugify(texto):
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


# =============================================================
# PARSER DE METADATOS DE NOTAS HTML
# =============================================================

class MetaParser(HTMLParser):
    """Extrae los <meta> tags de una nota HTML para listarla en el índice."""
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


def extraer_meta_nota(path):
    """Lee una nota HTML y devuelve sus metadatos: título, fecha, categoría, bajada, slug."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            html = f.read()
    except Exception as e:
        print(f"  [WARN] No se pudo leer {path}: {e}")
        return None

    p = MetaParser()
    p.feed(html)

    slug = os.path.basename(path).replace('.html', '')
    fecha = p.meta.get("article:published_time") or p.meta.get("date") or ""
    categoria = p.meta.get("article:section") or p.meta.get("category") or "General"
    titulo = p.titulo.replace(" — PPA Stream", "").strip()
    bajada = p.meta.get("description", "")

    return {
        "slug": slug,
        "titulo": titulo,
        "bajada": bajada,
        "fecha": fecha,
        "categoria": categoria,
        "path": path,
    }


def listar_notas_html():
    """Recorre site/stream/notas/ y devuelve lista de notas con sus metadatos."""
    if not os.path.exists(DIR_STREAM_NOTAS):
        return []
    notas = []
    for archivo in sorted(os.listdir(DIR_STREAM_NOTAS)):
        if not archivo.endswith('.html'):
            continue
        meta = extraer_meta_nota(os.path.join(DIR_STREAM_NOTAS, archivo))
        if meta:
            notas.append(meta)
    # Ordenar por fecha descendente
    notas.sort(key=lambda n: n.get("fecha", ""), reverse=True)
    return notas


# =============================================================
# GENERAR ÍNDICE DEL BLOG STREAM
# =============================================================

def generar_indice(notas):
    """Genera site/stream/index.html con el listado de notas."""

    # Lista de notas en el índice
    items = []
    for n in notas:
        # Parsear fecha
        f_leg = ""
        try:
            dt = datetime.fromisoformat(n["fecha"].replace('Z', '+00:00'))
            f_leg = fecha_legible(dt.astimezone(TZ_AR))
        except Exception:
            f_leg = n.get("fecha", "")

        items.append(f"""
    <article class="stream-item">
      <div class="stream-meta">
        <span class="stream-cat">{escapar(n.get('categoria', 'General'))}</span>
        <time class="stream-fecha">{escapar(f_leg)}</time>
      </div>
      <h2><a href="/stream/notas/{escapar(n['slug'])}.html">{escapar(n['titulo'])}</a></h2>
      <p>{escapar(n.get('bajada', ''))}</p>
    </article>""")

    contenido = "".join(items) if items else """
    <div class="stream-vacio">
      <p>Todavía no hay notas publicadas en Blog Stream.</p>
      <p class="vacio-sub">Esta sección reúne comentarios y reflexiones sobre participaciones en programas de streaming.</p>
    </div>"""

    html = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Blog Stream — PPA</title>
<meta name="description" content="Comentarios editoriales sobre entrevistas y programas de streaming. Análisis personal de PPA.">
<meta property="og:title" content="Blog Stream — PPA">
<meta property="og:description" content="Comentarios editoriales sobre programas de streaming.">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,900&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/ppa.css">
<link rel="stylesheet" href="/assets/interior.css">
<link rel="stylesheet" href="/assets/stream.css">
</head>
<body class="body-stream">

{comp.franja_datos()}

<header class="stream-header">
  <div class="contenedor">
    <div class="stream-kicker">Stream</div>
    <h1>Comentarios editoriales</h1>
    <p class="stream-intro">
      Miradas personales sobre participaciones en programas de streaming.
      Opiniones del editor, sin firma individual, con fuente clara.
    </p>
  </div>
</header>

{comp.nav_principal("Stream")}

<main class="stream-main">
  <div class="contenedor">
    {contenido}
  </div>
</main>

{comp.pie()}

</body>
</html>"""

    os.makedirs(DIR_STREAM, exist_ok=True)
    out = os.path.join(DIR_STREAM, "index.html")
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[PPA Stream] Índice: {out}")


def fecha_legible(iso):
    """ISO → '31 de mayo de 2026'."""
    try:
        d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return f"{d.day} de {MESES[d.month-1]} de {d.year}"
    except Exception:
        return ""


def parrafos(texto):
    """Convierte texto plano (líneas en blanco = párrafo) en <p>...</p>."""
    bloques = re.split(r'\n\s*\n', (texto or "").replace("\r\n", "\n").strip())
    return "\n".join(f"    <p>{escapar(b.strip())}</p>" for b in bloques if b.strip())


def escapar(s):
    if not s:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def generar_notas_desde_panel():
    """Lee stream_manual.json (lo que carga el panel69) y genera una página HTML
    por cada ítem, con embed de YouTube si hay. Devuelve la cantidad generada."""
    ruta = os.path.join(DIR_DATA, "stream_manual.json")
    if not os.path.exists(ruta):
        return 0
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return 0
    items = data.get("items", [])
    generadas = 0
    for it in items:
        slug = it.get("slug") or slugify(it.get("titulo", "nota"))
        titulo = it.get("titulo", "")
        bajada = it.get("bajada", "")
        texto = it.get("texto", "")
        yt_id = it.get("youtube_id", "")
        fecha_iso = it.get("fecha", datetime.now(TZ_AR).isoformat())
        categoria = it.get("categoria", "General")

        # Embed de YouTube (si hay id)
        embed = ""
        if yt_id:
            embed = (f'\n  <div class="stream-video">'
                     f'<iframe width="100%" height="315" '
                     f'src="https://www.youtube.com/embed/{yt_id}" '
                     f'title="{escapar(titulo)}" frameborder="0" '
                     f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
                     f'gyroscope; picture-in-picture" allowfullscreen></iframe></div>\n')

        html = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{escapar(titulo)} — PPA Stream</title>
<meta name="description" content="{escapar(bajada)}">
<meta property="og:title" content="{escapar(titulo)}">
<meta property="og:description" content="{escapar(bajada)}">
<meta property="og:type" content="article">
<meta property="article:published_time" content="{fecha_iso}">
<meta property="article:section" content="{escapar(categoria)}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,900&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/ppa.css">
<link rel="stylesheet" href="/assets/stream.css">
</head>
<body class="body-stream">

{comp.franja_datos()}

{comp.nav_principal("Stream")}

<article class="stream-nota">
  <a href="/stream/" class="stream-nota-volver">← Todas las notas</a>
  <header class="stream-nota-header">
    <h1>{escapar(titulo)}</h1>
    <p class="bajada">{escapar(bajada)}</p>
    <div class="meta">
      <span class="stream-cat">{escapar(categoria)}</span>
      <time datetime="{fecha_iso[:10]}">{fecha_legible(fecha_iso)}</time>
    </div>
  </header>
{embed}
  <div class="stream-nota-cuerpo">
{parrafos(texto)}
  </div>
</article>

</body>
</html>"""
        with open(os.path.join(DIR_STREAM_NOTAS, f"{slug}.html"), "w", encoding="utf-8") as f:
            f.write(html)
        generadas += 1
        print(f"   [stream] {slug}.html" + (" (con video)" if yt_id else ""))
    return generadas


def main():
    print(f"[PPA Stream] Inicio: {datetime.now(timezone.utc).isoformat()}")
    os.makedirs(DIR_STREAM_NOTAS, exist_ok=True)

    # 1) Generar notas desde lo cargado en el panel69
    n = generar_notas_desde_panel()
    if n:
        print(f"[PPA Stream] {n} notas generadas desde el panel")

    # 2) Listar todas las notas HTML (las del panel + las que ya existían)
    notas = listar_notas_html()
    print(f"[PPA Stream] {len(notas)} notas en site/stream/notas/")

    generar_indice(notas)
    print(f"[PPA Stream] Fin")


if __name__ == "__main__":
    main()
