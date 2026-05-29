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
    # ====== 2ª RONDA: reemplazos para los que fallaron ======
    # --- Comercio exterior (ICA) ---
    ("Exportaciones FOB alt 1",   "74.3_IEXNN_2004_M_27", "millones USD"),
    ("Exportaciones FOB alt 2",   "37.2_E_0_M_30", "millones USD"),
    ("Exportaciones total mensual","151.1_EXPORTAC_0_0_22", "millones USD"),
    ("Importaciones CIF alt 1",   "74.3_IIMNN_2004_M_32", "millones USD"),
    ("Importaciones alt 2",       "37.2_I_0_M_32", "millones USD"),
    ("Balanza comercial alt 1",   "151.1_SALDO_0_0_18", "millones USD"),
    ("Balanza comercial alt 2",   "74.3_ISNN_2004_M_15", "millones USD"),
    # --- Empleo (EPH trimestral) ---
    ("Desocupación alt 1",        "45.2_ECTDT_0_T_42", "%"),
    ("Desocupación alt 2",        "45.2_TD_0_T_18", "%"),
    ("Desocupación alt 3",        "192.1_TASDESOCUPACION_T_31", "%"),
    ("Tasa empleo alt",           "45.2_TE_0_T_15", "%"),
    ("Tasa actividad alt",        "45.2_TA_0_T_12", "%"),
    # --- Reservas BCRA (confirmar si hay diaria mejor que la mensual RID) ---
    ("Reservas intl (confirmada)","92.1_RID_0_0_32", "millones USD"),
    ("Base monetaria",            "175.1_BM_0_0_15", "millones $"),
    ("Tasa política monetaria",   "160.1_TPMBADLARABE_0_0_10", "% TNA"),

    # ====== 1ª RONDA (confirmados OK, dejo para re-chequear) ======
    ("IPC nacional nivel gral",   "101.1_I2NG_2016_M_22", "índice"),
    ("IPC núcleo",                "103.1_I2N_2016_M_15", "índice"),
    ("EMAE desest.",              "143.3_NO_PR_2004_A_21", "índice"),
    ("TCRM",                      "116.4_TCRM_0_D_36", "índice"),
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
