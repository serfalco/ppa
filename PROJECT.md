# PPA — Refundación

Estado: **operando en producción** · Fase A (autonomía y memoria) casi cerrada

Este archivo es el tablero maestro del nuevo PPA. El documento que gobierna las
decisiones es el [Documento integral v2.0](docs/00-documento-integral-v2.md).

## Dónde estamos

PPA publica solo, todos los días, sin intervención. Las dos ediciones salen
puntuales, los datos se actualizan solos y el sitio se despliega en Cloudflare
Pages al pushear a `main`. El activo que se está construyendo no es la portada
sino el cerebro: la memoria histórica, la trazabilidad y las relaciones entre
hechos y datos.

## Etapas del roadmap

| Etapa | Estado | Evidencia |
|---|---|---|
| 0. Definición | ✅ Terminada | 18 documentos en `docs/`, rector v2.0 |
| 1. Prototipo editorial | ✅ Terminada | Sitio completo en producción |
| 2. Agregador | ✅ Terminada | Ambas ediciones a diario; 37 fuentes activas, todas sanas |
| 3. Administración | ⚠️ Parcial | Panel funciona, pero sigue accesible por URL |
| 4. Datos PPA | ✅ En producción | 20 indicadores vivos; Tablero en el menú |
| 5. Migración | ✅ Terminada | Cloudflare Pages conectado; sin FTP ni Hostinger |

## Fases del documento integral (§41)

| Fase | Estado | Falta |
|---|---|---|
| A · Autonomía y memoria | Casi cerrada | Solo falta la puerta: 14 días corridos sin carga manual |
| B · Cerebro editorial | Pendiente | Texto completo, clustering, jerarquización, apertura |
| C · Documentos oficiales | Pendiente | Calendario INDEC, Boletín Oficial, licitaciones |
| D · Salud y transparencia | Parcial | Salud de fuentes ✅; falta tablero público y reporte semanal |
| E · Expansión | Pendiente | La Data narrada, REM avanzado, FCI, ON, nuevas salidas |

## Pendientes conocidos

Ordenados por impacto, según la prioridad recomendada del documento integral (§42).

1. **Panel sin autenticación** — `/panel69/` y `/admin/` son HTML accesible por
   URL (el mismo archivo servido en dos rutas). `site/_headers` los marca
   `noindex`, pero eso no es protección. Alcance real, verificado el 12/08: no
   hay credenciales embebidas y el panel solo lee tres JSON que ya son
   públicos, así que hoy no filtra nada que no esté publicado — lo que expone
   es la herramienta, no los datos. Igual hay que cerrarlo antes de darle
   capacidad de escritura. La solución prevista es Cloudflare Access (gratis),
   paso 11 de `docs/09`: son clics en el dashboard, no código.
2. **El TCRM está congelado y no hay fuente de reemplazo** — desde el 17/06.
   `datos.gob.ar` devuelve 400 para `168.1_T_CAMBIOR_D_0_0_26`, y las series de
   tipo de cambio real que sí existen ahí son **bilaterales** (Canadá, China,
   México, Uruguay, Vietnam, Chile) y **cortaron todas el 28/01/2026**. La API
   del BCRA tampoco lo tiene: solo minorista, mayorista y contable. La vía que
   queda es la planilla oficial `ITCRMSerie.xlsx` del BCRA, que es otra forma
   de bajada (Excel, no JSON) y hay que construirla.
3. **Merval y BADLAR conservan el valor previo** — Merval da 404 en
   argentinadatos y BADLAR da 400 en la variable 6 de la API BCRA v4. Ninguno
   rompe nada, pero los dos muestran un dato viejo sin decirlo.
4. **Un cron salteado** — la Merienda del 6 de agosto de 2026 no corrió (no
   existe la ejecución, no es que no hubo cambios). Los crons de GitHub
   Actions no garantizan puntualidad ni ejecución bajo carga, y hoy nada avisa
   cuando una edición no sale.
5. **EconoTuits vive de cache** — nueve cuentas de Nitter devuelven 404. Salen
   31 tuits, pero la mayoría no se refrescan.
6. **REM y Columnas vacías** — REM en 0 ediciones, Columnas no genera nada.
7. **Node 20 deprecado** — `actions/checkout@v4` y `actions/setup-python@v5`
   lo usan; GitHub ya los fuerza a Node 24 y avisa en cada corrida.

Cerrados el 11 y 12 de agosto de 2026: el MULC quedó automático
(`MULC_BCRA_ID = 78`); los resúmenes con IA se verificaron generando en
producción con `gemini-flash-latest`; el crash del Tablero, Documentos en cero
y la salud de fuentes inflada quedaron arreglados; y las tres fuentes caídas se
diagnosticaron y se dieron de baja por no tener ya un feed que corresponda a lo
que dicen ser.

## Regla de trabajo

Una tarea sólo entra en "terminado" cuando tiene un resultado visible, una
forma de verificarlo y documentación actualizada.

## Documentos

- **[Documento integral v2.0](docs/00-documento-integral-v2.md)** — el que manda
- [Documento rector v0.1](docs/00-documento-rector.md) — fundacional, superado
- [Mapa del sitio](docs/01-mapa-del-sitio.md)
- [Modelo editorial](docs/02-modelo-editorial.md)
- [Catálogo de fuentes](docs/03-catalogo-de-fuentes.md)
- [Catálogo de datos](docs/04-catalogo-de-datos.md)
- [Arquitectura Cloudflare](docs/05-arquitectura-cloudflare.md)
- [Roadmap](docs/06-roadmap.md)
- [Operación y emergencias](docs/07-operacion-y-emergencias.md)
- [Guía de estilo](docs/08-guia-de-estilo.md)
- [Migración a Cloudflare Pages](docs/09-migracion-cloudflare-pages.md)
- [Auditoría julio 2026](docs/10-auditoria-julio-2026.md)
- [Decisiones (ADR)](docs/decisiones/)
