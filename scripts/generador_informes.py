"""
PPA — generador_informes.py
Genera /informes/index.html con los informes institucionales
que llegan automáticamente de las fuentes Tier 3.
Lee data/notas_raw.json y filtra las fuentes institucionales.
Sin trabajo extra — usa el cache que ya existe.
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA, DIR_SITE
import componentes as comp

TZ_AR = timezone(timedelta(hours=-3))
JSON_RAW = os.path.join(DIR_DATA, "notas_raw.json")
DIR_INF  = os.path.join(DIR_SITE, "informes")

MESES = ["enero","febrero","marzo","abril","mayo","junio",
         "julio","agosto","septiembre","octubre","noviembre","diciembre"]

# Fuentes Tier 3 — institucionales
FUENTES_INST = {
    "bcra","indec","mecon","econviews","fiel","ieral","fundar",
    "iaraf","ceso","cedlas","cippec","ecogo"
}

def escapar(s):
    if not s: return ""
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def fecha_corta(iso):
    try:
        dt = datetime.fromisoformat(iso.replace('Z','+00:00')).astimezone(TZ_AR)
        return f"{dt.day} de {MESES[dt.month-1]}"
    except:
        return ""

def nota_html(nota):
    titulo = escapar(nota.get("titulo",""))
    fuente = escapar(nota.get("fuente_nombre",""))
    link   = escapar(nota.get("link","#"))
    fecha  = fecha_corta(nota.get("fecha_publicacion",""))
    desc   = escapar((nota.get("descripcion","") or "")[:200])

    return f"""
<article class="inf-item">
  <div class="inf-meta">
    <span class="inf-fuente">{fuente}</span>
    {f'<span class="inf-fecha">{fecha}</span>' if fecha else ''}
  </div>
  <h2 class="inf-titulo"><a href="{link}" target="_blank" rel="noopener">{titulo}</a></h2>
  {f'<p class="inf-desc">{desc}</p>' if desc else ''}
</article>"""

def generar_informes():
    if not os.path.exists(JSON_RAW):
        print("[Informes] Sin notas_raw.json — saltando")
        return

    with open(JSON_RAW,'r',encoding='utf-8') as f:
        raw = json.load(f)

    notas = raw.get("notas", [])

    # Filtrar solo fuentes institucionales
    informes = [n for n in notas if n.get("fuente_id","") in FUENTES_INST]
    # Ordenar más reciente primero
    informes.sort(key=lambda n: n.get("fecha_publicacion",""), reverse=True)

    if not informes:
        cuerpo = '<p class="inf-vacio">Sin informes disponibles por el momento.</p>'
    else:
        cuerpo = "".join(nota_html(n) for n in informes)

    html = (
        comp.head_comun(
            "Informes — PPA · Pulso Productivo Argentino",
            "Informes y publicaciones de consultoras, institutos y organismos sobre la economía argentina.",
            css_extra='<link rel="stylesheet" href="/assets/informes.css">'
        ) + f"""
<body>

{comp.cabecera("Informes")}

<main class="inf-main">
  <div class="contenedor">
    <div class="inf-header">
      <div class="kicker">Informes</div>
      <div class="kicker-linea"></div>
      <p class="inf-sub">Consultoras · Institutos · Organismos · {len(informes)} publicaciones</p>
    </div>
    <div class="inf-lista">
      {cuerpo}
    </div>
  </div>
</main>

{comp.pie()}
<script src="/assets/ppa.js"></script>
</body>
</html>"""
    )

    os.makedirs(DIR_INF, exist_ok=True)
    out = os.path.join(DIR_INF, "index.html")
    with open(out,'w',encoding='utf-8') as f:
        f.write(html)
    print(f"[Informes] Generado: {out} ({len(informes)} informes)")

def main():
    print(f"[Informes] Inicio: {datetime.now(timezone.utc).isoformat()}")
    generar_informes()
    print(f"[Informes] Fin")

if __name__ == "__main__":
    main()
