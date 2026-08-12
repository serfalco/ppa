"""
PPA — generador_salud.py
Genera /salud/ con el estado real de cada fuente, para que se vea de afuera.

Por qué existe: el fetcher viene midiendo la salud de las 40 fuentes en cada
corrida —si responden, cuándo publicaron por última vez, cuántos fallos
seguidos llevan— y eso quedaba enterrado en data/fuentes_runtime.json.
Acerca de lista el catálogo, pero es la foto del papel: dice qué fuentes hay,
no cómo vienen andando. Un lector no tenía forma de saber que una sección
está flaca porque su fuente dejó de publicar hace un mes.

Qué muestra y qué no: lo que el fetcher midió, sin maquillaje. Las que fallan
van arriba, no escondidas al final. Las dadas de baja aparecen con el motivo,
porque una fuente que se saca en silencio es un agujero que nadie puede
auditar. Los estados se explican en la página con la misma definición que usa
el código, no con eufemismos.

Si el archivo de salud no está, esto falla en vez de publicar una página
vacía: una tabla en verde sin datos atrás sería peor que no tenerla.

Cómo se corre:
    python scripts/generador_salud.py
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import FUENTES, DIR_SITE, DIR_DATA
import componentes as comp

TZ_AR = timezone(timedelta(hours=-3))

JSON_SALUD = os.path.join(DIR_DATA, "fuentes_runtime.json")

# Cada estado con su etiqueta visible, su clase CSS y la definición exacta que
# aplica el fetcher. El texto se muestra en la página: si alguien quiere saber
# qué quiere decir "degradada", lo tiene ahí y no tiene que leer el código.
ESTADOS = {
    "error": ("Con error", "mal",
              "Falló la última lectura. Todavía puede ser algo puntual: "
              "uno o dos fallos seguidos."),
    "degradada": ("Degradada", "mal",
                  "Tres o más lecturas fallidas seguidas. Ya no parece un "
                  "problema pasajero."),
    "suspendida": ("Suspendida", "mal",
                   "Catorce fallos seguidos, o más de siete días sin una "
                   "lectura buena. Se reintenta una vez por día en vez de en "
                   "cada corrida."),
    "recuperandose": ("Recuperándose", "media",
                      "Volvió a responder después de fallar, pero todavía no "
                      "acumula tres lecturas buenas seguidas."),
    "sin_novedades": ("Sin novedades", "media",
                      "Responde bien, pero no publica nada nuevo hace más de "
                      "siete días. No está rota: está quieta."),
    "ok": ("Al día", "bien",
           "Responde y publicó algo en los últimos siete días."),
}

# Orden de aparición: primero lo que requiere atención. Una página de salud
# que arranca con las que andan bien es un adorno.
ORDEN = ["suspendida", "degradada", "error", "recuperandose",
         "sin_novedades", "ok"]

# Estado que se le asigna a una fuente activa que el fetcher todavía no leyó
# nunca (recién agregada, por ejemplo). No se la cuenta como sana.
SIN_DATOS = ("Sin lecturas", "media",
             "Está en el catálogo pero el fetcher todavía no la leyó ni una "
             "vez. No hay nada medido sobre ella.")


def escapar(s):
    if not s:
        return ""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def _parsear(iso):
    if not iso:
        return None
    try:
        t = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
        return t if t.tzinfo else t.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def hace_cuanto(iso, ahora=None):
    """'hace 3 días', 'hace 2 horas'. Vacío si no hay dato — no '—' ni 0."""
    t = _parsear(iso)
    if t is None:
        return ""
    seg = ((ahora or datetime.now(timezone.utc)) - t).total_seconds()
    if seg < 0:
        return "recién"
    if seg < 3600:
        m = int(seg // 60)
        return "hace un momento" if m < 2 else f"hace {m} minutos"
    if seg < 86400:
        h = int(seg // 3600)
        return "hace 1 hora" if h == 1 else f"hace {h} horas"
    d = int(seg // 86400)
    if d == 1:
        return "hace 1 día"
    if d < 60:
        return f"hace {d} días"
    return f"hace {d // 30} meses"


def fecha_ar(iso):
    t = _parsear(iso)
    return t.astimezone(TZ_AR).strftime("%d/%m/%Y %H:%M") if t else ""


def cargar_salud():
    """El registro del fetcher. Si no está, se corta: no hay nada que mostrar."""
    if not os.path.exists(JSON_SALUD):
        raise FileNotFoundError(
            f"No existe {JSON_SALUD}. La página de salud sale de lo que mide "
            "el fetcher; sin eso no hay nada que publicar.")
    with open(JSON_SALUD, "r", encoding="utf-8") as f:
        return json.load(f)


def armar_filas(salud):
    """Cruza el catálogo con lo medido. Devuelve (activas, dadas_de_baja)."""
    registro = salud.get("fuentes", {})
    activas, bajas = [], []

    for f in FUENTES:
        fila = {
            "id": f["id"],
            "nombre": f.get("nombre", f["id"]),
            "categoria": f.get("categoria", ""),
            "web": f.get("web", ""),
        }
        if not f.get("activa", True):
            fila["baja"] = f.get("baja", "")
            bajas.append(fila)
            continue

        r = registro.get(f["id"]) or {}
        estado = r.get("estado")
        if estado in ESTADOS:
            fila["etiqueta"], fila["clase"], _ = ESTADOS[estado]
        else:
            # Sin lecturas, o un estado que el código dejó de usar. En los dos
            # casos lo honesto es decir que no hay medición, no inventar "ok".
            estado = "sin_datos"
            fila["etiqueta"], fila["clase"], _ = SIN_DATOS
        fila["estado"] = estado
        fila["error"] = r.get("error") or ""
        fila["ultima_publicacion"] = r.get("ultima_publicacion")
        fila["ultima_lectura"] = r.get("ultima_lectura")
        fila["notas"] = r.get("notas_obtenidas")
        fila["fallos"] = r.get("fallos_consecutivos") or 0
        activas.append(fila)

    prioridad = {e: i for i, e in enumerate(ORDEN)}
    activas.sort(key=lambda x: (prioridad.get(x["estado"], len(ORDEN)),
                                x["nombre"].lower()))
    bajas.sort(key=lambda x: x["nombre"].lower())
    return activas, bajas


def render_resumen(activas):
    """Los totales por estado. Solo se muestran los que tienen alguna fuente."""
    cuenta = {}
    for f in activas:
        cuenta[f["estado"]] = cuenta.get(f["estado"], 0) + 1

    bloques = []
    for estado in ORDEN + ["sin_datos"]:
        n = cuenta.get(estado)
        if not n:
            continue
        etiqueta, clase, _ = (SIN_DATOS if estado == "sin_datos"
                              else ESTADOS[estado])
        bloques.append(f"""
      <div class="salud-total salud-{clase}">
        <span class="salud-total-num">{n}</span>
        <span class="salud-total-lbl">{escapar(etiqueta)}</span>
      </div>""")
    return "".join(bloques)


def render_fila(f):
    detalles = []
    if f["ultima_publicacion"]:
        detalles.append(f'<span title="{escapar(fecha_ar(f["ultima_publicacion"]))}">'
                        f'Publicó {escapar(hace_cuanto(f["ultima_publicacion"]))}</span>')
    if f["ultima_lectura"]:
        detalles.append(f'<span title="{escapar(fecha_ar(f["ultima_lectura"]))}">'
                        f'Leída {escapar(hace_cuanto(f["ultima_lectura"]))}</span>')
    if f["fallos"]:
        plural = "fallo seguido" if f["fallos"] == 1 else "fallos seguidos"
        detalles.append(f'<span>{f["fallos"]} {plural}</span>')
    if f["error"]:
        detalles.append(f'<span class="salud-error">{escapar(f["error"])}</span>')

    nombre = escapar(f["nombre"])
    if f["web"]:
        nombre = (f'<a href="{escapar(f["web"])}" target="_blank" '
                  f'rel="noopener">{nombre}</a>')

    return f"""
      <tr>
        <td class="salud-nombre">{nombre}
          <span class="salud-cat">{escapar(f["categoria"])}</span>
        </td>
        <td class="salud-estado">
          <span class="salud-badge salud-{f["clase"]}">{escapar(f["etiqueta"])}</span>
        </td>
        <td class="salud-detalle">{" · ".join(detalles)}</td>
      </tr>"""


def render_bajas(bajas):
    if not bajas:
        return ""
    filas = "".join(f"""
      <li>
        <strong>{escapar(f["nombre"])}</strong>
        <span class="salud-cat">{escapar(f["categoria"])}</span>
        <p>{escapar(f["baja"]) or "Sin motivo anotado."}</p>
      </li>""" for f in bajas)
    return f"""
  <section class="salud-bloque">
    <h2>Dadas de baja</h2>
    <p class="salud-nota">
      No las leemos más. Van acá con el motivo porque una fuente que se saca
      en silencio es un agujero que nadie puede auditar: la sección queda más
      flaca y desde afuera no se entiende por qué. Si el sitio vuelve a
      publicar algo que corresponda al rótulo, se reactivan.
    </p>
    <ul class="salud-bajas">{filas}
    </ul>
  </section>"""


def render_glosario():
    filas = "".join(f"""
      <div class="salud-glosario-item">
        <span class="salud-badge salud-{clase}">{escapar(etiqueta)}</span>
        <p>{escapar(definicion)}</p>
      </div>""" for etiqueta, clase, definicion in
                    [ESTADOS[e] for e in ORDEN] + [SIN_DATOS])
    return f"""
  <section class="salud-bloque">
    <h2>Qué quiere decir cada estado</h2>
    <div class="salud-glosario">{filas}
    </div>
  </section>"""


def generar_salud():
    salud = cargar_salud()
    activas, bajas = armar_filas(salud)
    medido = salud.get("generado_en")

    sanas = sum(1 for f in activas if f["estado"] == "ok")
    filas = "".join(render_fila(f) for f in activas)

    cuando = fecha_ar(medido)
    linea_medicion = (f"Última medición: {escapar(cuando)}"
                      if cuando else "Sin fecha de medición en el registro")

    html = comp.head_comun(
        "Salud de las fuentes · Pulso Productivo Argentino",
        "Estado real de cada fuente que lee PPA: cuáles responden, cuáles "
        "dejaron de publicar y cuáles se dieron de baja, con el motivo.",
        css_extra='<link rel="stylesheet" href="/assets/interior.css">\n'
                  '<link rel="stylesheet" href="/assets/salud.css">'
    ) + f"""
<body class="body-salud">

{comp.cabecera()}

<header class="salud-cabecera">
  <div class="contenedor">
    <h1 class="salud-titulo">Salud de las fuentes</h1>
    <p class="salud-sub">{escapar(linea_medicion)}</p>
  </div>
</header>

<main class="contenedor salud-main">

  <p class="salud-intro">
    PPA no escribe noticias: lee {len(activas) + len(bajas)} fuentes y arma
    con eso la portada. Si una deja de responder o deja de publicar, la
    sección que alimenta se ve más flaca y desde afuera no hay manera de
    saber por qué. Esta página es eso: lo que el sistema mide en cada
    corrida, sin filtrar. Hoy hay <strong>{sanas} de {len(activas)}</strong>
    fuentes activas al día.
  </p>

  <section class="salud-bloque">
    <div class="salud-totales">{render_resumen(activas)}
    </div>
  </section>

  <section class="salud-bloque">
    <h2>Fuentes activas</h2>
    <p class="salud-nota">
      Ordenadas por estado: primero las que tienen algún problema. Los
      horarios están en hora argentina.
    </p>
    <table class="salud-tabla">
      <tbody>{filas}
      </tbody>
    </table>
  </section>
{render_bajas(bajas)}
{render_glosario()}

  <p class="salud-pie-nota">
    Esta página se regenera en cada edición a partir de
    <code>fuentes_runtime.json</code>, que escribe el propio lector de feeds.
    No hay carga a mano: lo que dice acá es lo que midió el sistema.
    Más sobre el criterio editorial en
    <a href="/como-trabajamos.html">Cómo trabajamos</a> y el catálogo completo
    en <a href="/acerca.html">Acerca de</a>.
  </p>

</main>

{comp.pie()}

<script src="/assets/ppa.js"></script>
</body>
</html>
"""

    destino = os.path.join(DIR_SITE, "salud")
    os.makedirs(destino, exist_ok=True)
    out = os.path.join(destino, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[PPA Salud] Generado: {out}")
    print(f"[PPA Salud] {len(activas)} activas ({sanas} al día) · "
          f"{len(bajas)} dadas de baja")


def main():
    print(f"[PPA Salud] Inicio: {datetime.now(timezone.utc).isoformat()}")
    generar_salud()
    print("[PPA Salud] Fin")


if __name__ == "__main__":
    main()
