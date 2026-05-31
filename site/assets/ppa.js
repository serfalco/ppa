/* =================================================================
   PPA — JavaScript de datos vivos v3.1
   CAMBIO CLAVE: el navegador lee UN SOLO /data/datos.json ya cocido
   por GitHub Actions, en vez de pegarle a 5-6 APIs externas.
   Mas rapido, mas robusto: si una fuente fallo, el JSON ya trae el
   ultimo valor bueno marcado como stale.
   Clima y fulbito siguen en vivo (livianos, no criticos).
   ================================================================= */

(function() {
  'use strict';

  const DATOS_URL  = '/data/datos.json';
  const REFRESH_MS = 15 * 60 * 1000;
  const REFRESH_CLIMA_MS  = 30 * 60 * 1000;
  const REFRESH_FULBITO_MS = 60 * 60 * 1000;

  const API_CLIMA = 'https://api.open-meteo.com/v1/forecast?latitude=-34.6&longitude=-58.4&current=temperature_2m,weather_code&timezone=America/Argentina/Buenos_Aires';

  const CLIMA_EMOJI = {
    0:'\u2600\ufe0f',1:'\ud83c\udf24\ufe0f',2:'\u26c5',3:'\u2601\ufe0f',45:'\ud83c\udf2b\ufe0f',48:'\ud83c\udf2b\ufe0f',
    51:'\ud83c\udf26\ufe0f',53:'\ud83c\udf26\ufe0f',55:'\ud83c\udf27\ufe0f',61:'\ud83c\udf27\ufe0f',63:'\ud83c\udf27\ufe0f',65:'\ud83c\udf27\ufe0f',
    71:'\u2744\ufe0f',73:'\u2744\ufe0f',75:'\u2744\ufe0f',80:'\ud83c\udf27\ufe0f',81:'\ud83c\udf27\ufe0f',82:'\u26c8\ufe0f',
    95:'\u26c8\ufe0f',96:'\u26c8\ufe0f',99:'\u26c8\ufe0f',
  };

  function fmtPesos(n)   { return '$' + Math.round(n).toLocaleString('es-AR'); }
  function fmtNumero(n)  { return Math.round(n).toLocaleString('es-AR'); }
  function fmtMillones(n){
    if (n >= 1000) return 'USD ' + (n / 1000).toFixed(1) + ' MM';
    return 'USD ' + Math.round(n).toLocaleString('es-AR') + ' M';
  }

  async function fetchJSON(url, timeout) {
    timeout = timeout || 10000;
    const controller = new AbortController();
    const id = setTimeout(function(){ controller.abort(); }, timeout);
    try {
      const r = await fetch(url, { signal: controller.signal, cache: 'no-store' });
      clearTimeout(id);
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return await r.json();
    } catch(e) {
      clearTimeout(id);
      console.warn('[PPA] fetch error:', url, e.message);
      return null;
    }
  }

  function d(datos, clave) {
    if (!datos || !datos.datos) return null;
    return datos.datos[clave] || null;
  }
  function venta(item) {
    if (!item || item.valor == null) return null;
    return (typeof item.valor === 'object') ? item.valor.venta : item.valor;
  }

  function pintar(id, texto, stale, suffix) {
    const el = document.getElementById(id);
    if (!el || texto == null) return;
    el.textContent = texto + (suffix || '') + (stale ? ' *' : '');
    el.classList.toggle('dato-stale', !!stale);
    if (stale) el.title = '* Ultimo valor conocido (dato desactualizado)';
  }

  // ---------------- TICKER ----------------
  function pintarTicker(datos) {
    const ofi = d(datos, 'dolar_oficial');
    const mep = d(datos, 'dolar_mep');
    const mer = d(datos, 'merval');
    const rp  = d(datos, 'riesgo_pais');
    if (ofi) {
      pintar('dolar-oficial', fmtPesos(venta(ofi)), ofi.stale);
      pintar('m-dolar-oficial', fmtPesos(venta(ofi)), ofi.stale);
    }
    if (mep) {
      pintar('dolar-mep', fmtPesos(venta(mep)), mep.stale);
      pintar('m-dolar-mep', fmtPesos(venta(mep)), mep.stale);
    }
    const blue = d(datos, 'dolar_blue');
    if (blue) {
      pintar('dolar-blue-cab', fmtPesos(venta(blue)), blue.stale);
      pintar('m-dolar-blue', fmtPesos(venta(blue)), blue.stale);
    }
    if (mer) {
      pintar('merval', fmtNumero(mer.valor), mer.stale);
    } else {
      const it = document.getElementById('merval-item');
      if (it) it.style.display = 'none';   // sin dato → no mostrar "Merval ..." cortado
    }
    if (rp) {
      pintar('riesgo-pais', fmtNumero(rp.valor), rp.stale, ' pb');
      pintar('m-riesgo', fmtNumero(rp.valor), rp.stale, ' pb');
    }
  }

  // ---------------- 5 TARJETAS ----------------
  function pintarTarjetas(datos) {
    if (!document.getElementById('tarjeta-riesgo')) return;
    const hora = datos && datos.generado_ar ? datos.generado_ar.split(' ')[1] : '';

    const rp  = d(datos, 'riesgo_pais');
    const ofi = d(datos, 'dolar_oficial');
    const mep = d(datos, 'dolar_mep');
    const ccl = d(datos, 'dolar_ccl');
    const blue= d(datos, 'dolar_blue');
    const mer = d(datos, 'merval');
    const res = d(datos, 'reservas');
    const bre = d(datos, 'brecha_mep');
    const ipc = d(datos, 'ipc_mensual');
    const emae= d(datos, 'emae');

    if (rp)  tarjeta('tarjeta-riesgo',        fmtNumero(rp.valor) + ' pb', rp.variacion, hora, rp.stale);
    if (ofi) tarjeta('tarjeta-dolar-oficial', fmtPesos(venta(ofi)), ofi.variacion, hora, ofi.stale);
    if (mep) tarjeta('tarjeta-dolar-mep',     fmtPesos(venta(mep)), mep.variacion, hora, mep.stale);
    if (ccl) tarjeta('tarjeta-dolar-ccl',     fmtPesos(venta(ccl)), ccl.variacion, hora, ccl.stale);
    if (blue)tarjeta('tarjeta-dolar-blue',    fmtPesos(venta(blue)), blue.variacion, hora, blue.stale);
    if (mer) tarjeta('tarjeta-merval',        fmtNumero(mer.valor), mer.variacion, hora, mer.stale);
    if (res) tarjeta('tarjeta-reservas',      fmtMillones(res.valor), null, hora, res.stale);
    if (bre) tarjeta('tarjeta-brecha',        (bre.valor >= 0 ? '+' : '') + bre.valor + '%', null, hora, bre.stale);
    if (ipc) tarjeta('tarjeta-ipc',           Number(ipc.valor).toFixed(1) + '%', null, ipc.periodo ? '' : null, ipc.stale);
    if (emae)tarjeta('tarjeta-emae',          fmtNumero(emae.valor), null, hora, emae.stale);

    // Oculta las tarjetas que no tienen dato (no quedan vacías en el carrusel)
    document.querySelectorAll('.tarjeta-dato').forEach(function(el){
      if (el.id === 'tarjeta-banda') return; // la banda se maneja aparte
      const v = el.querySelector('.tarjeta-valor');
      if (v && (v.textContent === '\u2026' || v.textContent.trim() === '')) {
        el.style.display = 'none';
      } else {
        el.style.display = '';
      }
    });

    pintarBanda(d(datos, 'banda'));
  }

  // Termómetro de banda cambiaria (carrusel)
  function pintarBanda(b) {
    const card = document.getElementById('tarjeta-banda');
    if (!card) return;
    if (!b || !b.valor || b.valor.piso == null) { card.style.display = 'none'; return; }
    card.style.display = '';
    const v = b.valor;
    const piso = document.getElementById('banda-piso');
    const techo = document.getElementById('banda-techo');
    const actual = document.getElementById('banda-actual');
    const marc = document.getElementById('banda-marcador');
    if (piso)  piso.textContent  = '$' + Math.round(v.piso).toLocaleString('es-AR');
    if (techo) techo.textContent = '$' + Math.round(v.techo).toLocaleString('es-AR');
    if (v.posicion != null && marc) {
      marc.style.left = v.posicion + '%';
      // color del marcador según zona
      const zona = v.posicion < 50 ? '#27ae60' : (v.posicion < 80 ? '#e8a33d' : '#c0392b');
      marc.style.background = zona;
    }
    if (actual && v.dolar != null) {
      actual.textContent = '$' + Math.round(v.dolar).toLocaleString('es-AR')
        + (v.posicion != null ? ' · ' + v.posicion + '%' : '');
    }
  }

  function tarjeta(id, valor, variacion, hora, stale) {
    const el = document.getElementById(id);
    if (!el) return;
    const elValor = el.querySelector('.tarjeta-valor');
    const elVar   = el.querySelector('.tarjeta-var');
    const elHora  = el.querySelector('.tarjeta-hora');
    if (elValor) {
      elValor.textContent = valor + (stale ? ' *' : '');
      elValor.classList.toggle('dato-stale', !!stale);
    }
    if (elHora) elHora.textContent = hora ? ('ult. ' + hora) : '';
    if (elVar) {
      if (variacion != null) {
        const signo = variacion >= 0 ? '\u25b2' : '\u25bc';
        elVar.className = 'tarjeta-var ' + (variacion >= 0 ? 'sube' : 'baja');
        elVar.textContent = signo + ' ' + Math.abs(variacion).toFixed(2) + '%';
      } else {
        elVar.textContent = '';
      }
    }
  }

  // ---------------- CIERRE DE MERCADO ----------------
  function dentroHorarioCierre() {
    const ahora = new Date();
    const arg = new Date(ahora.toLocaleString('en-US', { timeZone: 'America/Argentina/Buenos_Aires' }));
    const dia = arg.getDay();
    if (dia === 0 || dia === 6) return false;
    const minutos = arg.getHours() * 60 + arg.getMinutes();
    return minutos >= 17 * 60 + 15 && minutos < 19 * 60 + 30;
  }

  function pintarCierre(datos) {
    const widget = document.getElementById('widget-cierre');
    if (!widget) return;
    if (!dentroHorarioCierre()) { widget.style.display = 'none'; return; }
    const mep = d(datos, 'dolar_mep');
    const ccl = d(datos, 'dolar_ccl');
    const mer = d(datos, 'merval');
    const partes = [];
    if (mer) {
      const v = mer.variacion;
      const txtVar = (v != null)
        ? ' <span class="' + (v >= 0 ? 'sube' : 'baja') + '">' + (v >= 0 ? '+' : '') + v.toFixed(2) + '%</span>' : '';
      partes.push('<div class="cierre-item"><span class="cierre-label">Merval</span> <strong>' + fmtNumero(mer.valor) + '</strong>' + txtVar + '</div>');
    }
    if (mep) partes.push('<div class="cierre-item"><span class="cierre-label">Dolar MEP</span> <strong>' + fmtPesos(venta(mep)) + '</strong></div>');
    if (ccl) partes.push('<div class="cierre-item"><span class="cierre-label">Dolar CCL</span> <strong>' + fmtPesos(venta(ccl)) + '</strong></div>');
    if (!partes.length) { widget.style.display = 'none'; return; }
    const body = document.getElementById('cierre-body');
    if (body) { body.innerHTML = partes.join(''); widget.style.display = 'block'; }
  }

  // ---------------- CARGA UNIFICADA ----------------
  async function actualizarDatos() {
    const datos = await fetchJSON(DATOS_URL);
    if (!datos) return;
    pintarTicker(datos);
    pintarTarjetas(datos);
    // pintarCierre eliminado: el bloque "Cierre de mercado" era redundante
    // con el ticker y el carrusel. Cada dato va en un solo lugar.
  }

  // ---------------- CLIMA ----------------
  async function actualizarClima() {
    const el = document.getElementById('clima-widget');
    if (!el) return;
    const data = await fetchJSON(API_CLIMA);
    if (data && data.current) {
      const temp = Math.round(data.current.temperature_2m);
      const emoji = CLIMA_EMOJI[data.current.weather_code] || '';
      el.textContent = emoji + ' ' + temp + '\u00b0';
    }
  }

  // ---------------- FULBITO ----------------
  async function actualizarFulbito() {
    const data = await fetchJSON('/data/fulbito.json');
    const bar = document.getElementById('fulbito-bar');
    if (!bar) return;
    if (!data || !data.partidos || !data.partidos.length) { bar.style.display = 'none'; return; }
    const cont = document.getElementById('fulbito-partidos');
    if (cont) {
      cont.innerHTML = data.partidos.map(function(p){
        return '<span class="fulbito-partido">' + p.equipos + '<span class="hora">' + p.hora + '</span></span>';
      }).join('');
      bar.style.display = 'block';
    }
  }

  // ---------------- FINGERPRINT ----------------
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
  window.PPA = window.PPA || {};
  window.PPA.getFingerprint = getFingerprint;

  // ---------------- CARRUSEL AUTO-SCROLL ----------------
  function iniciarCarrusel() {
    const cont = document.getElementById('carrusel-datos');
    if (!cont) return;
    let pausado = false;
    // Pausa al pasar mouse o tocar
    cont.addEventListener('mouseenter', function(){ pausado = true; });
    cont.addEventListener('mouseleave', function(){ pausado = false; });
    cont.addEventListener('touchstart', function(){ pausado = true; }, {passive:true});
    cont.addEventListener('touchend',   function(){ setTimeout(function(){ pausado = false; }, 2000); });

    const VEL = 0.5; // px por frame
    function paso() {
      if (!pausado && cont.scrollWidth > cont.clientWidth) {
        cont.scrollLeft += VEL;
        // loop suave: al llegar al final, vuelve al inicio
        if (cont.scrollLeft + cont.clientWidth >= cont.scrollWidth - 1) {
          cont.scrollLeft = 0;
        }
      }
      requestAnimationFrame(paso);
    }
    requestAnimationFrame(paso);
  }

  // ---------------- INICIO ----------------
  function iniciar() {
    actualizarDatos();
    actualizarClima();
    actualizarFulbito();
    iniciarCarrusel();
    setInterval(actualizarDatos,   REFRESH_MS);
    setInterval(actualizarClima,   REFRESH_CLIMA_MS);
    setInterval(actualizarFulbito, REFRESH_FULBITO_MS);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }

})();

// ================================================================
// CABECERA STICKY + MENÚ HAMBURGUESA
// ================================================================
(function() {
  const cab     = document.getElementById('cabecera-ppa');
  const spacer  = document.getElementById('cab-spacer');
  const overlay = document.getElementById('menu-overlay');
  const drawer  = document.getElementById('menu-drawer');
  const btnAbrir  = document.getElementById('btn-menu');
  const btnCerrar = document.getElementById('btn-menu-cerrar');

  // ── Sticky al scrollear ──
  if (cab && spacer) {
    function checkSticky() {
      const es = window.scrollY > 10;
      cab.classList.toggle('sticky', es);
      cab.classList.toggle('expandida', !es);
      spacer.classList.toggle('sticky', es);
    }
    window.addEventListener('scroll', checkSticky, { passive: true });
    checkSticky();
  }

  // ── Menú hamburguesa ──
  function abrirMenu() {
    if (overlay) overlay.classList.add('abierto');
    if (drawer)  drawer.classList.add('abierto');
    document.body.style.overflow = 'hidden';
  }
  function cerrarMenu() {
    if (overlay) overlay.classList.remove('abierto');
    if (drawer)  drawer.classList.remove('abierto');
    document.body.style.overflow = '';
  }

  if (btnAbrir)  btnAbrir.addEventListener('click', abrirMenu);
  if (btnCerrar) btnCerrar.addEventListener('click', cerrarMenu);
  if (overlay)   overlay.addEventListener('click', cerrarMenu);

  // Cerrar con Escape
  document.addEventListener('keydown', e => { if (e.key === 'Escape') cerrarMenu(); });
})();
