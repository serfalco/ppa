/* =================================================================
   PPA — JavaScript de datos vivos v3
   Actualiza desde el navegador del lector, sin tocar el servidor
   Fix v3: localStorage para último valor conocido, nunca muestra —
   ================================================================= */

(function() {
  'use strict';

  // ---------------------------------------------------------------
  // CONFIG
  // ---------------------------------------------------------------
  const API_DOLAR_OFICIAL = 'https://dolarapi.com/v1/dolares/oficial';
  const API_DOLAR_MEP     = 'https://dolarapi.com/v1/dolares/bolsa';
  const API_DOLAR_CCL     = 'https://dolarapi.com/v1/dolares/contadoconliqui';
  const API_RIESGO        = 'https://api.argentinadatos.com/v1/finanzas/indices/riesgo-pais/ultimo';
  const API_MERVAL        = 'https://api.argentinadatos.com/v1/finanzas/indices/merval/ultimo';
  const API_RESERVAS      = 'https://apis.datos.gob.ar/series/api/series/?ids=174.1_T_1.0_0_100&last=1&format=json';
  const API_CLIMA         = 'https://api.open-meteo.com/v1/forecast?latitude=-34.6&longitude=-58.4&current=temperature_2m,weather_code&timezone=America/Argentina/Buenos_Aires';

  const REFRESH_MS = 15 * 60 * 1000; // 15 minutos
  const REFRESH_CLIMA_MS  = 30 * 60 * 1000;
  const REFRESH_FULBITO_MS = 60 * 60 * 1000;

  const CLIMA_EMOJI = {
    0:'☀️',1:'🌤️',2:'⛅',3:'☁️',
    45:'🌫️',48:'🌫️',
    51:'🌦️',53:'🌦️',55:'🌧️',
    61:'🌧️',63:'🌧️',65:'🌧️',
    71:'❄️',73:'❄️',75:'❄️',
    80:'🌧️',81:'🌧️',82:'⛈️',
    95:'⛈️',96:'⛈️',99:'⛈️',
  };

  // ---------------------------------------------------------------
  // CACHE (localStorage) — nunca muestra — si hay valor previo
  // ---------------------------------------------------------------
  function cacheSave(key, value) {
    try { localStorage.setItem('ppa_' + key, JSON.stringify({ v: value, t: Date.now() })); } catch(e) {}
  }
  function cacheLoad(key) {
    try {
      const raw = localStorage.getItem('ppa_' + key);
      if (!raw) return null;
      return JSON.parse(raw).v;
    } catch(e) { return null; }
  }

  // ---------------------------------------------------------------
  // HELPERS
  // ---------------------------------------------------------------
  function fmtPesos(n) {
    return '$' + Math.round(n).toLocaleString('es-AR');
  }
  function fmtNumero(n) {
    return Math.round(n).toLocaleString('es-AR');
  }
  function fmtMillones(n) {
    // Para reservas BCRA en millones de USD
    if (n >= 1000) return 'USD ' + (n / 1000).toFixed(1) + ' MM';
    return 'USD ' + Math.round(n).toLocaleString('es-AR') + ' M';
  }

  async function fetchJSON(url, timeout = 10000) {
    const controller = new AbortController();
    const id = setTimeout(() => controller.abort(), timeout);
    try {
      const r = await fetch(url, {
        signal: controller.signal,
        cache: 'no-store'
      });
      clearTimeout(id);
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return await r.json();
    } catch(e) {
      clearTimeout(id);
      console.warn('[PPA] fetch error:', url, e.message);
      return null;
    }
  }

  // Setea texto en un elemento. Si valor es null, usa caché. Si no hay caché, pone "s/d"
  function setTexto(id, valor, cacheKey, suffix) {
    const el = document.getElementById(id);
    if (!el) return;
    suffix = suffix || '';
    if (valor !== null && valor !== undefined) {
      cacheSave(cacheKey, valor);
      el.textContent = valor + suffix;
      el.classList.remove('dato-stale');
    } else {
      const cached = cacheLoad(cacheKey);
      if (cached !== null) {
        el.textContent = cached + suffix;
        el.classList.add('dato-stale'); // visual sutil de que es dato viejo
      }
      // Si no hay caché tampoco, no tocamos el elemento (se queda vacío o con lo que tenía)
    }
  }

  // ---------------------------------------------------------------
  // CLIMA
  // ---------------------------------------------------------------
  async function actualizarClima() {
    const el = document.getElementById('clima-widget');
    if (!el) return;
    const data = await fetchJSON(API_CLIMA);
    if (data && data.current) {
      const temp = Math.round(data.current.temperature_2m);
      const emoji = CLIMA_EMOJI[data.current.weather_code] || '';
      const val = `${emoji} ${temp}°`;
      el.textContent = val;
      cacheSave('clima', val);
    } else {
      const cached = cacheLoad('clima');
      if (cached) el.textContent = cached;
    }
  }

  // ---------------------------------------------------------------
  // TICKER PRINCIPAL
  // ---------------------------------------------------------------
  async function actualizarTicker() {
    // Lanzamos todo en paralelo
    const [dol, mep, merval, rp] = await Promise.all([
      fetchJSON(API_DOLAR_OFICIAL),
      fetchJSON(API_DOLAR_MEP),
      fetchJSON(API_MERVAL),
      fetchJSON(API_RIESGO),
    ]);

    // Dólar oficial
    const valDol = (dol && dol.venta) ? fmtPesos(dol.venta) : null;
    setTexto('dolar-oficial', valDol, 'dolar_oficial');

    // MEP
    const valMep = (mep && mep.venta) ? fmtPesos(mep.venta) : null;
    setTexto('dolar-mep', valMep, 'dolar_mep');

    // Merval
    const valMerval = (merval && merval.valor !== undefined) ? fmtNumero(merval.valor) : null;
    setTexto('merval', valMerval, 'merval');

    // Riesgo país
    const valRp = (rp && rp.valor !== undefined) ? fmtNumero(rp.valor) : null;
    setTexto('riesgo-pais', valRp, 'riesgo_pais', ' pb');
  }

  // ---------------------------------------------------------------
  // 5 TARJETAS INFOBAE (home v3)
  // ---------------------------------------------------------------
  async function actualizarTarjetas() {
    // Solo corren si existen los elementos en la página
    if (!document.getElementById('tarjeta-dolar-oficial')) return;

    const [dol, mep, merval, rp, reservas] = await Promise.all([
      fetchJSON(API_DOLAR_OFICIAL),
      fetchJSON(API_DOLAR_MEP),
      fetchJSON(API_MERVAL),
      fetchJSON(API_RIESGO),
      fetchJSON(API_RESERVAS),
    ]);

    const ahora = new Date().toLocaleTimeString('es-AR', { hour: '2-digit', minute: '2-digit' });

    // Tarjeta 1: Dólar Oficial
    if (dol && dol.venta) {
      actualizarTarjeta('tarjeta-dolar-oficial', {
        valor: fmtPesos(dol.venta),
        variacion: dol.variacion,
        hora: ahora,
        cacheKey: 'tarjeta_dolar_oficial'
      });
    } else {
      restaurarTarjeta('tarjeta-dolar-oficial', 'tarjeta_dolar_oficial');
    }

    // Tarjeta 2: Dólar MEP
    if (mep && mep.venta) {
      actualizarTarjeta('tarjeta-dolar-mep', {
        valor: fmtPesos(mep.venta),
        variacion: mep.variacion,
        hora: ahora,
        cacheKey: 'tarjeta_dolar_mep'
      });
    } else {
      restaurarTarjeta('tarjeta-dolar-mep', 'tarjeta_dolar_mep');
    }

    // Tarjeta 3: Riesgo País
    if (rp && rp.valor !== undefined) {
      actualizarTarjeta('tarjeta-riesgo', {
        valor: fmtNumero(rp.valor) + ' pb',
        variacion: rp.variacion,
        hora: ahora,
        cacheKey: 'tarjeta_riesgo'
      });
    } else {
      restaurarTarjeta('tarjeta-riesgo', 'tarjeta_riesgo');
    }

    // Tarjeta 4: Merval
    if (merval && merval.valor !== undefined) {
      actualizarTarjeta('tarjeta-merval', {
        valor: fmtNumero(merval.valor),
        variacion: merval.variacion,
        hora: ahora,
        cacheKey: 'tarjeta_merval'
      });
    } else {
      restaurarTarjeta('tarjeta-merval', 'tarjeta_merval');
    }

    // Tarjeta 5: Reservas BCRA
    if (reservas && reservas.data && reservas.data[0] && reservas.data[0][1] !== null) {
      const val = reservas.data[0][1];
      actualizarTarjeta('tarjeta-reservas', {
        valor: fmtMillones(val),
        variacion: null,
        hora: ahora,
        cacheKey: 'tarjeta_reservas'
      });
    } else {
      restaurarTarjeta('tarjeta-reservas', 'tarjeta_reservas');
    }
  }

  function actualizarTarjeta(id, { valor, variacion, hora, cacheKey }) {
    const el = document.getElementById(id);
    if (!el) return;
    const elValor = el.querySelector('.tarjeta-valor');
    const elVar   = el.querySelector('.tarjeta-var');
    const elHora  = el.querySelector('.tarjeta-hora');
    if (elValor) elValor.textContent = valor;
    if (elHora)  elHora.textContent  = 'últ. ' + hora;
    if (elVar) {
      if (variacion !== null && variacion !== undefined) {
        const signo = variacion >= 0 ? '▲' : '▼';
        const clase = variacion >= 0 ? 'sube' : 'baja';
        elVar.className = 'tarjeta-var ' + clase;
        elVar.textContent = signo + ' ' + Math.abs(variacion).toFixed(2) + '% (24hs)';
      } else {
        elVar.textContent = '';
      }
    }
    cacheSave(cacheKey, { valor, variacion, hora });
  }

  function restaurarTarjeta(id, cacheKey) {
    const cached = cacheLoad(cacheKey);
    if (cached) actualizarTarjeta(id, cached);
  }

  // ---------------------------------------------------------------
  // WIDGET CIERRE DE MERCADO (lunes a viernes, 17:15 a 19:30hs)
  // ---------------------------------------------------------------
  function dentroHorarioCierre() {
    const ahora = new Date();
    const ahoraArg = new Date(ahora.toLocaleString('en-US', { timeZone: 'America/Argentina/Buenos_Aires' }));
    const dia  = ahoraArg.getDay();
    const hora = ahoraArg.getHours();
    const min  = ahoraArg.getMinutes();
    if (dia === 0 || dia === 6) return false;
    const minutos = hora * 60 + min;
    return minutos >= 17 * 60 + 15 && minutos < 19 * 60 + 30;
  }

  async function actualizarCierreMercado() {
    const widget = document.getElementById('widget-cierre');
    if (!widget) return;
    if (!dentroHorarioCierre()) { widget.style.display = 'none'; return; }

    const [mep, ccl, merval] = await Promise.all([
      fetchJSON(API_DOLAR_MEP),
      fetchJSON(API_DOLAR_CCL),
      fetchJSON(API_MERVAL),
    ]);

    const partes = [];
    if (merval && merval.valor !== undefined) {
      const v = merval.variacion;
      const txtVar = (v !== null && v !== undefined)
        ? ` <span class="${v >= 0 ? 'sube' : 'baja'}">${v >= 0 ? '+' : ''}${v.toFixed(2)}%</span>`
        : '';
      partes.push(`<div class="cierre-item"><span class="cierre-label">Merval</span> <strong>${fmtNumero(merval.valor)}</strong>${txtVar}</div>`);
    }
    if (mep && mep.venta)  partes.push(`<div class="cierre-item"><span class="cierre-label">Dólar MEP</span> <strong>${fmtPesos(mep.venta)}</strong></div>`);
    if (ccl && ccl.venta)  partes.push(`<div class="cierre-item"><span class="cierre-label">Dólar CCL</span> <strong>${fmtPesos(ccl.venta)}</strong></div>`);

    if (!partes.length) { widget.style.display = 'none'; return; }

    const body = document.getElementById('cierre-body');
    if (body) { body.innerHTML = partes.join(''); widget.style.display = 'block'; }
  }

  // ---------------------------------------------------------------
  // MARQUESINA FULBITO
  // ---------------------------------------------------------------
  async function actualizarFulbito() {
    const data = await fetchJSON('/data/fulbito.json');
    const bar = document.getElementById('fulbito-bar');
    if (!bar) return;
    if (!data || !data.partidos || !data.partidos.length) { bar.style.display = 'none'; return; }
    const cont = document.getElementById('fulbito-partidos');
    if (cont) {
      cont.innerHTML = data.partidos.map(p =>
        `<span class="fulbito-partido">${p.equipos}<span class="hora">${p.hora}</span></span>`
      ).join('');
      bar.style.display = 'block';
    }
  }

  // ---------------------------------------------------------------
  // FINGERPRINT DISPOSITIVO (para encuesta)
  // ---------------------------------------------------------------
  function getFingerprint() {
    try {
      let fp = localStorage.getItem('ppa_fp');
      if (!fp) {
        fp = Math.random().toString(36).substr(2, 9) + Date.now().toString(36);
        localStorage.setItem('ppa_fp', fp);
      }
      return fp;
    } catch(e) { return 'nofp'; }
  }
  // Exponemos para que encuesta.js lo use
  window.PPA = window.PPA || {};
  window.PPA.getFingerprint = getFingerprint;

  // ---------------------------------------------------------------
  // INICIO
  // ---------------------------------------------------------------
  function iniciar() {
    actualizarClima();
    actualizarTicker();
    actualizarTarjetas();
    actualizarCierreMercado();
    actualizarFulbito();

    setInterval(actualizarClima,          REFRESH_CLIMA_MS);
    setInterval(actualizarTicker,         REFRESH_MS);
    setInterval(actualizarTarjetas,       REFRESH_MS);
    setInterval(actualizarCierreMercado,  REFRESH_MS);
    setInterval(actualizarFulbito,        REFRESH_FULBITO_MS);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }

})();
