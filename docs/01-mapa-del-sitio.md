# Mapa del sitio

Estado: propuesta inicial

## Navegación principal

1. Portada
2. La Data del Día
3. Datos PPA —se habilita al alcanzar tres módulos confiables—
4. REM
5. Columnas
6. TXT-Stream
7. EconoTuits
8. Documentos
9. Cómo trabajamos

Fulbito es una categoría editorial, no una entrada principal del menú.

## Portada

Orden acordado:

1. Cabecera sticky.
2. La Data del Día.
3. Categorías en dos columnas.
4. Tarjetas compactas de Datos PPA.
5. Columna principal a ancho completo.
6. TXT-Stream.
7. EconoTuits.
8. Footer.

### Cabecera sticky

Debe contener:

- Fecha.
- Edición actual.
- Marca PPA.
- Dólar oficial.
- MEP.
- Blue.
- Riesgo país, si existe una fuente aceptable.
- Menú hamburguesa.

En celular se prioriza legibilidad. El ticker no debe impedir abrir el menú ni provocar saltos de diseño.

### La Data del Día

Es el comienzo real de la portada. No debe haber una portada dentro de la portada ni un gran bloque promocional previo.

Cada elemento puede contener:

- Categoría.
- Título.
- Resumen propio.
- “Por qué importa”, cuando aporta valor.
- Fuente.
- Hora.
- Enlace original.

### Categorías iniciales

Taxonomía provisional:

- Agro.
- Análisis y consultoras.
- Automotor.
- Comex.
- Energía y minería.
- Finanzas.
- Fiscal.
- Internacional.
- Laboral.
- Logística.
- Mercados.
- Fulbito.

Debe existir una sola taxonomía compartida por recolección, edición, portada y archivo.

### Tarjetas de Datos PPA

Máximo recomendado en portada: seis.

Las tarjetas no son una copia del panel. Muestran sólo valor, variación, período y estado. Cada una enlaza a su explicación completa.

Si no hay datos confiables, la tarjeta no aparece.

### Columnas

- Título grande.
- Bajada.
- Primer fragmento.
- Degradado o corte visual.
- Enlace “Ver más”.

### EconoTuits

Ancho completo con tres grupos:

- Oficiales.
- Institucionales.
- Personales.

En celular se presentan como pestañas. La portada muestra pocos elementos; la página interior puede ampliar.

## La Data del Día

Página de edición completa con:

- Selector Desayuno/Merienda.
- Fecha.
- Resumen general opcional.
- Índice de categorías.
- Noticias agrupadas.
- Fuentes y horarios visibles.

## Datos PPA

Micrositio con navegación propia:

- Mercado y dólares.
- BCRA y reservas.
- TCRM.
- Tasas.
- Actividad y precios.
- Comercio exterior.
- Deuda.
- ON.
- Fondos comunes.
- Agro.
- Internacional.
- Metodologías.

No todas las secciones deben existir en el primer lanzamiento.

## REM

Debe presentar:

- Último REM.
- Expectativas por variable.
- Comparación con relevamientos anteriores.
- Explicación de qué es el REM.
- Fuente BCRA y período.

## Columnas

- Índice por fecha.
- Página individual.
- Autor.
- Bajada.
- Fecha.
- Lectura estimada.
- Artículos relacionados opcionales.

## TXT-Stream

- Índice cronológico.
- Categoría o tema.
- Página individual.
- Fuente original de audio/video cuando corresponda.
- Aviso claro cuando el texto sea una transcripción o adaptación.

El panel debe aceptar el texto generado por la herramienta actual de Gemini sin exigir edición técnica.

## Documentos

Biblioteca de informes y documentos seleccionados:

- Título.
- Organismo o autor.
- Fecha.
- Tipo de documento.
- Resumen PPA.
- Enlace original.
- Archivo preservado sólo cuando su licencia lo permita.

## Cómo trabajamos

Debe explicar:

- Selección de fuentes.
- Uso de automatización e IA.
- Política de correcciones.
- Diferencia entre dato oficial, estimación y opinión.
- Ausencia de asesoramiento financiero.
- Criterios de privacidad.

## URLs

Estructura propuesta:

```text
/
/la-data/
/la-data/AAAA-MM-DD/desayuno/
/la-data/AAAA-MM-DD/merienda/
/datos/
/datos/tcrm/
/datos/reservas/
/rem/
/columnas/
/columnas/{slug}/
/stream/
/stream/{slug}/
/econotuits/
/documentos/
/como-trabajamos/
/admin/                 acceso privado
```

