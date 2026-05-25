"""
PPA — exportar_config.py
Exporta la configuración de fuentes (que está en config.py) como JSON,
para que el panel admin la pueda leer desde el navegador.

Lo corre el workflow de GitHub Actions después del fetcher.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import FUENTES, CATEGORIAS, DIR_DATA

OUT = os.path.join(DIR_DATA, "fuentes_config.json")


def main():
    salida = {
        "categorias": CATEGORIAS,
        "fuentes": FUENTES,
    }
    os.makedirs(DIR_DATA, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(salida, f, ensure_ascii=False, indent=2)
    print(f"[exportar_config] Guardado: {OUT} ({len(FUENTES)} fuentes)")


if __name__ == "__main__":
    main()
