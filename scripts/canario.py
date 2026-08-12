"""
PPA — canario.py
Chequea que los datos publicados sigan siendo lo que dicen ser.

Por qué existe: las tres alarmas que ya tiene el repo detectan AUSENCIA. La
de pasos caídos avisa si un script revienta, el vigía si una edición no
arranca, la salud de fuentes si un feed deja de responder. Ninguna detecta
que algo conteste 200 OK y devuelva otra cosa.

Ese es el modo de falla más caro que tuvo el proyecto y no dejó rastro en
ningún tablero. El TCRM publicó 1460 con unidad "índice" durante meses: un
índice base 17/12/2015=100 no puede valer 1460 —era el dólar mayorista
disfrazado— y todo figuraba en verde. La BADLAR salía de la variable 6 del
BCRA hasta que el BCRA la renumeró. Nadie se enteró en el momento en ningún
caso.

Cómo funciona: no vuelve a pedir los datos ni se fía de cómo los bajó el
pipeline. Lee lo que quedó publicado en datos.json y le pregunta dos cosas a
cada uno:

  1. ¿El número tiene la magnitud de lo que dice ser? Los rangos de abajo son
     deliberadamente anchos: no vigilan el valor del día, vigilan el orden de
     magnitud. Un índice base 100 puede irse a 300 en años de deriva, pero si
     marca 1460 no es un índice.
  2. ¿Es de hace poco, para su frecuencia? Una serie diaria clavada hace seis
     semanas es una fuente muerta que todavía devuelve el último valor que
     supo.

Los rangos describen QUÉ ES cada indicador, no cuánto vale hoy. Por eso no
hay que actualizarlos cuando el dólar sube: solo si un indicador cambia de
unidad o de base.

Sale con código 1 si algo falla, así el workflow abre el aviso con el mismo
mecanismo de siempre.

Cómo se corre a mano:
    python scripts/canario.py
    python scripts/canario.py --archivo data/datos.json
"""

import json
import os
import sys
from datetime import datetime, timezone

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_DATOS = os.path.join(RAIZ, "data", "datos.json")

# Cuántos días se le perdona a cada frecuencia antes de considerar el dato
# viejo. Diaria son 7 y no 1 por los fines de semana largos y los feriados
# cambiarios; mensual son 75 porque el INDEC publica con rezago.
EDAD_MAXIMA = {
    "intradia": 3,
    "diaria": 7,
    "mensual": 75,
    "manual": 7,
}
EDAD_POR_DEFECTO = 15

# Excepciones por dato, cuando la frecuencia sola miente. En las series
# mensuales la `fecha` es el mes de referencia, no el de publicación, así que
# la antigüedad arranca contando desde antes de que el dato existiera: el
# EMAE de mayo recién sale a fines de julio, y para agosto ya "tiene" cien
# días sin que haya pasado nada malo. El límite tiene que ser el rezago real
# del organismo más un margen, o el canario canta todos los meses.
EDAD_MAXIMA_POR_DATO = {
    "emae": 135,  # INDEC publica con ~2 meses de rezago sobre el mes de referencia
}

# Qué es cada dato, en términos de magnitud. (mínimo, máximo, qué mide).
# El campo del final es lo que se imprime cuando falla, para que el aviso se
# entienda sin abrir el código.
RANGOS = {
    # Cotizaciones: pesos por dólar. Anchísimo a propósito — lo que tiene que
    # atrapar es que acá caiga un porcentaje o un índice, no la inflación.
    "dolar_oficial":   (100, 100_000, "pesos por dólar"),
    "dolar_blue":      (100, 100_000, "pesos por dólar"),
    "dolar_mep":       (100, 100_000, "pesos por dólar"),
    "dolar_ccl":       (100, 100_000, "pesos por dólar"),
    "dolar_mayorista": (100, 100_000, "pesos por dólar"),
    "dolar_cripto":    (100, 100_000, "pesos por dólar"),
    "dolar_tarjeta":   (100, 100_000, "pesos por dólar"),

    # Índices y tasas.
    "tcrm":         (20, 400, "índice base 17/12/2015=100"),
    "uva":          (100, 1_000_000, "índice base 31/3/2016=14,05"),
    "emae":         (50, 500, "índice de nivel de actividad"),
    "merval":       (1_000, 100_000_000, "puntos del índice Merval"),
    "riesgo_pais":  (50, 10_000, "puntos básicos"),
    "badlar":       (1, 300, "tasa nominal anual en %"),
    "call_baibar":  (1, 300, "tasa nominal anual en %"),

    # Variaciones porcentuales.
    "ipc_mensual":  (-10, 100, "variación mensual en %"),
    "ipc_nucleo":   (-10, 100, "variación mensual en %"),
    "brecha_mep":   (-50, 500, "brecha en %"),

    # Agregados monetarios, en millones de pesos. El piso de 100.000 MM es
    # lo que separa un agregado nacional de un número en otra unidad: la
    # circulación monetaria no puede ser de 23 millones de pesos.
    "base_monetaria": (100_000, 1e11, "millones de pesos"),
    "m2_privado":     (100_000, 1e11, "millones de pesos"),
    "circulacion":    (100_000, 1e11, "millones de pesos"),

    # Stocks en dólares.
    "reservas": (1_000, 1_000_000, "millones de dólares"),
}

# Datos cuyo valor es un diccionario: se indica qué clave numérica mirar.
# El resto de las claves se ignoran (no todas son números).
CLAVES_ANIDADAS = {
    "dolar_oficial":   "venta",
    "dolar_blue":      "venta",
    "dolar_mep":       "venta",
    "dolar_ccl":       "venta",
    "dolar_mayorista": "venta",
    "dolar_cripto":    "venta",
    "dolar_tarjeta":   "venta",
    "mulc":            "monto",
    "banda":           "techo",
}

# Los que tienen que estar sí o sí. Si uno desaparece de datos.json es que
# algo se rompió río arriba, aunque el resto siga saliendo.
OBLIGATORIOS = [
    "dolar_oficial", "dolar_blue", "dolar_mep", "dolar_mayorista",
    "riesgo_pais", "reservas", "merval", "tcrm", "badlar",
    "ipc_mensual",
]


def _numero(dato, clave):
    """El número a chequear, o None si el dato no expone uno."""
    v = dato.get("valor")
    if isinstance(v, dict):
        v = v.get(CLAVES_ANIDADAS.get(clave))
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        return None
    return float(v)


def _edad_dias(dato, ahora):
    """Antigüedad del dato en días, y de dónde se sacó.

    Se prefiere `fecha`, que es la fecha del dato en la fuente. Los
    intradiarios no la traen, así que ahí se usa `actualizado`: si un
    intradiario se bajó hace tres días, el pipeline dejó de correr.
    """
    for campo in ("fecha", "actualizado"):
        crudo = dato.get(campo)
        if not crudo:
            continue
        try:
            t = datetime.fromisoformat(str(crudo).replace("Z", "+00:00"))
        except ValueError:
            continue
        if t.tzinfo is None:
            t = t.replace(tzinfo=timezone.utc)
        return (ahora - t).total_seconds() / 86400, campo
    return None, None


def revisar(contenido, ahora=None):
    """Devuelve la lista de problemas. Vacía es que está todo bien."""
    ahora = ahora or datetime.now(timezone.utc)
    datos = contenido.get("datos") or {}
    fallos = []

    for clave in OBLIGATORIOS:
        if clave not in datos:
            fallos.append(f"falta `{clave}`: no está en datos.json")

    for clave, dato in sorted(datos.items()):
        if not isinstance(dato, dict):
            fallos.append(f"`{clave}`: el dato no es un objeto")
            continue

        if dato.get("stale"):
            fallos.append(f"`{clave}`: quedó conservado del día anterior "
                          f"(la fuente no respondió)")

        rango = RANGOS.get(clave)
        if rango:
            minimo, maximo, que_es = rango
            valor = _numero(dato, clave)
            if valor is None:
                fallos.append(f"`{clave}`: no tiene un valor numérico que mirar")
            elif not (minimo <= valor <= maximo):
                fallos.append(
                    f"`{clave}`: vale {valor:g} y debería ser {que_es} "
                    f"(entre {minimo:g} y {maximo:g}). No es un valor de esa "
                    f"magnitud: o cambió la fuente o cambió la unidad")

        dias, origen = _edad_dias(dato, ahora)
        frec = dato.get("frecuencia") or ""
        limite = EDAD_MAXIMA_POR_DATO.get(
            clave, EDAD_MAXIMA.get(frec, EDAD_POR_DEFECTO))
        if dias is None:
            fallos.append(f"`{clave}`: no tiene ni fecha ni marca de "
                          f"actualización, así que no se puede saber si es viejo")
        elif dias > limite:
            campo = "el dato es" if origen == "fecha" else "no se actualiza desde hace"
            fallos.append(
                f"`{clave}`: {campo} de hace {dias:.0f} días y es una serie "
                f"{frec or 'sin frecuencia declarada'} (máximo {limite}). "
                f"La fuente dejó de moverse")

    return fallos


def cargar(ruta):
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"No existe {ruta}")
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    args = sys.argv[1:]
    ruta = JSON_DATOS
    if "--archivo" in args:
        i = args.index("--archivo")
        if i + 1 >= len(args):
            print("--archivo necesita una ruta.")
            sys.exit(2)
        ruta = args[i + 1]

    ahora = datetime.now(timezone.utc)
    print(f"[Canario] {ahora.strftime('%Y-%m-%d %H:%M UTC')} · {ruta}")

    try:
        contenido = cargar(ruta)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        # Un datos.json ilegible es en sí mismo el hallazgo: es lo que lee
        # todo el sitio. Se avisa en vez de morir en silencio.
        print(f"[Canario] no pude leer los datos: {e}")
        _emitir_salida([f"`datos.json` no se puede leer: {e}"])
        sys.exit(1)

    fallos = revisar(contenido, ahora)
    total = len(contenido.get("datos") or {})

    if not fallos:
        print(f"[Canario] {total} datos revisados · todo en orden")
        return

    print(f"[Canario] {total} datos revisados · {len(fallos)} problema(s):")
    for f in fallos:
        print(f"   ✗ {f}")
    _emitir_salida(fallos)
    sys.exit(1)


def _emitir_salida(fallos):
    """Deja los hallazgos donde el workflow los pueda leer."""
    salida = os.environ.get("GITHUB_OUTPUT")
    if not salida:
        return
    with open(salida, "a", encoding="utf-8") as f:
        f.write(f"cantidad={len(fallos)}\n")
        f.write("detalle<<FIN\n")
        for x in fallos:
            f.write(f"- {x}\n")
        f.write("FIN\n")


if __name__ == "__main__":
    main()
