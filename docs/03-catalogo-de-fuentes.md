# Catálogo inicial de fuentes

Estado: base para auditoría. Una fuente listada aquí todavía no implica aprobación técnica.

## 1. Criterios de admisión

Una fuente se acepta cuando cumple la mayoría de estos criterios:

- Autoría identificable.
- URL estable.
- Fecha de publicación disponible.
- Contenido relevante para PPA.
- Frecuencia razonable.
- Posibilidad técnica y legal de lectura automatizada.
- Historial bajo de errores.
- Aporte que no duplica otras fuentes.

## 2. Estados posibles

| Estado | Significado |
|---|---|
| Candidata | Todavía no probada |
| En prueba | Se está midiendo |
| Activa | Puede publicar |
| Degradada | Funciona con fallos o retrasos |
| Suspendida | No publica, conserva historial |
| Descartada | No se volverá a intentar salvo decisión nueva |

## 3. Niveles de confianza

### Nivel A — fuente primaria

Organismos públicos, documentos oficiales, emisores o instituciones responsables del dato.

### Nivel B — fuente especializada

Medios sectoriales, cámaras, consultoras y centros de estudio con autoría clara.

### Nivel C — fuente general

Medios económicos o generales utilizados para actualidad y contexto.

### Nivel D — señal social

Publicaciones personales o institucionales en redes. Sirven para detectar temas; no sustituyen un documento primario cuando éste existe.

## 4. Fuentes públicas prioritarias

| Fuente | Uso | Nivel | Situación inicial |
|---|---|---:|---|
| BCRA | Reservas, tasas, TCRM, REM, variables monetarias | A | Prioritaria |
| INDEC | IPC, actividad, empleo, salarios, COMEX | A | Prioritaria |
| datos.gob.ar | Catálogo y series públicas | A | Prioritaria con validación de vigencia |
| Ministerio de Economía | Deuda, licitaciones y resultados fiscales | A | Prioritaria |
| CNV | ON, emisores, FCI y documentos regulatorios | A | Prioritaria, extracción compleja |
| CAFCI | Industria de fondos, planillas e informes mensuales | A/B | Prioritaria para segunda etapa |
| Bolsa de Comercio de Rosario | Agro, mercados y embarques | B | Candidata |
| Agricultura | Producción, estimaciones y comercio agroindustrial | A | Candidata |
| CIARA-CEC | Liquidación del complejo agroexportador | B | Candidata |

## 5. Fuentes periodísticas

La configuración heredada contiene 38 fuentes. Todas deben volver a probarse desde cero.

La selección final debe priorizar variedad y calidad antes que cantidad. Objetivo inicial: entre 12 y 20 fuentes sanas.

Familias relevantes:

- Economía general.
- Finanzas y mercados.
- Agro.
- Energía y minería.
- Comercio exterior.
- Trabajo.
- Logística.
- Automotor.
- Fiscal.
- Consultoras y centros de estudio.
- Internacional.
- Fulbito.

## 6. Redes sociales

EconoTuits no debe depender de una cuenta o instancia no oficial sin respaldo.

Primera selección recomendada:

- 4 o 5 cuentas oficiales.
- 4 o 5 institucionales.
- 4 o 5 personales.

Cada usuario debe validarse manualmente para evitar homónimos. El sistema anterior confundió una cuenta de Hacienda argentina con contenido de Puerto Rico; la nueva versión debe identificar también nombre visible, país y URL canónica.

## 7. Fede Machado y reservas

Sus publicaciones pueden incorporarse como:

- Fuente de una estimación atribuida.
- Referencia metodológica.
- Señal para una intervención manual.

Nunca debe etiquetarse esa cifra como “dato BCRA”. Debe conservarse el enlace a la publicación utilizada y la fecha de consulta.

## 8. Fuentes financieras sin pago

Principio:

- Si no hay fuente pública suficientemente confiable, se muestra un dato demorado o no se muestra.
- No se presentará scraping frágil como información en tiempo real.
- Yahoo Finance, estimadores privados y APIs comunitarias pueden ser respaldo, nunca fuente oficial implícita.

## 9. Salud de una fuente

Por cada ejecución se registra:

- Inicio y fin.
- Estado HTTP.
- Cantidad de elementos.
- Fecha del elemento más reciente.
- Error.
- Número de fallos consecutivos.
- Último éxito.
- Duración.

Reglas sugeridas:

- Tres fallos consecutivos: degradada.
- Siete días sin éxito: suspendida automáticamente.
- Contenido antiguo pero respuesta válida: estado “sin novedades”, no “saludable”.

## 10. Próxima auditoría

Para cada una de las 38 fuentes heredadas:

1. Confirmar URL oficial.
2. Confirmar RSS o método alternativo.
3. Revisar términos de uso.
4. Medir duplicación.
5. Medir calidad de títulos y fechas.
6. Aprobar, suspender o descartar.

