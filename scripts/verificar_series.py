"""
PPA — verificar_series.py
Herramienta de diagnóstico: prueba una lista de IDs candidatos de series
de datos.gob.ar y reporta cuáles devuelven dato fresco y cuáles no.

NO se usa en producción. Es para "luchar los datos": correlo una vez,
mirá qué IDs ganan, y esos van al motor (datos_economicos.py).

Cómo se corre (en tu compu o en el Action, donde haya internet libre):
    python scripts/verificar_series.py
"""

import requests
from datetime import datetime

HDRS = {"User-Agent": "Mozilla/5.0 (compatible; PPA-Bot/1.0)"}

# Candidatos a probar. Varios por indicador: el verificador dice cuál anda.
# Formato: (etiqueta, id_serie, que_esperamos)
CANDIDATOS = [
    # --- IPC ---
    ("IPC nacional nivel gral (nuevo)", "101.1_I2NG_2016_M_22", "índice mensual"),
    ("IPC GBA nivel gral (viejo v3)",   "148.3_INIVELGBA_DICI_M_26", "índice mensual"),
    ("IPC variación mensual directa",   "101.1_I2NG_2016_M_19", "% mensual"),
    ("IPC núcleo",                       "103.1_I2N_2016_M_15", "índice"),
    # --- EMAE ---
    ("EMAE desestacionalizado (v3)",    "143.3_NO_PR_2004_A_21", "índice"),
    ("EMAE serie original",             "143.3_NO_PR_2004_A_28", "índice"),
    # --- Reservas ---
    ("Reservas BCRA (v3)",              "174.1_T_1.0_0_100", "millones USD"),
    ("Reservas internacionales",        "92.1_RID_0_0_32", "millones USD"),
    # --- Comercio exterior ---
    ("Exportaciones FOB (v3)",          "37.3_EXPFOBNM_0_M_22", "millones USD"),
    ("Importaciones CIF (v3)",          "37.3_IMPCIFSM_0_M_23", "millones USD"),
    ("Balanza comercial saldo",         "173.2_BCSGYP_0_M_30", "millones USD"),
    # --- TCRM ---
    ("TCRM (v3)",                        "116.4_TCRM_0_D_36", "índice"),
    # --- Empleo (EPH trimestral) ---
    ("Desocupación (v3)",               "41.1_DEOCT_TOTAL_0_T_26", "%"),
    ("Tasa empleo (v3)",                "41.1_TEOCT_TOTAL_0_T_26", "%"),
    ("Tasa actividad (v3)",             "41.1_TAOCT_TOTAL_0_T_26", "%"),
    ("Desocupación alt",                "168.1_TD_0_M_24", "%"),
    # --- Salarios ---
    ("Índice salarios privado (v3)",    "148.3_ICTOTAL_DICI_M_16", "índice"),
    # --- Fiscal (las que nunca anduvieron) ---
    ("Recaudación tributaria total",    "168.1_T_RECAUDAC_0_0_38", "millones $"),
    ("Resultado primario SPN",          "168.1_T_RESULTADOP_0_0_25", "millones $"),
]


def probar(serie_id):
    url = (f"https://apis.datos.gob.ar/series/api/series/"
           f"?ids={serie_id}&last=2&format=json")
    try:
        r = requests.get(url, headers=HDRS, timeout=15)
        if r.status_code != 200:
            return ("HTTP " + str(r.status_code), None, None)
        j = r.json()
        data = j.get("data", [])
        data = [row for row in data if row[1] is not None]
        if not data:
            return ("sin datos", None, None)
        ultimo = data[-1]
        return ("OK", ultimo[1], ultimo[0])
    except Exception as e:
        return ("ERROR: " + str(e)[:40], None, None)


def main():
    print("=" * 72)
    print("PPA — Verificador de IDs de series datos.gob.ar")
    print("Fecha:", datetime.now().strftime("%Y-%m-%d %H:%M"))
    print("=" * 72)
    print()
    ganadores = []
    for etiqueta, serie_id, esperado in CANDIDATOS:
        estado, valor, fecha = probar(serie_id)
        icono = "✓" if estado == "OK" else "✗"
        print(f"{icono} {etiqueta:38s} {serie_id}")
        if estado == "OK":
            print(f"     -> {valor}  ({fecha})  [{esperado}]")
            ganadores.append((etiqueta, serie_id, valor, fecha))
        else:
            print(f"     -> {estado}")
        print()

    print("=" * 72)
    print(f"RESUMEN: {len(ganadores)}/{len(CANDIDATOS)} IDs responden con dato")
    print("=" * 72)
    for etiqueta, sid, val, fecha in ganadores:
        print(f"  ✓ {etiqueta:38s} = {val} ({fecha})")
    print()
    print("Copiá los IDs ganadores al diccionario SERIES de datos_economicos.py")


if __name__ == "__main__":
    main()
