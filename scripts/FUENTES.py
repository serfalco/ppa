"""
PPA — FUENTES.py
Lista completa de fuentes RSS del sitio.

Estructura de cada fuente:
  id       : clave única (usada en portada.json como fuente_id)
  nombre   : nombre visible en el sitio
  url      : feed RSS
  categoria: sección del sitio donde aparece
  tier     : 1 = prioritaria (aparece en home), 2 = complementaria
  activa   : si False se omite del procesamiento

Categorías disponibles:
  "Macro" | "Política" | "Mercados" | "Finanzas" | "Energía" | "Agro"
  "Minería" | "Comex" | "Laboral" | "Automotor" | "Logística"
  "Internacional" | "Expectativas de mercado"
"""

FUENTES = [

    # ================================================================
    # MEDIOS — Tier 1 (La Data del día / home)
    # ================================================================
    {
        "id": "ambito",
        "nombre": "Ámbito Financiero",
        "url": "https://www.ambito.com/rss/economia.xml",
        "categoria": "Macro",
        "tier": 1,
        "activa": True,
    },
    {
        "id": "lanacion",
        "nombre": "La Nación Economía",
        "url": "https://www.lanacion.com.ar/arc/outboundfeeds/rss/category/economia/",
        "categoria": "Macro",
        "tier": 1,
        "activa": True,
    },
    {
        "id": "clarin",
        "nombre": "Clarín Economía",
        "url": "https://www.clarin.com/rss/economia/",
        "categoria": "Macro",
        "tier": 1,
        "activa": True,
    },
    {
        "id": "cronista",
        "nombre": "El Cronista",
        "url": "https://www.cronista.com/arc/outboundfeeds/rss/",
        "categoria": "Macro",
        "tier": 1,
        "activa": True,
    },
    {
        "id": "pagina12",
        "nombre": "Página 12 Economía",
        "url": "https://www.pagina12.com.ar/rss/secciones/economia/notas",
        "categoria": "Macro",
        "tier": 1,
        "activa": True,
    },
    {
        "id": "bae",
        "nombre": "BAE Negocios",
        "url": "https://www.baenegocios.com/rss",
        "categoria": "Macro",
        "tier": 1,
        "activa": True,
    },
    {
        "id": "infobae",
        "nombre": "Infobae Economía",
        "url": "https://www.infobae.com/feeds/rss/economia/",
        "categoria": "Macro",
        "tier": 1,
        "activa": True,
    },

    # ================================================================
    # INSTITUCIONALES — BCRA, INDEC, etc. (vía Nitter para Twitter)
    # ================================================================
    {
        "id": "bcra",
        "nombre": "BCRA",
        "url": "https://nitter.net/BancoCentral_AR/rss",
        "categoria": "Macro",
        "tier": 1,
        "activa": True,
    },
    {
        "id": "indec",
        "nombre": "INDEC",
        "url": "https://nitter.net/INDECArgentina/rss",
        "categoria": "Macro",
        "tier": 1,
        "activa": True,
    },
    {
        "id": "mecon",
        "nombre": "Ministerio de Economía",
        "url": "https://www.argentina.gob.ar/noticias/rss-ministerio-de-economia.xml",
        "categoria": "Política",
        "tier": 1,
        "activa": True,
    },

    # ================================================================
    # EXPECTATIVAS DE MERCADO — Tier 1
    # ================================================================
    {
        "id": "econviews",
        "nombre": "Econviews",
        "url": "https://econviews.com/feed/",
        "categoria": "Expectativas de mercado",
        "tier": 1,
        "activa": True,
    },
    {
        "id": "fiel",
        "nombre": "FIEL",
        "url": "https://www.fiel.org.ar/publicaciones/feed/",
        "categoria": "Expectativas de mercado",
        "tier": 1,
        "activa": True,
    },
    {
        "id": "ieral",
        "nombre": "IERAL (Fundación Mediterránea)",
        "url": "https://www.ieral.org/feed.xml",
        "categoria": "Expectativas de mercado",
        "tier": 1,
        "activa": True,
    },
    {
        "id": "fundar",
        "nombre": "Fundar",
        "url": "https://fund.ar/feed/",
        "categoria": "Expectativas de mercado",
        "tier": 1,
        "activa": True,
    },

    # ================================================================
    # EXPECTATIVAS DE MERCADO — Tier 2 (complementarias)
    # ================================================================
    {
        "id": "iaraf",
        "nombre": "IARAF",
        "url": "https://www.iaraf.org/index.php/informes-economicos/area-fiscal?format=feed&type=rss",
        "categoria": "Expectativas de mercado",
        "tier": 2,
        "activa": True,
    },
    {
        "id": "ceso",
        "nombre": "CESO",
        "url": "https://ceso.com.ar/feed/",
        "categoria": "Expectativas de mercado",
        "tier": 2,
        "activa": True,
    },
    {
        "id": "cedlas",
        "nombre": "CEDLAS (UNLP)",
        "url": "https://cedlas.econo.unlp.edu.ar/wp/feed/",
        "categoria": "Expectativas de mercado",
        "tier": 2,
        "activa": True,
    },
    {
        "id": "cippec",
        "nombre": "CIPPEC",
        "url": "https://www.cippec.org/feed/",
        "categoria": "Expectativas de mercado",
        "tier": 2,
        "activa": True,
    },

    # ================================================================
    # SECTORIALES
    # ================================================================
    {
        "id": "bcr",
        "nombre": "Bolsa de Cereales de Rosario",
        "url": "https://www.bcr.com.ar/feed.xml",
        "categoria": "Agro",
        "tier": 1,
        "activa": True,
    },
    {
        "id": "magyp",
        "nombre": "Ministerio de Agricultura",
        "url": "https://www.argentina.gob.ar/noticias/rss-agricultura.xml",
        "categoria": "Agro",
        "tier": 1,
        "activa": True,
    },
    {
        "id": "acara",
        "nombre": "ACARA",
        "url": "https://acara.org.ar/feed.xml",
        "categoria": "Automotor",
        "tier": 1,
        "activa": True,
    },
    {
        "id": "adefa",
        "nombre": "ADEFA",
        "url": "https://adefa.com.ar/feed.xml",
        "categoria": "Automotor",
        "tier": 1,
        "activa": True,
    },
    {
        "id": "caem",
        "nombre": "CAEM",
        "url": "https://caem.com.ar/feed/",
        "categoria": "Minería",
        "tier": 1,
        "activa": True,
    },
    {
        "id": "fmi",
        "nombre": "FMI",
        "url": "https://www.imf.org/en/News/rss?language=eng",
        "categoria": "Internacional",
        "tier": 1,
        "activa": True,
    },
    {
        "id": "cepal",
        "nombre": "CEPAL",
        "url": "https://www.cepal.org/es/rss.xml",
        "categoria": "Internacional",
        "tier": 2,
        "activa": True,
    },
]

# Lookup rápido por id
FUENTES_POR_ID = {f["id"]: f for f in FUENTES}
