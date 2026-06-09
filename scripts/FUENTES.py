"""
PPA — FUENTES.py v2
Lista completa de fuentes RSS organizadas por categoría y tier.

TIERS:
  1 = medios generales, cache 6hs, corren en cada edición
  2 = sectoriales especializados, cache 24hs, corren en desayuno
  3 = institucionales/expectativas, cache 48hs, corren cada 2 días

La clave del dict es siempre "web" (no "url") por compatibilidad con el código existente.
"""

FUENTES = [

    # ================================================================
    # TIER 1 — Medios generales (cache 6hs)
    # ================================================================
    {"id":"ambito_fin",     "nombre":"Ámbito Finanzas",        "web":"https://www.ambito.com/rss/finanzas.xml",                          "categoria":"Finanzas",    "tier":1, "activa":True},
    {"id":"ambito_neg",     "nombre":"Ámbito Negocios",        "web":"https://www.ambito.com/rss/negocios.xml",                          "categoria":"Macro",       "tier":1, "activa":True},
    {"id":"ambito_autos",   "nombre":"Ámbito Autos",           "web":"https://www.ambito.com/rss/autos.xml",                             "categoria":"Automotor",   "tier":1, "activa":True},
    {"id":"ambito_fisc",    "nombre":"Ámbito Fiscal",          "web":"https://www.ambito.com/rss/novedades-fiscales.xml",                "categoria":"Fiscal",      "tier":1, "activa":True},
    {"id":"lanacion",       "nombre":"La Nación Economía",     "web":"https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/economia/?outputType=xml", "categoria":"Macro", "tier":1, "activa":True},
    {"id":"clarin",         "nombre":"Clarín Economía",        "web":"https://www.clarin.com/rss/economia/",                             "categoria":"Macro",       "tier":1, "activa":True},
    {"id":"cronista_fin",   "nombre":"El Cronista Finanzas",   "web":"https://www.cronista.com/rss/finanzas-mercados.xml",               "categoria":"Mercados",    "tier":1, "activa":True},
    {"id":"pagina12",       "nombre":"Página 12 Economía",     "web":"https://www.pagina12.com.ar/rss/secciones/economia",               "categoria":"Macro",       "tier":1, "activa":True},
    {"id":"bae",            "nombre":"BAE Negocios",           "web":"https://www.baenegocios.com/rss",                                  "categoria":"Macro",       "tier":1, "activa":True},
    {"id":"infobae",        "nombre":"Infobae Economía",       "web":"https://www.infobae.com/feeds/rss/economia/",                      "categoria":"Macro",       "tier":1, "activa":True},
    {"id":"eleconomista",   "nombre":"El Economista Finanzas", "web":"https://eleconomista.com.ar/finanzas/feed/",                       "categoria":"Finanzas",    "tier":1, "activa":True},
    {"id":"eleconomista_i", "nombre":"El Economista Internacional","web":"https://eleconomista.com.ar/internacional/feed/",              "categoria":"Internacional","tier":1, "activa":True},
    {"id":"eleconomista_n", "nombre":"El Economista Negocios", "web":"https://eleconomista.com.ar/negocios/feed/",                       "categoria":"Macro",       "tier":1, "activa":True},

    # ================================================================
    # TIER 2 — Sectoriales (cache 24hs)
    # ================================================================

    # Energía / Minería
    {"id":"mejorenergia",   "nombre":"Mejor Energía",          "web":"https://www.mejorenergia.com.ar/feed/",                            "categoria":"Energía",     "tier":2, "activa":True},
    {"id":"dataenergia",    "nombre":"Data Energía",           "web":"https://dataenergia.ar/feed/",                                     "categoria":"Energía",     "tier":2, "activa":True},
    {"id":"rionegro_en",    "nombre":"Río Negro Energía",      "web":"https://www.rionegro.com.ar/energia/feed/",                        "categoria":"Energía",     "tier":2, "activa":True},
    {"id":"noticiasnet_en", "nombre":"NoticiasNet Energía",    "web":"https://www.noticiasnet.com.ar/rss/energia-hoy/",                  "categoria":"Energía",     "tier":2, "activa":True},
    {"id":"shale24",       "nombre":"Shale24",                "web":"https://www.shale24.com/feed/",                                    "categoria":"Energía",     "tier":2, "activa":True},
    {"id":"econojournal",  "nombre":"EconoJournal",           "web":"https://econojournal.com.ar/feed/",                                "categoria":"Energía",     "tier":2, "activa":True},

    # Agro
    {"id":"bcr",            "nombre":"Bolsa de Cereales Rosario","web":"https://www.bcr.com.ar/feed.xml",                               "categoria":"Agro",        "tier":2, "activa":True},
    {"id":"magyp",          "nombre":"Ministerio de Agricultura","web":"https://www.argentina.gob.ar/noticias/rss-agricultura.xml",      "categoria":"Agro",        "tier":2, "activa":True},
    {"id":"investing_comm", "nombre":"Investing Commodities",  "web":"https://es.investing.com/rss/news_287.rss",                        "categoria":"Agro",        "tier":2, "activa":True},

    # Comex
    {"id":"tradenews",      "nombre":"Trade News",             "web":"https://tradenews.com.ar/feed/",                                   "categoria":"Comex",       "tier":2, "activa":True},
    {"id":"aduananews",     "nombre":"Aduana News",            "web":"https://aduananews.com/feed/",                                     "categoria":"Comex",       "tier":2, "activa":True},
    {"id":"mercojuris",     "nombre":"Mercojuris",             "web":"https://mercojuris.com/feed/",                                     "categoria":"Comex",       "tier":2, "activa":True},

    # Automotor
    {"id":"motorweb",       "nombre":"Motorweb Argentina",     "web":"https://motorwebargentina.com/feed/",                              "categoria":"Automotor",   "tier":2, "activa":True},
    {"id":"visionmotor",    "nombre":"Vision Motor",           "web":"https://visionmotor.com/feed/",                                    "categoria":"Automotor",   "tier":2, "activa":True},
    {"id":"autoblog",       "nombre":"Autoblog Argentina",     "web":"https://autoblog.com.ar/feed/",                                    "categoria":"Automotor",   "tier":2, "activa":True},
    {"id":"autoblog_nov",   "nombre":"Autoblog Novedades",     "web":"https://autoblog.com.ar/category/novedades/feed/",                 "categoria":"Automotor",   "tier":2, "activa":True},
    {"id":"autoblog_lan",   "nombre":"Autoblog Lanzamientos",  "web":"https://autoblog.com.ar/category/lanzamientos/feed/",              "categoria":"Automotor",   "tier":2, "activa":True},
    {"id":"diariodeautos",  "nombre":"Diario de Autos",        "web":"https://www.diariodeautos.com.ar/index.php?format=feed&type=rss",  "categoria":"Automotor",   "tier":2, "activa":True},
    {"id":"ambito_acara",   "nombre":"Ámbito ACARA",           "web":"https://www.ambito.com/rss/tags/acara.xml",                        "categoria":"Automotor",   "tier":2, "activa":True},
    {"id":"autocosmos",     "nombre":"Autocosmos Argentina",   "web":"https://noticias.autocosmos.com.ar/rss",                           "categoria":"Automotor",   "tier":2, "activa":True},
    {"id":"arodarpost",    "nombre":"A Rodar Post",           "web":"https://arodarpost.com.ar/feed/",                                  "categoria":"Automotor",   "tier":2, "activa":True},

    # Logística
    {"id":"webpicking",     "nombre":"Webpicking",             "web":"https://webpicking.com/feed/",                                     "categoria":"Logística",   "tier":2, "activa":True},
    {"id":"hablemoslog",    "nombre":"Hablemos de Logística",  "web":"https://hablemosdelogistica.com/feed/",                            "categoria":"Logística",   "tier":2, "activa":True},
    {"id":"enfasis_log",    "nombre":"Énfasis Logística",      "web":"https://thelogisticsworld.com/historico-enfasis-logistica-sudamerica/feed/", "categoria":"Logística", "tier":2, "activa":True},
    {"id":"infobae_movant", "nombre":"Infobae Movant LogComex","web":"https://www.infobae.com/feeds/rss/?sections=movant",               "categoria":"Logística",   "tier":2, "activa":True},

    # Laboral
    {"id":"eldial",         "nombre":"El Dial Laboral",        "web":"https://www.eldial.com/nuevo/rss-laboral.asp",                     "categoria":"Laboral",     "tier":2, "activa":True},
    {"id":"microjuris",     "nombre":"Microjuris Laboral",     "web":"https://aldia.microjuris.com/category/derecho-laboral/feed/",      "categoria":"Laboral",     "tier":2, "activa":True},
    {"id":"factor_lab",     "nombre":"Factor Laboral",         "web":"https://comercioyjusticia.info/factor/category/laboral/feed/",     "categoria":"Laboral",     "tier":2, "activa":True},
    {"id":"oit_podcast",    "nombre":"OIT Podcast",            "web":"https://voices.ilo.org/rss/podcast/fow-es-es.xml",                 "categoria":"Laboral",     "tier":2, "activa":True},

    # Mercados / Finanzas
    {"id":"investing_eco",  "nombre":"Investing Economía",     "web":"https://es.investing.com/rss/news_14.rss",                         "categoria":"Mercados",    "tier":2, "activa":True},

    # Internacional
    {"id":"cincodias",      "nombre":"Cinco Días",             "web":"https://cincodias.elpais.com/seccion/rss/economia/",               "categoria":"Internacional","tier":2, "activa":True},
    {"id":"eleconomista_es","nombre":"El Economista España",   "web":"https://www.eleconomista.es/rss/rss-mercados.php",                 "categoria":"Internacional","tier":2, "activa":True},
    {"id":"fmi",            "nombre":"FMI",                    "web":"https://www.imf.org/en/News/rss?language=eng",                     "categoria":"Internacional","tier":2, "activa":True},
    {"id":"cepal",          "nombre":"CEPAL",                  "web":"https://www.cepal.org/es/rss.xml",                                 "categoria":"Internacional","tier":2, "activa":True},

    # Fulbito
    {"id":"ole",            "nombre":"Olé",                    "web":"https://www.ole.com.ar/rss/home.xml",                              "categoria":"Fulbito",     "tier":2, "activa":True},
    {"id":"tycsports",      "nombre":"TyC Sports",             "web":"https://www.tycsports.com/rss.xml",                                "categoria":"Fulbito",     "tier":2, "activa":True},
    {"id":"infobae_dep",    "nombre":"Infobae Deportes",       "web":"https://www.infobae.com/feeds/rss/deportes/",                      "categoria":"Fulbito",     "tier":2, "activa":True},
    {"id":"pincha",         "nombre":"0221 Estudiantes",       "web":"https://www.0221.com.ar/rss/pages/estudiantes.xml",                "categoria":"Fulbito",     "tier":2, "activa":True},

    # ================================================================
    # iProfesional / iProUP (Tier 1 — cache 6hs)
    # ================================================================
    {"id":"iprof_eco",    "nombre":"iProfesional Economía",    "web":"https://www.iprofesional.com/rss/economia.xml",        "categoria":"Macro",       "tier":1, "activa":True},
    {"id":"iprof_fin",    "nombre":"iProfesional Finanzas",    "web":"https://www.iprofesional.com/rss/finanzas.xml",        "categoria":"Finanzas",    "tier":1, "activa":True},
    {"id":"iprof_comex",  "nombre":"iProfesional Comex",       "web":"https://www.iprofesional.com/rss/comex.xml",           "categoria":"Comex",       "tier":1, "activa":True},
    {"id":"iprof_imp",    "nombre":"iProfesional Impuestos",   "web":"https://www.iprofesional.com/rss/impuestos.xml",       "categoria":"Fiscal",      "tier":1, "activa":True},
    {"id":"iprof_mgmt",   "nombre":"iProfesional Management",  "web":"https://www.iprofesional.com/rss/management.xml",      "categoria":"Laboral",     "tier":1, "activa":True},
    {"id":"iprof_autos",  "nombre":"iProfesional Autos",       "web":"https://www.iprofesional.com/rss/autos.xml",           "categoria":"Automotor",   "tier":1, "activa":True},
    {"id":"iproup_fin",   "nombre":"iProUP Fintech",           "web":"https://www.iproup.com/rss/finanzas-4.0.xml",          "categoria":"Finanzas",    "tier":1, "activa":True},
    {"id":"iproup_eco",   "nombre":"iProUP Economía Digital",  "web":"https://www.iproup.com/rss/economia-digital.xml",      "categoria":"Mercados",    "tier":1, "activa":True},

    # ================================================================
    # TIER 3 — Institucionales / Expectativas (cache 48hs)
    # ================================================================
    {"id":"bcra",           "nombre":"BCRA",                   "web":"https://nitter.net/BancoCentral_AR/rss",                           "categoria":"Macro",       "tier":3, "activa":True},
    {"id":"indec",          "nombre":"INDEC",                  "web":"https://nitter.net/INDECArgentina/rss",                            "categoria":"Macro",       "tier":3, "activa":True},
    {"id":"mecon",          "nombre":"Ministerio de Economía", "web":"https://www.argentina.gob.ar/noticias/rss-ministerio-de-economia.xml","categoria":"Política",  "tier":3, "activa":True},
    {"id":"econviews",      "nombre":"Econviews",              "web":"https://econviews.com/feed/",                                      "categoria":"Expectativas de mercado","tier":3,"activa":True},
    {"id":"fiel",           "nombre":"FIEL",                   "web":"https://www.fiel.org.ar/publicaciones/feed/",                      "categoria":"Expectativas de mercado","tier":3,"activa":True},
    {"id":"ieral",          "nombre":"IERAL",                  "web":"https://www.ieral.org/feed.xml",                                   "categoria":"Expectativas de mercado","tier":3,"activa":True},
    {"id":"fundar",         "nombre":"Fundar",                 "web":"https://fund.ar/feed/",                                            "categoria":"Expectativas de mercado","tier":3,"activa":True},
    {"id":"iaraf",          "nombre":"IARAF",                  "web":"https://www.iaraf.org/index.php/informes-economicos/area-fiscal?format=feed&type=rss","categoria":"Expectativas de mercado","tier":3,"activa":True},
    {"id":"ceso",           "nombre":"CESO",                   "web":"https://ceso.com.ar/feed/",                                        "categoria":"Expectativas de mercado","tier":3,"activa":True},
    {"id":"cedlas",         "nombre":"CEDLAS UNLP",            "web":"https://cedlas.econo.unlp.edu.ar/wp/feed/",                        "categoria":"Expectativas de mercado","tier":3,"activa":True},
    {"id":"cippec",         "nombre":"CIPPEC",                 "web":"https://www.cippec.org/feed/",                                     "categoria":"Expectativas de mercado","tier":3,"activa":True},
    {"id":"pxq",            "nombre":"PxQ",                    "web":"https://pxqconsultora.com/feed/",                                  "categoria":"Expectativas de mercado","tier":3,"activa":False},
]

# Cache en horas por tier
CACHE_HORAS = {1: 6, 2: 24, 3: 48}

# Lookup rápido por id
FUENTES_POR_ID = {f["id"]: f for f in FUENTES}

# Lista negra de patrones SEO a descartar en el selector
TITULOS_BASURA = [
    "dólar hoy", "dollar hoy", "a cuánto cotiza", "a cuánto está",
    "precio hoy", "cotización hoy", "cuánto vale hoy",
    "blue hoy", "oficial hoy", "tipo de cambio hoy",
]
