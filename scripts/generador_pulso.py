"""
PPA — generador_pulso.py
"El Pulso del Día": lectura económica GENERADA por el sistema a partir de
data/datos.json. Sin IA — reglas deterministas sobre los datos.

Produce:
  - data/pulso.json           (los hechos, estructurados)
  - site/pulso/<slug>.html     (una página por hecho, DENTRO de la web)
  - site/pulso/index.html      (índice de los hechos del día)

Reglas de oro (alineadas con el documento rector §14-15, §26-27):
  - Un hecho SOLO se genera si su dato está presente y NO es "stale".
    Si el dato quedó viejo (la fuente no actualizó), no se afirma nada:
    es la regla de verificación — no publicar lo que no se puede sostener.
  - Cada hecho conserva su fuente y la fecha del dato.
  - Los números se calculan, no se escriben a mano.

Cómo se corre:
    python scripts/generador_pulso.py
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA, DIR_SITE
import componentes as comp

TZ_AR = timezone(timedelta(hours=-3))
JSON_DATOS = os.path.join(DIR_DATA, "datos.json")
JSON_PULSO = os.path.join(DIR_DATA, "pulso.json")
DIR_PULSO  = os.path.join(DIR_SITE, "pulso")
MAX_HECHOS = 6


# =============================================================
# FORMATO DE NÚMEROS (estilo argentino: miles con . decimales con ,)
# =============================================================

def _miles(n):
    try:
        return f"{int(round(n)):,}".replace(",", ".")
    except Exception:
        return str(n)

def pesos(x):
    return "$" + _miles(x)

def pct(x, dec=1):
    try:
        s = f"{float(x):.{dec}f}".replace(".", ",")
        return s + "%"
    except Exception:
        return str(x) + "%"

def firmado(x, dec=1):
    """Variación con signo: +2,2% / -0,2%"""
    try:
        v = float(x)
        s = f"{v:+.{dec}f}".replace(".", ",")
        return s + "%"
    except Exception:
        return str(x)


# =============================================================
# ACCESO A DATOS con verificación de frescura
# =============================================================

def cargar_datos():
    if not os.path.exists(JSON_DATOS):
        return {}, ""
    try:
        with open(JSON_DATOS, "r", encoding="utf-8") as f:
            d = json.load(f)
        return d.get("datos", {}), d.get("generado_ar", "")
    except Exception:
        return {}, ""


def vivo(datos, clave):
    """Devuelve el item si existe y NO es stale; si no, None.
    Este gate es la verificación: un dato viejo no genera hecho."""
    item = datos.get(clave)
    if not item or item.get("valor") is None:
        return None
    if item.get("stale"):
        return None
    return item


def fecha_dato(item, fallback):
    f = item.get("fecha") or ""
    if f and len(f) >= 10:
        try:
            dt = datetime.fromisoformat(f.replace("Z", "+00:00"))
            return dt.astimezone(TZ_AR).strftime("%d/%m/%Y")
        except Exception:
            pass
    return fallback


# =============================================================
# REGLAS — cada una devuelve un hecho (dict) o None
# =============================================================

def _venta(item):
    v = item.get("valor")
    if isinstance(v, dict):
        return v.get("venta")
    return v


def regla_brecha(datos, fref):
    ofi = vivo(datos, "dolar_oficial")
    mep = vivo(datos, "dolar_mep")
    if not (ofi and mep):
        return None
    v_ofi, v_mep = _venta(ofi), _venta(mep)
    if not (v_ofi and v_mep):
        return None
    brecha = (v_mep / v_ofi - 1) * 100

    ccl = vivo(datos, "dolar_ccl"); blue = vivo(datos, "dolar_blue")
    may = vivo(datos, "dolar_mayorista"); tar = vivo(datos, "dolar_tarjeta")
    v_ccl = _venta(ccl) if ccl else None
    v_blue = _venta(blue) if blue else None

    if brecha < 2:
        titulo = f"La brecha del dólar quedó casi planchada: {pct(brecha)}"
    else:
        titulo = f"La brecha del dólar MEP con el oficial es de {pct(brecha)}"

    baj = f"El MEP ({pesos(v_mep)}) frente al oficial ({pesos(v_ofi)})."
    extras = []
    if v_ccl:
        extras.append(f"el CCL marca {pct((v_ccl/v_ofi-1)*100)}")
    if v_blue:
        extras.append(f"el blue, {pct((v_blue/v_ofi-1)*100)}")
    if extras:
        baj += " Además, " + " y ".join(extras) + "."

    cuerpo = [
        f"El dólar oficial cerró a {pesos(v_ofi)} para la venta y el MEP a "
        f"{pesos(v_mep)}, dejando una brecha de {pct(brecha)} entre ambos.",
    ]
    if v_ccl or v_blue:
        pares = []
        if v_ccl: pares.append(f"el contado con liquidación ({pesos(v_ccl)}) marca {pct((v_ccl/v_ofi-1)*100)}")
        if v_blue: pares.append(f"el blue ({pesos(v_blue)}) queda en {pct((v_blue/v_ofi-1)*100)}")
        cuerpo.append("Mirando el resto de las cotizaciones, " + " y ".join(pares) + " de brecha contra el oficial.")

    tabla = [("Oficial (venta)", pesos(v_ofi))]
    if may: tabla.append(("Mayorista", pesos(_venta(may))))
    tabla.append(("MEP", pesos(v_mep)))
    if v_ccl: tabla.append(("CCL", pesos(v_ccl)))
    if v_blue: tabla.append(("Blue", pesos(v_blue)))
    if tar: tabla.append(("Tarjeta", pesos(_venta(tar))))

    return {
        "slug": "brecha-dolar",
        "categoria": "Cambiario",
        "titulo": titulo,
        "bajada": baj,
        "dato": {"n": pct(brecha), "txt": "Brecha entre el dólar MEP y el oficial"},
        "cuerpo": cuerpo,
        "tabla": tabla,
        "metodo": f"Brecha = (MEP ÷ Oficial − 1) × 100 = ({_miles(v_mep)} ÷ {_miles(v_ofi)} − 1) × 100 = {pct(brecha)}.",
        "criollo": "La brecha es cuánto más caro está el dólar financiero (el que se compra con bonos) que el oficial. Cuando es chica, los dos precios casi se tocan.",
        "fuente_nombre": "DolarApi · cálculo PPA",
        "fuente_url": "https://dolarapi.com",
        "dato_fecha": fecha_dato(mep, fref),
        "prioridad": 90,
    }


def regla_riesgo(datos, fref):
    rp = vivo(datos, "riesgo_pais")
    if not rp:
        return None
    n = rp["valor"]
    var = rp.get("variacion")
    if var is not None and var > 0.05:
        titulo = f"El riesgo país subió a {_miles(n)} puntos"
        movim = f"un alza del {pct(abs(var))} frente al día previo"
    elif var is not None and var < -0.05:
        titulo = f"El riesgo país bajó a {_miles(n)} puntos"
        movim = f"una baja del {pct(abs(var))} frente al día previo"
    else:
        titulo = f"El riesgo país cerró en {_miles(n)} puntos"
        movim = "sin cambios relevantes frente al día previo"

    return {
        "slug": "riesgo-pais",
        "categoria": "Deuda",
        "titulo": titulo,
        "bajada": f"El indicador quedó en {_miles(n)} puntos básicos, {movim}.",
        "dato": {"n": _miles(n), "txt": "puntos básicos" + (f" · {firmado(var)} en el día" if var is not None else "")},
        "cuerpo": [
            f"El riesgo país cerró en {_miles(n)} puntos básicos, {movim}. El indicador "
            "mide la sobretasa que paga la deuda argentina por encima de los bonos del "
            "Tesoro de Estados Unidos.",
            f"En números redondos, {_miles(n)} puntos equivalen a {pct(n/100)} de interés "
            "extra sobre lo que paga Estados Unidos por endeudarse.",
        ],
        "criollo": "Es como el puntaje crediticio del país. Si sube, pedir plata prestada afuera se encarece; si baja, se abarata.",
        "fuente_nombre": rp.get("fuente", "ArgentinaDatos"),
        "fuente_url": "https://argentinadatos.com",
        "dato_fecha": fecha_dato(rp, fref),
        "prioridad": 85,
    }


def regla_banda(datos, fref):
    b = vivo(datos, "banda")
    if not b:
        return None
    v = b["valor"]
    if not isinstance(v, dict):
        return None
    piso, techo = v.get("piso"), v.get("techo")
    dolar, pos = v.get("dolar"), v.get("posicion")
    if None in (piso, techo, dolar, pos):
        return None
    return {
        "slug": "banda-cambiaria",
        "categoria": "Banda cambiaria",
        "titulo": f"El dólar mayorista corre al {pct(pos,0)} de la banda",
        "bajada": f"Con piso en {pesos(piso)} y techo en {pesos(techo)}, el mayorista ({pesos(dolar)}) se ubica en el canal.",
        "dato": {"n": pct(pos, 0), "txt": "posición del mayorista dentro del canal piso–techo"},
        "cuerpo": [
            f"Bajo el esquema de bandas del Banco Central, el piso se desliza a {pesos(piso)} "
            f"y el techo a {pesos(techo)}. El dólar mayorista ({pesos(dolar)}) se ubica al "
            f"{pct(pos)} del recorrido entre ambos.",
        ],
        "metodo": f"Posición = (Mayorista − Piso) ÷ (Techo − Piso) × 100 = "
                  f"({_miles(dolar)} − {_miles(piso)}) ÷ ({_miles(techo)} − {_miles(piso)}) × 100 = {pct(pos)}.",
        "criollo": "El BCRA deja flotar el dólar dentro de un pasillo. Si se pega al techo hay más presión de suba; si se va al piso, lo contrario.",
        "fuente_nombre": "cálculo PPA (esquema BCRA)",
        "fuente_url": "https://www.bcra.gob.ar",
        "dato_fecha": fecha_dato(b, fref),
        "prioridad": 75,
    }


def regla_ipc(datos, fref):
    ipc = vivo(datos, "ipc_mensual")
    if not ipc:
        return None
    x = ipc["valor"]
    nuc = vivo(datos, "ipc_nucleo")
    xn = nuc["valor"] if nuc else None
    titulo = f"El IPC marcó {pct(x)} mensual"
    if xn is not None:
        titulo += f", con el núcleo en {pct(xn)}"
    cuerpo = [f"El último IPC nacional registró una variación mensual del {pct(x)}."]
    if xn is not None:
        cuerpo.append(
            f"El componente núcleo — que excluye precios estacionales y regulados y "
            f"suele marcar la tendencia de fondo — avanzó {pct(xn)}, "
            + ("por debajo" if xn < x else "por encima") + " del índice general."
        )
    return {
        "slug": "inflacion-ipc",
        "categoria": "Inflación",
        "titulo": titulo,
        "bajada": ("La inflación núcleo corrió por debajo del nivel general."
                   if (xn is not None and xn < x) else "Último dato del índice de precios."),
        "dato": {"n": pct(x), "txt": "IPC mensual" + (f" · núcleo {pct(xn)}" if xn is not None else "")},
        "cuerpo": cuerpo,
        "criollo": "El IPC general mide todo. El núcleo saca lo que sube o baja por temporada o por decisión del Estado, para mostrar la inflación de fondo.",
        "fuente_nombre": "INDEC · datos.gob.ar",
        "fuente_url": "https://www.indec.gob.ar",
        "dato_fecha": fecha_dato(ipc, fref),
        "prioridad": 80,
    }


def regla_reservas(datos, fref):
    r = vivo(datos, "reservas")   # si es stale, vivo() devuelve None y NO se publica
    if not r:
        return None
    n = r["valor"]
    var = r.get("variacion")
    mov = ""
    if var is not None:
        mov = f", {'una suba' if var >= 0 else 'una baja'} del {pct(abs(var))} en el día"
    return {
        "slug": "reservas-bcra",
        "categoria": "Reservas",
        "titulo": f"Las reservas del BCRA quedaron en US$ {_miles(n)} millones",
        "bajada": f"Stock bruto del Banco Central{mov}.",
        "dato": {"n": _miles(n), "txt": "millones de USD · reservas brutas" + (f" · {firmado(var)}" if var is not None else "")},
        "cuerpo": [
            f"Las reservas internacionales brutas del Banco Central cerraron en "
            f"US$ {_miles(n)} millones{mov}. Es el stock bruto, antes de descontar "
            "swaps, encajes y otras obligaciones.",
        ],
        "criollo": "Son los dólares que tiene el Banco Central. El número bruto es el total; el neto (que descuenta deudas) suele ser bastante más bajo.",
        "fuente_nombre": r.get("fuente", "BCRA API v4"),
        "fuente_url": "https://www.bcra.gob.ar",
        "dato_fecha": fecha_dato(r, fref),
        "prioridad": 88,
    }


REGLAS = [regla_brecha, regla_riesgo, regla_reservas, regla_ipc, regla_banda]


# =============================================================
# HTML
# =============================================================

def escapar(s):
    if s is None: return ""
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")


def pagina_hecho(h):
    tabla_html = ""
    if h.get("tabla"):
        filas = "".join(f"<tr><td>{escapar(a)}</td><td>{escapar(b)}</td></tr>" for a, b in h["tabla"])
        tabla_html = f'<table class="pulso-tabla">{filas}</table>'
    metodo_html = ""
    if h.get("metodo"):
        metodo_html = f'<div class="pulso-metodo"><div class="mt">Cómo se calcula</div>{escapar(h["metodo"])}</div>'
    criollo_html = ""
    if h.get("criollo"):
        criollo_html = f'<div class="pulso-criollo"><div class="mt">En criollo</div>{escapar(h["criollo"])}</div>'
    cuerpo_html = "".join(f'<p class="pulso-cuerpo">{escapar(p)}</p>' for p in h.get("cuerpo", []))

    css = '<link rel="stylesheet" href="/assets/pulso.css">'
    html = comp.head_comun(
        f'{h["titulo"]} — PPA', h.get("bajada",""), css_extra=css
    ) + f"""
<body class="body-hecho">
{comp.cabecera("La Data del Día")}
<main class="pulso-main"><div class="contenedor">

  <div class="pulso-breadcrumb"><a href="/">Portada</a> › <a href="/pulso/">El Pulso del Día</a> › {escapar(h["categoria"])}</div>

  <article class="hecho">
    <span class="hecho-cat">{escapar(h["categoria"])}</span>
    <h1 class="hecho-titulo">{escapar(h["titulo"])}</h1>
    <p class="hecho-bajada">{escapar(h["bajada"])}</p>

    <div class="dato-box"><span class="n">{escapar(h["dato"]["n"])}</span><span class="txt">{escapar(h["dato"]["txt"])}<br>dato del {escapar(h.get("dato_fecha",""))}</span></div>

    {cuerpo_html}
    {tabla_html}
    {metodo_html}
    {criollo_html}

    <div class="fuente-pie"><b>Fuente:</b> {escapar(h["fuente_nombre"])}. &nbsp;<a href="{escapar(h["fuente_url"])}" target="_blank" rel="noopener">Ver la fuente original →</a></div>
    <a href="/" class="pulso-volver">← Volver a la portada</a>
  </article>

</div></main>
{comp.pie()}
<script src="/assets/ppa.js"></script>
</body>
</html>"""
    return html


def pagina_indice(hechos, fref):
    css = '<link rel="stylesheet" href="/assets/pulso.css">'
    items = ""
    for h in hechos:
        items += f"""
      <a class="pulso-card" href="/pulso/{escapar(h['slug'])}.html">
        <span class="pulso-cat">{escapar(h['categoria'])}</span>
        <h2 class="pulso-h">{escapar(h['titulo'])}</h2>
        <p class="pulso-baj">{escapar(h['bajada'])}</p>
        <span class="pulso-go">Leer en PPA →</span>
      </a>"""
    html = comp.head_comun(
        "El Pulso del Día — PPA", "La lectura económica del día generada por PPA.", css_extra=css
    ) + f"""
<body class="body-pulso-indice">
{comp.cabecera("La Data del Día")}
<main class="pulso-main"><div class="contenedor">
  <div class="pulso-kicker"><span class="k">El Pulso del Día</span><span class="ln"></span><span class="tag">Generado por PPA</span></div>
  <p class="pulso-sub">Lectura automática de los movimientos económicos del día, generada a partir de los datos oficiales. Actualizado: {escapar(fref)}.</p>
  <div class="pulso-lista">{items}</div>
</div></main>
{comp.pie()}
<script src="/assets/ppa.js"></script>
</body>
</html>"""
    return html


# =============================================================
# MAIN
# =============================================================

def main():
    print(f"[Pulso] Inicio: {datetime.now(TZ_AR).strftime('%Y-%m-%d %H:%M')} ARG")
    datos, fref = cargar_datos()
    if not datos:
        print("[Pulso] Sin datos.json — nada que generar.")
        return

    hechos = []
    for regla in REGLAS:
        try:
            h = regla(datos, fref)
            if h:
                hechos.append(h)
        except Exception as e:
            print(f"[Pulso] ⚠ regla {regla.__name__}: {str(e)[:60]}")

    hechos.sort(key=lambda h: h.get("prioridad", 0), reverse=True)
    hechos = hechos[:MAX_HECHOS]

    # data/pulso.json
    salida = {
        "generado_en": datetime.now(timezone.utc).isoformat(),
        "generado_ar": fref,
        "hechos": hechos,
    }
    with open(JSON_PULSO, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)

    # páginas internas
    os.makedirs(DIR_PULSO, exist_ok=True)
    for h in hechos:
        ruta = os.path.join(DIR_PULSO, f"{h['slug']}.html")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(pagina_hecho(h))
    with open(os.path.join(DIR_PULSO, "index.html"), "w", encoding="utf-8") as f:
        f.write(pagina_indice(hechos, fref))

    print(f"[Pulso] {len(hechos)} hechos generados: {', '.join(h['slug'] for h in hechos)}")
    print(f"[Pulso] Guardado: {JSON_PULSO} + {len(hechos)} páginas en {DIR_PULSO}/")


if __name__ == "__main__":
    main()
