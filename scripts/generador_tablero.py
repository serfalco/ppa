"""
PPA — generador_tablero.py v3
Genera /tablero/index.html con los 6 bloques de datos económicos.
Los datos son cargados en tiempo real por el navegador (JS).
Este script solo genera el HTML estático con la estructura.
"""

import os
import sys
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config import DIR_SITE
from iconos import ICONO

TZ_AR = timezone(timedelta(hours=-3))


def generar_tablero():
    html = """<!DOCTYPE html>
<html lang="es-AR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tablero PPA · Pulso Productivo Argentino</title>
<meta name="description" content="Tablero de datos económicos argentinos en tiempo real: dólares, mercado, macro, sector externo, empleo y fiscal.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,700;0,900&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/ppa.css">
<link rel="stylesheet" href="/assets/tablero.css">
</head>
<body class="body-tablero">

<!-- FRANJA SUPERIOR -->
<div class="franja-datos">
  <div class="contenedor franja-flex">
    <a href="/" class="volver-home">← PPA</a>
    <span class="dato-mini" id="clima-widget"></span>
    <span class="dato-mini">USD <span id="dolar-oficial">…</span></span>
    <span class="dato-mini">MEP <span id="dolar-mep">…</span></span>
    <span class="dato-mini">Merval <span id="merval">…</span></span>
    <span class="dato-mini">Riesgo <span id="riesgo-pais">…</span></span>
  </div>
</div>

<!-- CABECERA -->
<header class="tablero-cabecera">
  <div class="contenedor">
    <h1 class="tablero-titulo">Tablero PPA</h1>
    <p class="tablero-sub">Datos económicos argentinos · Actualización cada 15 minutos</p>
    <p class="tablero-disclaimer">Los datos se cargan desde APIs públicas oficiales y gratuitas.
    Si una fuente no responde, se muestra el último valor conocido marcado como desactualizado.</p>
  </div>
</header>

<!-- NAV DEL TABLERO -->
<nav class="tablero-nav">
  <div class="contenedor">
    <a href="#dolares">Dólares</a> |
    <a href="#mercado">Mercado</a> |
    <a href="#macro">Macro</a> |
    <a href="#externo">Sector externo</a> |
    <a href="#empleo">Empleo y salarios</a> |
    <a href="#fiscal">Fiscal</a>
  </div>
</nav>

<main class="tablero-main">
  <div class="contenedor">

    <!-- ============================================================
         BLOQUE 1: DÓLARES
         ============================================================ -->
    <section class="tablero-bloque" id="dolares">
      <h2 class="bloque-titulo">Dólares</h2>
      <div class="tablero-grid">

        <div class="dato-card">
          <span class="dato-label">Oficial</span>
          <div class="dato-par">
            <span class="dato-compra" id="t-dol-oficial-compra">…</span>
            <span class="dato-sep">/</span>
            <span class="dato-venta" id="t-dol-oficial-venta">…</span>
          </div>
          <span class="dato-sub">compra / venta</span>
          <span class="dato-fuente">dolarapi.com</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">MEP (Bolsa)</span>
          <span class="dato-valor" id="t-dol-mep">…</span>
          <span class="dato-var" id="t-dol-mep-var"></span>
          <span class="dato-fuente">dolarapi.com</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">CCL (Contado con Liqui)</span>
          <span class="dato-valor" id="t-dol-ccl">…</span>
          <span class="dato-var" id="t-dol-ccl-var"></span>
          <span class="dato-fuente">dolarapi.com</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">Blue</span>
          <div class="dato-par">
            <span class="dato-compra" id="t-dol-blue-compra">…</span>
            <span class="dato-sep">/</span>
            <span class="dato-venta" id="t-dol-blue-venta">…</span>
          </div>
          <span class="dato-sub">compra / venta</span>
          <span class="dato-fuente">dolarapi.com</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">Mayorista</span>
          <span class="dato-valor" id="t-dol-mayorista">…</span>
          <span class="dato-fuente">dolarapi.com</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">Tarjeta</span>
          <span class="dato-valor" id="t-dol-tarjeta">…</span>
          <span class="dato-fuente">dolarapi.com</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">Cripto (USDT)</span>
          <span class="dato-valor" id="t-dol-cripto">…</span>
          <span class="dato-fuente">dolarapi.com</span>
        </div>

        <div class="dato-card dato-card-accent">
          <span class="dato-label">Brecha MEP / Oficial</span>
          <span class="dato-valor dato-grande" id="t-brecha-mep">…</span>
          <span class="dato-sub">MEP vs. dólar oficial</span>
        </div>

      </div>

      <!-- VELÓMETRO BANDA CAMBIARIA -->
      <div class="banda-velo-card" id="banda-velo-card" style="display:none">
        <div class="velo-label">BANDA CAMBIARIA · dólar mayorista</div>
        <div class="banda-velo">
          <svg viewBox="0 0 220 130">
            <defs><linearGradient id="bvg" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stop-color="#27ae60"/><stop offset="55%" stop-color="#e8c84a"/><stop offset="100%" stop-color="#c0392b"/>
            </linearGradient></defs>
            <path d="M 20 115 A 90 90 0 0 1 200 115" fill="none" stroke="url(#bvg)" stroke-width="16" stroke-linecap="round"/>
            <g id="banda-aguja" transform="rotate(0 110 115)">
              <line x1="110" y1="115" x2="110" y2="40" stroke="#1a1a1a" stroke-width="3"/>
              <circle cx="110" cy="115" r="6" fill="#1a1a1a"/>
            </g>
          </svg>
        </div>
        <div class="banda-velo-num" id="banda-velo-num">…</div>
        <div class="banda-velo-sub" id="banda-velo-sub">del recorrido de la banda</div>
        <div class="banda-velo-pies">
          <span class="p" id="banda-velo-piso">…</span>
          <span class="t" id="banda-velo-techo">…</span>
        </div>
      </div>
    </section>

    <!-- ============================================================
         BLOQUE 2: MERCADO
         ============================================================ -->
    <section class="tablero-bloque" id="mercado">
      <h2 class="bloque-titulo">Mercado</h2>
      <div class="tablero-grid">

        <div class="dato-card">
          <span class="dato-label">Merval</span>
          <span class="dato-valor dato-grande" id="t-merval">…</span>
          <span class="dato-var" id="t-merval-var"></span>
          <span class="dato-fuente">argentinadatos.com</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">Riesgo País</span>
          <span class="dato-valor dato-grande" id="t-riesgo">…</span>
          <span class="dato-sub">puntos básicos</span>
          <span class="dato-fuente">argentinadatos.com</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">AL30 (bono en USD)</span>
          <span class="dato-valor" id="t-al30">s/d</span>
          <span class="dato-fuente">BYMA delayed</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">GD30 (bono en USD)</span>
          <span class="dato-valor" id="t-gd30">s/d</span>
          <span class="dato-fuente">BYMA delayed</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">GD35 (bono en USD)</span>
          <span class="dato-valor" id="t-gd35">s/d</span>
          <span class="dato-fuente">BYMA delayed</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">Reservas BCRA</span>
          <span class="dato-valor" id="t-reservas">…</span>
          <span class="dato-sub">millones de USD</span>
          <span class="dato-fuente">datos.gob.ar</span>
        </div>

      </div>
    </section>

    <!-- ============================================================
         BLOQUE 3: MACRO
         ============================================================ -->
    <section class="tablero-bloque" id="macro">
      <h2 class="bloque-titulo">Macro</h2>
      <div class="tablero-grid">

        <div class="dato-card">
          <span class="dato-label">IPC mensual (último)</span>
          <span class="dato-valor dato-grande" id="t-ipc-mensual">…</span>
          <span class="dato-sub" id="t-ipc-mensual-fecha">cargando…</span>
          <span class="dato-fuente">INDEC vía datos.gob.ar</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">IPC interanual</span>
          <span class="dato-valor dato-grande" id="t-ipc-interanual">…</span>
          <span class="dato-fuente">INDEC vía datos.gob.ar</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">IPC acumulado año</span>
          <span class="dato-valor" id="t-ipc-acumulado">…</span>
          <span class="dato-fuente">INDEC vía datos.gob.ar</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">EMAE (último)</span>
          <span class="dato-valor" id="t-emae">…</span>
          <span class="dato-sub" id="t-emae-var">variación mensual/interanual</span>
          <span class="dato-fuente">INDEC vía datos.gob.ar</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">Reservas Brutas BCRA</span>
          <span class="dato-valor" id="t-reservas-macro">…</span>
          <span class="dato-sub">millones de USD</span>
          <span class="dato-fuente">datos.gob.ar</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">Base Monetaria</span>
          <span class="dato-valor" id="t-base-monetaria">…</span>
          <span class="dato-sub">millones de pesos</span>
          <span class="dato-fuente">BCRA</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">Tasa política monetaria</span>
          <span class="dato-valor" id="t-tasa-politica">…</span>
          <span class="dato-sub">% TNA</span>
          <span class="dato-fuente">BCRA</span>
        </div>

      </div>
    </section>

    <!-- ============================================================
         BLOQUE 4: SECTOR EXTERNO
         ============================================================ -->
    <section class="tablero-bloque" id="externo">
      <h2 class="bloque-titulo">Sector externo</h2>
      <div class="tablero-grid">

        <div class="dato-card">
          <span class="dato-label">Exportaciones (último mes)</span>
          <span class="dato-valor dato-proximo" id="t-exportaciones">próximamente</span>
          <span class="dato-sub">millones de USD</span>
          <span class="dato-fuente">INDEC vía datos.gob.ar</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">Importaciones (último mes)</span>
          <span class="dato-valor dato-proximo" id="t-importaciones">próximamente</span>
          <span class="dato-sub">millones de USD</span>
          <span class="dato-fuente">INDEC vía datos.gob.ar</span>
        </div>

        <div class="dato-card dato-card-accent">
          <span class="dato-label">Saldo comercial</span>
          <span class="dato-valor dato-grande dato-proximo" id="t-saldo-comercial">próximamente</span>
          <span class="dato-sub">millones de USD</span>
          <span class="dato-fuente">INDEC vía datos.gob.ar</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">TCRM</span>
          <span class="dato-valor" id="t-tcrm">…</span>
          <span class="dato-sub">Tipo de cambio real multilateral</span>
          <span class="dato-fuente">BCRA vía datos.gob.ar</span>
        </div>

      </div>
    </section>

    <!-- ============================================================
         BLOQUE 5: EMPLEO Y SALARIOS
         ============================================================ -->
    <section class="tablero-bloque" id="empleo">
      <h2 class="bloque-titulo">Empleo y salarios</h2>
      <div class="tablero-grid">

        <div class="dato-card">
          <span class="dato-label">Desocupación</span>
          <span class="dato-valor dato-grande dato-proximo" id="t-desocupacion">próximamente</span>
          <span class="dato-sub" id="t-desocupacion-fecha">último trimestre</span>
          <span class="dato-fuente">INDEC vía datos.gob.ar</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">Tasa de empleo</span>
          <span class="dato-valor dato-proximo" id="t-empleo">próximamente</span>
          <span class="dato-fuente">INDEC vía datos.gob.ar</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">Tasa de actividad</span>
          <span class="dato-valor dato-proximo" id="t-actividad">próximamente</span>
          <span class="dato-fuente">INDEC vía datos.gob.ar</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">Índice de salarios (privado)</span>
          <span class="dato-valor" id="t-salarios-privado">…</span>
          <span class="dato-fuente">INDEC vía datos.gob.ar</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">Salario Mínimo Vital y Móvil</span>
          <span class="dato-valor" id="t-smvm">…</span>
          <span class="dato-sub">pesos corrientes</span>
          <span class="dato-fuente">datos.gob.ar</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">Canasta básica total</span>
          <span class="dato-valor" id="t-cbt">…</span>
          <span class="dato-sub">línea de pobreza familiar</span>
          <span class="dato-fuente">INDEC vía datos.gob.ar</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">Canasta básica alimentaria</span>
          <span class="dato-valor" id="t-cba">…</span>
          <span class="dato-sub">línea de indigencia familiar</span>
          <span class="dato-fuente">INDEC vía datos.gob.ar</span>
        </div>

      </div>
    </section>

    <!-- ============================================================
         BLOQUE 6: FISCAL
         ============================================================ -->
    <section class="tablero-bloque" id="fiscal">
      <h2 class="bloque-titulo">Fiscal</h2>
      <div class="tablero-grid">

        <div class="dato-card">
          <span class="dato-label">Recaudación tributaria</span>
          <span class="dato-valor" id="t-recaudacion">…</span>
          <span class="dato-sub">millones de pesos — último mes</span>
          <span class="dato-fuente">AFIP vía datos.gob.ar</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">IVA</span>
          <span class="dato-valor" id="t-iva">…</span>
          <span class="dato-sub">millones de pesos</span>
          <span class="dato-fuente">AFIP vía datos.gob.ar</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">Ganancias</span>
          <span class="dato-valor" id="t-ganancias">…</span>
          <span class="dato-sub">millones de pesos</span>
          <span class="dato-fuente">AFIP vía datos.gob.ar</span>
        </div>

        <div class="dato-card">
          <span class="dato-label">Retenciones</span>
          <span class="dato-valor" id="t-retenciones">…</span>
          <span class="dato-sub">millones de pesos</span>
          <span class="dato-fuente">AFIP vía datos.gob.ar</span>
        </div>

        <div class="dato-card dato-card-accent">
          <span class="dato-label">Resultado primario</span>
          <span class="dato-valor dato-grande" id="t-resultado-primario">…</span>
          <span class="dato-sub">acumulado año — millones de pesos</span>
          <span class="dato-fuente">Secretaría de Hacienda vía datos.gob.ar</span>
        </div>

        <div class="dato-card dato-card-accent">
          <span class="dato-label">Resultado financiero</span>
          <span class="dato-valor dato-grande" id="t-resultado-financiero">…</span>
          <span class="dato-sub">acumulado año — millones de pesos</span>
          <span class="dato-fuente">Secretaría de Hacienda vía datos.gob.ar</span>
        </div>

      </div>
    </section>

  </div>
</main>

<!-- PIE -->
<footer class="pie">
  <div class="contenedor">
    <strong>PPA · Pulso Productivo Argentino</strong><br>
    <span class="pie-bajada">Publicación económica · pulsoproductivo.com.ar</span>
    <div class="pie-meta">
      <a href="/">Portada</a> ·
      <a href="/institucional/">Lo que se dice</a> ·
      <a href="/expectativas/">Expectativas</a> ·
      <a href="/tablero/">Tablero</a> ·
      <a href="/como-trabajamos.html">Cómo trabajamos</a> ·
      <a href="/acerca.html">Acerca de</a>
    </div>
    <div class="pie-legal">Editor responsable: Sergio Falco</div>
  </div>
</footer>

<script src="/assets/ppa.js"></script>
<script src="/assets/tablero.js"></script>

</body>
</html>"""

    # Insertar íconos en los títulos de sección
    titulos_iconos = {
        '<h2 class="bloque-titulo">Dólares</h2>':
            f'<h2 class="bloque-titulo">{ICONO["dolares"]}Dólares</h2>',
        '<h2 class="bloque-titulo">Mercado</h2>':
            f'<h2 class="bloque-titulo">{ICONO["mercado"]}Mercado</h2>',
        '<h2 class="bloque-titulo">Macro</h2>':
            f'<h2 class="bloque-titulo">{ICONO["macro"]}Macro</h2>',
        '<h2 class="bloque-titulo">Sector externo</h2>':
            f'<h2 class="bloque-titulo">{ICONO["comex"]}Sector externo</h2>',
        '<h2 class="bloque-titulo">Empleo y salarios</h2>':
            f'<h2 class="bloque-titulo">{ICONO["empleo"]}Empleo y salarios</h2>',
        '<h2 class="bloque-titulo">Fiscal</h2>':
            f'<h2 class="bloque-titulo">{ICONO["fiscal"]}Fiscal</h2>',
    }
    for viejo, nuevo in titulos_iconos.items():
        html = html.replace(viejo, nuevo)

    dir_tablero = os.path.join(DIR_SITE, "tablero")
    os.makedirs(dir_tablero, exist_ok=True)
    out = os.path.join(dir_tablero, "index.html")
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[PPA Tablero] Generado: {out}")


def main():
    print(f"[PPA Tablero] Inicio: {datetime.now(timezone.utc).isoformat()}")
    generar_tablero()
    print(f"[PPA Tablero] Fin")

if __name__ == "__main__":
    main()
