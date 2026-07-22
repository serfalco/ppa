# Auditoría y cambios — 22 de julio de 2026

Auditoría del repo contra el documento rector v2.0 (10-jul-2026), más los cambios ejecutados en esta pasada.

## Qué encontré

El repo está mucho más avanzado que lo que dice PROJECT.md ("Etapa 0"): el agregador, las dos ediciones, el motor de datos y el sitio completo ya funcionan. La única dependencia real de Hostinger era el paso de deploy por FTP en dos workflows — no hay PHP ni backend: `site/` es 100% estático. La migración a Cloudflare Pages es una limpieza, no una obra.

Hallazgos principales, del más al menos importante:

1. **Hostinger/FTP**: solo en los pasos "Deploy a Hostinger" de `datos-mercado.yml` y `edicion-merienda.yml`. Eliminado.
2. **Sin histórico acumulativo**: `datos.json` se pisaba en cada corrida; solo TCRM guardaba serie. La memoria del sistema (el activo central según el doc rector) no se estaba construyendo.
3. **`fuentes_runtime.json` huérfano**: existe el archivo de salud de fuentes (con datos de junio) pero ningún script lo escribía — el código que lo generaba se perdió. El panel lo lee pero mostraba datos congelados.
4. **Muchas fuentes RSS rotas**: el último registro de salud muestra ~40 fuentes en error/404/403 de ~90 configuradas. Hay que depurar el catálogo (URLs de feeds que cambiaron).
5. **Riesgo país: el manual pisaba al automático**: la carga del panel tenía prioridad sobre la cadena de fuentes, al revés de lo que pide la Fase A.
6. **Gemini 1.5 Flash discontinuado**: el resumidor apuntaba a `gemini-1.5-flash`, retirado por Google. Con la key actual probablemente fallaba en silencio (el paso tiene `continue-on-error`).
7. **Paneles públicos sin auth**: `/panel69/` y `/admin/` (idénticos) son HTML accesible por URL; la cola editorial vive en localStorage del navegador. Mitigación inmediata: Cloudflare Access (gratis) — está en la guía de migración.
8. **Restos**: workflows duplicados viejos fuera de `.github/workflows/` (eliminados), `infomondia.xls` de 4.8 MB en la raíz que ningún script referencia (candidato a borrar), `generador_home_backup.py`.

## Qué cambié

- **Workflows**: fuera FTP/Hostinger; deploy pasa a ser el push a `main` con Cloudflare Pages conectado al repo. Agregué paso de histórico y alerta automática (issue de GitHub con label `alerta`) cuando un workflow falla — primera pieza del sistema de alertas del doc rector (§36).
- **`scripts/historico.py` (nuevo)**: memoria acumulativa en `data/historico/{indicador}.jsonl`. Una observación por día por indicador, solo valores frescos (no stale), escritura atómica, idempotente, fecha tomada del `generado_en` de datos.json. Base para rachas, récords y La Data narrada.
- **`scripts/fetcher.py`**: salud de fuentes real según §35 — estados ok / sin_novedades / degradada (3 fallos) / suspendida (7 días sin éxito, reintento diario) / recuperandose (3 éxitos para volver). Escribe `fuentes_runtime.json` (el panel vuelve a tener datos vivos). Testeado con suite propia.
- **`scripts/datos_economicos.py`**: riesgo país ahora automático primero (ArgentinaDatos → Rava → Ámbito → indicadores.ar), manual solo respaldo, con campo `modo` (`automatico` / `manual_respaldo`) como huella (§14). MULC preparado para API BCRA (`MULC_BCRA_ID`, ver abajo).
- **`scripts/descubrir_bcra.py` (nuevo)**: lista las variables de la API BCRA v4 filtrando por palabra clave, para encontrar el ID de compras netas MULC. Correr donde haya internet, verificar contra el Informe Monetario Diario, setear `MULC_BCRA_ID` en datos_economicos.py y el MULC queda automático.
- **`scripts/resumidor.py`**: modelo configurable por env `GEMINI_MODEL`, default `gemini-2.5-flash-lite`. Cambiar de modelo ya no toca código.
- **`site/_headers` (nuevo)**: cabeceras de seguridad + no indexar paneles + cache corto para `/data/`.
- **`docs/09-migracion-cloudflare-pages.md` (nuevo)**: guía paso a paso de conexión, dominio, Access para el panel y reactivación de crons.

## Qué NO toqué (a propósito)

- Los generadores de HTML y el diseño del sitio.
- El catálogo de fuentes (hay que depurarlo, pero es trabajo editorial con internet).
- panel69/admin (la solución correcta es Cloudflare Access + rediseño del flujo editorial, Fase D).

## Pendientes inmediatos (en orden)

1. Conectar Cloudflare Pages (guía en docs/09) y reactivar los tres workflows.
2. Verificar que la key de Gemini funcione con `gemini-2.5-flash-lite` (correr la edición manual y mirar el log del Resumidor).
3. Correr `python scripts/descubrir_bcra.py mulc compra divisas` con internet y setear `MULC_BCRA_ID`.
4. Depurar las ~40 fuentes RSS rotas (la salud ahora las va a ir suspendiendo sola, pero conviene corregir URLs de las importantes: Cronista, BCR, Bichos de Campo, INDEC, BCRA).
5. Puerta de salida Fase A: 14 días sin alimentación manual.

## Después (Fase B, por orden del doc)

Clustering de notas por hecho → resúmenes desde texto completo → verificación de cifras → apertura automática. El histórico es el insumo de La Data narrada (§5): con ~2 semanas de datos ya se pueden detectar rachas y máximos.
