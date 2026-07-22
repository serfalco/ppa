"""
PPA — descubrir_bcra.py
Herramienta de diagnóstico (como verificar_series.py, NO corre en producción).

Lista TODAS las variables de la API BCRA v4 (/estadisticas/v4.0/monetarias)
y filtra por palabra clave, para encontrar IDs nuevos — en particular el de
las COMPRAS NETAS DE DIVISAS / intervención en el MULC, que hoy se carga
a mano desde el panel (Fase A: automatizar MULC).

Cómo se corre (donde haya internet libre — tu compu o un Action):
    python scripts/descubrir_bcra.py                # lista todo
    python scripts/descubrir_bcra.py mulc divisas   # filtra por palabras

Cuando encuentres el ID correcto:
  1. Verificá que el valor coincida con el Informe Monetario Diario.
  2. En datos_economicos.py, seteá  MULC_BCRA_ID = <id>  (arriba de todo).
  3. Desde ese momento el MULC sale de la API y el panel queda de respaldo.
"""

import sys
import requests

HDRS = {"User-Agent": "Mozilla/5.0 (compatible; PPA-Bot/1.0)"}
URL = "https://api.bcra.gob.ar/estadisticas/v4.0/monetarias"


def main():
    filtros = [p.lower() for p in sys.argv[1:]]
    try:
        r = requests.get(URL, headers=HDRS, timeout=20)
        r.raise_for_status()
        data = r.json()
    except Exception:
        try:
            import urllib3
            urllib3.disable_warnings()
            r = requests.get(URL, headers=HDRS, timeout=20, verify=False)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            print(f"✗ No pude consultar la API BCRA: {e}")
            sys.exit(1)

    resultados = data.get("results", data if isinstance(data, list) else [])
    encontradas = 0
    for var in resultados:
        idv = var.get("idVariable")
        desc = (var.get("descripcion") or "").strip()
        if filtros and not any(f in desc.lower() for f in filtros):
            continue
        encontradas += 1
        print(f"  ID {idv:>4} · {desc}")

    print(f"\n{encontradas} variables"
          + (f" que contienen {filtros}" if filtros else " en total"))
    if filtros and encontradas == 0:
        print("Probá con otras palabras: 'compra', 'divisas', 'cambio', 'mulc'")


if __name__ == "__main__":
    main()
