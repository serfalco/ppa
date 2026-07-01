# Catálogo inicial de Datos PPA

Estado: propuesta. Ningún indicador se considera aprobado hasta validar fuente, significado y serie.

## 1. Contrato común

Todo dato debe guardar:

- Identificador estable.
- Nombre visible.
- Valor.
- Unidad.
- Fecha o período del dato.
- Momento de consulta.
- Fuente.
- URL de fuente o metodología.
- Frecuencia esperada.
- Estado: vigente, demorado, estimado, manual o no disponible.
- Observaciones.

Las observaciones históricas son acumulativas: no se reemplaza el pasado con un único JSON.

## 2. Primera prioridad

| Indicador | Fuente preferida | Frecuencia | Viabilidad | Observación |
|---|---|---|---|---|
| TCRM | BCRA | Diaria hábil | Alta | Serie y metodología oficiales |
| Reservas brutas | BCRA | Diaria hábil | Alta | No confundir con netas |
| Dólar oficial | BCRA | Diaria/intradía | Alta | Fuente oficial preferida |
| MEP y CCL | Proveedor gratuito identificado | Intradía | Media | Etiquetar demoras y fuente |
| Blue | Proveedor gratuito identificado | Intradía | Media | Es referencia informal |
| Riesgo país | Cierre atribuido o estimador identificado | Diaria | Media/baja | No existe fuente pública libre ideal |
| Tasas BCRA | BCRA | Diaria | Alta | Validar ID y definición de cada serie |
| Exportaciones | INDEC | Mensual | Alta | Base mensual descargable |
| Importaciones | INDEC | Mensual | Alta | Base mensual descargable |
| Saldo comercial | INDEC/cálculo PPA | Mensual | Alta | Mostrar si es dato o cálculo |

## 3. Segunda prioridad

| Indicador | Fuente | Frecuencia | Viabilidad | Observación |
|---|---|---|---|---|
| Compras/ventas BCRA | BCRA o carga atribuida | Diaria | Media | Puede comenzar manual |
| Reservas netas | Estimación metodológica | Variable | Media | Requiere fórmula versionada |
| IPC | INDEC | Mensual | Alta | Mensual, interanual y acumulado |
| EMAE | INDEC | Mensual | Alta | Distinguir nivel y variación |
| REM | BCRA | Mensual | Alta | Comparar relevamientos |
| Vencimientos soberanos | Economía | Mensual | Media | Requiere normalización |
| Licitaciones del Tesoro | Economía | Según calendario | Media/alta | Calendario y resultados |
| Emisiones de ON | CNV/emisores | Según evento | Media | Documentos dispersos |

## 4. Tercera prioridad

| Área | Datos posibles | Fuente inicial | Riesgo principal |
|---|---|---|---|
| FCI | Patrimonio, flujos, clases y cartera | CAFCI/CNV | Excel y PDF variables |
| Agro | Producción, precios, embarques, liquidación | Agricultura/BCR/CIARA | Licencias de cotizaciones |
| Internacional | Dow, Nasdaq, S&P 500 | Proveedor gratuito | Estabilidad y licencia |
| Empleo | Actividad, empleo, desempleo y salarios | INDEC | Diferentes frecuencias |
| Fiscal | Recaudación y resultados | ARCA/Hacienda | Cambios de formatos |

## 5. Reservas

Se presentan como series distintas:

### Reservas brutas

Dato oficial publicado por BCRA.

### Reservas netas

Estimación construida restando determinados pasivos y componentes. Debe publicar:

- Fórmula.
- Componentes incluidos y excluidos.
- Fuente de cada componente.
- Autor o criterio metodológico.
- Versión de metodología.

### Reservas líquidas

No se asume equivalente a reservas netas. Requiere definición propia.

### Metas FMI

Se muestran separadas porque responden a definiciones específicas de cada acuerdo.

## 6. Riesgo país

Campos adicionales:

- Tipo: cierre EMBI, estimador intradiario o carga manual.
- Proveedor.
- Hora de mercado.
- Diferencia respecto del último cierre.

Nunca se fusionan estimador y cierre dentro de una misma serie sin identificación.

## 7. TCRM

Debe incluir:

- Serie histórica completa.
- Valor actual.
- Promedios y rangos seleccionados.
- Variación mensual y anual.
- Bilaterales relevantes cuando estén disponibles.
- Explicación de ponderaciones y actualización.

El archivo heredado `infomondia.xls` se conserva sólo como material de contraste hasta validar que toda su información puede recuperarse de la descarga oficial del BCRA.

## 8. ON

Modelo deseado:

- Emisor.
- Clase o serie.
- Moneda.
- Monto buscado.
- Monto adjudicado.
- Tasa o margen.
- Fecha de licitación.
- Fecha de emisión.
- Vencimiento.
- Amortización.
- Calificación, cuando exista.
- Documentos originales.

Primera versión aceptable: calendario curado manualmente. La automatización total no es requisito inicial.

## 9. Fondos comunes

Primera versión posible:

- Patrimonio total de la industria.
- Participación por categoría.
- Variación mensual.
- Moneda.
- Cantidad de fondos.
- Composición agregada de cartera.

No se construirá inicialmente un recomendador ni ranking de “mejores fondos”.

## 10. Antigüedad y estados

Cada indicador define un tiempo de vigencia. Ejemplo:

| Frecuencia | Vigente | Demorado | No disponible |
|---|---|---|---|
| Intradía | Dentro del horario y ventana prevista | Superó la ventana | No hay último valor válido |
| Diaria | Último día hábil esperado | Falta una publicación | Falta por varios períodos |
| Mensual | Último período publicado | Superó calendario esperado | No existe serie válida |

La interfaz debe mostrar la fecha, no sólo un asterisco.

