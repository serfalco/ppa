# Migración a Cloudflare Pages — guía operativa

Estado: **lista para ejecutar**. Hostinger y FTP ya fueron eliminados de los workflows (julio 2026). El sitio se publica desde el repo vía Cloudflare Pages.

## Cómo funciona ahora

```text
GitHub Actions (fetcher, ediciones, datos de mercado)
        ↓ commit a main (data/ + site/)
Cloudflare Pages (conectado al repo)
        ↓ deploy automático del directorio site/
pulsoproductivo.com.ar
```

No hay build: `site/` ya contiene HTML estático generado por Python. Cada push a `main` dispara un deploy que tarda menos de un minuto.

## Pasos de conexión (una sola vez, ~10 minutos)

1. Entrar a [dash.cloudflare.com](https://dash.cloudflare.com) → **Workers & Pages** → **Create** → pestaña **Pages** → **Connect to Git**.
2. Autorizar GitHub y elegir el repo de PPA.
3. Configuración del build:
   - **Production branch:** `main`
   - **Build command:** (vacío — no hay build)
   - **Build output directory:** `site`
4. **Save and Deploy**. En un minuto el sitio queda en `<proyecto>.pages.dev`.
5. Verificar en la URL `.pages.dev` que portada, `/data/datos.json`, La Data, REM y el archivo se vean bien.

## Dominio propio

6. En el proyecto de Pages → **Custom domains** → **Set up a custom domain** → `pulsoproductivo.com.ar` (y `www` si se usa).
7. Si el dominio ya está administrado en Cloudflare (DNS), el registro se crea solo. Si el DNS está en NIC/otro lado, delegar los nameservers a Cloudflare primero (Cloudflare los indica al agregar el sitio).
8. Esperar el certificado (automático) y probar `https://pulsoproductivo.com.ar`.

## Después de conectar

9. **Reactivar los crons**: en GitHub → Actions → habilitar los tres workflows (quedaron deshabilitados durante la pausa). También se pueden probar a mano con *Run workflow*.
10. **Borrar los secrets FTP** en GitHub (Settings → Secrets): `FTP_SERVER`, `FTP_USERNAME`, `FTP_PASSWORD`. Ya no se usan.
11. **Proteger el panel**: en Cloudflare → **Zero Trust → Access → Applications** → crear una aplicación para `pulsoproductivo.com.ar/panel69/*` y `/admin/*` con política "solo el mail de Sergio". Es gratis hasta 50 usuarios. Hoy el panel es HTML público sin contraseña: esto lo cierra sin tocar código.
12. Cuando todo funcione unos días: dar de baja Hostinger.

## Límites del plan gratuito (holgados para PPA)

- 500 deploys por mes. Con el ritmo actual (≈9 commits de datos + 2 ediciones + 2 fetch por día hábil) son ~280/mes. Si algún día se queda corto, bajar la frecuencia del cron de datos o filtrar qué paths disparan deploy.
- Ancho de banda ilimitado, sitios estáticos sin costo.

## Qué se eliminó del repo

- Paso "Deploy a Hostinger" (FTP) en `datos-mercado.yml` y `edicion-merienda.yml`.
- Copias viejas y duplicadas de workflows fuera de `.github/workflows/`.
- Dependencia de los secrets FTP.
