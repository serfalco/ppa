/* =================================================================
   PPA Tablero v3.1 — Lee UN SOLO /data/datos.json ya cocido.
   Antes le pegaba a ~15 APIs desde el navegador (lento y fragil).
   Ahora GitHub Actions cocina el JSON y el navegador solo lo lee.
   Cada dato trae su flag stale; los datos sin valor quedan en s/d.
   ================================================================= */

(function() {
  'use strict';

  const DATOS_URL  = '/data/datos.json';
  const REFRESH_MS = 15 * 60 * 1000;

  function $(id){ return document.getElementById(id); }
  function pesos(n){ return '$' + Math.round(n).toLocaleString('es-AR'); }
  function num(n, dec){
    dec = dec || 0;
    return dec > 0 ? Number(n).toFixed(dec) : Math.round(n).toLocaleString('es-AR');
  }
  function pct(n){ return Number(n).toFixed(1) + '%'; }
  function millones(n){ return 'USD ' + (n/1000).toFixed(1) + ' MM'; }

  async function fetchJSON(url){
    const c = new AbortController();
    const t = setTimeout(function(){ c.abort(); }, 12000);
    try {
      const r = await fetch(url, { signal: c.signal, cache: 'no-store' });
      clearTimeout(t);
      if (!r.ok) throw new Error('HTTP ' + r.status);
      return await r.json();
    } catch(e) {
      clearTimeout(t);
      console.warn('[Tablero] error:', url, e.message);
      return null;
    }
  }

  function d(datos, clave){
    if (!datos || !datos.datos) return null;
    return datos.datos[clave] || null;
  }
  function venta(item){
    if (!item || item.valor == null) return null;
    return (typeof item.valor === 'object') ? item.valor.venta : item.valor;
  }
  function compra(item){
    if (!item || item.valor == null) return null;
    return (typeof item.valor === 'object') ? item.valor.compra : item.valor;
  }

  // set: pinta texto en un id; si valor null deja s/d; marca stale
  function set(id, texto, stale){
    const el = $(id);
    if (!el) return;
    if (texto != null) {
      el.textContent = texto + (stale ? ' *' : '');
      el.classList.toggle('dato-stale', !!stale);
      if (stale) el.title = '* Ultimo valor conocido (dato desactualizado)';
    }
  }

  // variacion con flecha
  function setVar(id, variacion){
    const el = $(id);
    if (!el || variacion == null) return;
    const signo = variacion >= 0 ? '\u25b2 +' : '\u25bc ';
    el.textContent = signo + Math.abs(variacion).toFixed(2) + '%';
    el.className = 'dato-var ' + (variacion >= 0 ? 'sube' : 'baja');
  }

  function pintarTablero(datos){
    // ---- DOLARES ----
    const ofi = d(datos,'dolar_oficial'), mep = d(datos,'dolar_mep'),
          ccl = d(datos,'dolar_ccl'), blue = d(datos,'dolar_blue'),
          may = d(datos,'dolar_mayorista'), tar = d(datos,'dolar_tarjeta'),
          cri = d(datos,'dolar_cripto'), brecha = d(datos,'brecha_mep');

    if (ofi) { set('t-dol-oficial-compra', pesos(compra(ofi)), ofi.stale);
               set('t-dol-oficial-venta',  pesos(venta(ofi)),  ofi.stale); }
    if (mep) { set('t-dol-mep', pesos(venta(mep)), mep.stale); setVar('t-dol-mep-var', mep.variacion); }
    if (ccl) { set('t-dol-ccl', pesos(venta(ccl)), ccl.stale); setVar('t-dol-ccl-var', ccl.variacion); }
    if (blue){ set('t-dol-blue-compra', pesos(compra(blue)), blue.stale);
               set('t-dol-blue-venta',  pesos(venta(blue)),  blue.stale); }
    if (may) set('t-dol-mayorista', pesos(venta(may)), may.stale);
    if (tar) set('t-dol-tarjeta',   pesos(venta(tar)), tar.stale);
    if (cri) set('t-dol-cripto',    pesos(venta(cri)), cri.stale);
    if (brecha) set('t-brecha-mep', (brecha.valor >= 0 ? '+' : '') + brecha.valor + '%', brecha.stale);

    // ---- MERCADO ----
    const mer = d(datos,'merval'), rp = d(datos,'riesgo_pais'), res = d(datos,'reservas');
    if (mer) { set('t-merval', num(mer.valor), mer.stale); setVar('t-merval-var', mer.variacion); }
    if (rp)  set('t-riesgo', num(rp.valor) + ' pb', rp.stale);
    if (res) { set('t-reservas', millones(res.valor), res.stale);
               set('t-reservas-macro', millones(res.valor), res.stale); }

    // ---- MULC (BCRA compró/vendió en el mercado) ----
    const mulc = d(datos, 'mulc');
    const mulcLabel = document.getElementById('t-mulc-label');
    const mulcMonto = document.getElementById('t-mulc-monto');
    if (mulc && mulc.valor && mulc.valor.operacion && mulcLabel) {
      const op = mulc.valor.operacion.toLowerCase();
      const monto = mulc.valor.monto;
      const unidad = mulc.unidad || 'MM USD';
      const esCompra = op.includes('compr');
      mulcLabel.textContent = (esCompra ? '🟢 Compró' : '🔴 Vendió') + ' US$ ' + monto + ' M';
      mulcLabel.className = 'bcra-mulc ' + (esCompra ? 'compro' : 'vendio');
      if (mulcMonto) mulcMonto.textContent = unidad + (mulc.stale ? ' *' : '');
    } else if (mulcLabel) {
      mulcLabel.textContent = 's/d';
    }

    // ---- CONTEXTO: variación diaria / mensual / anual ----
    function ctx(id, valor, tipo) {
      // tipo: 'pesos' | 'pct' | 'pb' | 'usd'
      const el = document.getElementById(id);
      if (!el || valor == null) return;
      const signo = valor >= 0 ? '+' : '';
      let txt = '', cls = valor >= 0 ? 'sube' : 'baja';
      if (tipo === 'pct') txt = signo + Number(valor).toFixed(1) + '%';
      else if (tipo === 'pb') txt = signo + Math.round(valor) + ' pb';
      else if (tipo === 'usd') txt = signo + 'USD ' + Math.round(Math.abs(valor)) + ' M';
      else txt = signo + Number(valor).toFixed(2);
      el.textContent = txt;
      el.className = 'ctx-item ' + cls;
    }

    // Reservas contexto
    if (res && res.variacion != null) ctx('t-reservas-var-dia', res.variacion, 'pct');

    // Riesgo contexto
    if (rp && rp.variacion != null) ctx('t-riesgo-var-dia', rp.variacion, 'pb');

    // TCRM contexto
    if (tcrm && tcrm.variacion != null) ctx('t-tcrm-var-dia', tcrm.variacion, 'pct');

    // IPC contexto interanual (si viene en el dato)
    const ipcAnual = d(datos, 'ipc_interanual');
    if (ipcAnual) {
      const el = document.getElementById('t-ipc-interanual-ctx');
      if (el) { el.textContent = 'i.a. ' + pct(ipcAnual.valor); el.className = 'ctx-item'; }
    }

    // bonos AL30/GD30/GD35: pendientes de BYMA EOD -> quedan en s/d

    // ---- MACRO + BCRA monetario ----
    const ipc  = d(datos,'ipc_mensual'), emae = d(datos,'emae'),
          bm   = d(datos,'base_monetaria'),
          m2   = d(datos,'m2_privado'),
          circ = d(datos,'circulacion'),
          badl = d(datos,'badlar'),
          baib = d(datos,'call_baibar');

    if (bm)   set('t-base-monetaria', millones(bm.valor)   + ' M$', bm.stale);
    if (m2)   set('t-m2-privado',     millones(m2.valor)   + ' M$', m2.stale);
    if (circ) set('t-circulacion',    millones(circ.valor) + ' M$', circ.stale);

    // BADLAR: aparece en el bloque BCRA (t-badlar) y en Macro (t-badlar-macro)
    if (badl) {
      const badlStr = num(badl.valor, 2) + '%';
      set('t-badlar',       badlStr, badl.stale);
      set('t-badlar-macro', badlStr, badl.stale);
    }
    if (baib) set('t-baibar', num(baib.valor, 2) + '%', baib.stale);
    if (ipc) { set('t-ipc-mensual', pct(ipc.valor), ipc.stale);
               if (ipc.periodo) set('t-ipc-mensual-fecha', ipc.periodo); }
    if (emae) set('t-emae', num(emae.valor,1), emae.stale);

    const uva = d(datos,'uva');
    if (uva) set('t-uva', num(uva.valor, 2), uva.stale);

    // ---- SECTOR EXTERNO ----
    const exp = d(datos,'exportaciones'), imp = d(datos,'importaciones'),
          saldo = d(datos,'saldo_comercial'), tcrm = d(datos,'tcrm');
    if (exp) set('t-exportaciones', 'USD ' + num(exp.valor) + ' M', exp.stale);
    if (imp) set('t-importaciones', 'USD ' + num(imp.valor) + ' M', imp.stale);
    if (saldo) {
      const el = $('t-saldo-comercial');
      if (el) {
        el.textContent = (saldo.valor >= 0 ? '+' : '') + 'USD ' + num(saldo.valor) + ' M' + (saldo.stale ? ' *' : '');
        el.className = 'dato-valor dato-grande ' + (saldo.valor >= 0 ? 'sube' : 'baja');
      }
    }
    if (tcrm) set('t-tcrm', num(tcrm.valor,2), tcrm.stale);

    // ---- EMPLEO ----
    const des = d(datos,'desocupacion');
    if (des) { set('t-desocupacion', pct(des.valor), des.stale);
               if (des.periodo) set('t-desocupacion-fecha', des.periodo); }
    // empleo, actividad, salarios, smvm, cba, cbt: pendientes de IDs validos
    // FISCAL: pendiente de integrar series de Hacienda

    // ---- BANDA CAMBIARIA (velometro) ----
    pintarVelo(d(datos, 'banda'));
  }

  function pintarVelo(b) {
    const card = document.getElementById('banda-velo-card');
    if (!card) return;
    if (!b || !b.valor || b.valor.piso == null) { card.style.display = 'none'; return; }
    card.style.display = '';
    const v = b.valor;
    const piso = document.getElementById('banda-velo-piso');
    const techo = document.getElementById('banda-velo-techo');
    const num = document.getElementById('banda-velo-num');
    const sub = document.getElementById('banda-velo-sub');
    const aguja = document.getElementById('banda-aguja');
    if (piso)  piso.textContent  = 'Piso $' + Math.round(v.piso).toLocaleString('es-AR');
    if (techo) techo.textContent = 'Techo $' + Math.round(v.techo).toLocaleString('es-AR');
    if (num && v.dolar != null) num.textContent = '$' + Math.round(v.dolar).toLocaleString('es-AR');
    if (sub && v.posicion != null) sub.textContent = v.posicion + '% del recorrido de la banda';
    if (aguja && v.posicion != null) {
      const ang = (v.posicion / 100) * 180 - 90;
      aguja.setAttribute('transform', 'rotate(' + ang + ' 110 115)');
    }
  }

  async function cargar(){
    const datos = await fetchJSON(DATOS_URL);
    if (!datos) return;
    pintarTablero(datos);
  }

  cargar();
  setInterval(cargar, REFRESH_MS);

})();
