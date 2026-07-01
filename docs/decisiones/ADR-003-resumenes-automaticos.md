# ADR-003 — Publicar resúmenes automáticos con corrección posterior

Estado: aceptada  
Fecha: 2026-07-01

## Decisión

Los resúmenes propios se generan y publican automáticamente. Sergio puede corregir, ocultar o destacar después de la publicación.

## Motivo

El proyecto tiene un solo editor con intervención ocasional. Exigir aprobación previa haría inviable mantener dos ediciones.

## Salvaguardas

- Fuente y enlace obligatorios.
- Controles contra invenciones y copias extensas.
- Degradación a título y enlace si falla el resumen.
- Registro de correcciones.

