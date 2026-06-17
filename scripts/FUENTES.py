"""
PPA — FUENTES.py
Capa base limpia: 37 fuentes RSS verificadas el 17/06/2026.
Una sola lista, una sola taxonomía de 12 categorías.

TIERS (controlan el cache del fetcher):
  1 = medios generales      → cache 6hs
  2 = sectoriales           → cache 24hs
  3 = consultoras/institucional → cache 48hs

El feed va en la clave "web" por compatibilidad con el código existente.
"""

FUENTES = [

    # ===== AGRO =====
    {"id":"bichos_campo", "nombre":"Bichos de Campo", "web":"https://bichosdecampo.com/feed/", "categoria":"Agro", "tier":2, "activa":True},
    {"id":"infocampo", "nombre":"Infocampo", "web":"https://www.infocampo.com.ar/feed/", "categoria":"Agro", "tier":2, "activa":True},
    {"id":"investing_commodities", "nombre":"Investing Commodities", "web":"https://es.investing.com/rss/news_287.rss", "categoria":"Agro", "tier":2, "activa":True},

    # ===== ANÁLISIS CONSULTORAS =====
    {"id":"ceso", "nombre":"CESO", "web":"https://ceso.com.ar/feed/", "categoria":"Análisis Consultoras", "tier":3, "activa":True},
    {"id":"cippec", "nombre":"CIPPEC", "web":"https://www.cippec.org/feed/", "categoria":"Análisis Consultoras", "tier":3, "activa":True},
    {"id":"econviews", "nombre":"Econviews", "web":"https://econviews.com/feed/", "categoria":"Análisis Consultoras", "tier":3, "activa":True},
    {"id":"fundar", "nombre":"Fundar", "web":"https://fund.ar/feed/", "categoria":"Análisis Consultoras", "tier":3, "activa":True},
    {"id":"iaraf", "nombre":"IARAF", "web":"https://www.iaraf.org/index.php/informes-economicos/area-fiscal?format=feed&type=rss", "categoria":"Análisis Consultoras", "tier":3, "activa":True},

    # ===== AUTOMOTOR =====
    {"id":"arodar", "nombre":"A Rodar Post", "web":"https://arodarpost.com.ar/feed/", "categoria":"Automotor", "tier":2, "activa":True},
    {"id":"autocosmos", "nombre":"Autocosmos Argentina", "web":"https://noticias.autocosmos.com.ar/rss", "categoria":"Automotor", "tier":2, "activa":True},
    {"id":"diario_autos", "nombre":"Diario de Autos", "web":"https://www.diariodeautos.com.ar/index.php?format=feed&type=rss", "categoria":"Automotor", "tier":2, "activa":True},
    {"id":"iprof_autos", "nombre":"iProfesional Autos", "web":"https://www.iprofesional.com/rss/autos", "categoria":"Automotor", "tier":1, "activa":True},
    {"id":"motorweb", "nombre":"Motorweb Argentina", "web":"https://motorwebargentina.com/feed/", "categoria":"Automotor", "tier":2, "activa":True},
    {"id":"vision_motor", "nombre":"Vision Motor", "web":"https://visionmotor.com/feed/", "categoria":"Automotor", "tier":2, "activa":True},
    {"id":"ambito_autos", "nombre":"Ámbito Autos", "web":"https://www.ambito.com/rss/autos.xml", "categoria":"Automotor", "tier":1, "activa":True},

    # ===== COMEX =====
    {"id":"aduana_news", "nombre":"Aduana News", "web":"https://aduananews.com/feed/", "categoria":"Comex", "tier":2, "activa":True},
    {"id":"iprof_comex", "nombre":"iProfesional Comex", "web":"https://www.iprofesional.com/rss/comex", "categoria":"Comex", "tier":1, "activa":True},
    {"id":"mercojuris", "nombre":"Mercojuris", "web":"https://mercojuris.com/feed/", "categoria":"Comex", "tier":2, "activa":True},
    {"id":"trade_news", "nombre":"Trade News", "web":"https://tradenews.com.ar/feed/", "categoria":"Comex", "tier":2, "activa":True},

    # ===== ENERGÍA Y MINERÍA =====
    {"id":"data_energia", "nombre":"Data Energía", "web":"https://dataenergia.ar/feed/", "categoria":"Energía y Minería", "tier":2, "activa":True},
    {"id":"econojournal", "nombre":"EconoJournal", "web":"https://econojournal.com.ar/feed/", "categoria":"Energía y Minería", "tier":1, "activa":True},
    {"id":"noticiasnet_energia", "nombre":"NoticiasNet Energía", "web":"https://www.noticiasnet.com.ar/rss/energia-hoy/", "categoria":"Energía y Minería", "tier":2, "activa":True},

    # ===== FINANZAS =====
    {"id":"iprof_economia", "nombre":"iProfesional Economía", "web":"https://www.iprofesional.com/rss/economia", "categoria":"Finanzas", "tier":1, "activa":True},
    {"id":"iprof_finanzas", "nombre":"iProfesional Finanzas", "web":"https://www.iprofesional.com/rss/finanzas", "categoria":"Finanzas", "tier":1, "activa":True},
    {"id":"iproup_fintech", "nombre":"iProUP Fintech", "web":"https://www.iproup.com/rss/finanzas", "categoria":"Finanzas", "tier":1, "activa":True},
    {"id":"lanacion_eco", "nombre":"La Nación Economía", "web":"https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/economia/?outputType=xml", "categoria":"Finanzas", "tier":1, "activa":True},
    {"id":"ambito_fin", "nombre":"Ámbito Finanzas", "web":"https://www.ambito.com/rss/finanzas.xml", "categoria":"Finanzas", "tier":1, "activa":True},

    # ===== FISCAL =====
    {"id":"iprof_impuestos", "nombre":"iProfesional Impuestos", "web":"https://www.iprofesional.com/rss/impuestos", "categoria":"Fiscal", "tier":1, "activa":True},
    {"id":"ambito_fisc", "nombre":"Ámbito Fiscal", "web":"https://www.ambito.com/rss/novedades-fiscales.xml", "categoria":"Fiscal", "tier":1, "activa":True},

    # ===== INTERNACIONAL =====
    {"id":"investing_intl", "nombre":"Investing Internacional", "web":"https://es.investing.com/rss/news_11.rss", "categoria":"Internacional", "tier":1, "activa":True},

    # ===== LABORAL =====
    {"id":"iprof_management", "nombre":"iProfesional Management", "web":"https://www.iprofesional.com/rss/management", "categoria":"Laboral", "tier":1, "activa":True},
    {"id":"microjuris_laboral", "nombre":"Microjuris Laboral", "web":"https://aldia.microjuris.com/category/derecho-laboral/feed/", "categoria":"Laboral", "tier":2, "activa":True},
    {"id":"oit_podcast", "nombre":"OIT Podcast", "web":"https://voices.ilo.org/rss/podcast/fow-es-es.xml", "categoria":"Laboral", "tier":3, "activa":True},

    # ===== LOGÍSTICA =====
    {"id":"webpicking", "nombre":"Webpicking", "web":"https://webpicking.com/feed/", "categoria":"Logística", "tier":2, "activa":True},

    # ===== MERCADOS =====
    {"id":"investing_economia", "nombre":"Investing Economía", "web":"https://es.investing.com/rss/news_14.rss", "categoria":"Mercados", "tier":1, "activa":True},
    {"id":"iproup_eco", "nombre":"iProUP Economía Digital", "web":"https://www.iproup.com/rss/economia-digital", "categoria":"Mercados", "tier":1, "activa":True},

    # ===== FULBITO =====
    {"id":"est_0221", "nombre":"0221 Estudiantes", "web":"https://www.0221.com.ar/rss/pages/estudiantes.xml", "categoria":"Fulbito", "tier":2, "activa":True},
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
