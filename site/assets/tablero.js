/* =================================================================
   PPA Tablero v3 — Carga todos los datos económicos desde APIs
   Fallback: localStorage para último valor conocido
   Nunca muestra "—", muestra "s/d" solo si no hay caché
   ================================================================= */

(function() {
  'use strict';

  const REFRESH_MS    = 15 * 60 * 1000;
  const REFRESH_INF_MS = 60 * 60 * 1000; // datos de baja frecuencia: 1 hora

  // APIs
  const APIS = {
    // Dólares
    oficial:    'https://dolarapi.com/v1/dolares/oficial',
    mep:        'https://dolarapi.com/v1/dolares/bolsa',
    ccl:        'https://dolarapi.com/v1/dolares/contadoconliqui',
    blue:       'https://dolarapi.com/v1/dolares/blue',
    mayorista:  'https://dolarapi.com/v1/dolares/mayorista',
    tarjeta:    'https://dolarapi.com/v1/dolares/tarjeta',
    cripto:     'https://dolarapi.com/v1/dolares/cripto',
    // Mercado / macro
    merval:     'https://api.argentinadatos.com/v1/finanzas/indices/merval/ultimo',
    riesgo:     'https://api.argentinadatos.com/v1/finanzas/indices/riesgo-pais/ultimo',
    // Series datos.gob.ar (IPC, EMAE, reservas, empleo, fiscal, comercio exterior, etc.)
    // IPC nivel general mensual: serie 148.3_INIVELGBA_DICI_M_26 (INDEC base dic 2016)
    ipc_mensual:   'https://apis.datos.gob.ar/series/api/series/?ids=148.3_INIVELGBA_DICI_M_26&last=13&format=json',
    // EMAE mensual desestacionalizado
    emae:          'https://apis.datos.gob.ar/series/api/series/?ids=143.3_NO_PR_2004_A_21&last=2&format=json',
    // Reservas internacionales BCRA (millones USD)
    reservas:      'https://apis.datos.gob.ar/series/api/series/?ids=174.1_T_1.0_0_100&last=2&format=json',
    // Exportaciones FOB (millones USD)
    exportaciones: 'https://apis.datos.gob.ar/series/api/series/?ids=37.3_EXPFOBNM_0_M_22&last=2&format=json',
    // Importaciones CIF (millones USD)
    importaciones: 'https://apis.datos.gob.ar/series/api/series/?ids=37.3_IMPCIFSM_0_M_23&last=2&format=json',
    // TCRM
    tcrm:          'https://apis.datos.gob.ar/series/api/series/?ids=116.4_TCRM_0_D_36&last=2&format=json',
    // Desocupación (EPH)
    desocupacion:  'https://apis.datos.gob.ar/series/api/series/?ids=41.1_DEOCT_TOTAL_0_T_26&last=1&format=json',
    // Empleo
    tasa_empleo:   'https://apis.datos.gob.ar/series/api/series/?ids=41.1_TEOCT_TOTAL_0_T_26&last=1&format=json',
    // Actividad
    tasa_actividad:'https://apis.datos.gob.ar/series/api/series/?ids=41.1_TAOCT_TOTAL_0_T_26&last=1&format=json',
    // Índice salarios sector privado
    salarios:      'https://apis.datos.gob.ar/series/api/series/?ids=148.3_ICTOTAL_DICI_M_16&last=2&format=json',
  };

  // ---------------------------------------------------------------
  // CACHE
  // ---------------------------------------------------------------
  function save(key, val) {
    try { localStorage.setItem('tab_' + key, JSON.stringify({ v: val, t: Date.now() })); } catch(e) {}
  }
  function load(key) {
    try {
      const r = localStorage.getItem('tab_' + key);
      if (!r) return null;
      return JSON.parse(r).v;
    } catch(e) { return null; }
  }

  // ---------------------------------------------------------------
  // HELPERS
  // ---------------------------------------------------------------
  async function fetchJ(url) {
    const c = new AbortController();
    const t = setTimeout(() => c.abort(), 12000);
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

  function $ (id) { return document.getElementById(id); }

  function set(id, txt, cacheKey) {
    const el = $(id);
    if (!el) return;
    if (txt !== null && txt !== undefined) {
      el.textContent = txt;
      el.classList.remove('dato-stale');
      if (cacheKey) save(cacheKey, txt);
    } else {
      const cached = cacheKey ? load(cacheKey) : null;
      if (cached !== null) {
        el.textContent = cached + ' *';
        el.classList.add('dato-stale');
        el.title = '* Último valor conocido (dato desactualizado)';
      }
    }
  }

  function pesos(n) { return '$' + Math.round(n).toLocaleString('es-AR'); }
  function num(n, dec) {
    if (dec === undefined) dec = 0;
    return dec > 0 ? Number(n).toFixed(dec) : Math.round(n).toLocaleString('es-AR');
  }
  function pct(n) { return Number(n).toFixed(1) + '%'; }
  function millones(n) { return 'USD ' + (n/1000).toFixed(1) + ' MM'; }
  function millonesPesos(n) { return '$' + (n/1000000).toFixed(1) + ' B'; } // billones

  function varHtml(variacion, elId) {
    const el = $(elId);
    if (!el || variacion === null || variacion === undefined) return;
    const signo = variacion >= 0 ? '▲ +' : '▼ ';
    el.textContent = signo + Math.abs(variacion).toFixed(2) + '%';
    el.className = 'dato-var ' + (variacion >= 0 ? 'sube' : 'baja');
  }

  // Extrae el valor de la serie de datos.gob.ar (último dato no nulo)
  function serieVal(data, idx) {
    idx = idx || 0;
    if (!data || !data.data) return null;
    for (let i = data.data.length - 1; i >= 0; i--) {
      if (data.data[i][1] !== null) return data.data[i][idx + 1];
    }
    return null;
  }
  function serieFecha(data) {
    if (!data || !data.data) return null;
    for (let i = data.data.length - 1; i >= 0; i--) {
      if (data.data[i][1] !== null) return data.data[i][0];
    }
    return null;
  }

  // ---------------------------------------------------------------
  // BLOQUE 1: DÓLARES
  // ---------------------------------------------------------------
  async function cargarDolares() {
    const [oficial, mep, ccl, blue, mayor, tarjeta, cripto] = await Promise.all([
      fetchJ(APIS.oficial), fetchJ(APIS.mep), fetchJ(APIS.ccl),
      fetchJ(APIS.blue), fetchJ(APIS.mayorista), fetchJ(APIS.tarjeta), fetchJ(APIS.cripto),
    ]);

    set('t-dol-oficial-compra', oficial?.compra ? pesos(oficial.compra) : null, 'dol_of_c');
    set('t-dol-oficial-venta',  oficial?.venta  ? pesos(oficial.venta)  : null, 'dol_of_v');
    set('t-dol-mep',  mep?.venta  ? pesos(mep.venta)  : null, 'dol_mep');
    set('t-dol-ccl',  ccl?.venta  ? pesos(ccl.venta)  : null, 'dol_ccl');
    set('t-dol-blue-compra', blue?.compra ? pesos(blue.compra) : null, 'dol_bl_c');
    set('t-dol-blue-venta',  blue?.venta  ? pesos(blue.venta)  : null, 'dol_bl_v');
    set('t-dol-mayorista', mayor?.venta   ? pesos(mayor.venta) : null, 'dol_may');
    set('t-dol-tarjeta',   tarjeta?.venta ? pesos(tarjeta.venta) : null, 'dol_tar');
    set('t-dol-cripto',    cripto?.venta  ? pesos(cripto.venta)  : null, 'dol_cri');

    // Brecha MEP / Oficial
    if (mep?.venta && oficial?.venta) {
      const brecha = ((mep.venta / oficial.venta - 1) * 100).toFixed(1);
      const signo = brecha >= 0 ? '+' : '';
      set('t-brecha-mep', signo + brecha + '%', 'brecha_mep');
    } else {
      set('t-brecha-mep', null, 'brecha_mep');
    }

    varHtml(mep?.variacion,  't-dol-mep-var');
    varHtml(ccl?.variacion,  't-dol-ccl-var');
  }

  // ---------------------------------------------------------------
  // BLOQUE 2: MERCADO
  // ---------------------------------------------------------------
  async function cargarMercado() {
    const [merval, riesgo, reservas] = await Promise.all([
      fetchJ(APIS.merval), fetchJ(APIS.riesgo), fetchJ(APIS.reservas),
    ]);

    set('t-merval', merval?.valor !== undefined ? num(merval.valor) : null, 'merval');
    varHtml(merval?.variacion, 't-merval-var');
    set('t-riesgo', riesgo?.valor !== undefined ? num(riesgo.valor) + ' pb' : null, 'riesgo');
    const resVal = serieVal(reservas);
    set('t-reservas', resVal !== null ? millones(resVal) : null, 'reservas');
    set('t-reservas-macro', resVal !== null ? millones(resVal) : null, 'reservas_macro');

    // Bonos: s/d hasta integrar BYMA delayed
    ['t-al30','t-gd30','t-gd35'].forEach(id => {
      const el = $(id);
      if (el && el.textContent === 's/d') {
        el.title = 'Datos de bonos pendientes de integrar (BYMA delayed)';
      }
    });
  }

  // ---------------------------------------------------------------
  // BLOQUE 3: MACRO (baja frecuencia)
  // ---------------------------------------------------------------
  async function cargarMacro() {
    const [ipc, emae] = await Promise.all([
      fetchJ(APIS.ipc_mensual), fetchJ(APIS.emae),
    ]);

    if (ipc && ipc.data && ipc.data.length > 1) {
      const n = ipc.data.length;
      const ultimo = ipc.data[n - 1];
      const anterior = ipc.data[n - 2];
      if (ultimo && ultimo[1] !== null && anterior && anterior[1] !== null) {
        const variacion = ((ultimo[1] / anterior[1] - 1) * 100);
        set('t-ipc-mensual', pct(variacion), 'ipc_mensual');
        // fecha en formato "mm/yyyy"
        const f = ultimo[0].substring(0, 7);
        set('t-ipc-mensual-fecha', f, 'ipc_fecha');

        // Interanual: comparar con mismo mes del año anterior (12 posiciones atrás)
        if (n >= 13) {
          const hace12 = ipc.data[n - 13];
          if (hace12 && hace12[1] !== null) {
            const ia = ((ultimo[1] / hace12[1] - 1) * 100);
            set('t-ipc-interanual', pct(ia), 'ipc_ia');
          }
        }

        // Acumulado año: comparar con diciembre del año anterior
        // Buscar el último dato de diciembre en la serie
        let dicAnterior = null;
        const anioActual = parseInt(ultimo[0].substring(0, 4));
        for (let i = n - 1; i >= 0; i--) {
          if (ipc.data[i][0].startsWith((anioActual - 1) + '-12')) {
            dicAnterior = ipc.data[i][1];
            break;
          }
        }
        if (dicAnterior !== null) {
          const acum = ((ultimo[1] / dicAnterior - 1) * 100);
          set('t-ipc-acumulado', pct(acum), 'ipc_acum');
        }
      }
    } else {
      set('t-ipc-mensual', null, 'ipc_mensual');
      set('t-ipc-interanual', null, 'ipc_ia');
    }

    if (emae && emae.data && emae.data.length >= 2) {
      const ultimo = emae.data[emae.data.length - 1];
      const anterior = emae.data[emae.data.length - 2];
      if (ultimo[1] !== null && anterior[1] !== null) {
        const varMes = ((ultimo[1] / anterior[1] - 1) * 100);
        set('t-emae', num(ultimo[1], 1), 'emae');
        set('t-emae-var', (varMes >= 0 ? '▲' : '▼') + ' ' + Math.abs(varMes).toFixed(1) + '% mensual', 'emae_var');
      }
    } else {
      set('t-emae', null, 'emae');
    }
  }

  // ---------------------------------------------------------------
  // BLOQUE 4: SECTOR EXTERNO
  // ---------------------------------------------------------------
  async function cargarExterno() {
    const [exp, imp, tcrm] = await Promise.all([
      fetchJ(APIS.exportaciones), fetchJ(APIS.importaciones), fetchJ(APIS.tcrm),
    ]);

    const expVal = serieVal(exp);
    const impVal = serieVal(imp);
    set('t-exportaciones', expVal !== null ? 'USD ' + num(expVal) + ' M' : null, 'exp');
    set('t-importaciones', impVal !== null ? 'USD ' + num(impVal) + ' M' : null, 'imp');

    if (expVal !== null && impVal !== null) {
      const saldo = expVal - impVal;
      const txt = (saldo >= 0 ? '+' : '') + 'USD ' + num(saldo) + ' M';
      const el = $('t-saldo-comercial');
      if (el) {
        el.textContent = txt;
        el.className = 'dato-valor dato-grande ' + (saldo >= 0 ? 'sube' : 'baja');
      }
      save('saldo', txt);
    } else {
      set('t-saldo-comercial', null, 'saldo');
    }

    const tcrmVal = serieVal(tcrm);
    set('t-tcrm', tcrmVal !== null ? num(tcrmVal, 2) : null, 'tcrm');
  }

  // ---------------------------------------------------------------
  // BLOQUE 5: EMPLEO Y SALARIOS
  // ---------------------------------------------------------------
  async function cargarEmpleo() {
    const [desocu, empleo, activ, salarios] = await Promise.all([
      fetchJ(APIS.desocupacion), fetchJ(APIS.tasa_empleo),
      fetchJ(APIS.tasa_actividad), fetchJ(APIS.salarios),
    ]);

    const desocuVal = serieVal(desocu);
    set('t-desocupacion', desocuVal !== null ? pct(desocuVal) : null, 'desocu');
    const desocuFecha = serieFecha(desocu);
    if (desocuFecha) set('t-desocupacion-fecha', desocuFecha.substring(0, 7), 'desocu_fecha');

    set('t-empleo',   serieVal(empleo)  !== null ? pct(serieVal(empleo))  : null, 'empleo');
    set('t-actividad', serieVal(activ) !== null ? pct(serieVal(activ))  : null, 'activ');
    set('t-salarios-privado', serieVal(salarios) !== null ? num(serieVal(salarios)) : null, 'salarios');

    // SMVM, CBT, CBA: datos.gob.ar (frecuencia baja, a confirmar IDs exactos)
    ['t-smvm', 't-cbt', 't-cba'].forEach(id => {
      const el = $(id);
      if (el && (el.textContent === '…' || el.textContent === '')) {
        const cached = load(id.replace('t-',''));
        if (cached) { el.textContent = cached; el.classList.add('dato-stale'); }
      }
    });
  }

  // ---------------------------------------------------------------
  // BLOQUE 6: FISCAL (datos de baja frecuencia)
  // ---------------------------------------------------------------
  async function cargarFiscal() {
    // Los IDs de series fiscales de Hacienda hay que confirmarlos con la API
    // Por ahora mostramos caché o placeholder
    ['t-recaudacion','t-iva','t-ganancias','t-retenciones',
     't-resultado-primario','t-resultado-financiero','t-base-monetaria','t-tasa-politica'].forEach(id => {
      const ckey = id.replace('t-','').replace(/-/g,'_');
      const cached = load(ckey);
      const el = $(id);
      if (el && cached) {
        el.textContent = cached + ' *';
        el.classList.add('dato-stale');
        el.title = '* Último valor conocido';
      }
    });
    // TODO: integrar series fiscales de datos.gob.ar cuando confirmemos IDs
  }

  // ---------------------------------------------------------------
  // INIT
  // ---------------------------------------------------------------
  async function cargarTodo() {
    // Datos de alta frecuencia
    await Promise.all([cargarDolares(), cargarMercado()]);
    // Datos de baja frecuencia
    await Promise.all([cargarMacro(), cargarExterno(), cargarEmpleo(), cargarFiscal()]);
  }

  cargarTodo();
  setInterval(cargarDolares,  REFRESH_MS);
  setInterval(cargarMercado,  REFRESH_MS);
  setInterval(cargarMacro,    REFRESH_INF_MS);
  setInterval(cargarExterno,  REFRESH_INF_MS);
  setInterval(cargarEmpleo,   REFRESH_INF_MS);

})();
