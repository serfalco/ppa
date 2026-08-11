# PPA — Documento integral del diario económico automático

**Proyecto:** Pulso Productivo Argentino · pulsoproductivo.com.ar  
**Responsable:** Sergio Falco (Checho)  
**Versión:** 2.0 integrada  
**Fecha:** 10 de julio de 2026  
**Estado:** documento rector y propuesta de arquitectura — no implica cambios automáticos en el repositorio

---

## 1. Idea central

PPA no debe pensarse solamente como una página web ni como un agregador de noticias.

El verdadero producto es un **motor de conocimiento económico argentino** que:

1. recolecta noticias, datos y documentos;
2. identifica hechos;
3. agrupa coberturas repetidas;
4. conecta los hechos con indicadores;
5. jerarquiza por relevancia;
6. redacta con trazabilidad;
7. verifica cifras, nombres y fechas;
8. acumula memoria histórica;
9. publica distintas salidas.

El diario web es una de esas salidas. El mismo núcleo podría alimentar más adelante:

- newsletter;
- canal de WhatsApp;
- Telegram;
- podcast;
- videos;
- redes sociales;
- API pública;
- informes especiales.

La evolución conceptual es:

```text
Fuentes → Noticias → Página web
```

hacia:

```text
Fuentes
   ↓
Cerebro PPA
   ↓
Conocimiento económico estructurado
   ↓
Web · Newsletter · WhatsApp · Podcast · Video · API
```

---

## 2. Diagnóstico: qué existe hoy

Aunque el repositorio pueda definirse como una etapa inicial, PPA ya opera como un diario semiautomático razonablemente sólido.

### Lo que ya funciona

- Agregador con decenas de fuentes RSS verificadas.
- Cache por niveles de actualización.
- Fetcher tolerante a fallos.
- Cache versionado en GitHub.
- Filtro de títulos basura.
- Deduplicación básica.
- Cupos por categoría y fuente.
- Ocho notas seleccionadas para portada.
- Dos ediciones diarias automáticas:
  - Desayuno.
  - Merienda.
- Datos de:
  - dólares;
  - brecha;
  - reservas;
  - BADLAR;
  - base monetaria;
  - M2;
  - UVA;
  - circulación;
  - IPC;
  - IPC núcleo;
  - EMAE;
  - TCRM;
  - Merval;
  - riesgo país;
  - banda cambiaria.
- Conservación del último valor válido.
- Uso de valores “stale” cuando una fuente no actualiza.
- Resúmenes con IA.
- Documentación editorial y técnica avanzada.

### Brechas actuales

1. La IA comprime títulos y bajadas, pero todavía no comprende el texto completo.
2. Algunas cargas manuales contradicen el objetivo de autonomía.
3. No existe agrupamiento semántico real por tema.
4. La jerarquización depende demasiado de recencia y cupos.
5. Falta implementar completamente la salud automática de fuentes.
6. No hay un histórico acumulativo completo para todos los datos.
7. EconoTuits depende de una infraestructura frágil.
8. TXT-Stream depende todavía de carga manual.
9. La web muestra información, pero el sistema todavía no construye una memoria económica unificada.

---

## 3. La estructura editorial de PPA

La navegación principal propuesta es:

1. Portada
2. La Data del Día
3. Datos PPA
4. REM
5. Columnas
6. TXT-Stream
7. EconoTuits
8. Documentos
9. En criollo
10. Cómo trabajamos

Cada sección es una forma diferente de mostrar lo que el cerebro ya procesó.

---

## 4. Portada

La portada debe ser una edición y no una simple lista de enlaces.

### Contenido

- Apertura editorial automática.
- Entre seis y ocho temas principales.
- Una tarjeta por hecho, no una tarjeta por medio.
- Fuentes múltiples debajo de cada tema.
- La Data del Día.
- Agenda económica.
- Indicadores destacados.
- Acceso a documentos primarios.
- Alertas sobre publicaciones próximas:
  - IPC;
  - REM;
  - licitaciones;
  - recaudación;
  - actividad;
  - comercio exterior.

### Apertura editorial

La apertura debe unir:

- los dos o tres temas principales;
- los movimientos de datos relevantes;
- lo que se espera durante el día;
- el contexto económico inmediato.

Debe firmarse de forma transparente como:

**Redacción automática PPA**

La apertura solo puede usar hechos y datos presentes en el sistema. No puede inventar explicaciones ni completar vacíos por intuición.

---

## 5. La Data del Día

Es una lectura breve y automática de los movimientos significativos.

No es solo mostrar números. Debe detectar:

- máximos y mínimos;
- cruces de umbrales;
- rachas;
- aceleraciones;
- cambios de tendencia;
- diferencias contra el día anterior;
- diferencias contra la semana y el mes;
- relaciones plausibles con hechos del día.

Ejemplos:

> El riesgo país acumula cinco ruedas consecutivas de baja.

> Las reservas cerraron en su mayor nivel de los últimos tres meses.

> El dólar financiero subió, pero la brecha se mantuvo estable por la variación del oficial.

La explicación debe separar siempre:

- dato;
- cálculo PPA;
- estimación;
- interpretación editorial.

---

## 6. Datos PPA

Datos PPA es el sistema estructurado de indicadores y micrositios.

### Primera versión

- TCRM histórico.
- TCRM bilateral.
- Dólar oficial.
- Dólar MEP.
- Dólar CCL.
- Dólar blue.
- Compras y ventas del BCRA.
- Reservas internacionales brutas.
- Riesgo país.
- Tasas del BCRA.
- Inflación.
- EMAE y actividad.
- Exportaciones.
- Importaciones.
- Saldo comercial.
- Principales socios comerciales.
- Calendario de vencimientos soberanos.
- Emisiones de obligaciones negociables.
- Fondos comunes de inversión.
- Mercados internacionales.
- Agro.
- Energía.
- Empleo.
- Recaudación.

Cada indicador debe cumplir un contrato de datos común:

- valor;
- unidad;
- fecha del dato;
- fecha de consulta;
- fuente;
- método de obtención;
- frecuencia;
- vigencia;
- estado;
- intervención editorial;
- explicación;
- metodología;
- histórico.

---

## 7. El sistema “En criollo”

Las definiciones no deben redactarse manualmente cada vez que aparece un término.

“En criollo” debe convertirse en una pieza estructural y reutilizable.

Cada concepto tendrá una ficha única con:

- Qué es.
- Qué mide.
- Cómo se calcula.
- Qué no mide.
- Fuente.
- Frecuencia.
- Fecha del dato.
- Nota metodológica.
- Intervención editorial, si la hubo.
- Ejemplo.
- Histórico.
- Documentación oficial relacionada.

Ejemplo:

> **En criollo:** el TCRM compara el poder del peso contra las monedas de los principales socios comerciales, corrigiendo por inflación.

La misma definición se reutiliza en:

- tarjetas de Datos PPA;
- notas;
- aperturas;
- documentos;
- glosario;
- ayudas emergentes;
- enlaces internos.

Los términos económicos detectados en textos se enlazan automáticamente a sus fichas.

### Primer micrositio recomendado

**TCRM**

Porque tiene:

- serie histórica;
- frecuencia diaria;
- metodología oficial;
- explicación pedagógica útil;
- vínculos con comercio exterior, inflación y competitividad.

---

## 8. REM

El REM debe ser más que una tabla mensual.

Debe mostrar:

- valor esperado actual;
- valor esperado en el relevamiento anterior;
- variación de expectativas;
- dispersión entre participantes;
- evolución histórica;
- comparación contra el dato finalmente observado;
- errores pasados de pronóstico;
- resumen “En criollo”.

Ejemplo:

> El mercado ahora espera una inflación anual menor que en el relevamiento anterior, pero elevó su estimación de tipo de cambio.

---

## 9. Columnas

Esta sección debe conservar identidad humana.

### Regla editorial

- La IA no escribe columnas de opinión.
- Puede ayudar a editar, corregir o estructurar.
- Debe quedar claro quién firma.
- Opinión y hechos deben estar separados.
- Las fuentes y datos mencionados deben enlazarse.

Las columnas pueden funcionar como la parte humana de un sistema mayormente automático.

---

## 10. TXT-Stream

TXT-Stream puede convertirse en una sección automática de entrevistas, streams y podcasts.

### Estado actual

- El generador técnico existe.
- La sección depende de carga manual.
- Hay poca o ninguna producción reciente.

### Rediseño

1. Lista blanca de canales y playlists.
2. Detección automática de nuevos videos.
3. Obtención de transcripciones.
4. Resumen de 300 a 500 palabras.
5. Identificación de:
   - entrevistado;
   - contexto;
   - ideas centrales;
   - cifras;
   - citas breves;
   - minutos relevantes.
6. Verificación de citas contra la transcripción.
7. Embed y enlace al contenido original.
8. Declaración visible del grado de edición.

Si no se puede verificar una cita, se publica solamente:

- video;
- metadatos;
- enlace;
- breve descripción segura.

La sección no debe rellenarse por obligación. Si no hay buen material, no publica.

---

## 11. EconoTuits

La sección no debería depender de una única instancia de Nitter.

### Problemas detectados

- Muchas cuentas configuradas no entregan contenido fresco.
- Existen caches congelados.
- Hay riesgo de homónimos.
- El filtro de frescura debe ser obligatorio.
- Una única instancia externa es un punto de falla.

### Rediseño

- Bluesky como fuente estable.
- Telegram para organismos y consultoras.
- Nitter solo como fuente opcional o degradada.
- Registro de verificación de cada cuenta:
  - nombre;
  - handle;
  - país;
  - URL;
  - evidencia;
  - fecha de verificación.
- Curaduría de 12 a 15 cuentas.
- Eliminación automática de publicaciones viejas.
- Agrupamiento de conversaciones por tema.
- Sección “Lo que se comenta”.

### Regla central

Una publicación social nunca se convierte automáticamente en fuente de una cifra.

Puede:

- disparar una búsqueda;
- conducir al documento primario;
- publicarse como opinión atribuida;
- mostrarse como estimación del autor.

Nunca debe confundirse con un dato oficial.

---

## 12. Documentos

PPA puede diferenciarse explotando documentos oficiales con calendario conocido.

### Fuentes prioritarias

- INDEC.
- BCRA.
- Ministerio de Economía.
- Tesoro.
- ARCA.
- Boletín Oficial.
- FMI.
- Secretaría de Energía.
- CNV.
- CIARA-CEC.
- SIPA.
- Presupuesto Abierto.

### Documentos automatizables

- Calendario de difusión del INDEC.
- Informes técnicos del IPC.
- EMAE.
- Comercio exterior.
- Mercado de cambios.
- REM.
- Licitaciones del Tesoro.
- Recaudación.
- Boletín Oficial.
- Liquidación agroexportadora.
- Trabajo registrado.
- Deuda pública.
- Emisiones de ON.

### Proceso

1. Detectar documento nuevo.
2. Descargarlo.
3. Extraer texto y tablas.
4. Identificar cifras clave.
5. Validar rangos plausibles.
6. Comparar con el dato anterior.
7. Generar resumen.
8. Enlazar al documento primario.
9. Guardar la extracción estructurada.
10. Publicar solo si pasa la verificación.

Si la extracción falla, se publica únicamente:

> Salió el informe — consultar documento oficial.

---

## 13. Fuentes por método de ingesta

### Capa 1 — APIs estructuradas

- BCRA API.
- datos.gob.ar.
- ArgentinaDatos.
- DolarApi.
- CriptoYa.
- Data912.
- Presupuesto Abierto.
- Secretaría de Energía.
- FRED.
- Stooq.
- CoinGecko.
- FMI.

Son las fuentes más fáciles de automatizar y verificar.

### Capa 2 — Documentos oficiales

- PDFs.
- Excel.
- comunicados;
- boletines;
- calendarios;
- resoluciones.

Requieren extracción y controles adicionales.

### Capa 3 — RSS periodístico

- Medios económicos.
- diarios nacionales;
- consultoras;
- medios sectoriales;
- fuentes regionales.

Sirven para detectar hechos, cobertura y contexto.

### Capa 4 — Señal social y multimedia

- Bluesky.
- Telegram.
- YouTube.
- podcasts.
- Nitter como respaldo eventual.

Es la capa más frágil y debe usarse como señal, no como verdad primaria.

---

## 14. Riesgo país

No deben mezclarse:

1. cierre atribuido a JP Morgan;
2. estimador intradiario;
3. valor manual o editorial.

Cada serie debe mostrarse separada.

### Campos obligatorios

- tipo de valor;
- fuente;
- fecha;
- hora;
- método;
- responsable, si hubo intervención;
- estado de verificación.

Ejemplo:

```text
Estimador intradiario
Fuente consultada: ...
Hora: ...
Método: ...
```

El panel puede permitir intervención, pero debe dejar una huella visible.

---

## 15. Reservas

Separar claramente:

- reservas internacionales brutas;
- reservas netas;
- reservas líquidas;
- meta FMI.

### Reglas

- Las reservas brutas provienen del BCRA.
- Las reservas netas son una estimación.
- Las reservas líquidas son una estimación.
- La meta FMI responde a un criterio específico del programa.

No deben publicarse reservas netas sin:

- fórmula;
- versión de metodología;
- tratamiento de swaps;
- encajes;
- DEG;
- oro;
- obligaciones;
- atribución.

Si se adopta un criterio externo, debe quedar documentado y versionado.

---

## 16. Comercio exterior

COMEX es altamente viable.

### Datos posibles

- exportaciones;
- importaciones;
- saldo;
- grandes rubros;
- usos económicos;
- socios;
- cantidades;
- precios;
- series históricas.

Fuentes:

- INDEC;
- datos.gob.ar;
- bases descargables oficiales.

El micrositio puede conectar comercio exterior con:

- TCRM;
- actividad;
- agro;
- energía;
- Brasil;
- China;
- reservas;
- recaudación.

---

## 17. Vencimientos soberanos

Es viable, pero exige normalización editorial.

### Fuentes

- reportes mensuales;
- reportes trimestrales;
- deuda pública;
- boletines de Economía;
- cronogramas oficiales.

### Datos a estructurar

- fecha;
- instrumento;
- moneda;
- capital;
- interés;
- jurisdicción;
- tenedor;
- monto;
- estado;
- fuente.

La normalización debe conservar siempre el documento original.

---

## 18. Obligaciones negociables

La CNV ofrece información, pero está dispersa.

### Primera etapa

Calendario curado:

- empresa;
- instrumento;
- moneda;
- tasa;
- monto;
- fecha de suscripción;
- vencimiento;
- resultado.

### Segunda etapa

Automatización desde:

- avisos de suscripción;
- prospectos;
- suplementos;
- resultados.

---

## 19. Fondos comunes de inversión

FCI merece un micrositio propio.

### Datos posibles

- patrimonio total;
- suscripciones;
- rescates;
- participación por tipo;
- moneda;
- duración;
- cartera;
- money market;
- renta fija;
- renta variable;
- evolución histórica.

### Fuentes

- CAFCI;
- ArgentinaDatos;
- planillas diarias;
- informes mensuales.

La extracción debe validarse con un prototipo porque algunas descargas pueden presentar problemas técnicos.

---

## 20. Internacional y agro

### Internacional

Indicadores sugeridos:

- S&P 500;
- Dow Jones;
- Nasdaq;
- petróleo Brent;
- Bitcoin;
- tasas internacionales;
- bonos del Tesoro estadounidense.

No depender de Yahoo Finance como fuente central sin revisar estabilidad y condiciones de uso.

### Agro

- precios;
- exportaciones;
- liquidación;
- producción;
- embarques;
- cosecha;
- principales complejos exportadores.

Fuentes posibles:

- INDEC;
- BCR;
- CIARA-CEC;
- Agricultura;
- datos oficiales sectoriales.

Las cotizaciones en tiempo real pueden requerir acuerdos específicos.

---

## 21. El cerebro PPA

El sitio no es el cerebro.

El cerebro es el sistema que transforma fuentes dispersas en conocimiento estructurado.

### Flujo general

```text
RSS · APIs · PDFs · BCRA · INDEC · Mercados
                       ↓
                  Recolector
                       ↓
                  Normalizador
                       ↓
             Detector de hechos
                       ↓
              Clustering de temas
                       ↓
            Relación con indicadores
                       ↓
               Jerarquización
                       ↓
                Redacción IA
                       ↓
                Verificación
                       ↓
          JSON · HTML · Micrositios
                       ↓
             Cloudflare Pages
```

---

## 22. Cómo piensa durante el día

### 22.1 Observa

Lee periódicamente:

- RSS;
- APIs;
- BCRA;
- INDEC;
- Boletín Oficial;
- mercado;
- documentos;
- redes verificadas.

Todavía no publica.

### 22.2 Entiende

Convierte múltiples notas en un solo hecho.

Ejemplo:

- “El Tesoro renovó el 120%”.
- “Fuerte licitación del Gobierno”.
- “Economía consiguió refinanciar vencimientos”.

El cerebro entiende que es el mismo tema.

### 22.3 Relaciona

Conecta el hecho con:

- deuda;
- bonos;
- riesgo país;
- vencimientos;
- tasas;
- liquidez;
- expectativas.

### 22.4 Mira los datos

Observa si al mismo tiempo:

- bajó el riesgo país;
- subieron los bonos;
- se movió el dólar;
- cambiaron las reservas;
- aumentó la cobertura mediática.

### 22.5 Decide importancia

Calcula un puntaje con:

1. cantidad de fuentes independientes;
2. calidad de la mejor fuente;
3. recencia;
4. conexión con indicadores;
5. relevancia económica;
6. presencia de documento primario;
7. penalizaciones por duplicación, opinión o baja calidad.

### 22.6 Escribe

Resume el hecho y no una nota individual.

Debajo muestra:

- fuente oficial;
- coberturas periodísticas;
- documentos;
- datos relacionados.

### 22.7 Aprende

Acumula memoria:

- rachas;
- máximos;
- mínimos;
- eventos similares;
- respuestas históricas de mercado;
- evolución de expectativas;
- relaciones recurrentes.

---

## 23. El grafo económico

El cerebro puede construir un mapa de relaciones.

```text
Riesgo país
├── Bonos
├── Deuda
├── Reservas
├── FMI
├── Licitaciones
└── Acceso al crédito

Inflación
├── Tasas
├── Salarios
├── Consumo
├── Recaudación
└── Tipo de cambio

Vaca Muerta
├── Exportaciones
├── Energía
├── Reservas
├── Inversiones
└── Infraestructura
```

Cada hecho se conecta automáticamente a ese mapa.

Este grafo no tiene que ser perfecto desde el primer día. Puede empezar como un catálogo curado de relaciones y crecer con el uso.

---

## 24. Clustering: de notas a temas

La unidad editorial deja de ser la nota y pasa a ser el hecho.

### Hoy

Cinco medios cubren una licitación y compiten por cinco lugares.

### Propuesta

Una tarjeta:

> El Tesoro renovó el 140% de los vencimientos.

Debajo:

- Ámbito;
- La Nación;
- iProfesional;
- documento de Economía.

### Ventajas

- reduce duplicados;
- mejora la portada;
- aumenta la trazabilidad;
- permite comparar enfoques;
- usa la cobertura como señal de relevancia;
- evita que un medio monopolice la edición.

---

## 25. Jerarquización híbrida

El puntaje de un tema combina reglas e IA.

### Factores

- número de fuentes independientes;
- nivel de fuente;
- recencia;
- presencia de fuente oficial;
- movimiento de indicador relacionado;
- importancia económica;
- impacto sectorial;
- continuidad con temas previos;
- novedad;
- cobertura nacional;
- penalización por opinión;
- penalización por clickbait;
- penalización por falta de sustento.

El puntaje debe guardarse para auditoría.

---

## 26. Redacción automática

La IA debe trabajar con texto completo cuando sea posible.

### Salida esperada

- título PPA;
- resumen;
- por qué importa;
- fuentes;
- cifras detectadas;
- personas;
- fechas;
- nivel de confianza;
- términos “En criollo”;
- relaciones con indicadores.

### Regla

La IA no publica.

Python recibe la respuesta, la valida y decide si pasa a producción.

---

## 27. Verificación automática

Una segunda capa debe comprobar:

- que cada cifra exista;
- que los nombres estén en la fuente;
- que las fechas coincidan;
- que las citas sean reales;
- que el resumen no agregue causalidad no sustentada;
- que la fuente esté enlazada;
- que el documento primario esté presente cuando corresponde.

Si falla:

- se descarta el resumen;
- se publica título y enlace;
- se marca como “modo sobrio”.

---

## 28. Modo sobrio

La IA nunca debe ser indispensable.

Si la API de IA falla:

- se publican títulos;
- se publican enlaces;
- se publican datos;
- se publican documentos;
- se omite apertura o resumen;
- el diario sigue saliendo.

PPA debe fallar volviéndose más sencillo, no dejando de funcionar.

---

## 29. Arquitectura técnica

La primera versión puede vivir completamente en GitHub.

```text
Repositorio GitHub
├── Código Python
├── Datos JSON / JSONL
├── GitHub Actions
└── Archivos estáticos
        ↓
Cloudflare Pages
```

### Componentes

- Python: cerebro.
- GitHub: código y memoria.
- GitHub Actions: reloj y ejecución.
- JSON/JSONL: almacenamiento inicial.
- API de IA: redacción y clasificación.
- Cloudflare Pages: publicación.
- Panel: corrección, ocultamiento y destacados.

No hace falta:

- servidor permanente;
- base de datos externa;
- computadora encendida;
- WordPress;
- PHP para el núcleo.

---

## 30. Estructura sugerida del repositorio

```text
pulso-productivo/
├── cerebro/
│   ├── recolectar/
│   │   ├── rss.py
│   │   ├── bcra.py
│   │   ├── indec.py
│   │   ├── mercados.py
│   │   └── documentos.py
│   ├── entender/
│   │   ├── normalizar.py
│   │   ├── deduplicar.py
│   │   ├── agrupar_temas.py
│   │   ├── relacionar.py
│   │   └── jerarquizar.py
│   ├── redactar/
│   │   ├── resumenes.py
│   │   ├── apertura.py
│   │   ├── data_del_dia.py
│   │   └── verificar.py
│   ├── publicar/
│   │   ├── portada.py
│   │   ├── datos_ppa.py
│   │   ├── documentos.py
│   │   └── generar_html.py
│   └── ejecutar_edicion.py
├── data/
│   ├── noticias_brutas/
│   ├── temas/
│   ├── indicadores/
│   ├── documentos/
│   ├── definiciones/
│   ├── fuentes/
│   └── ediciones/
├── public/
├── tests/
├── requirements.txt
└── .github/workflows/
```

---

## 31. Cómo se activa

GitHub Actions despierta el sistema según un horario.

Ejemplo:

```yaml
name: Cerebro PPA

on:
  schedule:
    - cron: "30 8 * * 1-5"
    - cron: "40 20 * * 1-5"
  workflow_dispatch:

jobs:
  ejecutar:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - run: pip install -r requirements.txt

      - run: python cerebro/ejecutar_edicion.py
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}

      - run: |
          git config user.name "PPA Bot"
          git config user.email "ppa-bot@users.noreply.github.com"
          git add data/ public/
          git commit -m "Edición automática" || exit 0
          git push
```

Los horarios de GitHub Actions se expresan en UTC.

También debe existir ejecución manual para pruebas.

---

## 32. El día automático

Hora argentina propuesta:

| Hora | Proceso |
|---|---|
| 05:30 | Fetch profundo de RSS, datos y documentos |
| 06:00 | Normalización, clustering y chequeo |
| 06:30 | Publicación Desayuno |
| 10:00–17:00 | Datos de mercado cada 30–60 minutos hábiles |
| 13:00 | Fetch liviano |
| 17:00 | Cierre de datos y mercados |
| 17:40 | Publicación Merienda |
| 20:00 | Snapshot histórico y salud |
| Sábado 10:00 | Digest semanal opcional |

El sistema se despierta, trabaja, publica y se apaga.

No necesita ejecutarse permanentemente.

---

## 33. La memoria

La máquina temporal de GitHub desaparece al terminar.

Por eso la memoria se guarda en archivos persistentes del repositorio.

### Ejemplo

```json
{"fecha":"2026-07-08","valor":438,"fuente":"ArgentinaDatos"}
{"fecha":"2026-07-09","valor":425,"fuente":"ArgentinaDatos"}
{"fecha":"2026-07-10","valor":419,"fuente":"ArgentinaDatos"}
```

Formato sugerido:

- JSON para estados actuales.
- JSONL para históricos.
- CSV cuando sea útil para inspección.
- SQLite más adelante, si el volumen lo exige.

### Qué habilita

- gráficos;
- comparaciones;
- rachas;
- récords;
- detección de anomalías;
- auditoría;
- explicaciones históricas;
- búsqueda de eventos similares.

---

## 34. Cómo usa la IA

Python es el director.

La IA recibe tareas acotadas:

- clasificar;
- agrupar;
- resumir;
- extraer;
- comparar;
- proponer relaciones;
- escribir apertura;
- detectar jerga.

La IA devuelve JSON estructurado.

Ejemplo:

```json
{
  "titulo": "El riesgo país volvió a bajar",
  "resumen": "El indicador cerró...",
  "por_que_importa": "Una baja sostenida...",
  "cifras_detectadas": [
    {
      "valor": 419,
      "fuente": "ArgentinaDatos"
    }
  ],
  "confianza": 0.94
}
```

Python verifica el resultado antes de publicar.

---

## 35. Salud de fuentes

Por cada fuente se registra:

- HTTP;
- cantidad de ítems;
- fecha del contenido más reciente;
- duración;
- fallos consecutivos;
- última lectura correcta;
- estado.

### Estados

- saludable;
- sin novedades;
- degradada;
- suspendida;
- recuperándose.

### Reglas sugeridas

- 3 fallos seguidos: degradada.
- 7 días sin éxito: suspendida.
- 3 éxitos consecutivos: reactivada.
- Respuesta válida con contenido viejo: sin novedades.

---

## 36. Alertas

El sistema debe avisar solo cuando necesita atención.

### Canales

- issue automático de GitHub;
- Telegram;
- reporte semanal.

### Alertas

- workflow fallido;
- fuente degradada;
- serie desactualizada;
- dato fuera de rango;
- documento no procesado;
- cuota de IA agotada;
- portada incompleta;
- dato sin fecha;
- nota sin fuente.

---

## 37. Autoverificación

Después de publicar:

- ¿hay entre 6 y 8 temas?
- ¿todos tienen fuente?
- ¿todos tienen enlace?
- ¿cada dato tiene fecha?
- ¿cada estimación está identificada?
- ¿hay duplicados?
- ¿la portada se generó?
- ¿el JSON es válido?
- ¿Cloudflare recibió el cambio?

Si algo falla, la edición anterior permanece disponible.

---

## 38. Transparencia

“Cómo trabajamos” debe ser parte del producto.

### Debe explicar

- cómo se eligen temas;
- cómo se usan fuentes;
- qué hace la IA;
- qué verifica Python;
- qué significa “estimación”;
- qué significa “cálculo PPA”;
- qué fue corregido;
- salud de fuentes;
- fecha de actualización de indicadores;
- metodología;
- criterios editoriales;
- límites del sistema.

Mostrar las costuras aumenta la confianza.

---

## 39. Marco legal y de buena vecindad

- Resúmenes propios.
- Enlaces visibles.
- Atribución.
- No republicar artículos completos.
- Texto descargado solo para procesamiento.
- Respeto de robots.txt.
- User-Agent identificado.
- Frecuencia moderada.
- Fuentes oficiales preferidas.
- Uso de IA declarado.
- Correcciones trazables.
- Datos de terceros citados.

---

## 40. Costos

### Gratuito

- GitHub Actions.
- Cloudflare Pages.
- APIs oficiales.
- JSON/JSONL.
- Telegram.
- clustering local liviano.
- almacenamiento en repositorio, dentro de límites razonables.

### Pago recomendado

La IA.

Costo estimado inicial:

**USD 3 a 8 por mes**, según proveedor y volumen.

El diseño debe permitir cambiar de modelo sin reconstruir todo el sistema.

---

## 41. Plan de implementación

### Fase A — Autonomía y memoria

- eliminar cargas manuales;
- automatizar riesgo país;
- automatizar MULC;
- histórico acumulativo;
- alertas;
- test canario.

**Puerta de salida:** 14 días sin alimentación manual.

### Fase B — Cerebro editorial

- texto completo;
- clustering;
- jerarquización;
- resúmenes verificados;
- apertura;
- modo sobrio.

**Puerta de salida:** una semana estable sin duplicados graves ni cifras inventadas.

### Fase C — Documentos oficiales

- calendario INDEC;
- día del IPC;
- Boletín Oficial;
- licitaciones;
- recaudación.

**Puerta de salida:** publicar automáticamente un informe oficial el mismo día de su salida.

### Fase D — Salud y transparencia

- estados automáticos;
- tablero público;
- reporte semanal;
- auditoría.

### Fase E — Expansión

- La Data narrada;
- REM avanzado;
- FCI;
- ON;
- TXT-Stream;
- EconoTuits;
- digest semanal;
- nuevas salidas.

---

## 42. Prioridad recomendada

Orden práctico:

1. Automatizar todos los datos manuales.
2. Crear el histórico acumulativo.
3. Implementar salud y alertas.
4. Agrupar noticias por tema.
5. Resumir desde texto completo.
6. Verificar cifras y nombres.
7. Generar apertura automática.
8. Construir “En criollo”.
9. Automatizar documentos.
10. Rehacer EconoTuits.
11. Automatizar TXT-Stream.
12. Expandir a newsletter, WhatsApp y audio.

---

## 43. Qué es realmente PPA

PPA puede dejar de ser:

> un agregador con resúmenes.

Y convertirse en:

> un sistema automático, trazable y pedagógico que entiende la economía argentina, acumula memoria y publica distintas formas de explicar lo que está pasando.

El activo no será la portada.

El activo será:

- la memoria;
- las relaciones;
- el histórico;
- las definiciones;
- las metodologías;
- la trazabilidad;
- el grafo económico;
- el sistema de verificación;
- la capacidad de generar productos desde un mismo conocimiento.

Cada día que funciona, el sistema se vuelve más valioso.

---

## 44. Síntesis final

La primera versión puede construirse con:

- Python;
- GitHub;
- GitHub Actions;
- JSON/JSONL;
- una API de IA;
- Cloudflare Pages.

Sin servidor permanente.

Sin WordPress.

Sin base de datos externa al comienzo.

El cerebro duerme dentro del repositorio. GitHub lo despierta varias veces por día. Recolecta, ordena, relaciona, redacta, verifica, publica y vuelve a apagarse.

La web es la vidriera.

**El verdadero proyecto es el cerebro.**
