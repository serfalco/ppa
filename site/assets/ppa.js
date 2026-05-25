/* =================================================================
   PPA — JavaScript de datos vivos
   Actualiza desde el navegador del lector, sin tocar el servidor
   ================================================================= */

(function() {
  'use strict';

  // ---------------------------------------------------------------
  // CONFIG
  // ---------------------------------------------------------------
  const API_DOLAR = 'https://dolarapi.com/v1/dolares/oficial';
  const API_RIESGO = 'https://api.argentinadatos.com/v1/finanzas/indices/riesgo-pais/ultimo';
  const API_CLIMA = 'https://api.open-meteo.com/v1/forecast?latitude=-34.6&longitude=-58.4&current=temperature_2m,weather_code&timezone=America/Argentina/Buenos_Aires';

  const REFRESH_DOLAR_MIN = 15;
  const REFRESH_CLIMA_MIN = 30;
  const REFRESH_FULBITO_MIN = 60;

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
  // TICKER: DÓLAR + RIESGO PAÍS
  // ---------------------------------------------------------------
  async function actualizarTicker() {
    // Dólar oficial
    const dol = await fetchJSON(API_DOLAR);
    const elDol = document.getElementById('dolar-oficial');
    if (elDol && dol && dol.venta) {
      elDol.textContent = fmtPesos(dol.venta);
    }

    // Riesgo país
    const rp = await fetchJSON(API_RIESGO);
    const elRp = document.getElementById('riesgo-pais');
    if (elRp && rp && rp.valor !== undefined) {
      elRp.textContent = fmtNumero(rp.valor) + ' pb';
    }
  }

  // ---------------------------------------------------------------
  // WIDGET MULC (solo lun-vie, 17-20hs hora Argentina)
  // ---------------------------------------------------------------
  function dentroHorarioMulc() {
    const ahora = new Date();
    // hora local del navegador puede no ser Argentina, lo arreglamos con offset
    // pero asumimos que la mayoría de usuarios argentinos están en zona horaria correcta
    const dia = ahora.getDay();        // 0 = domingo
    const hora = ahora.getHours();

    if (dia === 0 || dia === 6) return false; // fin de semana
    if (hora >= 17 && hora < 20) return true;
    return false;
  }

  async function actualizarMulc() {
    const widget = document.getElementById('widget-mulc');
    if (!widget) return;

    if (!dentroHorarioMulc()) {
      widget.style.display = 'none';
      return;
    }

    // El dato del MULC viene del backend (lo carga el fetcher cuando lee Ámbito/Cronista)
    // Por ahora mostramos placeholder. Se puede conectar a un endpoint propio cuando el sitio esté en hosting.
    const body = document.getElementById('mulc-body');
    if (body) {
      // En la versión inicial dejamos el widget visible solo cuando hay data en /data/mulc.json
      const data = await fetchJSON('/data/mulc.json');
      if (data && data.dato) {
        widget.style.display = 'block';
        body.innerHTML = data.dato;
      } else {
        widget.style.display = 'none';
      }
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
    actualizarMulc();
    actualizarFulbito();

    // Refrescos periódicos
    setInterval(actualizarClima, REFRESH_CLIMA_MIN * 60 * 1000);
    setInterval(actualizarTicker, REFRESH_DOLAR_MIN * 60 * 1000);
    setInterval(actualizarMulc, 5 * 60 * 1000);  // chequeo cada 5 min por el horario
    setInterval(actualizarFulbito, REFRESH_FULBITO_MIN * 60 * 1000);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }
})();
