/* =================================================================
   PPA — JavaScript de datos vivos
   Actualiza desde el navegador del lector, sin tocar el servidor
   ================================================================= */

(function() {
  'use strict';

  // ---------------------------------------------------------------
  // CONFIG
  // ---------------------------------------------------------------
  const API_DOLAR_OFICIAL = 'https://dolarapi.com/v1/dolares/oficial';
  const API_DOLAR_MEP = 'https://dolarapi.com/v1/dolares/bolsa';
  const API_DOLAR_CCL = 'https://dolarapi.com/v1/dolares/contadoconliqui';
  const API_RIESGO = 'https://api.argentinadatos.com/v1/finanzas/indices/riesgo-pais/ultimo';
  const API_CLIMA = 'https://api.open-meteo.com/v1/forecast?latitude=-34.6&longitude=-58.4&current=temperature_2m,weather_code&timezone=America/Argentina/Buenos_Aires';
  const API_MERVAL = 'https://api.argentinadatos.com/v1/finanzas/indices/merval/ultimo';

  const REFRESH_DOLAR_MIN = 15;
  const REFRESH_CLIMA_MIN = 30;
  const REFRESH_FULBITO_MIN = 60;
  const REFRESH_MERCADO_MIN = 15;

  // Códigos del clima de Open-Meteo → emoji
  const CLIMA_EMOJI = {
    0: '☀️', 1: '🌤️', 2: '⛅', 3: '☁️',
    45: '🌫️', 48: '🌫️',
    51: '🌦️', 53: '🌦️', 55: '🌧️',
    61: '🌧️', 63: '🌧️', 65: '🌧️',
    71: '❄️', 73: '❄️', 75: '❄️',
    80: '🌧️', 81: '🌧️', 82: '⛈️',
    95: '⛈️', 96: '⛈️', 99: '⛈️',
  };

  // ---------------------------------------------------------------
  // HELPERS
  // ---------------------------------------------------------------
  function fmtPesos(n) {
    return '$' + Math.round(n).toLocaleString('es-AR');
  }

  function fmtNumero(n) {
    return Math.round(n).toLocaleString('es-AR');
  }

  async function fetchJSON(url, timeout = 8000) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    try {
      const r = await fetch(url, { signal: controller.signal });
      clearTimeout(id);
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return await r.json();
    } catch (e) {
      clearTimeout(id);
      console.warn('[PPA] Error fetch ' + url, e.message);
      return null;
    }
  }

  // ---------------------------------------------------------------
  // CLIMA
  // ---------------------------------------------------------------
  async function actualizarClima() {
    const el = document.getElementById('clima-widget');
    if (!el) return;

    const data = await fetchJSON(API_CLIMA);
    if (!data || !data.current) {
      el.textContent = '';
      return;
    }

    const temp = Math.round(data.current.temperature_2m);
    const code = data.current.weather_code;
    const emoji = CLIMA_EMOJI[code] || '';
    el.textContent = `${emoji} ${temp}°`;
  }

  // ---------------------------------------------------------------
  // TICKER: DÓLAR OFICIAL + DÓLAR MEP + MERVAL + RIESGO PAÍS
  // ---------------------------------------------------------------
  async function actualizarTicker() {
    // Dólar oficial
    const dol = await fetchJSON(API_DOLAR_OFICIAL);
    const elDol = document.getElementById('dolar-oficial');
    if (elDol && dol && dol.venta) {
      elDol.textContent = fmtPesos(dol.venta);
    }

    // Dólar MEP
    const mep = await fetchJSON(API_DOLAR_MEP);
    const elMep = document.getElementById('dolar-mep');
    if (elMep && mep && mep.venta) {
      elMep.textContent = fmtPesos(mep.venta);
    }

    // Merval
    const merval = await fetchJSON(API_MERVAL);
    const elMerval = document.getElementById('merval');
    if (elMerval && merval && merval.valor !== undefined) {
      elMerval.textContent = fmtNumero(merval.valor);
    }

    // Riesgo país
    const rp = await fetchJSON(API_RIESGO);
    const elRp = document.getElementById('riesgo-pais');
    if (elRp && rp && rp.valor !== undefined) {
      elRp.textContent = fmtNumero(rp.valor) + ' pb';
    }
  }

  // ---------------------------------------------------------------
  // WIDGET CIERRE DE MERCADO (lunes a viernes, 17 a 19hs)
  // ---------------------------------------------------------------
  function dentroHorarioCierre() {
    const ahora = new Date();
    // Convertir a hora Argentina (UTC-3)
    const offsetArg = -3 * 60;
    const offsetLocal = ahora.getTimezoneOffset();
    const minDif = offsetArg - offsetLocal * -1;
    const ahoraArg = new Date(ahora.getTime() + minDif * 60000);

    const dia = ahoraArg.getDay();   // 0=domingo, 6=sábado
    const hora = ahoraArg.getHours();

    if (dia === 0 || dia === 6) return false;
    if (hora >= 17 && hora < 19) return true;
    return false;
  }

  async function actualizarCierreMercado() {
    const widget = document.getElementById('widget-cierre');
    if (!widget) return;

    if (!dentroHorarioCierre()) {
      widget.style.display = 'none';
      return;
    }

    // Tomamos los datos que ya tenemos en las APIs durante el horario de cierre
    const [mep, ccl, merval] = await Promise.all([
      fetchJSON(API_DOLAR_MEP),
      fetchJSON(API_DOLAR_CCL),
      fetchJSON(API_MERVAL),
    ]);

    const partes = [];
    if (merval && merval.valor !== undefined) {
      const variacion = merval.variacion !== undefined ? merval.variacion : null;
      const signo = variacion !== null ? (variacion >= 0 ? '+' : '') : '';
      const claseColor = variacion !== null ? (variacion >= 0 ? 'sube' : 'baja') : '';
      const txtVar = variacion !== null ? ` <span class="${claseColor}">${signo}${variacion.toFixed(2)}%</span>` : '';
      partes.push(`<div class="cierre-item"><span class="cierre-label">Merval</span> <strong>${fmtNumero(merval.valor)}</strong>${txtVar}</div>`);
    }
    if (mep && mep.venta) {
      partes.push(`<div class="cierre-item"><span class="cierre-label">Dólar MEP</span> <strong>${fmtPesos(mep.venta)}</strong></div>`);
    }
    if (ccl && ccl.venta) {
      partes.push(`<div class="cierre-item"><span class="cierre-label">Dólar CCL</span> <strong>${fmtPesos(ccl.venta)}</strong></div>`);
    }

    if (partes.length === 0) {
      widget.style.display = 'none';
      return;
    }

    const body = document.getElementById('cierre-body');
    if (body) {
      body.innerHTML = partes.join('');
      widget.style.display = 'block';
    }
  }

  // ---------------------------------------------------------------
  // MARQUESINA FULBITO
  // ---------------------------------------------------------------
  async function actualizarFulbito() {
    // Lee partidos del día desde /data/fulbito.json (lo arma el backend con API-Football)
    const data = await fetchJSON('/data/fulbito.json');
    const bar = document.getElementById('fulbito-bar');
    if (!bar) return;

    if (!data || !data.partidos || data.partidos.length === 0) {
      bar.style.display = 'none';
      return;
    }

    const cont = document.getElementById('fulbito-partidos');
    if (!cont) return;

    cont.innerHTML = data.partidos.map(p =>
      `<span class="fulbito-partido">${p.equipos}<span class="hora">${p.hora}</span></span>`
    ).join('');

    bar.style.display = 'block';
  }

  // ---------------------------------------------------------------
  // INICIO
  // ---------------------------------------------------------------
  function iniciar() {
    actualizarClima();
    actualizarTicker();
    actualizarCierreMercado();
    actualizarFulbito();

    // Refrescos periódicos
    setInterval(actualizarClima, REFRESH_CLIMA_MIN * 60 * 1000);
    setInterval(actualizarTicker, REFRESH_DOLAR_MIN * 60 * 1000);
    setInterval(actualizarCierreMercado, REFRESH_MERCADO_MIN * 60 * 1000);
    setInterval(actualizarFulbito, REFRESH_FULBITO_MIN * 60 * 1000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }
})();
