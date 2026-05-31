"""
PPA — generador_expectativas.py
Genera la sección "Expectativas de mercado": lista las publicaciones recientes
de las consultoras y firmas profesionales argentinas.

Lee: data/notas.json
Filtra: solo notas con categoría "Expectativas de mercado"
Genera: site/expectativas/index.html

Cómo se corre:
    python scripts/generador_expectativas.py
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA, DIR_SITE
import componentes as comp
from FUENTES import FUENTES

JSON_NOTAS = os.path.join(DIR_DATA, "notas.json")
DIR_EXPECTATIVAS = os.path.join(DIR_SITE, "expectativas")

TZ_AR = timezone(timedelta(hours=-3))
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
         "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
DIAS_SEMANA = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]


def escapar(s):
    if not s:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def fecha_legible(dt):
    return f"{DIAS_SEMANA[dt.weekday()]} {dt.day} de {MESES[dt.month - 1]} de {dt.year}"


def cargar_notas_expectativas():
    """Carga notas filtradas por categoría Expectativas de mercado."""
    if not os.path.exists(JSON_NOTAS):
        return []
    try:
        with open(JSON_NOTAS, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception:
        return []
    notas = [n for n in data.get("notas", []) if n.get("categoria") == "Expectativas de mercado"]
    notas.sort(key=lambda n: n.get("fecha_publicacion", ""), reverse=True)
    return notas


def fuentes_activas_expectativas():
    """Lista las firmas activas de Expectativas de mercado."""
    return [f for f in FUENTES if f["categoria"] == "Expectativas de mercado" and f.get("activa", True)]


def render_nota(nota):
    """HTML de una nota individual en el listado."""
    try:
        dt = datetime.fromisoformat(nota["fecha_publicacion"].replace('Z', '+00:00'))
        fecha_leg = fecha_legible(dt.astimezone(TZ_AR))
    except Exception:
        fecha_leg = ""

    return f"""
    <article class="exp-item">
      <div class="exp-firma">{escapar(nota['fuente_nombre'])}</div>
      <h3>
        <a href="{escapar(nota['link'])}" target="_blank" rel="noopener">{escapar(nota['titulo'])}</a>
      </h3>
      <p class="exp-bajada">{escapar(nota.get('bajada', ''))}</p>
      <div class="exp-meta">
        <span class="exp-fecha">{escapar(fecha_leg)}</span>
      </div>
    </article>"""


def render_lista_firmas(firmas):
    """HTML del listado de firmas activas en el sidebar."""
    items = []
    for f in firmas:
        items.append(f"""
      <li>
        <a href="{escapar(f['web'])}" target="_blank" rel="noopener">
          <strong>{escapar(f['nombre'])}</strong>
        </a>
      </li>""")
    return "".join(items)


def generar_expectativas():
    notas = cargar_notas_expectativas()
    firmas = fuentes_activas_expectativas()

    ahora_ar = datetime.now(TZ_AR)
    actualizado = ahora_ar.strftime("%d/%m/%Y %H:%M")

    if notas:
        notas_html = "".join([render_nota(n) for n in notas])
    else:
        notas_html = """
        <div class="exp-vacio">
          <p>No hay publicaciones recientes de las firmas.</p>
        </div>"""

    firmas_html = render_lista_firmas(firmas)

    html = f"""<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Expectativas de mercado — PPA</title>
<meta name="description" content="Las consultoras y firmas que arman las expectativas del mercado argentino.">
<meta property="og:title" content="Expectativas de mercado — PPA">
<meta property="og:description" content="Las consultoras y firmas que arman las expectativas del mercado argentino.">
<meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900;1,400;1,900&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/ppa.css">
<style>
  :root {{
    --exp-acento: #c87c1c;
  }}
  .exp-page {{
    max-width: 1100px;
    margin: 0 auto;
    padding: 0 32px 60px;
  }}
  .exp-header {{
    border-bottom: 3px double var(--tinta);
    padding: 36px 0 24px;
    text-align: center;
    position: relative;
  }}
  .exp-header::before, .exp-header::after {{
    content: ''; position: absolute; left: 0; right: 0; height: 1px; background: var(--tinta);
  }}
  .exp-header::before {{ top: 8px; }}
  .exp-header::after {{ bottom: 8px; }}
  .exp-kicker {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 10px; letter-spacing: 0.4em; text-transform: uppercase;
    color: var(--exp-acento); font-weight: 600;
  }}
  .exp-page h1 {{
    font-family: 'Playfair Display', serif;
    font-weight: 900; font-style: italic;
    font-size: clamp(36px, 6vw, 60px); line-height: 1; color: var(--tinta);
    margin: 8px 0;
  }}
  .exp-intro {{
    font-family: 'Source Serif 4', serif;
    font-style: italic; font-size: 17px; color: var(--gris);
    max-width: 600px; margin: 14px auto 0; line-height: 1.5;
  }}
  .exp-actualizado {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase;
    color: var(--gris); margin-top: 10px;
  }}
  .exp-nav {{
    border-bottom: 1px solid var(--linea);
    padding: 14px 0;
    background: var(--papel-2);
    margin-bottom: 32px;
  }}
  .exp-nav .contenedor {{
    display: flex; justify-content: center; gap: 28px; flex-wrap: wrap;
  }}
  .exp-nav a {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 12px; letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--tinta); font-weight: 500;
  }}
  .exp-nav a.activo {{ color: var(--exp-acento); font-weight: 700; }}

  .exp-layout {{
    display: grid;
    grid-template-columns: 1fr 280px;
    gap: 40px;
    margin-top: 24px;
  }}
  @media (max-width: 900px) {{
    .exp-layout {{ grid-template-columns: 1fr; }}
  }}

  .exp-item {{
    padding: 18px 0 22px;
    border-bottom: 1px solid var(--linea);
  }}
  .exp-firma {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 11px;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--exp-acento);
    font-weight: 700;
    margin-bottom: 6px;
  }}
  .exp-item h3 {{
    font-family: 'Playfair Display', serif;
    font-size: 22px; font-weight: 700; line-height: 1.2;
    margin-bottom: 8px;
  }}
  .exp-item h3 a {{ color: var(--tinta); }}
  .exp-item h3 a:hover {{ color: var(--exp-acento); }}
  .exp-bajada {{
    font-family: 'Source Serif 4', serif;
    font-size: 15px; color: var(--gris); line-height: 1.5;
    margin-bottom: 8px;
  }}
  .exp-meta {{
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 11px; color: var(--gris); letter-spacing: 0.04em;
  }}

  .exp-sidebar {{
    border-left: 1px solid var(--linea);
    padding-left: 28px;
  }}
  .exp-sidebar h3 {{
    font-family: 'Playfair Display', serif;
    font-size: 22px; font-weight: 700; font-style: italic;
    border-bottom: 2px solid var(--exp-acento);
    padding-bottom: 8px; margin-bottom: 14px;
  }}
  .exp-sidebar ul {{
    list-style: none; padding: 0;
  }}
  .exp-sidebar li {{
    padding: 7px 0;
    border-bottom: 1px dotted var(--linea);
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 13px;
  }}
  .exp-sidebar a {{ color: var(--tinta); }}
  .exp-sidebar a:hover {{ color: var(--exp-acento); }}

  .exp-vacio {{
    text-align: center; padding: 80px 20px; color: var(--gris);
    font-family: 'Source Serif 4', serif; font-style: italic;
  }}
</style>
</head>
<body>

{comp.franja_datos()}

<header class="exp-header">
  <div class="contenedor">
    <div class="exp-kicker">Expectativas</div>
    <h1>Las firmas</h1>
    <p class="exp-intro">
      Las consultoras y firmas profesionales que arman las expectativas del
      mercado argentino. Análisis macro, financiero y sectorial.
    </p>
    <p class="exp-actualizado">Actualizado: {escapar(actualizado)}</p>
  </div>
</header>

{comp.nav_principal("Expectativas")}

<main class="exp-page">
  <div class="exp-layout">
    <section class="exp-notas">
      {notas_html}
    </section>
    <aside class="exp-sidebar">
      <h3>Firmas activas</h3>
      <ul>{firmas_html}</ul>
    </aside>
  </div>
</main>

{comp.pie()}

</body>
</html>"""

    os.makedirs(DIR_EXPECTATIVAS, exist_ok=True)
    out = os.path.join(DIR_EXPECTATIVAS, "index.html")
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[PPA Expectativas] Generado: {out} ({len(notas)} notas, {len(firmas)} firmas activas)")


def main():
    print(f"[PPA Expectativas] Inicio: {datetime.now(timezone.utc).isoformat()}")
    generar_expectativas()
    print(f"[PPA Expectativas] Fin")


if __name__ == "__main__":
    main()
