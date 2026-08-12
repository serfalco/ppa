"""
PPA — generador_rem.py
Sección REM — Relevamiento de Expectativas de Mercado del BCRA

Publica mensualmente (segunda quincena). Este script:
1. Detecta si hay un REM nuevo en el BCRA
2. Lo descarga (Excel) y extrae las proyecciones clave
3. Genera /rem/index.html con el más reciente + listado histórico
4. Cachea en data/rem/ para no rebajar en cada corrida

Datos que extrae del Excel:
  - Inflación esperada: próximos 12 meses (promedio de consultoras)
  - Tipo de cambio: fin de año
  - PBI: variación anual esperada
  - Tasa de política monetaria esperada

El Excel del BCRA tiene estructura fija: filas = variables, columnas = horizontes.
"""

import json
import os
import sys
import re
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA, DIR_SITE
import componentes as comp

TZ_AR     = timezone(timedelta(hours=-3))
DIR_REM   = os.path.join(DIR_SITE, "rem")
DIR_REM_DATA = os.path.join(DIR_DATA, "rem")
JSON_REM  = os.path.join(DIR_DATA, "rem_indice.json")

MESES_ES = ["enero","febrero","marzo","abril","mayo","junio",
            "julio","agosto","septiembre","octubre","noviembre","diciembre"]
DIAS_SEMANA = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]

# URL base del BCRA para el REM
# El patrón es: rem_YYYYMM.xls o rem_YYYYMM.xlsx
BCRA_REM_PAGE = "https://www.bcra.gob.ar/PublicacionesEstadisticas/Relevamiento_Expectativas_de_Mercado.asp"
BCRA_REM_BASE = "https://www.bcra.gob.ar/Pdfs/PublicacionesEstadisticas/"

def escapar(s):
    if not s: return ""
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def fecha_legible(dt):
    return f"{DIAS_SEMANA[dt.weekday()]} {dt.day} de {MESES_ES[dt.month-1]} de {dt.year}"

def mes_nombre(yyyy_mm):
    try:
        y, m = int(yyyy_mm[:4]), int(yyyy_mm[5:7])
        return f"{MESES_ES[m-1].capitalize()} {y}"
    except:
        return yyyy_mm


# ================================================================
# SCRAPER — detectar y bajar el REM más reciente
# ================================================================

def _detectar_rem_via_nitter():
    """Busca tuits de @BancoCentral_AR con #REMBCRA para detectar nuevo REM."""
    import requests, re, urllib3
    urllib3.disable_warnings()
    try:
        r = requests.get("https://nitter.net/BancoCentral_AR/rss",
                        timeout=15, verify=False,
                        headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            return []
        feed = feedparser.parse(r.text)
        resultados = []
        for entry in feed.entries:
            texto = entry.get('title','') + entry.get('summary','')
            if '#REMBCRA' in texto or 'rembcra' in texto.lower():
                link_bcra = re.search(r'https://[^\s"<>]*bcra\.gob\.ar[^\s"<>]*', texto)
                resultados.append({
                    "titulo": entry.get('title',''),
                    "link":   link_bcra.group(0) if link_bcra else "",
                    "fecha":  entry.get('published',''),
                })
        return resultados
    except Exception as e:
        print(f"   ⚠ Nitter REMBCRA: {str(e)[:50]}")
        return []


# Meses como los abrevia el BCRA en el nombre del archivo.
MESES = {"ene": "01", "feb": "02", "mar": "03", "abr": "04", "may": "05",
         "jun": "06", "jul": "07", "ago": "08", "sep": "09", "set": "09",
         "oct": "10", "nov": "11", "dic": "12"}

# Cómo se llaman hoy los archivos del REM, verificado el 12/08/2026 en la
# página del BCRA:
#   tablas-relevamiento-expectativas-mercado-jul-2026.xlsx
# Antes eran rem_202607.xls. El patrón viejo queda como segunda opción por si
# vuelve, pero el que encuentra algo hoy es el primero.
PATRON_ACTUAL = re.compile(
    r'href=["\']([^"\']*relevamiento-expectativas-mercado-'
    r'([a-z]{3})-(\d{4})\.(xlsx?))["\']', re.IGNORECASE)
PATRON_VIEJO = re.compile(
    r'href=["\']([^"\']*rem[_\-]?(\d{4})[-_]?(\d{2})[^"\']*\.(xlsx?))["\']',
    re.IGNORECASE)


def _links_rem(html):
    """Links a las tablas del REM, del nombre nuevo y del viejo.

    Solo interesan los que tienen mes y año en el nombre: los otros archivos
    de la página —metodología, listado, ranking, histórico— no son una
    edición del REM. El histórico es una serie aparte y merecería su propio
    tratamiento, no entrar como si fuera el informe del mes.
    """
    resultados = []
    for href, mes, anio, ext in PATRON_ACTUAL.findall(html):
        mm = MESES.get(mes.lower())
        if not mm:
            continue
        resultados.append({"url": _absoluta(href), "periodo": f"{anio}-{mm}",
                           "ext": ext.lower()})
    for href, anio, mes, ext in PATRON_VIEJO.findall(html):
        resultados.append({"url": _absoluta(href), "periodo": f"{anio}-{mes}",
                           "ext": ext.lower()})
    # Con "tablas-" primero: el archivo de datos gana sobre cualquier otro
    # que comparta período.
    resultados.sort(key=lambda x: "tablas-" not in x["url"].lower())
    return resultados


def _absoluta(href):
    if href.startswith("http"):
        return href
    return "https://www.bcra.gob.ar" + ("" if href.startswith("/") else "/") + href


def detectar_rem_disponibles():
    """Scraping de la página del BCRA para encontrar links al REM."""
    import requests, urllib3
    urllib3.disable_warnings()
    try:
        r = requests.get(BCRA_REM_PAGE, timeout=15, verify=False,
                         headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code != 200:
            print(f"   ⚠ BCRA página REM: HTTP {r.status_code}")
            return []
        resultados = _links_rem(r.text)
        # Deduplicar y ordenar desc
        seen = set()
        unicos = []
        for r in sorted(resultados, key=lambda x: x["periodo"], reverse=True):
            if r["periodo"] not in seen:
                seen.add(r["periodo"])
                unicos.append(r)
        print(f"   ✓ REM detectados: {[x['periodo'] for x in unicos[:6]]}")
        return unicos
    except Exception as e:
        print(f"   ⚠ Error detectando REM: {str(e)[:60]}")
        return []


def bajar_rem(info):
    """Descarga el Excel del REM y lo guarda en data/rem/."""
    import requests, urllib3
    urllib3.disable_warnings()
    os.makedirs(DIR_REM_DATA, exist_ok=True)
    periodo = info["periodo"]
    ext     = info.get("ext", "xlsx")
    fname   = f"rem_{periodo}.{ext}"
    fpath   = os.path.join(DIR_REM_DATA, fname)
    if os.path.exists(fpath):
        print(f"   ↩ REM {periodo}: ya descargado")
        return fpath
    try:
        r = requests.get(info["url"], timeout=30, verify=False,
                         headers={"User-Agent": "Mozilla/5.0"})
        r.raise_for_status()
        with open(fpath, "wb") as f:
            f.write(r.content)
        print(f"   ✓ REM {periodo} descargado ({len(r.content)//1024} KB)")
        return fpath
    except Exception as e:
        print(f"   ⚠ Error bajando REM {periodo}: {str(e)[:60]}")
        return None


def parsear_rem(fpath, periodo):
    """Extrae variables clave del Excel del REM."""
    try:
        import pandas as pd
        # El REM tiene estructura variable entre versiones; intentar leer
        engine = "xlrd" if fpath.endswith(".xls") else "openpyxl"
        try:
            df = pd.read_excel(fpath, engine=engine, header=None)
        except Exception:
            # Fallback: intentar con el otro engine
            alt_engine = "openpyxl" if engine == "xlrd" else "xlrd"
            df = pd.read_excel(fpath, engine=alt_engine, header=None)

        # Buscar filas que contengan palabras clave
        vars_encontradas = {}
        keywords = {
            "inflacion_12m": ["inflación", "inflacion", "IPC", "CPI", "precios"],
            "tcn_fin_anio":  ["tipo de cambio", "dólar", "dollar", "USD", "TCN"],
            "pbi":           ["PBI", "PIB", "GDP", "producto bruto"],
            "tasa":          ["tasa", "rate", "política monetaria"],
        }
        for idx, row in df.iterrows():
            row_str = " ".join([str(v).lower() for v in row if v and str(v) != "nan"])
            for clave, kws in keywords.items():
                if clave not in vars_encontradas:
                    for kw in kws:
                        if kw.lower() in row_str:
                            # Tomar el primer número numérico de la fila
                            nums = [v for v in row if isinstance(v, (int, float)) and not pd.isna(v)]
                            if nums:
                                vars_encontradas[clave] = round(float(nums[0]), 2)
                            break

        return {
            "periodo":       periodo,
            "mes_nombre":    mes_nombre(periodo),
            "datos":         vars_encontradas,
            "parseado_en":   datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        print(f"   ⚠ Error parseando REM {periodo}: {str(e)[:80]}")
        return {
            "periodo":    periodo,
            "mes_nombre": mes_nombre(periodo),
            "datos":      {},
        }


# ================================================================
# CARGAR ÍNDICE LOCAL
# ================================================================

def cargar_indice():
    if not os.path.exists(JSON_REM):
        return []
    try:
        with open(JSON_REM,'r',encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

def guardar_indice(indice):
    with open(JSON_REM,'w',encoding='utf-8') as f:
        json.dump(indice, f, ensure_ascii=False, indent=2)


# ================================================================
# HTML
# ================================================================

def card_rem_html(item, es_ultimo=False):
    periodo   = item.get("periodo","")
    mes       = item.get("mes_nombre", mes_nombre(periodo))
    datos     = item.get("datos", {})
    clase     = "rem-card rem-card-ultimo" if es_ultimo else "rem-card"

    def fmt_dato(clave, label, sufijo=""):
        v = datos.get(clave)
        if v is None: return ""
        return f'<div class="rem-dato"><span class="rem-dato-label">{label}</span><span class="rem-dato-valor">{v}{sufijo}</span></div>'

    datos_html = (
        fmt_dato("inflacion_12m", "Inflación esperada 12m", "%") +
        fmt_dato("tcn_fin_anio",  "Dólar fin de año", " $/USD") +
        fmt_dato("pbi",           "PBI variación anual", "%") +
        fmt_dato("tasa",          "Tasa esperada", "% TNA")
    )

    return f"""
<article class="{clase}">
  <div class="rem-card-header">
    <h2 class="rem-mes">{escapar(mes)}</h2>
    {'<span class="rem-badge">Último</span>' if es_ultimo else ''}
  </div>
  {f'<div class="rem-datos">{datos_html}</div>' if datos_html else '<p class="rem-sin-datos">Datos en procesamiento</p>'}
  <a href="/rem/{periodo}/" class="rem-ver">Ver informe completo →</a>
</article>"""


def generar_pagina_rem(indice):
    ahora = datetime.now(TZ_AR)
    if not indice:
        cuerpo = '<p class="rem-vacio">Aún no hay ediciones del REM disponibles.</p>'
    else:
        ultimo = indice[0]
        anteriores = indice[1:]
        cuerpo = f"""
<div class="rem-ultimo">
  <div class="rem-ultimo-label">Última edición</div>
  {card_rem_html(ultimo, es_ultimo=True)}
</div>"""
        if anteriores:
            cards = "".join(card_rem_html(item) for item in anteriores[:12])
            cuerpo += f'<div class="rem-historico"><h2 class="rem-hist-titulo">Ediciones anteriores</h2><div class="rem-grid">{cards}</div></div>'

    html = comp.head_comun(
        "REM — Relevamiento de Expectativas de Mercado · PPA",
        "Las proyecciones de inflación, dólar y PBI de las principales consultoras argentinas, según el REM del BCRA.",
        css_extra='<link rel="stylesheet" href="/assets/rem.css">'
    ) + f"""
<body class="body-rem">

{comp.cabecera("REM")}

<main class="rem-main">
  <div class="contenedor">

    <div class="rem-header">
      <h1 class="rem-titulo">REM</h1>
      <p class="rem-subtitulo">Relevamiento de Expectativas de Mercado</p>
      <div class="rem-explicacion">
        <p>El REM es una encuesta mensual del <strong>Banco Central de la República Argentina</strong> a consultoras, centros de investigación y entidades financieras del país y el exterior.</p>
        <p>Reúne proyecciones de los principales especialistas sobre inflación, tipo de cambio, actividad, tasas, empleo, exportaciones e importaciones.</p>
        <p class="rem-aclaracion">Los pronósticos no constituyen proyecciones propias del BCRA — son las expectativas del mercado.</p>
        <a href="https://www.bcra.gob.ar/relevamiento-expectativas-mercado-rem/" target="_blank" rel="noopener" class="rem-link-bcra">Ver informes oficiales en el BCRA →</a>
      </div>
    </div>

    {cuerpo}

  </div>
</main>

{comp.pie()}
<script src="/assets/ppa.js"></script>
</body>
</html>"""

    os.makedirs(DIR_REM, exist_ok=True)
    out = os.path.join(DIR_REM, "index.html")
    with open(out,'w',encoding='utf-8') as f:
        f.write(html)
    print(f"[REM] Generado: {out} ({len(indice)} ediciones)")


# ================================================================
# MAIN
# ================================================================

def _diagnostico():
    """Detecta, baja y parsea sin tocar el sitio ni data/.

    Sirve para ver si el parser entiende la planilla del mes antes de que la
    edición dependa de eso. El parser busca palabras clave por fila y se
    queda con el primer número: si la planilla cambió de forma, lo que sale
    es un número equivocado y no un error, así que hay que mirarlo.
    """
    import tempfile
    global DIR_REM_DATA

    print("Buscando ediciones del REM en el BCRA…")
    disponibles = detectar_rem_disponibles()
    if not disponibles:
        print("No se detectó ninguna. La página cambió de nuevo: revisar el patrón.")
        return

    for info in disponibles[:2]:
        print(f"\n=== {info['periodo']} · {info['url']}")
        DIR_REM_DATA = tempfile.mkdtemp()
        fpath = bajar_rem(info)
        if not fpath:
            continue

        try:
            import pandas as pd
            hojas = pd.read_excel(fpath, sheet_name=None, header=None,
                                  engine="openpyxl")
            print(f"    hojas: {list(hojas)}")
            primera = list(hojas.values())[0]
            print(f"    la primera mide {primera.shape[0]}x{primera.shape[1]}")
            print("    secciones y una fila de muestra de cada una:")
            anterior_fue_titulo = False
            for i, fila in primera.iterrows():
                celdas = [str(v)[:34] for v in list(fila)[:6]
                          if str(v) != "nan"]
                if not celdas:
                    anterior_fue_titulo = False
                    continue
                # Un título de sección es una fila con una sola celda de texto;
                # las filas de datos traen período, referencia y números.
                es_titulo = len(celdas) == 1 and not celdas[0][0].isdigit()
                if es_titulo:
                    print(f"      {i:3d} § " + celdas[0])
                    anterior_fue_titulo = True
                elif anterior_fue_titulo:
                    print(f"      {i:3d}   " + " | ".join(celdas))
                    anterior_fue_titulo = False
        except Exception as e:
            print(f"    no pude abrir la planilla: {str(e)[:80]}")

        datos = parsear_rem(fpath, info["periodo"])
        print(f"    el parser extrajo: {datos.get('datos')}")
        if not datos.get("datos"):
            print("    ← vacío: el parser no reconoce esta planilla")


def main():
    if "--diagnostico" in sys.argv[1:]:
        _diagnostico()
        return
    print(f"[REM] Inicio: {datetime.now(timezone.utc).isoformat()}")
    indice = cargar_indice()
    periodos_conocidos = {item["periodo"] for item in indice}

    # Detectar REMs disponibles en el BCRA
    disponibles = detectar_rem_disponibles()

    actualizados = 0
    for info in disponibles[:6]:  # solo los últimos 6
        periodo = info["periodo"]
        if periodo in periodos_conocidos:
            continue  # ya lo tenemos
        fpath = bajar_rem(info)
        if not fpath:
            continue
        datos_rem = parsear_rem(fpath, periodo)
        indice.append(datos_rem)
        actualizados += 1

    # Ordenar desc por periodo
    indice.sort(key=lambda x: x.get("periodo",""), reverse=True)
    guardar_indice(indice)

    if actualizados:
        print(f"[REM] {actualizados} ediciones nuevas agregadas")
    else:
        print(f"[REM] Sin novedades ({len(indice)} ediciones en índice)")

    generar_pagina_rem(indice)
    print(f"[REM] Fin")

if __name__ == "__main__":
    main()
