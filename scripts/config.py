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

# Descripciones editoriales de cada fuente, para la página de transparencia.
# Solo el texto: qué fuentes existen y con qué URL lo define FUENTES.py, que
# es el catálogo que realmente lee el fetcher.
#
# Antes esta lista era una copia entera del catálogo, con id, URL y tier
# duplicados, y se desincronizaban sin que nada avisara: al sumar CAEM y CEDOL
# al catálogo, la página "Acerca de" y fuentes_config.json siguieron mostrando
# 38 fuentes mientras el sistema leía 40. Una fuente que se publica y no se
# declara contradice la transparencia que pide el documento rector.
DESCRIPCIONES_FUENTES = {
    "aduana_news": "Comercio exterior, aduana y normativa.",
    "ambito_autos": "Sección autos de Ámbito Financiero.",
    "ambito_fin": "Sección finanzas de Ámbito Financiero.",
    "ambito_fisc": "Novedades fiscales de Ámbito Financiero.",
    "arodar": "Industria automotriz argentina, lanzamientos y mercado.",
    "autocosmos": "Noticias del mundo automotor.",
    "bichos_campo": "Actualidad del agro, ganadería y vida rural.",
    "caem": "Cámara Argentina de Empresarios Mineros. Actividad y novedades del sector minero.",
    "cedol": "Cámara Empresaria de Operadores Logísticos. Índice de costos logísticos y actividad del sector.",
    "ceso": "Centro de Estudios Económicos y Sociales Scalabrini Ortiz. Informes heterodoxos.",
    "cippec": "Centro de Implementación de Políticas Públicas. Análisis de políticas y Estado.",
    "data_energia": "Datos y análisis del sector energético.",
    "diario_autos": "Actualidad del sector automotor.",
    "econojournal": "Periodismo especializado en energía.",
    "econviews": "Consultora de Miguel Kiguel. Análisis macroeconómico.",
    "est_0221": "Estudiantes de La Plata, desde 0221.",
    "fundar": "Think tank de desarrollo productivo y políticas públicas.",
    "iaraf": "Instituto Argentino de Análisis Fiscal. Informes fiscales y tributarios.",
    "infocampo": "Noticias agropecuarias, mercados y tecnología del campo.",
    "investing_agro": "Noticias económicas y de mercados de Investing.",
    "investing_economia": "Noticias de mercados y economía.",
    "investing_intl": "Noticias económicas internacionales.",
    "investing_intl2": "Noticias económicas globales de Investing.",
    "iprof_autos": "Sección autos de iProfesional.",
    "iprof_comex": "Sección comercio exterior de iProfesional.",
    "iprof_economia": "Sección economía de iProfesional.",
    "iprof_finanzas": "Sección finanzas de iProfesional.",
    "iprof_impuestos": "Sección impuestos de iProfesional.",
    "iprof_management": "Management, empleo y recursos humanos.",
    "iproup_eco": "Economía digital y mercados.",
    "iproup_fintech": "Fintech y finanzas digitales.",
    "lanacion_eco": "Sección economía de La Nación.",
    "mercojuris": "Novedades jurídicas y de comercio exterior del Mercosur.",
    "microjuris_laboral": "Novedades de derecho laboral.",
    "motorweb": "Pruebas, lanzamientos y mercado automotor.",
    "noticiasnet_energia": "Energía y petróleo de la Patagonia.",
    "oit_podcast": "Podcast de la OIT sobre el futuro del trabajo.",
    "trade_news": "Comercio internacional y logística.",
    "vision_motor": "Revista de actualidad automotriz.",
    "webpicking": "Logística, supply chain y comercio.",
}


def _fuentes_con_descripcion():
    """El catálogo de FUENTES.py enriquecido con su descripción editorial.

    Una sola fuente de verdad: si una fuente entra o sale del catálogo, esta
    lista la sigue sola. La clave "rss" se conserva por compatibilidad con lo
    que ya consume fuentes_config.json."""
    from FUENTES import FUENTES as _CATALOGO
    salida = []
    for f in _CATALOGO:
        d = dict(f)
        d["rss"] = f.get("web", "")
        d["descripcion"] = DESCRIPCIONES_FUENTES.get(f["id"], "")
        salida.append(d)
    return salida


FUENTES = _fuentes_con_descripcion()


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
