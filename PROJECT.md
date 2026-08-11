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
| 2. Agregador | ✅ Terminada | Ambas ediciones a diario; 34 de 38 fuentes sanas |
| 3. Administración | ⚠️ Parcial | Panel funciona, pero sigue accesible por URL |
| 4. Datos PPA | ✅ En producción | 20 indicadores vivos; Tablero en el menú |
| 5. Migración | ✅ Terminada | Cloudflare Pages conectado; sin FTP ni Hostinger |

## Fases del documento integral (§41)

| Fase | Estado | Falta |
|---|---|---|
| A · Autonomía y memoria | Casi cerrada | MULC automático; puerta de 14 días sin carga manual |
| B · Cerebro editorial | Pendiente | Texto completo, clustering, jerarquización, apertura |
| C · Documentos oficiales | Pendiente | Calendario INDEC, Boletín Oficial, licitaciones |
| D · Salud y transparencia | Parcial | Salud de fuentes ✅; falta tablero público y reporte semanal |
| E · Expansión | Pendiente | La Data narrada, REM avanzado, FCI, ON, nuevas salidas |

## Pendientes conocidos

Ordenados por impacto, según la prioridad recomendada del documento integral (§42).

1. **MULC sin automatizar** — `MULC_BCRA_ID = None` en `datos_economicos.py`.
   Correr `scripts/descubrir_bcra.py mulc compra divisas` donde haya internet,
   verificar contra el Informe Monetario Diario y setear el ID. Es lo último
   que bloquea la puerta de salida de la Fase A.
2. **Panel sin autenticación** — `/panel69/` y `/admin/` son HTML accesible por
   URL. `site/_headers` los marca `noindex`, pero eso no es protección.
   La solución prevista es Cloudflare Access (gratis), en `docs/09`.
3. **Resúmenes de Gemini sin verificar** — el paso corre con
   `continue-on-error`, así que si la key falla, falla en silencio. Confirmar
   que `gemini-2.5-flash-lite` está generando resúmenes de verdad.
4. **Un cron salteado** — la Merienda del 6 de agosto de 2026 no corrió (no
   existe la ejecución, no es que no hubo cambios). Los crons de GitHub
   Actions no garantizan puntualidad ni ejecución bajo carga.
5. **Tres fuentes caídas** — `fundar`, `microjuris_laboral` y
   `noticiasnet_energia`. Desde el fix del diagnóstico, el registro de salud
   informa el motivo real (404, bloqueo, XML inválido) en vez de un mensaje
   genérico: mirar `data/fuentes_runtime.json` tras la próxima corrida.

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
