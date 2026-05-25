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
    "Macro",
    "Política",
    "Energía",
    "Agro",
    "Minería",
    "Comercio Exterior",
    "Automotor",
    "Logística",
    "Internacional",
]


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
    # ============ MACRO / ECONOMÍA (22) ============
    {
        "id": "bcra",
        "nombre": "BCRA",
        "categoria": "Macro",
        "tier": 1,
        "rss": "https://www.bcra.gob.ar/Noticias/RSS_Noticias.xml",
        "web": "https://www.bcra.gob.ar",
        "descripcion": "Banco Central de la República Argentina. Informes monetarios, política cambiaria, comunicados oficiales.",
        "activa": True,
    },
    {
        "id": "indec",
        "nombre": "INDEC",
        "categoria": "Macro",
        "tier": 1,
        "rss": "https://www.indec.gob.ar/rss.xml",
        "web": "https://www.indec.gob.ar",
        "descripcion": "Instituto Nacional de Estadística y Censos. IPC, EMAE, industria, empleo, comercio exterior.",
        "activa": True,
    },
    {
        "id": "iaraf",
        "nombre": "IARAF",
        "categoria": "Macro",
        "tier": 1,
        "rss": "https://www.iaraf.org/feed/",
        "web": "https://www.iaraf.org",
        "descripcion": "Instituto Argentino de Análisis Fiscal. Análisis de gasto público, recaudación, coparticipación.",
        "activa": True,
    },
    {
        "id": "fiel",
        "nombre": "FIEL",
        "categoria": "Macro",
        "tier": 1,
        "rss": "https://www.fiel.org/feed/",
        "web": "https://www.fiel.org",
        "descripcion": "Fundación de Investigaciones Económicas Latinoamericanas. Una de las fundaciones económicas más antiguas.",
        "activa": True,
    },
    {
        "id": "fundar",
        "nombre": "Fundar",
        "categoria": "Macro",
        "tier": 1,
        "rss": "https://fund.ar/feed/",
        "web": "https://fund.ar",
        "descripcion": "Centro de estudios económicos y políticos con enfoque productivo.",
        "activa": True,
    },
    {
        "id": "ieral",
        "nombre": "IERAL / Fundación Mediterránea",
        "categoria": "Macro",
        "tier": 1,
        "rss": "https://www.ieral.org/feed/",
        "web": "https://www.ieral.org",
        "descripcion": "Instituto de Estudios sobre la Realidad Argentina y Latinoamericana. Mirada desde Córdoba.",
        "activa": True,
    },
    {
        "id": "cedlas",
        "nombre": "CEDLAS",
        "categoria": "Macro",
        "tier": 2,
        "rss": "https://www.cedlas.econo.unlp.edu.ar/wp/feed/",
        "web": "https://www.cedlas.econo.unlp.edu.ar",
        "descripcion": "Centro de Estudios Distributivos, Laborales y Sociales (UNLP). Pobreza, desigualdad, mercado laboral.",
        "activa": True,
    },
    {
        "id": "ecolatina",
        "nombre": "Ecolatina",
        "categoria": "Macro",
        "tier": 2,
        "rss": "https://www.ecolatina.com/feed/",
        "web": "https://www.ecolatina.com",
        "descripcion": "Consultora económica fundada por Roberto Lavagna.",
        "activa": True,
    },
    {
        "id": "idesa",
        "nombre": "IDESA",
        "categoria": "Macro",
        "tier": 2,
        "rss": "https://www.idesa.org/feed/",
        "web": "https://www.idesa.org",
        "descripcion": "Instituto para el Desarrollo Social Argentino. Análisis laboral y previsional.",
        "activa": True,
    },
    {
        "id": "empiria",
        "nombre": "Empiria Consultores",
        "categoria": "Macro",
        "tier": 2,
        "rss": "https://empiria.com.ar/feed/",
        "web": "https://empiria.com.ar",
        "descripcion": "Consultora económica de Hernán Lacunza.",
        "activa": True,
    },
    {
        "id": "lcg",
        "nombre": "LCG",
        "categoria": "Macro",
        "tier": 2,
        "rss": "https://www.lcgsa.com.ar/feed/",
        "web": "https://www.lcgsa.com.ar",
        "descripcion": "Consultora económica con énfasis en macro y finanzas.",
        "activa": True,
    },
    {
        "id": "invecq",
        "nombre": "Invecq",
        "categoria": "Macro",
        "tier": 2,
        "rss": "https://invecq.com/feed/",
        "web": "https://invecq.com",
        "descripcion": "Consultora económica.",
        "activa": True,
    },
    {
        "id": "ojf",
        "nombre": "Orlando J. Ferreres",
        "categoria": "Macro",
        "tier": 2,
        "rss": "https://www.ojf.com/feed/",
        "web": "https://www.ojf.com",
        "descripcion": "Consultora económica clásica con índices propios de actividad.",
        "activa": True,
    },
    {
        "id": "analytica",
        "nombre": "Analytica",
        "categoria": "Macro",
        "tier": 2,
        "rss": "https://analytica.com.ar/feed/",
        "web": "https://analytica.com.ar",
        "descripcion": "Consultora económica.",
        "activa": True,
    },
    {
        "id": "outlier",
        "nombre": "Outlier",
        "categoria": "Macro",
        "tier": 2,
        "rss": "https://outlier.com.ar/feed/",
        "web": "https://outlier.com.ar",
        "descripcion": "Consultora de Gabriel Caamaño Gómez. Análisis macro y financiero.",
        "activa": True,
    },
    {
        "id": "ecogo",
        "nombre": "EcoGo",
        "categoria": "Macro",
        "tier": 2,
        "rss": "https://ecogo.com.ar/feed/",
        "web": "https://ecogo.com.ar",
        "descripcion": "Consultora de Marina Dal Poggetto.",
        "activa": True,
    },
    {
        "id": "iae",
        "nombre": "IAE Business School",
        "categoria": "Macro",
        "tier": 3,
        "rss": "https://www.iae.edu.ar/feed/",
        "web": "https://www.iae.edu.ar",
        "descripcion": "Escuela de Negocios de la Universidad Austral.",
        "activa": True,
    },
    {
        "id": "ucema",
        "nombre": "UCEMA",
        "categoria": "Macro",
        "tier": 3,
        "rss": "https://ucema.edu.ar/feed/",
        "web": "https://ucema.edu.ar",
        "descripcion": "Universidad del CEMA. Centro de Estudios Macroeconómicos de Argentina.",
        "activa": True,
    },
    {
        "id": "utdt",
        "nombre": "Universidad Di Tella",
        "categoria": "Macro",
        "tier": 3,
        "rss": "https://www.utdt.edu/feed/",
        "web": "https://www.utdt.edu",
        "descripcion": "UTDT. Publica índices de confianza del consumidor y otros indicadores.",
        "activa": True,
    },
    {
        "id": "ambito",
        "nombre": "Ámbito Financiero",
        "categoria": "Macro",
        "tier": 2,
        "rss": "https://www.ambito.com/rss/home.xml",
        "web": "https://www.ambito.com",
        "descripcion": "Medio financiero. Sección Finanzas para cierre de mercado.",
        "activa": True,
    },
    {
        "id": "cronista",
        "nombre": "El Cronista",
        "categoria": "Macro",
        "tier": 2,
        "rss": "https://www.cronista.com/rss/feed.xml",
        "web": "https://www.cronista.com",
        "descripcion": "Diario económico. Sección Finanzas y Mercados.",
        "activa": True,
    },
    {
        "id": "eleconomista",
        "nombre": "El Economista",
        "categoria": "Macro",
        "tier": 3,
        "rss": "https://eleconomista.com.ar/feed/",
        "web": "https://eleconomista.com.ar",
        "descripcion": "Medio económico argentino.",
        "activa": True,
    },

    # ============ POLÍTICA (4) ============
    {
        "id": "cippec",
        "nombre": "CIPPEC",
        "categoria": "Política",
        "tier": 1,
        "rss": "https://www.cippec.org/feed/",
        "web": "https://www.cippec.org",
        "descripcion": "Centro de Implementación de Políticas Públicas para la Equidad y el Crecimiento.",
        "activa": True,
    },
    {
        "id": "synopsis",
        "nombre": "Synopsis",
        "categoria": "Política",
        "tier": 2,
        "rss": "https://www.synopsisconsultores.com/feed/",
        "web": "https://www.synopsisconsultores.com",
        "descripcion": "Consultora política de Lucas Romero. Sin RSS público — usar RSS.app o Kill The Newsletter.",
        "activa": False,
    },
    {
        "id": "nuevamayoria",
        "nombre": "Nueva Mayoría",
        "categoria": "Política",
        "tier": 2,
        "rss": "https://www.nuevamayoria.com/feed/",
        "web": "https://www.nuevamayoria.com",
        "descripcion": "Centro de estudios de Rosendo Fraga. Sin RSS público — usar RSS.app o Kill The Newsletter.",
        "activa": False,
    },
    {
        "id": "fundpensar",
        "nombre": "Fundación Pensar",
        "categoria": "Política",
        "tier": 3,
        "rss": "https://fundacionpensar.org/feed/",
        "web": "https://fundacionpensar.org",
        "descripcion": "Think tank vinculado al PRO.",
        "activa": True,
    },

    # ============ ENERGÍA (4) ============
    {
        "id": "econojournal",
        "nombre": "EconoJournal",
        "categoria": "Energía",
        "tier": 1,
        "rss": "https://econojournal.com.ar/feed/",
        "web": "https://econojournal.com.ar",
        "descripcion": "Medio especializado en energía argentina.",
        "activa": True,
    },
    {
        "id": "secenergia",
        "nombre": "Secretaría de Energía",
        "categoria": "Energía",
        "tier": 2,
        "rss": "https://www.argentina.gob.ar/economia/energia/feed",
        "web": "https://www.argentina.gob.ar/economia/energia",
        "descripcion": "Secretaría de Energía de la Nación.",
        "activa": True,
    },
    {
        "id": "iea",
        "nombre": "International Energy Agency",
        "categoria": "Energía",
        "tier": 2,
        "rss": "https://www.iea.org/rss",
        "web": "https://www.iea.org",
        "descripcion": "Agencia Internacional de Energía. Informes globales del sector.",
        "activa": True,
    },
    {
        "id": "masenergia",
        "nombre": "Más Energía",
        "categoria": "Energía",
        "tier": 3,
        "rss": "https://mase.lmneuquen.com/rss/pages/portada.xml",
        "web": "https://mase.lmneuquen.com",
        "descripcion": "Suplemento de energía de La Mañana de Neuquén.",
        "activa": True,
    },
    {
        "id": "energiaestrategica",
        "nombre": "Energía Estratégica",
        "categoria": "Energía",
        "tier": 1,
        "rss": "https://energiaestrategica.com/feed/",
        "web": "https://energiaestrategica.com",
        "descripcion": "Medio líder en noticias de energía renovable en español.",
        "activa": True,
    },

    # ============ AGRO (5) ============
    {
        "id": "bcr",
        "nombre": "Bolsa de Comercio de Rosario",
        "categoria": "Agro",
        "tier": 1,
        "rss": "https://www.bcr.com.ar/es/rss.xml",
        "web": "https://www.bcr.com.ar",
        "descripcion": "Bolsa de Comercio de Rosario. Estimaciones de cosecha, precios FOB, análisis del sector.",
        "activa": True,
    },
    {
        "id": "bichos",
        "nombre": "Bichos de Campo",
        "categoria": "Agro",
        "tier": 2,
        "rss": "https://bichosdecampo.com/feed/",
        "web": "https://bichosdecampo.com",
        "descripcion": "Medio agropecuario.",
        "activa": True,
    },
    {
        "id": "agrositio",
        "nombre": "Agrositio",
        "categoria": "Agro",
        "tier": 2,
        "rss": "https://www.agrositio.com.ar/rss/feed.xml",
        "web": "https://www.agrositio.com.ar",
        "descripcion": "Portal agropecuario.",
        "activa": True,
    },
    {
        "id": "valorsoja",
        "nombre": "Valor Soja",
        "categoria": "Agro",
        "tier": 2,
        "rss": "https://www.valorsoja.com/feed/",
        "web": "https://www.valorsoja.com",
        "descripcion": "Especializado en mercado de soja y commodities agrícolas.",
        "activa": True,
    },
    {
        "id": "usda",
        "nombre": "USDA",
        "categoria": "Agro",
        "tier": 3,
        "rss": "https://www.usda.gov/rss/latest-releases.xml",
        "web": "https://www.usda.gov",
        "descripcion": "Departamento de Agricultura de Estados Unidos. Referencia mundial en commodities.",
        "activa": True,
    },
    {
        "id": "rosgan",
        "nombre": "Rosgan",
        "categoria": "Agro",
        "tier": 1,
        "rss": "https://rosgan.com.ar/feed/",
        "web": "https://rosgan.com.ar",
        "descripcion": "Mercado ganadero de la Bolsa de Comercio de Rosario.",
        "activa": True,
    },

    # ============ MINERÍA (4) ============
    {
        "id": "panoraminer",
        "nombre": "Panorama Minero",
        "categoria": "Minería",
        "tier": 1,
        "rss": "https://panoramaminero.com/feed/",
        "web": "https://panoramaminero.com",
        "descripcion": "Medio minero argentino.",
        "activa": True,
    },
    {
        "id": "miningpress",
        "nombre": "Mining Press",
        "categoria": "Minería",
        "tier": 2,
        "rss": "https://miningpress.com/feed/",
        "web": "https://miningpress.com",
        "descripcion": "Medio especializado en minería.",
        "activa": True,
    },
    {
        "id": "caem",
        "nombre": "CAEM",
        "categoria": "Minería",
        "tier": 2,
        "rss": "https://caem.com.ar/feed/",
        "web": "https://caem.com.ar",
        "descripcion": "Cámara Argentina de Empresarios Mineros.",
        "activa": True,
    },
    {
        "id": "abeceb",
        "nombre": "Abeceb",
        "categoria": "Minería",
        "tier": 3,
        "rss": "https://abeceb.com/feed/",
        "web": "https://abeceb.com",
        "descripcion": "Consultora económica con foco en sectores productivos.",
        "activa": True,
    },

    # ============ COMERCIO EXTERIOR (5) ============
    {
        "id": "cari",
        "nombre": "CARI",
        "categoria": "Comercio Exterior",
        "tier": 1,
        "rss": "https://cari.org.ar/feed/",
        "web": "https://cari.org.ar",
        "descripcion": "Consejo Argentino para las Relaciones Internacionales. El think tank más prestigioso en RR.II.",
        "activa": True,
    },
    {
        "id": "cei",
        "nombre": "CEI / Cancillería",
        "categoria": "Comercio Exterior",
        "tier": 1,
        "rss": "https://cancilleria.gob.ar/es/cei/feed",
        "web": "https://cancilleria.gob.ar/es/cei",
        "descripcion": "Centro de Economía Internacional (Ministerio de RR.EE.).",
        "activa": True,
    },
    {
        "id": "iri",
        "nombre": "IRI La Plata",
        "categoria": "Comercio Exterior",
        "tier": 2,
        "rss": "https://www.iri.edu.ar/feed/",
        "web": "https://www.iri.edu.ar",
        "descripcion": "Instituto de Relaciones Internacionales de la UNLP.",
        "activa": True,
    },
    {
        "id": "cac",
        "nombre": "CAC",
        "categoria": "Comercio Exterior",
        "tier": 2,
        "rss": "https://www.cac.com.ar/feed/",
        "web": "https://www.cac.com.ar",
        "descripcion": "Cámara Argentina de Comercio y Servicios.",
        "activa": True,
    },
    {
        "id": "elizondo",
        "nombre": "Marcelo Elizondo",
        "categoria": "Comercio Exterior",
        "tier": 2,
        "rss": "https://marceloelizondo.com.ar/feed/",
        "web": "https://marceloelizondo.com.ar",
        "descripcion": "Especialista en comercio internacional. Director del Comité de Economía Internacional del CARI.",
        "activa": True,
    },

    # ============ AUTOMOTOR (4) ============
    {
        "id": "acara",
        "nombre": "ACARA",
        "categoria": "Automotor",
        "tier": 1,
        "rss": "https://www.acara.org.ar/feed/",
        "web": "https://www.acara.org.ar",
        "descripcion": "Asociación de Concesionarios. Fuente oficial de patentamientos mensuales.",
        "activa": True,
    },
    {
        "id": "adefa",
        "nombre": "ADEFA",
        "categoria": "Automotor",
        "tier": 1,
        "rss": "https://www.adefa.org.ar/feed/",
        "web": "https://www.adefa.org.ar",
        "descripcion": "Asociación de Fábricas de Automotores. Datos de producción y exportación.",
        "activa": True,
    },
    {
        "id": "arodarpost",
        "nombre": "A Rodar Post",
        "categoria": "Automotor",
        "tier": 1,
        "rss": "https://arodarpost.com.ar/feed/",
        "web": "https://arodarpost.com.ar",
        "descripcion": "Cobertura del mercado automotor por Horacio Alonso.",
        "activa": True,
    },
    {
        "id": "afac",
        "nombre": "AFAC",
        "categoria": "Automotor",
        "tier": 2,
        "rss": "https://www.afac.org.ar/feed/",
        "web": "https://www.afac.org.ar",
        "descripcion": "Asociación de Fábricas Argentinas de Componentes (autopartistas).",
        "activa": True,
    },

    # ============ LOGÍSTICA (4) ============
    {
        "id": "cedol",
        "nombre": "CEDOL",
        "categoria": "Logística",
        "tier": 1,
        "rss": "https://www.cedol.org.ar/feed/",
        "web": "https://www.cedol.org.ar",
        "descripcion": "Cámara Empresaria de Operadores Logísticos. Publica el Índice de Costos Logísticos homologado por UTN.",
        "activa": True,
    },
    {
        "id": "fadeeac",
        "nombre": "FADEEAC",
        "categoria": "Logística",
        "tier": 1,
        "rss": "https://www.fadeeac.org.ar/feed/",
        "web": "https://www.fadeeac.org.ar",
        "descripcion": "Federación Arg. de Entidades del Autotransporte de Cargas. Publica el ICT auditado por UBA.",
        "activa": True,
    },
    {
        "id": "argenports",
        "nombre": "Argenports",
        "categoria": "Logística",
        "tier": 2,
        "rss": "https://argenports.com/feed/",
        "web": "https://argenports.com",
        "descripcion": "Puertos y logística marítima.",
        "activa": True,
    },
    {
        "id": "tradenews",
        "nombre": "Trade News",
        "categoria": "Logística",
        "tier": 3,
        "rss": "https://www.trade-news.com.ar/feed/",
        "web": "https://www.trade-news.com.ar",
        "descripcion": "Medio especializado en comercio exterior y logística.",
        "activa": True,
    },
    {
        "id": "webpicking",
        "nombre": "Webpicking",
        "categoria": "Logística",
        "tier": 2,
        "rss": "https://webpicking.com/feed/",
        "web": "https://webpicking.com",
        "descripcion": "Portal de logística y supply chain en América Latina.",
        "activa": True,
    },

    # ============ INTERNACIONAL (5) ============
    {
        "id": "ft",
        "nombre": "Financial Times",
        "categoria": "Internacional",
        "tier": 1,
        "rss": "https://www.ft.com/rss/home",
        "web": "https://www.ft.com",
        "descripcion": "Diario económico internacional de referencia.",
        "activa": True,
    },
    {
        "id": "economist",
        "nombre": "The Economist",
        "categoria": "Internacional",
        "tier": 1,
        "rss": "https://www.economist.com/finance-and-economics/rss.xml",
        "web": "https://www.economist.com",
        "descripcion": "Sección Finance & Economics.",
        "activa": True,
    },
    {
        "id": "bloomberg",
        "nombre": "Bloomberg Economics",
        "categoria": "Internacional",
        "tier": 1,
        "rss": "https://feeds.bloomberg.com/economics/news.rss",
        "web": "https://www.bloomberg.com",
        "descripcion": "Sección Economics de Bloomberg.",
        "activa": True,
    },
    {
        "id": "fmi",
        "nombre": "FMI",
        "categoria": "Internacional",
        "tier": 1,
        "rss": "https://www.imf.org/en/News/rss",
        "web": "https://www.imf.org",
        "descripcion": "Fondo Monetario Internacional. Comunicados oficiales.",
        "activa": True,
    },
    {
        "id": "cepal",
        "nombre": "CEPAL",
        "categoria": "Internacional",
        "tier": 2,
        "rss": "https://www.cepal.org/es/rss/noticias.xml",
        "web": "https://www.cepal.org",
        "descripcion": "Comisión Económica para América Latina y el Caribe.",
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
