"""
PPA — verificar_series.py
Herramienta de diagnóstico: prueba una lista de IDs candidatos de series
de datos.gob.ar y reporta cuáles devuelven dato fresco y cuáles no.

NO se usa en producción. Es para "luchar los datos": correlo una vez,
mirá qué IDs ganan, y esos van al motor (datos_economicos.py).

Cómo se corre (en tu compu o en el Action, donde haya internet libre):
    python scripts/verificar_series.py
    python scripts/verificar_series.py --buscar "tipo de cambio real multilateral"
    python scripts/verificar_series.py --ids 168.1_T_CAMBIOR_D_0_0_26

`--buscar` le pregunta a datos.gob.ar qué series existen para un texto y
prueba cada una. Es la salida cuando un ID deja de andar: la lista de
CANDIDATOS es de IDs que alguien tipeó alguna vez, y cuando el organismo
retira una serie el ID viejo devuelve 400 sin decir cuál lo reemplaza.
"""

import sys
import requests
from datetime import datetime

HDRS = {"User-Agent": "Mozilla/5.0 (compatible; PPA-Bot/1.0)"}

# Candidatos a probar. Varios por indicador: el verificador dice cuál anda.
# Formato: (etiqueta, id_serie, que_esperamos)
CANDIDATOS = [
    # ====== 4ª RONDA: lista nueva a verificar (la que sonaba muy completa) ======
    # Macro / IPC
    ("IPC mensual (nueva)",        "148.7_INIVELGERS_0_0_17", "% mensual"),
    ("IPC interanual (nueva)",     "148.7_INIVELGERA_0_0_21", "% i.a."),
    ("IPC acumulado (nueva)",      "148.7_INIVELGERC_0_0_25", "% acum"),
    # Sector externo / BCRA
    ("Reservas brutas BCRA",       "2.1_REP_0_0_24", "MM USD"),
    ("TCRM diario (nueva)",        "168.1_T_CAMBIOR_D_0_0_26", "índice"),
    ("Exportaciones mensual",      "11.3_IEM_0_0_19", "MM USD"),
    ("Importaciones mensual",      "11.3_IIM_0_0_19", "MM USD"),
    ("Saldo comercial",            "11.3_BALANZAM_0_0_22", "MM USD"),
    # Empleo / canastas / salarios
    ("SMVM",                       "431.1_SMVM_C_0_0_36", "$"),
    ("CBT GBA",                    "153.1_CBT_REG_GBA_0_0_20", "$"),
    ("CBA GBA",                    "153.1_CBA_REG_GBA_0_0_20", "$"),
    ("Desocupación (nueva)",       "431.1_TD_U_0_0_18", "%"),
    ("Tasa empleo (nueva)",        "431.1_TE_U_0_0_14", "%"),
    # Fiscal
    ("Recaudación total",          "172.3_RECAUDACIO_0_V_34", "M $"),
    ("IVA",                        "172.3_IVA_0_V_11", "M $"),
    ("Ganancias",                  "172.3_GANANCIAS_0_V_27", "M $"),
    ("Retenciones (DEX)",          "172.3_DERECHOS_D_0_V_31", "M $"),
    ("Resultado primario SPN",     "365.1_RP_SPN_0_M_19", "M $"),
    ("Resultado financiero SPN",   "365.1_RF_SPN_0_M_22", "M $"),
    # ====== CONFIRMADOS OK (re-chequeo) ======
    ("IPC nacional (confirmado)",  "101.1_I2NG_2016_M_22", "índice"),
    ("EMAE (confirmado)",          "143.3_NO_PR_2004_A_21", "índice"),
    ("Reservas (confirmado)",      "92.1_RID_0_0_32", "MM USD"),
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


def buscar(texto, limite=10):
    """Le pregunta a datos.gob.ar qué series existen para un texto.

    Devuelve [(titulo, id, unidades, frecuencia, desde, hasta)]. El buscador
    es el que sabe qué IDs están vigentes; probarlos después es lo que
    distingue una serie viva de una que quedó publicada pero congelada.
    """
    url = ("https://apis.datos.gob.ar/series/api/search/"
           f"?q={requests.utils.quote(texto)}&limit={limite}")
    try:
        r = requests.get(url, headers=HDRS, timeout=20)
        if r.status_code != 200:
            print(f"   el buscador respondió HTTP {r.status_code}")
            return []
        filas = r.json().get("data", [])
    except Exception as e:
        print(f"   no pude consultar el buscador: {str(e)[:60]}")
        return []

    salida = []
    for f in filas:
        salida.append((
            _primero(f, ("field_title", "title", "field_description",
                         "description")) or "(sin título)",
            _id_de(f),
            _primero(f, ("field_units", "units")),
            _primero(f, ("field_frequency", "frequency",
                         "distribution_index_frequency")),
            _primero(f, ("serie_tiempo_indice_inicio", "time_index_start")),
            _primero(f, ("serie_tiempo_indice_final", "time_index_end")),
        ))

    # Si no se pudo sacar ningún ID, el problema es que la API cambió los
    # nombres de los campos. Mostrarlos evita otra ronda a ciegas: es el
    # mismo error que tener un ID viejo hardcodeado, un nivel más arriba.
    if filas and not any(s[1] for s in salida):
        print("   no reconocí el campo del ID. La API devolvió estas claves:")
        for k in sorted(filas[0].keys()):
            print(f"     {k} = {str(filas[0][k])[:60]}")
    return salida


def _primero(fila, claves):
    """Primer valor no vacío entre varios nombres posibles de campo."""
    for k in claves:
        v = fila.get(k)
        if v:
            return str(v)
    return ""


def _id_de(fila):
    """El ID de la serie, sin depender de cómo se llame el campo hoy.

    La API ya renombró campos antes. Se prueban los nombres conocidos y, si
    ninguno está, cualquier clave que termine en "id" cuyo valor tenga la
    forma de un ID de serie (`168.1_T_CAMBIOR_D_0_0_26`).
    """
    for k in ("field_id", "serie_id", "id"):
        if fila.get(k):
            return str(fila[k])
    for k, v in fila.items():
        if k.lower().endswith("id") and isinstance(v, str) and "_" in v:
            return v
    return ""


def modo_buscar(texto):
    """Busca por texto, prueba cada candidato y ordena por dato más reciente."""
    print("=" * 72)
    print(f"Buscando series para: {texto!r}")
    print("=" * 72)
    print()

    encontradas = buscar(texto)
    if not encontradas:
        print("Sin resultados.")
        return

    vivas = []
    for titulo, sid, unidades, frecuencia, desde, hasta in encontradas:
        if not sid:
            continue
        estado, valor, fecha = probar(sid)
        icono = "✓" if estado == "OK" else "✗"
        print(f"{icono} {titulo[:60]}")
        print(f"     {sid}  [{unidades} · {frecuencia} · {desde}→{hasta}]")
        if estado == "OK":
            print(f"     -> último: {valor} ({fecha})")
            vivas.append((fecha, sid, titulo, valor, frecuencia))
        else:
            print(f"     -> {estado}")
        print()

    print("=" * 72)
    print(f"RESUMEN: {len(vivas)} de {len(encontradas)} responden con dato")
    print("=" * 72)
    # Más reciente primero: cuando hay varias vigentes, la que trae el dato de
    # ayer es la que sirve, no la que cortó hace dos años.
    for fecha, sid, titulo, valor, frecuencia in sorted(vivas, reverse=True):
        print(f"  {fecha}  {sid:32s} {valor:>14}  {frecuencia:10s} {titulo[:40]}")


def modo_ids(ids):
    """Prueba IDs puntuales pasados por línea de comandos."""
    print("=" * 72)
    print(f"Probando {len(ids)} ID(s)")
    print("=" * 72)
    print()
    for sid in ids:
        estado, valor, fecha = probar(sid)
        icono = "✓" if estado == "OK" else "✗"
        print(f"{icono} {sid}")
        print(f"     -> {valor} ({fecha})" if estado == "OK" else f"     -> {estado}")
        print()


def probar_bcra():
    """Prueba la API oficial del BCRA (reservas, monetarias, tasas).
    Esta API usa HTTPS y a veces requiere ignorar verificación SSL."""
    print()
    print("=" * 72)
    print("API BCRA — https://api.bcra.gob.ar")
    print("=" * 72)
    endpoints = [
        ("Variables monetarias", "https://api.bcra.gob.ar/estadisticas/v3.0/Monetarias"),
        ("Reservas",             "https://api.bcra.gob.ar/estadisticas/v3.0/Reservas?limit=5"),
        ("Tasas",                "https://api.bcra.gob.ar/estadisticas/v3.0/Tasas"),
    ]
    for nombre, url in endpoints:
        try:
            # El BCRA a veces tiene cadena SSL incompleta; probamos con verify
            r = requests.get(url, headers=HDRS, timeout=15, verify=True)
            estado = "OK " + str(r.status_code)
            muestra = r.text[:120].replace("\n", " ")
            print(f"✓ {nombre:24s} -> {estado}")
            print(f"     {muestra}")
        except requests.exceptions.SSLError:
            # Reintento sin verificar SSL (el BCRA es conocido por esto)
            try:
                import urllib3
                urllib3.disable_warnings()
                r = requests.get(url, headers=HDRS, timeout=15, verify=False)
                print(f"⚠  {nombre:24s} -> OK {r.status_code} (requiere verify=False por SSL)")
                print(f"     {r.text[:120]}")
            except Exception as e2:
                print(f"✗ {nombre:24s} -> {str(e2)[:60]}")
        except Exception as e:
            print(f"✗ {nombre:24s} -> {str(e)[:60]}")
        print()


def main():
    args = sys.argv[1:]
    if args and args[0] == "--buscar":
        texto = " ".join(args[1:]).strip()
        if not texto:
            print('Falta el texto: --buscar "tipo de cambio real multilateral"')
            sys.exit(1)
        modo_buscar(texto)
        return
    if args and args[0] == "--ids":
        ids = [i for a in args[1:] for i in a.split(",") if i]
        if not ids:
            print("Falta al menos un ID: --ids 168.1_T_CAMBIOR_D_0_0_26")
            sys.exit(1)
        modo_ids(ids)
        return

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

    # Probar también la API del BCRA
    probar_bcra()


if __name__ == "__main__":
    main()
