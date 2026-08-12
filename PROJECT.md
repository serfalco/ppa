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
| D · Salud y transparencia | Parcial | Salud de fuentes ✅, vigía ✅ (se avisa a sí mismo si se rompe), alarma de pasos caídos ✅ — las dos probadas con simulacro; falta tablero público y reporte semanal |
| E · Expansión | Pendiente | La Data narrada, REM avanzado, FCI, ON, nuevas salidas |

## Pendientes conocidos

Ordenados por impacto, según la prioridad recomendada del documento integral (§42).

1. **REM y Columnas vacías** — REM en 0 ediciones. Columnas no genera nada
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

EconoTuits resultó ser otra cosa que lo anotado: no vivía de cache por
fuentes muertas, sino porque Nitter limita por ritmo y la corrida disparaba
veintiocho pedidos seguidos. Con pausa, sesión reusada y reintento, las
cuentas vivas vuelven a traer en el momento. Se corrigió el handle de la CNV,
se cableó el corte por antigüedad que estaba escrito sin usarse, y se
probaron las veintiocho cuentas una por una contra Nitter: diecisiete dan 404
y @laspina responde con un tuit de 2011. Quedan once activas, todas con
contenido verificado ese día — seis de ellas con tuits de la misma semana.
@SecHacienda sigue activa aunque su tuit más nuevo sea de marzo de 2025: el
corte no la publica mientras siga así, y si Nitter vuelve a ver tuits nuevos
entra sola.

También se dieron de baja `/panel69/` y `/admin/`. Eran el mismo archivo
servido en dos rutas y figuraban como riesgo de seguridad desde la auditoría
de julio, pero el problema real era otro: no hacían nada. Sin login, sin
escribir —solo `localStorage` y copiar al portapapeles— y los tres archivos
que los generadores esperaban de ellos nunca existieron en el repo. No estaban
linkeados desde ninguna página viva. Quedan en el historial de git si algún
día hace falta mirarlos.

Las alertas del repo no funcionaban, y hacía meses. Las cinco vías —"Alerta si
falló" de la edición, la del fetcher, la de datos de mercado, el vigía y el
aviso de pasos caídos— etiquetaban el issue como `alerta`, una etiqueta que no
existía en el repo. `gh issue create` aborta entero cuando falta, y el
`|| true` del final se comía el error: ninguna emitió un solo aviso. Lo
encontró el simulacro en su primer uso. Ahora la etiqueta existe, cada
workflow la crea por las dudas, y un fallo al avisar deja un `::warning::` en
vez de desaparecer.

Con la alarma andando se pudo emparejar el criterio de la edición, que hasta
ahora era arbitrario: diez pasos toleraban fallar y seis no, sin que la
diferencia respondiera a nada. La regla quedó explícita: todo lo que produce
una sección puede caerse —esa sección se queda con lo del día anterior, el
resto sale y la alarma lo dice—, y solo el fetcher y el selector cortan la
edición, porque producen las notas del día y publicar la portada de ayer con
la fecha de hoy sería mentir. Datos económicos pasó al primer grupo: adentro
cada indicador ya tiene cadena de fuentes y valor conservado, así que ninguna
API caída lo mata; lo único que lo tumbaba era un bug propio, y eso tapaba la
edición entera por una sección. La corrida del 12/08 18:49 UTC pasó los 28
pasos en verde con el criterio nuevo.

Al vigía le faltaba lo mismo que él vino a resolver. Si el script se caía por
un bug salía sin escribir `faltantes`, el aviso quedaba sin correr y el único
rastro era el rojo en Actions: un centinela que podía morir en silencio. Ahora
hay un segundo aviso para ese caso, que no afirma que faltó una edición sino
que el control quedó sin cubrir, y un simulacro para probarlo. Los dos
simulacros —el de pasos caídos y el del vigía roto— abrieron su issue: son los
únicos avisos que el repo emitió en su historia, y los dos salieron a pedido.

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
