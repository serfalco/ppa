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
| 3. Administración | ⏸️ Sin empezar | El panel se dio de baja: no escribía nada. El flujo editorial es Fase D |
| 4. Datos PPA | ✅ En producción | 20 indicadores vivos; Tablero en el menú |
| 5. Migración | ✅ Terminada | Cloudflare Pages conectado; sin FTP ni Hostinger |

## Fases del documento integral (§41)

| Fase | Estado | Falta |
|---|---|---|
| A · Autonomía y memoria | Casi cerrada | Solo falta la puerta: 14 días corridos sin carga manual |
| B · Cerebro editorial | Pendiente | Texto completo, clustering, jerarquización, apertura |
| C · Documentos oficiales | Pendiente | Calendario INDEC, Boletín Oficial, licitaciones |
| D · Salud y transparencia | Parcial | Salud de fuentes ✅, vigía de ediciones ✅; falta tablero público y reporte semanal |
| E · Expansión | Pendiente | La Data narrada, REM avanzado, FCI, ON, nuevas salidas |

## Pendientes conocidos

Ordenados por impacto, según la prioridad recomendada del documento integral (§42).

1. **EconoTuits vive de cache** — nueve cuentas de Nitter devuelven 404. Salen
   31 tuits, pero la mayoría no se refrescan.
2. **REM y Columnas vacías** — REM en 0 ediciones. Columnas no genera nada
   porque lee `columnas_manual.json`, que solo podía producir el panel dado de
   baja: no es un generador roto, es una sección sin flujo de carga. Igual que
   TXT-Stream con `stream_manual.json`. Reponerlos es rediseñar el flujo
   editorial, que el documento integral pone en la Fase D.

Cerrados el 11 y 12 de agosto de 2026: el MULC quedó automático
(`MULC_BCRA_ID = 78`); los resúmenes con IA se verificaron generando en
producción con `gemini-flash-latest`; el crash del Tablero, Documentos en cero
y la salud de fuentes inflada quedaron arreglados; las tres fuentes caídas se
diagnosticaron y se dieron de baja por no tener ya un feed que corresponda a lo
que dicen ser; el TCRM pasó a salir del ITCRM oficial del BCRA; y Merval y BADLAR
volvieron a publicarse — la BADLAR con el ID vigente del BCRA (140 en vez de
6) y el Merval desde Yahoo Finance, porque argentinadatos discontinuó ese
endpoint. Y el cron salteado dejó de ser un punto ciego: un vigía revisa
después de cada edición que haya salido y abre un aviso si falta. Y las
acciones de los workflows subieron a las versiones sobre Node 24, así que se
terminó el warning en cada corrida.

También se dieron de baja `/panel69/` y `/admin/`. Eran el mismo archivo
servido en dos rutas y figuraban como riesgo de seguridad desde la auditoría
de julio, pero el problema real era otro: no hacían nada. Sin login, sin
escribir —solo `localStorage` y copiar al portapapeles— y los tres archivos
que los generadores esperaban de ellos nunca existieron en el repo. No estaban
linkeados desde ninguna página viva. Quedan en el historial de git si algún
día hace falta mirarlos.

Sobre el TCRM conviene recordar qué pasó, porque es el caso que más se puede
repetir: no había página. El generador bajaba la serie de datos.gob.ar en cada
corrida y armaba `/tcrm/` con eso, y como esa API dejó de responder abortaba
antes de escribir el cache, así que el fallback no tenía nada que usar. El
número que se mostraba era 1460 con unidad "índice", casi igual al dólar
mayorista: no era el ITCRM. La planilla oficial da 85,41 al 11/08, que es la
magnitud correcta para un índice base 17/12/2015=100.

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
