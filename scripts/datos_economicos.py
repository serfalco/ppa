"""
PPA — datos_economicos.py
Motor de datos económicos. Corre en GitHub Actions (no en el navegador).

Junta TODO en un solo data/datos.json ya cocido y validado:
  - Dólares (dolarapi)
  - Merval + Riesgo País (scraping con FALLBACK en cadena, número + variación)
  - Reservas BCRA y series mensuales (datos.gob.ar)

Reglas de oro:
  - Cada fuente falla sin romper el resto (igual que fetcher.py).
  - Si una fuente no responde HOY, se conserva el ÚLTIMO VALOR BUENO
    (leído del datos.json anterior) y se marca como "stale".
  - Cada dato lleva su frecuencia y la fecha real del período.
  - El navegador solo LEE este JSON, no consulta APIs.

Cómo se corre:
    python scripts/datos_economicos.py                 # todo
    python scripts/datos_economicos.py --solo-mercado  # solo intradía (cron horario)
    python scripts/datos_economicos.py --solo-mensual  # solo baja frecuencia (cron diario)
"""

import json
import os
import sys
import re
from datetime import datetime, timezone, timedelta

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA

TZ_AR = timezone(timedelta(hours=-3))
JSON_DATOS = os.path.join(DIR_DATA, "datos.json")

# User-Agent de navegador real: varias fuentes filtran bots básicos
HDRS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json, text/html, */*",
}


# =============================================================
# HELPERS
# =============================================================

def ahora_iso():
    return datetime.now(timezone.utc).isoformat()


def get_json(url, timeout=12):
    """GET que devuelve JSON o None. Nunca tira excepción."""
    try:
        r = requests.get(url, headers=HDRS, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"   ⚠  JSON {url[:55]}… -> {str(e)[:70]}")
        return None


def get_html(url, timeout=12):
    """GET que devuelve texto HTML o None. Nunca tira excepción."""
    try:
        r = requests.get(url, headers=HDRS, timeout=timeout)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"   ⚠  HTML {url[:55]}… -> {str(e)[:70]}")
        return None


def cargar_previo():
    """Lee el datos.json anterior para tener fallback de último valor bueno."""
    if not os.path.exists(JSON_DATOS):
        return {}
    try:
        with open(JSON_DATOS, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def valor_previo(previo, clave):
    """Devuelve el dict del dato `clave` guardado antes, o None."""
    try:
        return previo.get("datos", {}).get(clave)
    except Exception:
        return None


def dato(valor, *, unidad=None, fecha=None, variacion=None,
         periodo=None, fuente=None, frecuencia=None):
    """Construye un dato normalizado y consistente."""
    d = {
        "valor": valor,
        "actualizado": ahora_iso(),
        "stale": False,
    }
    if unidad is not None:     d["unidad"] = unidad
    if fecha is not None:      d["fecha"] = fecha
    if variacion is not None:  d["variacion"] = variacion
    if periodo is not None:    d["periodo"] = periodo
    if fuente is not None:     d["fuente"] = fuente
    if frecuencia is not None: d["frecuencia"] = frecuencia
    return d


def conservar(previo, clave):
    """Devuelve el valor anterior marcado como stale, o None si no había."""
    prev = valor_previo(previo, clave)
    if prev is None:
        return None
    prev = dict(prev)
    prev["stale"] = True
    return prev


def primer_numero(texto):
    """Extrae el primer número entero de un texto (ej '508 pb' -> 508)."""
    if not texto:
        return None
    m = re.search(r"\d[\d.\s]*", texto.replace(".", "").replace("\xa0", " "))
    if not m:
        return None
    limpio = re.sub(r"[^\d]", "", m.group(0))
    return int(limpio) if limpio else None


# =============================================================
# RIESGO PAÍS — scraping con FALLBACK EN CADENA
# =============================================================
# Se prueban las fuentes en orden hasta que una devuelva un número
# plausible (100–5000 pb). Devuelve número + variación si se puede.

def _rp_argentinadatos():
    """API JSON. Da valor y, con la serie, calculamos variación."""
    ultimo = get_json("https://api.argentinadatos.com/v1/finanzas/indices/riesgo-pais/ultimo")
    if not ultimo or "valor" not in ultimo:
        return None
    valor = int(round(ultimo["valor"]))
    variacion = None
    fecha = ultimo.get("fecha")
    # Serie completa para variación día a día
    serie = get_json("https://api.argentinadatos.com/v1/finanzas/indices/riesgo-pais")
    if isinstance(serie, list) and len(serie) >= 2:
        try:
            prev = serie[-2]["valor"]
            if prev:
                variacion = round((valor / prev - 1) * 100, 2)
        except Exception:
            pass
    return {"valor": valor, "variacion": variacion, "fecha": fecha,
            "fuente": "argentinadatos.com"}


def _rp_rava():
    """Rava Bursátil — perfil RIESGO PAIS. El dato viene embebido en el HTML
    dentro de un atributo/JSON de Vue (ej '"ultimo":508' o '"cierre":508').
    Probamos varios patrones porque Rava cambia la estructura seguido."""
    html = get_html("https://www.rava.com/perfil/RIESGO%20PAIS")
    if not html:
        return None
    val, variacion = None, None
    # 1) JSON embebido tipo "ultimo":508.0 / "cierre":508
    for campo in ("ultimo", "cierre", "ultimoPrecio", "valor"):
        m = re.search(rf'"{campo}"\s*:\s*"?(\d[\d.,]*)"?', html)
        if m:
            val = primer_numero(m.group(1))
            if val and 100 <= val <= 5000:
                break
            val = None
    # 2) Variación porcentual si aparece
    mv = re.search(r'"variacion"\s*:\s*"?(-?\d[\d.,]*)"?', html)
    if mv:
        try:
            variacion = round(float(mv.group(1).replace(",", ".")), 2)
        except Exception:
            variacion = None
    # 3) Fallback: primer número plausible cerca de "riesgo"
    if val is None:
        m = re.search(r"riesgo[^0-9]{0,60}(\d[\d.]{2,5})", html, re.IGNORECASE)
        cand = primer_numero(m.group(1)) if m else None
        if cand and 100 <= cand <= 5000:
            val = cand
    if val:
        return {"valor": val, "variacion": variacion, "fecha": None, "fuente": "rava.com"}
    return None


def _rp_indicadores_ar():
    """indicadores.ar — trae 'Valor Actual' limpio en el HTML.
    OJO: su 'Variación' es del período seleccionado (default 1 año), NO del día.
    Por eso tomamos SOLO el número y descartamos su variación."""
    html = get_html("https://indicadores.ar/indicadores-economicos/riesgo-pais")
    if not html:
        return None
    val = None
    # 1) JSON embebido por si usa framework JS
    for campo in ("valor", "value", "ultimo", "actual", "valorActual"):
        m = re.search(rf'"{campo}"\s*:\s*"?(\d[\d.,]*)"?', html)
        if m:
            cand = primer_numero(m.group(1))
            if cand and 100 <= cand <= 5000:
                val = cand
                break
    # 2) Texto: número plausible cerca de "Valor Actual"
    if val is None:
        m = re.search(r"valor\s*actual[^0-9]{0,40}(\d[\d.]{2,5})", html, re.IGNORECASE)
        cand = primer_numero(m.group(1)) if m else None
        if cand and 100 <= cand <= 5000:
            val = cand
    if val:
        # variacion=None a propósito: la de esta página es anual, no diaria
        return {"valor": val, "variacion": None, "fecha": None,
                "fuente": "indicadores.ar"}
    return None


def _rp_ambito():
    """Ámbito publica el riesgo país en su sección de mercados."""
    html = get_html("https://www.ambito.com/contenidos/riesgo-pais.html")
    if not html:
        return None
    m = re.search(r"(\d[\d.]{2,5})\s*(?:pb|puntos)", html, re.IGNORECASE)
    val = primer_numero(m.group(1)) if m else None
    if val and 100 <= val <= 5000:
        return {"valor": val, "variacion": None, "fecha": None, "fuente": "ambito.com"}
    return None


# Orden de preferencia. La primera que devuelva número plausible gana.
# Rava PRIMERO: trae el valor INTRADÍA real (actualizado durante la rueda).
# argentinadatos da el cierre del día anterior, por eso quedaba atrasado.
FUENTES_RIESGO = [
    ("rava", _rp_rava),
    ("ambito", _rp_ambito),
    ("indicadores.ar", _rp_indicadores_ar),
    ("argentinadatos", _rp_argentinadatos),
]


def _leer_manual():
    """Lee riesgo_manual.json (lo que carga Checho en el panel69).
    Devuelve el dict o None. No falla nunca."""
    ruta = os.path.join(DIR_DATA, "riesgo_manual.json")
    if not os.path.exists(ruta):
        return None
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _manual_fresco(manual, horas=30):
    """True si el dato manual fue cargado hace menos de `horas`."""
    if not manual or not manual.get("cargado_en"):
        return False
    try:
        t = datetime.fromisoformat(manual["cargado_en"].replace("Z", "+00:00"))
        edad = (datetime.now(timezone.utc) - t).total_seconds() / 3600
        return edad < horas
    except Exception:
        return False


def obtener_riesgo_pais(previo):
    # 1) PRIORIDAD: dato manual del panel (lo que Checho vio en Rava y cargó).
    manual = _leer_manual()
    if manual and manual.get("riesgo_pais") and _manual_fresco(manual):
        v = manual["riesgo_pais"]
        print(f"· Riesgo País: MANUAL {v} pb (cargado en panel)")
        return dato(v, unidad="pb", fuente="carga manual",
                    fecha=manual.get("cargado_en"), frecuencia="manual")

    # 2) Si no hay manual fresco, cadena automática (Rava primero)
    print("· Riesgo País (fallback en cadena)")
    for nombre, fn in FUENTES_RIESGO:
        try:
            res = fn()
        except Exception as e:
            print(f"   ⚠  {nombre} excepción: {str(e)[:60]}")
            res = None
        if res and res.get("valor"):
            print(f"   ✓ {res['valor']} pb vía {res['fuente']}"
                  + (f" ({res['variacion']:+.2f}%)" if res.get('variacion') is not None else ""))
            return dato(
                res["valor"], unidad="pb",
                variacion=res.get("variacion"),
                fecha=res.get("fecha"),
                fuente=res["fuente"],
                frecuencia="intradia",
            )
    print("   ✗ Ninguna fuente respondió. Conservo último valor bueno.")
    return conservar(previo, "riesgo_pais")


def obtener_mulc(previo):
    """Lee el dato de intervención del BCRA (compró/vendió) cargado en el panel.
    Solo se muestra si es fresco; si no, conserva el anterior."""
    manual = _leer_manual()
    if manual and manual.get("mulc") and _manual_fresco(manual):
        m = manual["mulc"]
        print(f"· MULC: BCRA {m.get('operacion')} {m.get('monto')} {m.get('unidad','MM USD')}")
        return dato(
            {"operacion": m.get("operacion"), "monto": m.get("monto")},
            unidad=m.get("unidad", "MM USD"),
            fecha=manual.get("cargado_en"),
            fuente="BCRA (carga manual)",
            frecuencia="diaria",
        )
    return conservar(previo, "mulc")


# =============================================================
# DÓLARES (dolarapi)
# =============================================================

def obtener_dolares(previo):
    print("· Dólares (dolarapi.com)")
    mapa = {
        "dolar_oficial": "https://dolarapi.com/v1/dolares/oficial",
        "dolar_mep":     "https://dolarapi.com/v1/dolares/bolsa",
        "dolar_ccl":     "https://dolarapi.com/v1/dolares/contadoconliqui",
        "dolar_blue":    "https://dolarapi.com/v1/dolares/blue",
        "dolar_mayorista": "https://dolarapi.com/v1/dolares/mayorista",
        "dolar_tarjeta": "https://dolarapi.com/v1/dolares/tarjeta",
        "dolar_cripto":  "https://dolarapi.com/v1/dolares/cripto",
    }
    out = {}
    for clave, url in mapa.items():
        j = get_json(url)
        if j and (j.get("venta") is not None):
            out[clave] = dato(
                {"compra": j.get("compra"), "venta": j.get("venta")},
                unidad="ARS",
                variacion=j.get("variacion"),
                fuente="dolarapi.com",
                frecuencia="intradia",
            )
        else:
            cons = conservar(previo, clave)
            if cons:
                out[clave] = cons
    print(f"   ✓ {len([k for k in out if not out[k].get('stale')])} dólares vivos")

    # Brecha MEP / Oficial (derivada)
    try:
        mep = out.get("dolar_mep", {}).get("valor", {}).get("venta")
        ofi = out.get("dolar_oficial", {}).get("valor", {}).get("venta")
        if mep and ofi:
            brecha = round((mep / ofi - 1) * 100, 1)
            out["brecha_mep"] = dato(brecha, unidad="%", frecuencia="intradia",
                                     fuente="cálculo PPA")
    except Exception:
        pass
    return out


# =============================================================
# MERVAL
# =============================================================

def obtener_merval(previo):
    print("· Merval")
    j = get_json("https://api.argentinadatos.com/v1/finanzas/indices/merval/ultimo")
    if j and j.get("valor") is not None:
        print(f"   ✓ {j['valor']}")
        return dato(round(j["valor"]), unidad="puntos",
                    variacion=j.get("variacion"),
                    fuente="argentinadatos.com", frecuencia="intradia")
    print("   ✗ sin dato, conservo previo")
    return conservar(previo, "merval")


# =============================================================
# SERIES datos.gob.ar (reservas + mensuales/trimestrales)
# =============================================================
# Cada serie: (clave, id_serie, unidad, frecuencia, tipo)
#   tipo "nivel"   -> muestro el valor tal cual
#   tipo "var_men" -> muestro la variación % mensual (IPC: nivel general)
SERIES = [
    # Reservas YA NO acá: vienen del BCRA v4 diario (ver obtener_bcra)
    # IPC nacional nivel general (verificado OK)
    ("ipc_mensual",   "101.1_I2NG_2016_M_22",      "%",      "mensual", "var_men"),
    # IPC núcleo (verificado OK) — como variación mensual
    ("ipc_nucleo",    "103.1_I2N_2016_M_15",       "%",      "mensual", "var_men"),
    # EMAE desestacionalizado (verificado OK)
    ("emae",          "143.3_NO_PR_2004_A_21",     "puntos", "mensual", "nivel"),
    # TCRM diario (verificado 30/05: dato fresco, mejor que el anterior)
    ("tcrm",          "168.1_T_CAMBIOR_D_0_0_26",  "índice", "diaria",  "nivel"),
    # PENDIENTES (IDs muertos, a reemplazar tras 2ª verificación):
    # exportaciones, importaciones, saldo comercial, desocupación
]


def obtener_series(previo):
    print("· Series datos.gob.ar")
    out = {}
    for clave, serie_id, unidad, frec, tipo in SERIES:
        url = (f"https://apis.datos.gob.ar/series/api/series/"
               f"?ids={serie_id}&last=14&format=json")
        j = get_json(url)
        valor, fecha, variacion = None, None, None
        if j and j.get("data"):
            data = [row for row in j["data"] if row[1] is not None]
            if data:
                fecha = data[-1][0]
                if tipo == "var_men" and len(data) >= 2:
                    ult, ant = data[-1][1], data[-2][1]
                    if ant:
                        valor = round((ult / ant - 1) * 100, 1)
                else:
                    valor = round(data[-1][1], 2)
        if valor is not None:
            out[clave] = dato(valor, unidad=unidad, fecha=fecha,
                              periodo=(fecha[:7] if fecha else None),
                              fuente="datos.gob.ar", frecuencia=frec)
            print(f"   ✓ {clave}: {valor} {unidad} ({fecha})")
        else:
            cons = conservar(previo, clave)
            if cons:
                out[clave] = cons
            print(f"   ⚠  {clave}: sin dato nuevo"
                  + (" (conservo previo)" if cons else " (sin previo)"))

    # Saldo comercial: se reactivará cuando confirmemos IDs de exp/imp
    return out


# =============================================================
# BANDA CAMBIARIA — cálculo propio + posición del dólar
# =============================================================
# Esquema vigente desde ene-2026: piso y techo se deslizan a diario
# hasta completar, al último día hábil del mes, el % del IPC con
# rezago T-2 (el último dato publicado). El techo SUBE y el piso BAJA.
#
# Anclamos en valores oficiales conocidos y proyectamos. Estos anclas
# se actualizan cuando cambia el mes; mientras tanto el cálculo diario
# mantiene el valor razonable.
BANDA_ANCLA = {
    # fin de mayo 2026 (última rueda): valores oficiales publicados
    "fecha": "2026-05-31",
    "piso": 790.19,    # arranque junio (tras IPC abril 2.6%)
    "techo": 1762.64,
    # ritmo mensual aplicado en junio = IPC de abril (T-2) = 2.6%
    "ipc_mensual_pct": 2.6,
}


# Variables BCRA v4 que consultamos
# IDs verificados contra el Informe Monetario Diario (mayo 2026)
# Fuente: api.bcra.gob.ar/estadisticas/v4.0/monetarias/{idVariable}
#
#   ID   1 = Reservas internacionales (diaria, millones USD)
#   ID   6 = BADLAR bancos privados (diaria, % TNA)
#      NOTA: ID 6 = BADLAR privada. La "tasa de política monetaria" dejó
#      de existir como tal desde jul-2025 (pases a 0). BADLAR es la
#      referencia real del mercado para plazo fijo hoy.
#   ID  15 = Base monetaria (diaria, millones de pesos)
#   ID  17 = M2 privado transaccional (diaria, millones de pesos)
#      = Billetes+monedas públicos + cuentas corrientes y cajas de ahorro
#        del sector privado en pesos (excluyendo vista remunerada PJ)
#   ID  27 = BAIBAR / Call entre bancos privados hasta 15 días (diaria, % TNA)
#   ID   7 = Circulación monetaria (diaria, millones de pesos)
#
# Los IDs se verifican con GET /estadisticas/v4.0/monetarias (lista completa).
# Si un ID devuelve 0 o None en producción, revisar la lista y corregir.
_BCRA_VARS = [
    # clave interna     ID   unidad     descripción visible
    ("reservas",         1,  "MM USD",  "Reservas BCRA (millones USD)"),
    ("badlar",           6,  "% TNA",   "BADLAR bancos privados"),
    ("base_monetaria",  15,  "MM $",    "Base monetaria (millones $)"),
    ("m2_privado",      17,  "MM $",    "M2 privado transaccional (millones $)"),
    ("call_baibar",     27,  "% TNA",   "BAIBAR call bancos privados"),
    ("circulacion",      7,  "MM $",    "Circulación monetaria (millones $)"),
    # UVA: Unidad de Valor Adquisitivo (base 31/3/2016=14.05)
    # Del IMD 22-may: 1956.47 — clave para hipotecarios y contratos
    ("uva",             29,  "índice",  "UVA (base 31/3/2016=14.05)"),
]

def _bcra_get(id_variable):
    """Llama a BCRA v4 para una variable. Reintenta sin SSL si falla."""
    import urllib3
    url = f"https://api.bcra.gob.ar/estadisticas/v4.0/monetarias/{id_variable}?limit=2"
    j = get_json(url)
    if j is None:
        try:
            urllib3.disable_warnings()
            r = requests.get(url, headers=HDRS, timeout=12, verify=False)
            r.raise_for_status()
            j = r.json()
        except Exception:
            return None
    return j

def obtener_bcra(previo):
    """API oficial BCRA v4. Trae reservas, tasa política y base monetaria."""
    print("· BCRA v4 (reservas + tasa + base monetaria)")
    out = {}
    for clave, id_var, unidad, desc in _BCRA_VARS:
        j = _bcra_get(id_var)
        if not j:
            cons = conservar(previo, clave)
            if cons:
                out[clave] = cons
            print(f"   ⚠  {clave}: BCRA no respondió (conservo previo)")
            continue
        try:
            detalle = j["results"][0]["detalle"]
            ultimo = detalle[0]
            valor = round(float(ultimo["valor"]), 2 if id_var == 6 else 0)
            fecha = ultimo.get("fecha")
            variacion = None
            if len(detalle) > 1:
                prev_v = float(detalle[1]["valor"])
                if prev_v:
                    variacion = round((valor - prev_v) / prev_v * 100, 2)
            out[clave] = dato(valor, unidad=unidad, fecha=fecha, variacion=variacion,
                              fuente="BCRA API v4", frecuencia="diaria")
            print(f"   ✓ {clave}: {valor} {unidad} ({fecha})")
        except Exception as e:
            cons = conservar(previo, clave)
            if cons:
                out[clave] = cons
            print(f"   ⚠  {clave}: formato inesperado ({str(e)[:50]})")
    return out


def obtener_banda(previo, datos_actuales):
    """Calcula piso/techo de la banda para hoy y la posición del dólar
    mayorista (o oficial) dentro de ella. Devuelve un dato compuesto."""
    print("· Banda cambiaria (cálculo)")
    try:
        from datetime import date
        ancla = BANDA_ANCLA
        f_ancla = datetime.strptime(ancla["fecha"], "%Y-%m-%d").date()
        hoy = datetime.now(TZ_AR).date()
        dias = (hoy - f_ancla).days
        # tasa diaria equivalente al % mensual (30 días)
        tasa_mensual = ancla["ipc_mensual_pct"] / 100.0
        tasa_diaria = (1 + tasa_mensual) ** (1 / 30) - 1
        # techo sube, piso baja
        techo = ancla["techo"] * ((1 + tasa_diaria) ** max(dias, 0))
        piso = ancla["piso"] * ((1 - tasa_diaria) ** max(dias, 0))

        # Dólar de referencia para la posición: mayorista; si no, oficial
        ref = None
        for clave in ("dolar_mayorista", "dolar_oficial"):
            item = datos_actuales.get(clave)
            if item and item.get("valor") is not None:
                ref = (item["valor"]["venta"] if isinstance(item["valor"], dict)
                       else item["valor"])
                break

        posicion = None
        if ref and techo > piso:
            posicion = round((ref - piso) / (techo - piso) * 100, 1)
            posicion = max(0, min(100, posicion))

        print(f"   ✓ piso ${piso:.0f} · techo ${techo:.0f}"
              + (f" · dólar al {posicion}%" if posicion is not None else ""))
        return dato(
            {"piso": round(piso), "techo": round(techo),
             "dolar": round(ref) if ref else None, "posicion": posicion},
            fuente="cálculo PPA (esquema BCRA)",
            frecuencia="diaria",
        )
    except Exception as e:
        print(f"   ⚠  no se pudo calcular: {str(e)[:60]}")
        return conservar(previo, "banda")


# =============================================================
# PROCESO PRINCIPAL
# =============================================================

def main():
    args = sys.argv[1:]
    solo_mercado = "--solo-mercado" in args
    solo_mensual = "--solo-mensual" in args
    hacer_mercado = not solo_mensual
    hacer_mensual = not solo_mercado

    print(f"[PPA Datos] Inicio: {ahora_iso()}")
    print(f"[PPA Datos] Modo: "
          + ("solo mercado" if solo_mercado else "solo mensual" if solo_mensual else "completo"))
    print()

    os.makedirs(DIR_DATA, exist_ok=True)
    previo = cargar_previo()
    datos = dict(previo.get("datos", {}))  # arranco del previo y voy pisando

    if hacer_mercado:
        datos.update(obtener_dolares(previo))
        datos["merval"] = obtener_merval(previo) or datos.get("merval")
        datos["riesgo_pais"] = obtener_riesgo_pais(previo) or datos.get("riesgo_pais")
        datos["mulc"] = obtener_mulc(previo) or datos.get("mulc")
        bcra = obtener_bcra(previo)
        for k, v in bcra.items():
            datos[k] = v or datos.get(k)
        datos["banda"] = obtener_banda(previo, datos) or datos.get("banda")

    if hacer_mensual:
        datos.update(obtener_series(previo))

    # Limpio claves que quedaron en None
    datos = {k: v for k, v in datos.items() if v is not None}

    salida = {
        "generado_en": ahora_iso(),
        "generado_ar": datetime.now(TZ_AR).strftime("%d/%m/%Y %H:%M"),
        "datos": datos,
    }
    with open(JSON_DATOS, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)

    vivos = len([k for k, v in datos.items() if not v.get("stale")])
    print()
    print(f"[PPA Datos] {len(datos)} datos en total · {vivos} frescos · "
          f"{len(datos) - vivos} conservados")
    print(f"[PPA Datos] Guardado: {JSON_DATOS}")
    print(f"[PPA Datos] Fin: {ahora_iso()}")


if __name__ == "__main__":
    main()
