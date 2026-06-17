"""
PPA — Pulso Productivo Argentino
Configuración general del sistema

Este archivo define:
- Las 57 fuentes RSS con su categoría y tier
- Los parámetros del algoritmo de destacados
- Las APIs externas que se usan para datos vivos

Las URLs marcadas con [VALIDAR] son tentativas y deben verificarse
manualmente abriendo el feed en el navegador.
"""

# =============================================================
# CATEGORÍAS DEL DIARIO (orden en que aparecen en la nav)
# =============================================================
CATEGORIAS = [
    "Agro",
    "Análisis Consultoras",
    "Automotor",
    "Comex",
    "Energía y Minería",
    "Finanzas",
    "Fiscal",
    "Internacional",
    "Laboral",
    "Logística",
    "Mercados",
    "Fulbito",
]

# =============================================================
# CONFIGURACIÓN DE VENTANAS DE TIEMPO POR TIER
# =============================================================
# Cuántas horas dura una nota en portada según el tier de su fuente
VENTANA_HORAS_POR_TIER = {
    1: 24 * 7,   # Tier 1: 7 días
    2: 24 * 3,   # Tier 2: 3 días
    3: 24,       # Tier 3: 24 horas
}

# Ventana especial para Documentos en circulación (papers e informes)
VENTANA_DOCUMENTOS_HORAS = 24 * 30  # 30 días


# =============================================================
# FUENTES RSS (57 en total)
# =============================================================
# Cada fuente tiene:
#   id: identificador único (sin espacios, en minúsculas)
#   nombre: nombre visible en el sitio
#   categoria: una de las CATEGORIAS de arriba
#   tier: 1 (peso alto en destacados), 2 (medio), 3 (bajo)
#   rss: URL del feed RSS
#   web: URL del sitio (para link "ver más")
#   descripcion: texto breve para tooltips y panel admin
#   activa: True/False (panel puede suspender sin borrar)

FUENTES = [
    # ============ AGRO ============
    {
        "id": "bichos_campo",
        "nombre": "Bichos de Campo",
        "categoria": "Agro",
        "tier": 2,
        "rss": "https://bichosdecampo.com/feed/",
        "web": "https://bichosdecampo.com/feed/",
        "descripcion": "Actualidad del agro, ganadería y vida rural.",
        "activa": True,
    },
    {
        "id": "infocampo",
        "nombre": "Infocampo",
        "categoria": "Agro",
        "tier": 2,
        "rss": "https://www.infocampo.com.ar/feed/",
        "web": "https://www.infocampo.com.ar/feed/",
        "descripcion": "Noticias agropecuarias, mercados y tecnología del campo.",
        "activa": True,
    },
    {
        "id": "investing_commodities",
        "nombre": "Investing Commodities",
        "categoria": "Agro",
        "tier": 2,
        "rss": "https://es.investing.com/rss/news_287.rss",
        "web": "https://es.investing.com/rss/news_287.rss",
        "descripcion": "Cotizaciones y noticias de commodities agrícolas.",
        "activa": True,
    },
    # ============ ANÁLISIS CONSULTORAS ============
    {
        "id": "ceso",
        "nombre": "CESO",
        "categoria": "Análisis Consultoras",
        "tier": 3,
        "rss": "https://ceso.com.ar/feed/",
        "web": "https://ceso.com.ar/feed/",
        "descripcion": "Centro de Estudios Económicos y Sociales Scalabrini Ortiz. Informes heterodoxos.",
        "activa": True,
    },
    {
        "id": "cippec",
        "nombre": "CIPPEC",
        "categoria": "Análisis Consultoras",
        "tier": 3,
        "rss": "https://www.cippec.org/feed/",
        "web": "https://www.cippec.org/feed/",
        "descripcion": "Centro de Implementación de Políticas Públicas. Análisis de políticas y Estado.",
        "activa": True,
    },
    {
        "id": "econviews",
        "nombre": "Econviews",
        "categoria": "Análisis Consultoras",
        "tier": 3,
        "rss": "https://econviews.com/feed/",
        "web": "https://econviews.com/feed/",
        "descripcion": "Consultora de Miguel Kiguel. Análisis macroeconómico.",
        "activa": True,
    },
    {
        "id": "fundar",
        "nombre": "Fundar",
        "categoria": "Análisis Consultoras",
        "tier": 3,
        "rss": "https://fund.ar/feed/",
        "web": "https://fund.ar/feed/",
        "descripcion": "Think tank de desarrollo productivo y políticas públicas.",
        "activa": True,
    },
    {
        "id": "iaraf",
        "nombre": "IARAF",
        "categoria": "Análisis Consultoras",
        "tier": 3,
        "rss": "https://www.iaraf.org/index.php/informes-economicos/area-fiscal?format=feed&type=rss",
        "web": "https://www.iaraf.org/index.php/informes-economicos/area-fiscal?format=feed&type=rss",
        "descripcion": "Instituto Argentino de Análisis Fiscal. Informes fiscales y tributarios.",
        "activa": True,
    },
    # ============ AUTOMOTOR ============
    {
        "id": "arodar",
        "nombre": "A Rodar Post",
        "categoria": "Automotor",
        "tier": 2,
        "rss": "https://arodarpost.com.ar/feed/",
        "web": "https://arodarpost.com.ar/feed/",
        "descripcion": "Industria automotriz argentina, lanzamientos y mercado.",
        "activa": True,
    },
    {
        "id": "autocosmos",
        "nombre": "Autocosmos Argentina",
        "categoria": "Automotor",
        "tier": 2,
        "rss": "https://noticias.autocosmos.com.ar/rss",
        "web": "https://noticias.autocosmos.com.ar/rss",
        "descripcion": "Noticias del mundo automotor.",
        "activa": True,
    },
    {
        "id": "diario_autos",
        "nombre": "Diario de Autos",
        "categoria": "Automotor",
        "tier": 2,
        "rss": "https://www.diariodeautos.com.ar/index.php?format=feed&type=rss",
        "web": "https://www.diariodeautos.com.ar/index.php?format=feed&type=rss",
        "descripcion": "Actualidad del sector automotor.",
        "activa": True,
    },
    {
        "id": "iprof_autos",
        "nombre": "iProfesional Autos",
        "categoria": "Automotor",
        "tier": 1,
        "rss": "https://www.iprofesional.com/rss/autos",
        "web": "https://www.iprofesional.com/rss/autos",
        "descripcion": "Sección autos de iProfesional.",
        "activa": True,
    },
    {
        "id": "motorweb",
        "nombre": "Motorweb Argentina",
        "categoria": "Automotor",
        "tier": 2,
        "rss": "https://motorwebargentina.com/feed/",
        "web": "https://motorwebargentina.com/feed/",
        "descripcion": "Pruebas, lanzamientos y mercado automotor.",
        "activa": True,
    },
    {
        "id": "vision_motor",
        "nombre": "Vision Motor",
        "categoria": "Automotor",
        "tier": 2,
        "rss": "https://visionmotor.com/feed/",
        "web": "https://visionmotor.com/feed/",
        "descripcion": "Revista de actualidad automotriz.",
        "activa": True,
    },
    {
        "id": "ambito_autos",
        "nombre": "Ámbito Autos",
        "categoria": "Automotor",
        "tier": 1,
        "rss": "https://www.ambito.com/rss/autos.xml",
        "web": "https://www.ambito.com/rss/autos.xml",
        "descripcion": "Sección autos de Ámbito Financiero.",
        "activa": True,
    },
    # ============ COMEX ============
    {
        "id": "aduana_news",
        "nombre": "Aduana News",
        "categoria": "Comex",
        "tier": 2,
        "rss": "https://aduananews.com/feed/",
        "web": "https://aduananews.com/feed/",
        "descripcion": "Comercio exterior, aduana y normativa.",
        "activa": True,
    },
    {
        "id": "iprof_comex",
        "nombre": "iProfesional Comex",
        "categoria": "Comex",
        "tier": 1,
        "rss": "https://www.iprofesional.com/rss/comex",
        "web": "https://www.iprofesional.com/rss/comex",
        "descripcion": "Sección comercio exterior de iProfesional.",
        "activa": True,
    },
    {
        "id": "mercojuris",
        "nombre": "Mercojuris",
        "categoria": "Comex",
        "tier": 2,
        "rss": "https://mercojuris.com/feed/",
        "web": "https://mercojuris.com/feed/",
        "descripcion": "Novedades jurídicas y de comercio exterior del Mercosur.",
        "activa": True,
    },
    {
        "id": "trade_news",
        "nombre": "Trade News",
        "categoria": "Comex",
        "tier": 2,
        "rss": "https://tradenews.com.ar/feed/",
        "web": "https://tradenews.com.ar/feed/",
        "descripcion": "Comercio internacional y logística.",
        "activa": True,
    },
    # ============ ENERGÍA Y MINERÍA ============
    {
        "id": "data_energia",
        "nombre": "Data Energía",
        "categoria": "Energía y Minería",
        "tier": 2,
        "rss": "https://dataenergia.ar/feed/",
        "web": "https://dataenergia.ar/feed/",
        "descripcion": "Datos y análisis del sector energético.",
        "activa": True,
    },
    {
        "id": "econojournal",
        "nombre": "EconoJournal",
        "categoria": "Energía y Minería",
        "tier": 1,
        "rss": "https://econojournal.com.ar/feed/",
        "web": "https://econojournal.com.ar/feed/",
        "descripcion": "Periodismo especializado en energía.",
        "activa": True,
    },
    {
        "id": "noticiasnet_energia",
        "nombre": "NoticiasNet Energía",
        "categoria": "Energía y Minería",
        "tier": 2,
        "rss": "https://www.noticiasnet.com.ar/rss/energia-hoy/",
        "web": "https://www.noticiasnet.com.ar/rss/energia-hoy/",
        "descripcion": "Energía y petróleo de la Patagonia.",
        "activa": True,
    },
    # ============ FINANZAS ============
    {
        "id": "iprof_economia",
        "nombre": "iProfesional Economía",
        "categoria": "Finanzas",
        "tier": 1,
        "rss": "https://www.iprofesional.com/rss/economia",
        "web": "https://www.iprofesional.com/rss/economia",
        "descripcion": "Sección economía de iProfesional.",
        "activa": True,
    },
    {
        "id": "iprof_finanzas",
        "nombre": "iProfesional Finanzas",
        "categoria": "Finanzas",
        "tier": 1,
        "rss": "https://www.iprofesional.com/rss/finanzas",
        "web": "https://www.iprofesional.com/rss/finanzas",
        "descripcion": "Sección finanzas de iProfesional.",
        "activa": True,
    },
    {
        "id": "iproup_fintech",
        "nombre": "iProUP Fintech",
        "categoria": "Finanzas",
        "tier": 1,
        "rss": "https://www.iproup.com/rss/finanzas",
        "web": "https://www.iproup.com/rss/finanzas",
        "descripcion": "Fintech y finanzas digitales.",
        "activa": True,
    },
    {
        "id": "lanacion_eco",
        "nombre": "La Nación Economía",
        "categoria": "Finanzas",
        "tier": 1,
        "rss": "https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/economia/?outputType=xml",
        "web": "https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/economia/?outputType=xml",
        "descripcion": "Sección economía de La Nación.",
        "activa": True,
    },
    {
        "id": "ambito_fin",
        "nombre": "Ámbito Finanzas",
        "categoria": "Finanzas",
        "tier": 1,
        "rss": "https://www.ambito.com/rss/finanzas.xml",
        "web": "https://www.ambito.com/rss/finanzas.xml",
        "descripcion": "Sección finanzas de Ámbito Financiero.",
        "activa": True,
    },
    # ============ FISCAL ============
    {
        "id": "iprof_impuestos",
        "nombre": "iProfesional Impuestos",
        "categoria": "Fiscal",
        "tier": 1,
        "rss": "https://www.iprofesional.com/rss/impuestos",
        "web": "https://www.iprofesional.com/rss/impuestos",
        "descripcion": "Sección impuestos de iProfesional.",
        "activa": True,
    },
    {
        "id": "ambito_fisc",
        "nombre": "Ámbito Fiscal",
        "categoria": "Fiscal",
        "tier": 1,
        "rss": "https://www.ambito.com/rss/novedades-fiscales.xml",
        "web": "https://www.ambito.com/rss/novedades-fiscales.xml",
        "descripcion": "Novedades fiscales de Ámbito Financiero.",
        "activa": True,
    },
    # ============ INTERNACIONAL ============
    {
        "id": "investing_intl",
        "nombre": "Investing Internacional",
        "categoria": "Internacional",
        "tier": 1,
        "rss": "https://es.investing.com/rss/news_11.rss",
        "web": "https://es.investing.com/rss/news_11.rss",
        "descripcion": "Noticias económicas internacionales.",
        "activa": True,
    },
    # ============ LABORAL ============
    {
        "id": "iprof_management",
        "nombre": "iProfesional Management",
        "categoria": "Laboral",
        "tier": 1,
        "rss": "https://www.iprofesional.com/rss/management",
        "web": "https://www.iprofesional.com/rss/management",
        "descripcion": "Management, empleo y recursos humanos.",
        "activa": True,
    },
    {
        "id": "microjuris_laboral",
        "nombre": "Microjuris Laboral",
        "categoria": "Laboral",
        "tier": 2,
        "rss": "https://aldia.microjuris.com/category/derecho-laboral/feed/",
        "web": "https://aldia.microjuris.com/category/derecho-laboral/feed/",
        "descripcion": "Novedades de derecho laboral.",
        "activa": True,
    },
    {
        "id": "oit_podcast",
        "nombre": "OIT Podcast",
        "categoria": "Laboral",
        "tier": 3,
        "rss": "https://voices.ilo.org/rss/podcast/fow-es-es.xml",
        "web": "https://voices.ilo.org/rss/podcast/fow-es-es.xml",
        "descripcion": "Podcast de la OIT sobre el futuro del trabajo.",
        "activa": True,
    },
    # ============ LOGÍSTICA ============
    {
        "id": "webpicking",
        "nombre": "Webpicking",
        "categoria": "Logística",
        "tier": 2,
        "rss": "https://webpicking.com/feed/",
        "web": "https://webpicking.com/feed/",
        "descripcion": "Logística, supply chain y comercio.",
        "activa": True,
    },
    # ============ MERCADOS ============
    {
        "id": "investing_economia",
        "nombre": "Investing Economía",
        "categoria": "Mercados",
        "tier": 1,
        "rss": "https://es.investing.com/rss/news_14.rss",
        "web": "https://es.investing.com/rss/news_14.rss",
        "descripcion": "Noticias de mercados y economía.",
        "activa": True,
    },
    {
        "id": "iproup_eco",
        "nombre": "iProUP Economía Digital",
        "categoria": "Mercados",
        "tier": 1,
        "rss": "https://www.iproup.com/rss/economia-digital",
        "web": "https://www.iproup.com/rss/economia-digital",
        "descripcion": "Economía digital y mercados.",
        "activa": True,
    },
    # ============ FULBITO ============
    {
        "id": "est_0221",
        "nombre": "0221 Estudiantes",
        "categoria": "Fulbito",
        "tier": 2,
        "rss": "https://www.0221.com.ar/rss/pages/estudiantes.xml",
        "web": "https://www.0221.com.ar/rss/pages/estudiantes.xml",
        "descripcion": "Estudiantes de La Plata, desde 0221.",
        "activa": True,
    },
]


# =============================================================
# APIs EXTERNAS PARA DATOS VIVOS
# =============================================================
APIS = {
    "dolar_oficial":  "https://dolarapi.com/v1/dolares/oficial",
    "dolar_mep":      "https://dolarapi.com/v1/dolares/bolsa",
    "dolar_ccl":      "https://dolarapi.com/v1/dolares/contadoconliqui",
    "dolar_blue":     "https://dolarapi.com/v1/dolares/blue",
    "riesgo_pais":    "https://api.argentinadatos.com/v1/finanzas/indices/riesgo-pais/ultimo",
    "clima_ba":       "https://api.open-meteo.com/v1/forecast?latitude=-34.6&longitude=-58.4&current=temperature_2m,weather_code&timezone=America/Argentina/Buenos_Aires",
    # API-Football requiere key gratuita (registrarse en api-football.com)
    # Se carga vía variable de entorno API_FOOTBALL_KEY
}


# =============================================================
# PARÁMETROS DEL ALGORITMO
# =============================================================

# Cuántas horas hacia atrás considerar para "noticia reciente"
HORAS_VENTANA = 24

# Cuántos destacados en tapa
DESTACADOS_CANT = 5

# Cuántas notas máximo por categoría en portada
NOTAS_POR_CATEGORIA = 6

# Cuántas notas en "Último Momento" sidebar
ULTIMO_MOMENTO_CANT = 10

# Equipos de fútbol que activan la marquesina Fulbito
EQUIPOS_FULBITO = [
    "Estudiantes",          # siempre
    "Boca Juniors",
    "River Plate",
    "Independiente",
    "Racing Club",
    "San Lorenzo",
    # selección argentina y mundiales se detectan por nombre de torneo
]

TORNEOS_FULBITO = [
    "World Cup",
    "Copa America",
    "Copa Libertadores",
    "FIFA Club World Cup",
    "Friendlies",  # amistosos de selección
]


# =============================================================
# RUTAS DEL PROYECTO
# =============================================================
import os

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIR_DATA = os.path.join(RAIZ, "data")
DIR_SITE = os.path.join(RAIZ, "site")
DIR_ARCHIVO = os.path.join(DIR_SITE, "archivo")

# Archivos JSON principales
JSON_NOTAS = os.path.join(DIR_DATA, "notas.json")          # todas las notas activas
JSON_FUENTES_RUNTIME = os.path.join(DIR_DATA, "fuentes_runtime.json")  # estado de cada fuente (salud)
JSON_BORRADOS = os.path.join(DIR_DATA, "borrados.json")    # IDs marcados como basura
JSON_NOTAS_PROPIAS = os.path.join(DIR_DATA, "notas_propias.json")  # las que escribe Sergio Falco
