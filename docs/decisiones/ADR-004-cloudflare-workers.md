# ADR-004 — Cloudflare Workers como plataforma principal

Estado: aceptada  
Fecha: 2026-07-01

## Decisión

Usar Cloudflare Workers con Static Assets para el sitio y la API. Usar D1 para información estructurada, R2 para archivos y Cloudflare Access para administración.

Mantener inicialmente en GitHub Actions los procesos pesados de RSS, Excel, PDF y resumen por lotes.

## Motivo

La combinación ofrece bajo costo, despliegue simple y separación entre alojamiento, datos y tareas programadas. Workers Free no es adecuado para procesar todas las fuentes pesadas en una sola ejecución.

## Consecuencias

- Se elimina FTP y Hostinger.
- Python puede seguir utilizándose donde sea útil.
- La publicación pública queda integrada con Cloudflare.
- El cambio de DNS se realizará desde NIC Argentina.

