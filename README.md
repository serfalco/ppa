# PPA — Pulso Productivo Argentino

Diario económico institucional de Argentina. Agregador automático de informes de instituciones, consultoras y medios financieros. Una edición editorial diaria a las 18hs (Merienda) más datos vivos durante todo el día.

## Estructura

```
ppa/
├── scripts/
│   ├── config.py          → 57 fuentes RSS, categorías, parámetros
│   ├── fetcher.py         → lee RSS, filtra, deduplica → notas.json
│   ├── selector.py        → algoritmo de destacados → portada.json
│   ├── generador.py       → arma HTML estático del sitio
│   └── exportar_config.py → exporta config para el panel admin
│
├── data/                  → JSONs generados (notas, portada, estado)
│
├── site/                  → sitio web estático (se sube a Hostinger)
│   ├── index.html         → portada (regenerada cada día)
│   ├── admin/             → panel de control con clave
│   ├── archivo/           → ediciones históricas (Google las indexa)
│   └── assets/            → CSS + JS de datos vivos
│
├── .github/workflows/
│   └── edicion-merienda.yml → cron de GitHub Actions (18hs diario)
│
└── requirements.txt
```

## Cómo corre

1. **Cron diario a las 18hs Argentina:**
   - GitHub Actions ejecuta el workflow
   - `fetcher.py` lee las 57 fuentes RSS
   - `selector.py` elige los 5 destacados
   - `generador.py` arma el HTML
   - Se hace deploy automático a Hostinger por FTP

2. **Datos vivos en el navegador (JavaScript):**
   - Cada lector que abre el sitio ve clima/dólar/riesgo país en tiempo real
   - Las APIs que se usan son todas gratis: dolarapi, argentinadatos, open-meteo
   - El widget MULC aparece solo lunes a viernes entre 17 y 20hs
   - La marquesina Fulbito aparece solo si hay partidos relevantes

3. **Panel admin (`/admin`):**
   - Pestaña Fuentes: gestionar las 57 fuentes con indicadores de salud
   - Pestaña Notas: borrar notas individuales del día
   - Pestaña Mi Columna: escribir columna semanal de Sergio Falco
   - Botón Edición Extra: dispara una regeneración manual

## Antes de la primera vez

Hay que configurar en GitHub Secrets:
- `FTP_SERVER` → servidor FTP de Hostinger
- `FTP_USERNAME` → usuario FTP
- `FTP_PASSWORD` → contraseña FTP
- `API_FOOTBALL_KEY` → key gratuita de api-football.com (para la marquesina)

Y en `site/admin/index.html` cambiar `CLAVE_HARDCODED` por tu clave real.

## Pendientes

- [ ] Validar las 57 URLs de RSS (en `scripts/config.py`)
- [ ] Configurar GitHub Secrets con datos FTP de Hostinger
- [ ] Cambiar clave del panel admin
- [ ] Crear cuenta gratis en api-football.com para la marquesina Fulbito
- [ ] Implementar webhook que procesa la cola de cambios del panel (lo dejo para v2)
- [ ] Implementar lectura del dato MULC desde Ámbito/Cronista (procesador específico)
- [ ] Implementar calendario mensual del archivo histórico (lo dejo para cuando haya 30+ ediciones)
