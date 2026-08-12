"""
PPA — probar_canario.py
Prueba el canario contra casos armados a mano.

Por qué: el canario es lo que avisa cuando una fuente cambia de contenido sin
cambiar de estado. Si el canario tiene un bug, no se nota nunca —igual que
las alertas del repo, que estuvieron muertas meses porque les faltaba una
etiqueta—. Y hay un modo de falla peor que no tenerlo: uno que cante siempre.
Un canario que grita todos los días se ignora a la semana.

Por eso el primer caso es el que más importa: con datos sanos tiene que
callarse. Los demás reproducen los desastres reales que el proyecto ya vivió.

Cómo se corre:
    python scripts/probar_canario.py
"""

import copy
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import canario

AHORA = datetime(2026, 8, 12, 20, 0, tzinfo=timezone.utc)


def _iso(dias):
    return (AHORA - timedelta(days=dias)).isoformat()


def datos_sanos():
    """Una foto verosímil de datos.json con todo en orden."""
    def d(valor, unidad, frec, dias=1, **extra):
        base = {"valor": valor, "unidad": unidad, "frecuencia": frec,
                "actualizado": _iso(0), "stale": False}
        if frec != "intradia":
            base["fecha"] = _iso(dias)
        base.update(extra)
        return base

    return {"datos": {
        "dolar_oficial":   d({"compra": 1465, "venta": 1515}, "ARS", "intradia"),
        "dolar_blue":      d({"compra": 1520, "venta": 1540}, "ARS", "intradia"),
        "dolar_mep":       d({"compra": 1521, "venta": 1529}, "ARS", "intradia"),
        "dolar_mayorista": d({"compra": 1482, "venta": 1491}, "ARS", "intradia"),
        "riesgo_pais":     d(465, "pb", "intradia"),
        "reservas":        d(49564.0, "MM USD", "diaria", 2),
        "merval":          d(2999524, "puntos", "diaria", 0),
        "tcrm":            d(85.41, "índice", "diaria", 1),
        "badlar":          d(25.0, "% TNA", "diaria", 1),
        "ipc_mensual":     d(1.9, "%", "mensual", 72),
        "emae":            d(165.47, "puntos", "mensual", 104),
        "circulacion":     d(23_000_000.0, "MM $", "diaria", 1),
        "uva":             d(1956.47, "índice", "diaria", 1),
    }}


def correr(nombre, contenido, espera_texto=None):
    """Corre el canario y verifica si cantó o no, y por qué."""
    fallos = canario.revisar(contenido, AHORA)
    if espera_texto is None:
        ok = not fallos
        detalle = "silencio" if ok else f"cantó de más: {fallos}"
    else:
        ok = any(espera_texto in f for f in fallos)
        detalle = (f"lo detectó" if ok
                   else f"NO lo detectó (dijo: {fallos or 'nada'})")
    print(f"  {'✓' if ok else '✗'} {nombre}: {detalle}")
    return ok


def main():
    print("[Probar canario]")
    resultados = []

    # El caso que más importa: con todo sano no tiene que decir nada.
    resultados.append(correr("datos sanos → no canta", datos_sanos()))

    # El desastre del TCRM: un índice base 100 publicando 1460. Respondía
    # 200 OK, el pipeline no fallaba, y estuvo mal durante meses.
    c = datos_sanos(); c["datos"]["tcrm"]["valor"] = 1460.0
    resultados.append(correr("TCRM en 1460 (era el dólar mayorista)", c, "tcrm"))

    # La UVA que estamos publicando hoy: 22 en vez de ~1956.
    c = datos_sanos(); c["datos"]["uva"]["valor"] = 22.0
    resultados.append(correr("UVA en 22 (debería rondar 1956)", c, "uva"))

    # La circulación monetaria en una unidad que no es millones de pesos.
    c = datos_sanos(); c["datos"]["circulacion"]["valor"] = 23.0
    resultados.append(correr("circulación en 23", c, "circulacion"))

    # Una serie diaria clavada: la fuente sigue contestando el último valor
    # que supo. Es el caso del call, parado hace 44 días.
    c = datos_sanos(); c["datos"]["badlar"]["fecha"] = _iso(44)
    resultados.append(correr("serie diaria clavada hace 44 días", c, "badlar"))

    # Un intradiario que no se actualiza: el pipeline dejó de correr.
    c = datos_sanos(); c["datos"]["dolar_blue"]["actualizado"] = _iso(5)
    resultados.append(correr("dólar intradiario sin actualizar hace 5 días",
                             c, "dolar_blue"))

    # Un dato que quedó conservado del día anterior.
    c = datos_sanos(); c["datos"]["reservas"]["stale"] = True
    resultados.append(correr("dato conservado (stale)", c, "reservas"))

    # Un obligatorio que desaparece de datos.json.
    c = datos_sanos(); del c["datos"]["riesgo_pais"]
    resultados.append(correr("falta un dato obligatorio", c, "riesgo_pais"))

    # Un valor que deja de ser numérico.
    c = datos_sanos(); c["datos"]["merval"]["valor"] = "sin datos"
    resultados.append(correr("valor no numérico", c, "merval"))

    # El EMAE con su rezago normal no tiene que cantar: es la excepción que
    # evita un aviso falso todos los meses.
    c = datos_sanos(); c["datos"]["emae"]["fecha"] = _iso(120)
    resultados.append(correr("EMAE con rezago normal → no canta por edad",
                             c, None))

    print()
    fallados = resultados.count(False)
    if fallados:
        print(f"[Probar canario] {fallados} de {len(resultados)} casos MAL")
        sys.exit(1)
    print(f"[Probar canario] {len(resultados)} casos OK")


if __name__ == "__main__":
    main()
