"""
PPA — generador_tcrm.py
Genera la página "El peso en perspectiva" (/tcrm/).

Fuente: API de series datos.gob.ar
  Serie: 168.1_T_CAMBIOR_D_0_0_26
  ITCRM diario, base 17/12/2015=100, desde 01/01/1997
  Una llamada descarga toda la historia (~7000 puntos).

El gráfico es SVG + JS inline: línea histórica con hitos marcados.
Sin dependencias externas — compatible con el sitio estático.

Actualización: cada vez que corre el generador (edición mañana/tarde).
La data se guarda en data/tcrm_historico.json para no rebajar en cada
corrida; se actualiza si el último punto tiene más de 24hs.
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_DATA, DIR_SITE
import componentes as comp

TZ_AR = timezone(timedelta(hours=-3))
JSON_TCRM = os.path.join(DIR_DATA, "tcrm_historico.json")
DIR_TCRM  = os.path.join(DIR_SITE, "tcrm")

# ================================================================
# HITOS ECONÓMICOS ARGENTINOS (1997 → hoy)
# Cada hito: (fecha_iso, etiqueta_corta, descripcion_hover)
# Fuente: sección 20 del PPA_MAESTRO.md
# ================================================================
HITOS = [
    ("2001-12-20", "Crisis 2001",        "Crisis política y económica · fin de la convertibilidad"),
    ("2002-01-07", "Devaluación",         "Fin del 1=1 · devaluación y pesificación · TCRM se dispara"),
    ("2003-05-25", "Kirchner",            "Inicio gobierno Kirchner · dólar alto competitivo"),
    ("2007-12-10", "CFK I",               "Inicio CFK I · apreciación gradual del peso"),
    ("2011-10-31", "1er cepo",            "Primer cepo cambiario · control de cambios"),
    ("2015-12-10", "Macri · fin cepo",    "Macri · salida del cepo · devaluación · unificación cambiaria"),
    ("2018-04-27", "Crisis cambiaria",    "Corrida cambiaria · vuelta al FMI · mayor préstamo de la historia"),
    ("2019-08-11", "PASO 2019",           "PASO 2019 · salto del dólar tras resultado electoral"),
    ("2019-09-01", "2do cepo",            "Nuevo cepo cambiario (fin gobierno Macri)"),
    ("2023-12-10", "Milei",               "Milei · devaluación inicial ~$800 · licuación"),
    ("2025-04-14", "Banda cambiaria",     "Salida parcial del cepo · banda de flotación BCRA"),
]


# ================================================================
# BAJAR / CACHEAR DATA
# ================================================================

def _tcrm_fresco(cache):
    """Devuelve True si el cache tiene menos de 24hs."""
    ts = cache.get("descargado_en")
    if not ts:
        return False
    try:
        dt = datetime.fromisoformat(ts)
        return (datetime.now(timezone.utc) - dt).total_seconds() < 86400
    except Exception:
        return False


def obtener_tcrm():
    """Devuelve lista de [fecha_iso, valor] del TCRM, desde cache o API."""
    # Intentar cache primero
    if os.path.exists(JSON_TCRM):
        try:
            with open(JSON_TCRM, "r", encoding="utf-8") as f:
                cache = json.load(f)
            if _tcrm_fresco(cache) and cache.get("data"):
                print(f"[TCRM] Cache fresco ({len(cache['data'])} puntos)")
                return cache["data"]
        except Exception:
            pass

    # Bajar de la API
    print("[TCRM] Descargando serie histórica de datos.gob.ar...")
    import requests, urllib3
    urllib3.disable_warnings()

    url = ("https://apis.datos.gob.ar/series/api/series/"
           "?ids=168.1_T_CAMBIOR_D_0_0_26"
           "&format=json&limit=10000&sort=asc")
    try:
        r = requests.get(url, timeout=30, verify=False)
        r.raise_for_status()
        j = r.json()
        data = [[row[0], row[1]] for row in j["data"] if row[1] is not None]
        if not data:
            raise ValueError("Sin datos en la respuesta")
        print(f"[TCRM] Descargados {len(data)} puntos ({data[0][0]} → {data[-1][0]})")
        # Guardar cache
        cache = {
            "descargado_en": datetime.now(timezone.utc).isoformat(),
            "data": data,
        }
        os.makedirs(DIR_DATA, exist_ok=True)
        with open(JSON_TCRM, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False)
        return data
    except Exception as e:
        print(f"[TCRM] ⚠ Error descargando serie: {e}")
        # Si hay cache viejo, usarlo igual
        if os.path.exists(JSON_TCRM):
            try:
                with open(JSON_TCRM, "r", encoding="utf-8") as f:
                    cache = json.load(f)
                if cache.get("data"):
                    print(f"[TCRM] Usando cache viejo ({len(cache['data'])} puntos)")
                    return cache["data"]
            except Exception:
                pass
        return []


# ================================================================
# GENERAR HTML
# ================================================================

def generar_tcrm():
    data = obtener_tcrm()
    if not data:
        print("[TCRM] Sin data, abortando generación")
        return

    # Serializar para el JS inline
    # Muestrear para no inflar el HTML: 1 dato cada 5 días hábiles (~semana)
    # preserva la forma de la curva sin los 7000 puntos completos
    paso = 5
    data_muestreada = data[::paso]
    # Siempre incluir el último punto
    if data_muestreada[-1] != data[-1]:
        data_muestreada.append(data[-1])

    data_js = json.dumps(data_muestreada)
    hitos_js = json.dumps(HITOS)

    ultimo_fecha = data[-1][0]
    ultimo_valor = round(data[-1][1], 2)
    primer_fecha = data[0][0]

    # Valor actual vs promedio histórico
    valores = [v for _, v in data if v]
    promedio = round(sum(valores) / len(valores), 1)
    maximo = round(max(valores), 1)
    minimo = round(min(valores), 1)

    html = f"""{comp.head_comun(
        "El peso en perspectiva — TCRM histórico · PPA",
        "Tipo de Cambio Real Multilateral de Argentina desde 1997 hasta hoy, con hitos económicos históricos.",
        css_extra='<link rel="stylesheet" href="/assets/ppa.css"><link rel="stylesheet" href="/assets/tcrm.css">'
    )}
<body class="body-tcrm">

{comp.franja_datos()}
{comp.cabecera()}
{comp.nav_principal("Tablero")}

<main class="tcrm-main">
  <div class="contenedor">

    <div class="tcrm-intro">
      <div class="tcrm-intro-texto">
        <h1 class="tcrm-titulo">El peso en perspectiva</h1>
        <p class="tcrm-sub">Tipo de Cambio Real Multilateral · base 17/12/2015 = 100</p>
        <p class="tcrm-desc">
          El TCRM mide el valor del peso frente a una canasta de monedas de los principales
          socios comerciales (dólar, real, euro, yuan), ajustado por inflación relativa.
          Un índice alto = peso barato = más competitivo. Un índice bajo = peso caro.
        </p>
      </div>
      <div class="tcrm-stats">
        <div class="tcrm-stat">
          <span class="tcrm-stat-label">Hoy</span>
          <span class="tcrm-stat-valor" id="tcrm-actual">{ultimo_valor}</span>
          <span class="tcrm-stat-fecha">{ultimo_fecha}</span>
        </div>
        <div class="tcrm-stat">
          <span class="tcrm-stat-label">Promedio histórico</span>
          <span class="tcrm-stat-valor">{promedio}</span>
          <span class="tcrm-stat-fecha">{primer_fecha[:4]}–hoy</span>
        </div>
        <div class="tcrm-stat">
          <span class="tcrm-stat-label">Máximo</span>
          <span class="tcrm-stat-valor">{maximo}</span>
        </div>
        <div class="tcrm-stat">
          <span class="tcrm-stat-label">Mínimo</span>
          <span class="tcrm-stat-valor">{minimo}</span>
        </div>
      </div>
    </div>

    <!-- GRÁFICO -->
    <div class="tcrm-grafico-wrap">
      <canvas id="tcrm-canvas"></canvas>
      <div class="tcrm-tooltip" id="tcrm-tooltip" style="display:none">
        <span class="tt-fecha" id="tt-fecha"></span>
        <span class="tt-valor" id="tt-valor"></span>
        <span class="tt-hito" id="tt-hito"></span>
      </div>
    </div>

    <!-- LEYENDA DE HITOS -->
    <div class="tcrm-hitos-leyenda">
      <h3>Hitos históricos marcados en el gráfico</h3>
      <div class="hitos-grid" id="hitos-grid"></div>
    </div>

    <!-- NOTA METODOLÓGICA -->
    <div class="tcrm-nota">
      <strong>Fuente:</strong> BCRA vía API de Series de Tiempo de datos.gob.ar
      (ID 168.1_T_CAMBIOR_D_0_0_26). Serie oficial ITCRM diario, base 17/12/2015=100,
      desde 01/01/1997. El ITCRM es multilateral: canasta ponderada por comercio
      (no es solo el dólar). Para bilateral dólar o real, ver ITCRB del BCRA.
      <br>
      <a href="/tablero/">← Volver al Tablero</a>
    </div>

  </div>
</main>

{comp.pie()}

<script>
// ================================================================
// DATA Y HITOS
// ================================================================
const DATA   = {data_js};
const HITOS  = {hitos_js};
const PROMEDIO = {promedio};

// ================================================================
// CANVAS CHART — línea histórica con hitos
// ================================================================
(function() {{
  const canvas = document.getElementById('tcrm-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  // Colores del tema PPA (papel/tinta)
  const C = {{
    tinta:    '#1a1a1a',
    gris:     '#5a5750',
    linea:    '#b8b1a0',
    papel2:   '#ebe5d6',
    rojo:     '#9a1b1b',
    verde:    '#2d5a3d',
    azul:     '#1e3a5f',
    hito:     'rgba(154, 27, 27, 0.7)',
    promedio: 'rgba(45, 90, 61, 0.4)',
  }};

  function resize() {{
    const w = canvas.parentElement.clientWidth;
    canvas.width  = w;
    canvas.height = Math.round(w * 0.42);
    draw();
  }}

  const PAD = {{ top: 32, right: 20, bottom: 52, left: 58 }};

  function draw() {{
    const W = canvas.width, H = canvas.height;
    const chartW = W - PAD.left - PAD.right;
    const chartH = H - PAD.top  - PAD.bottom;
    ctx.clearRect(0, 0, W, H);

    if (!DATA.length) return;

    const valores  = DATA.map(d => d[1]);
    const fechas   = DATA.map(d => d[0]);
    const minV = Math.min(...valores) * 0.97;
    const maxV = Math.max(...valores) * 1.02;
    const minT = new Date(fechas[0]).getTime();
    const maxT = new Date(fechas[fechas.length-1]).getTime();

    function xOf(fecha) {{
      const t = new Date(fecha).getTime();
      return PAD.left + ((t - minT) / (maxT - minT)) * chartW;
    }}
    function yOf(v) {{
      return PAD.top + chartH - ((v - minV) / (maxV - minV)) * chartH;
    }}

    // Fondo área
    ctx.fillStyle = '#faf7f1';
    ctx.fillRect(PAD.left, PAD.top, chartW, chartH);

    // Grilla horizontal
    ctx.strokeStyle = C.linea;
    ctx.lineWidth = 0.5;
    const ticks = [60, 80, 100, 120, 140, 160, 180, 200];
    ctx.font = '10px IBM Plex Sans, sans-serif';
    ctx.fillStyle = C.gris;
    ctx.textAlign = 'right';
    ticks.forEach(v => {{
      if (v < minV || v > maxV) return;
      const y = yOf(v);
      ctx.beginPath(); ctx.moveTo(PAD.left, y); ctx.lineTo(PAD.left + chartW, y);
      ctx.stroke();
      ctx.fillText(v, PAD.left - 6, y + 3);
    }});

    // Línea del promedio histórico
    const yProm = yOf(PROMEDIO);
    ctx.strokeStyle = C.promedio;
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath(); ctx.moveTo(PAD.left, yProm); ctx.lineTo(PAD.left + chartW, yProm);
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.fillStyle = C.verde;
    ctx.font = '9px IBM Plex Sans, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('Promedio ' + PROMEDIO, PAD.left + 4, yProm - 4);

    // Eje X: años cada 2
    ctx.fillStyle = C.gris;
    ctx.font = '10px IBM Plex Sans, sans-serif';
    ctx.textAlign = 'center';
    const anioMin = parseInt(fechas[0].slice(0,4));
    const anioMax = parseInt(fechas[fechas.length-1].slice(0,4));
    for (let a = anioMin; a <= anioMax; a += 2) {{
      const x = xOf(a + '-01-01');
      if (x < PAD.left || x > PAD.left + chartW) continue;
      ctx.strokeStyle = C.linea;
      ctx.lineWidth = 0.5;
      ctx.beginPath(); ctx.moveTo(x, PAD.top); ctx.lineTo(x, PAD.top + chartH);
      ctx.stroke();
      ctx.fillStyle = C.gris;
      ctx.fillText(a, x, H - PAD.bottom + 14);
    }}

    // Área bajo la curva
    ctx.beginPath();
    ctx.moveTo(xOf(fechas[0]), yOf(valores[0]));
    DATA.forEach(([f, v]) => ctx.lineTo(xOf(f), yOf(v)));
    ctx.lineTo(xOf(fechas[fechas.length-1]), PAD.top + chartH);
    ctx.lineTo(xOf(fechas[0]), PAD.top + chartH);
    ctx.closePath();
    ctx.fillStyle = 'rgba(30, 58, 95, 0.07)';
    ctx.fill();

    // Línea principal
    ctx.beginPath();
    ctx.moveTo(xOf(fechas[0]), yOf(valores[0]));
    DATA.forEach(([f, v]) => ctx.lineTo(xOf(f), yOf(v)));
    ctx.strokeStyle = C.azul;
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // Hitos: líneas verticales rojas finas
    HITOS.forEach(([fecha, etiqueta, desc], i) => {{
      const x = xOf(fecha);
      if (x < PAD.left || x > PAD.left + chartW) return;
      ctx.strokeStyle = C.hito;
      ctx.lineWidth = 1;
      ctx.setLineDash([3, 3]);
      ctx.beginPath(); ctx.moveTo(x, PAD.top); ctx.lineTo(x, PAD.top + chartH);
      ctx.stroke();
      ctx.setLineDash([]);
      // Número del hito
      const num = i + 1;
      ctx.fillStyle = C.rojo;
      ctx.font = 'bold 8px IBM Plex Sans, sans-serif';
      ctx.textAlign = 'center';
      ctx.fillText(num, x, PAD.top - 6);
    }});

    // Borde del área del gráfico
    ctx.strokeStyle = C.tinta;
    ctx.lineWidth = 1;
    ctx.strokeRect(PAD.left, PAD.top, chartW, chartH);
  }}

  // ── Leyenda de hitos ──
  const grid = document.getElementById('hitos-grid');
  if (grid) {{
    HITOS.forEach(([fecha, etiqueta, desc], i) => {{
      const div = document.createElement('div');
      div.className = 'hito-item';
      div.innerHTML = `<span class="hito-num">${{i+1}}</span>
        <span class="hito-fecha">${{fecha.slice(0,7)}}</span>
        <span class="hito-label">${{etiqueta}}</span>
        <span class="hito-desc">${{desc}}</span>`;
      grid.appendChild(div);
    }});
  }}

  // ── Tooltip con mouse ──
  const tooltip = document.getElementById('tcrm-tooltip');
  canvas.addEventListener('mousemove', function(e) {{
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const chartW = canvas.width - PAD.left - PAD.right;
    const minT = new Date(DATA[0][0]).getTime();
    const maxT = new Date(DATA[DATA.length-1][0]).getTime();
    // Encontrar punto más cercano
    const t = minT + ((mx - PAD.left) / chartW) * (maxT - minT);
    let best = 0, bestD = Infinity;
    DATA.forEach(([f], i) => {{
      const d = Math.abs(new Date(f).getTime() - t);
      if (d < bestD) {{ bestD = d; best = i; }}
    }});
    const [fecha, valor] = DATA[best];
    document.getElementById('tt-fecha').textContent = fecha;
    document.getElementById('tt-valor').textContent = 'TCRM ' + valor.toFixed(2);
    // Hito cercano?
    const hitosCercanos = HITOS.filter(([hf]) => Math.abs(new Date(hf).getTime() - new Date(fecha).getTime()) < 30*86400000);
    document.getElementById('tt-hito').textContent = hitosCercanos.length ? hitosCercanos[0][1] : '';
    if (tooltip) {{
      tooltip.style.display = 'block';
      tooltip.style.left = Math.min(mx + 12, canvas.width - 160) + 'px';
      tooltip.style.top = (e.clientY - rect.top - 40) + 'px';
    }}
  }});
  canvas.addEventListener('mouseleave', () => {{
    if (tooltip) tooltip.style.display = 'none';
  }});

  // Touch: tap muestra tooltip
  canvas.addEventListener('touchmove', function(e) {{
    e.preventDefault();
    const touch = e.touches[0];
    canvas.dispatchEvent(new MouseEvent('mousemove', {{
      clientX: touch.clientX, clientY: touch.clientY
    }}));
  }}, {{passive: false}});

  window.addEventListener('resize', resize);
  resize();
}})();
</script>

</body>
</html>"""

    os.makedirs(DIR_TCRM, exist_ok=True)
    out = os.path.join(DIR_TCRM, "index.html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[TCRM] Generado: {out} ({len(data)} puntos, {len(data_muestreada)} en gráfico)")


def main():
    print(f"[TCRM] Inicio: {datetime.now(timezone.utc).isoformat()}")
    generar_tcrm()
    print(f"[TCRM] Fin")


if __name__ == "__main__":
    main()
