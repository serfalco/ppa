"""
PPA — generador_acerca.py
Genera site/acerca.html con la estructura "Qué es / Cómo funciona / Nuestras fuentes".

Lee el config.py y arma automáticamente la lista de fuentes activas
agrupadas por categoría. Las fuentes suspendidas NO aparecen en el listado público.

Cómo se corre:
    python scripts/generador_acerca.py
"""

import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import FUENTES, CATEGORIAS, DIR_SITE


def escapar(s):
    if not s:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def url_corta(url):
    """Devuelve solo el dominio para mostrar en el listado."""
    if not url:
        return ""
    return url.replace("https://", "").replace("http://", "").replace("www.", "").rstrip("/")


def render_lista_fuentes():
    """Arma el HTML de la lista de fuentes agrupada por categoría."""
    secciones = []

    for cat in CATEGORIAS:
        # Solo activas, ocultas las suspendidas
        fuentes_cat = [f for f in FUENTES if f["categoria"] == cat and f.get("activa", True)]
        if not fuentes_cat:
            continue

        items = []
        for f in fuentes_cat:
            sigla = escapar(f["nombre"])
            desc = escapar(f.get("descripcion", ""))
            web = escapar(f.get("web", ""))
            url_visible = escapar(url_corta(f.get("web", "")))

            items.append(f"""
        <li>
          <strong>{sigla}</strong> — {desc}
          <a href="{web}" target="_blank" rel="noopener" class="fuente-link">{url_visible} →</a>
        </li>""")

        secciones.append(f"""
      <section class="categoria-bloque">
        <h3>{escapar(cat)}</h3>
        <ul class="lista-fuentes">
          {"".join(items)}
        </ul>
      </section>""")

    return "".join(secciones)


def generar_acerca():
    activas = sum(1 for f in FUENTES if f.get("activa", True))
    lista_html = render_lista_fuentes()

    html = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Acerca de — PPA</title>
<meta name="description" content="Qué es PPA, cómo funciona y cuáles son las fuentes que alimentan la publicación.">
<meta property="og:title" content="Acerca de — PPA">
<meta property="og:description" content="Qué es PPA, cómo funciona y cuáles son nuestras fuentes.">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,900&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/ppa.css">
<style>
  .pagina-acerca {{
    max-width: 760px;
    margin: 0 auto;
    padding: 0 32px 60px;
    font-family: 'Source Serif 4', Georgia, serif;
  }}
  .pagina-acerca .volver {{
    display: inline-block;
    margin: 24px 0;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 12px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--gris);
  }}
  .pagina-acerca .volver:hover {{ color: var(--rojo); }}

  .pagina-acerca h1 {{
    font-family: 'Playfair Display', serif;
    font-size: clamp(36px, 5vw, 52px);
    font-weight: 900;
    font-style: italic;
    line-height: 1.05;
    margin-bottom: 18px;
    border-bottom: 3px double var(--tinta);
    padding-bottom: 18px;
  }}
  .pagina-acerca h2 {{
    font-family: 'Playfair Display', serif;
    font-size: 26px;
    font-weight: 700;
    margin-top: 36px;
    margin-bottom: 14px;
    color: var(--tinta);
  }}
  .pagina-acerca h3 {{
    font-family: 'Playfair Display', serif;
    font-size: 20px;
    font-weight: 700;
    font-style: italic;
    margin-top: 28px;
    margin-bottom: 14px;
    color: var(--rojo);
    border-bottom: 1px solid var(--linea);
    padding-bottom: 6px;
  }}
  .pagina-acerca p {{
    font-size: 17px;
    line-height: 1.7;
    margin-bottom: 18px;
    color: var(--tinta);
  }}
  .lista-fuentes {{
    list-style: none;
    padding: 0;
    margin: 0 0 20px 0;
  }}
  .lista-fuentes li {{
    padding: 10px 0;
    border-bottom: 1px dotted var(--linea);
    font-size: 15px;
    line-height: 1.5;
  }}
  .lista-fuentes li:last-child {{ border-bottom: none; }}
  .lista-fuentes strong {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 13px;
    letter-spacing: 0.05em;
    color: var(--tinta);
    font-weight: 700;
  }}
  .fuente-link {{
    display: block;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 11px;
    color: var(--gris);
    margin-top: 4px;
    letter-spacing: 0.04em;
  }}
  .fuente-link:hover {{ color: var(--rojo); }}
  .totales {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 12px;
    color: var(--gris);
    letter-spacing: 0.05em;
    margin-bottom: 20px;
  }}
</style>
</head>
<body>

<div class="barra-superior">
  <div class="contenedor">
    <span class="fecha-barra">PPA · Pulso Productivo Argentino</span>
    <span><a href="/" style="color:inherit">Volver a portada →</a></span>
  </div>
</div>

<article class="pagina-acerca">

  <a href="/" class="volver">← Volver a portada</a>

  <h1>Acerca de PPA</h1>

  <h2>Qué es</h2>

  <p>
    PPA — Pulso Productivo Argentino es una publicación económica que filtra, organiza y
    presenta el trabajo de las principales instituciones, organismos, cámaras y consultoras
    de Argentina.
  </p>

  <p>
    No producimos noticias de actualidad. Lo que hacemos es reunir en un solo lugar lo que
    publican quienes saben, con curaduría editorial y atribución clara de cada fuente.
  </p>

  <h2>Cómo funciona</h2>

  <p>
    Periódicamente, un sistema automatizado revisa las publicaciones de las fuentes
    seleccionadas, descarta lo viejo, deduplica lo repetido y organiza el contenido por
    categoría. La selección de fuentes la hacemos nosotros, una por una; el ordenamiento
    diario lo hace el sistema según reglas que definimos.
  </p>

  <p>
    En <a href="/como-trabajamos.html"><strong>Cómo trabajamos</strong></a> está explicada
    la línea editorial completa: los principios, los criterios y lo que no vas a encontrar
    en PPA.
  </p>

  <h2>Nuestras fuentes</h2>

  <p class="totales">PPA agrega contenido de {activas} fuentes activas, distribuidas por categoría:</p>

  {lista_html}

</article>

<footer class="pie">
  <div class="contenedor">
    <strong>PPA · Pulso Productivo Argentino</strong><br>
    <span class="pie-bajada">Publicación económica</span>
    <div class="pie-meta">
      <a href="/">Portada</a> ·
      <a href="/como-trabajamos.html">Cómo trabajamos</a> ·
      <a href="/acerca.html">Acerca de</a>
    </div>
  </div>
</footer>

</body>
</html>
"""

    out = os.path.join(DIR_SITE, "acerca.html")
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[PPA Acerca] Generado: {out} ({activas} fuentes activas)")


def main():
    print(f"[PPA Acerca] Inicio: {datetime.now(timezone.utc).isoformat()}")
    generar_acerca()
    print(f"[PPA Acerca] Fin")


if __name__ == "__main__":
    main()
