# Web de Xucaphe

La web se publica con GitHub Pages desde la carpeta `docs/`:
**https://xucadev.github.io/xucaphe-media/**

| Archivo | Para qué sirve |
|---|---|
| `docs/index.html` | Página principal: juego ¿estafa o real?, recursos, videos, Chris, redes y contacto |
| `docs/estilo.css` | Estilo compartido (colores, tipografías, botones) |
| `docs/404.html` | Página de error para enlaces que no existen (GitHub Pages la usa sola) |
| `docs/403.html` | Página de acceso no permitido (ver nota abajo) |
| `docs/privacidad.html` | Política de privacidad (la usa la app de Google/YouTube: **no cambiar la URL**) |
| `docs/robots.txt`, `docs/sitemap.xml` | Para buscadores |
| `docs/site.webmanifest`, `favicon.*`, `icon-*.png`, `apple-touch-icon.png` | Iconos y "añadir a pantalla de inicio" |
| `docs/og.jpg` | Imagen que sale al compartir el enlace en WhatsApp, redes o el SmartLink |

## Secciones con enlace directo

Estos anclajes son fijos; se pueden usar en el SmartLink, en descripciones y en los videos:

| Sección | Enlace |
|---|---|
| Juego ¿estafa o real? | `https://xucadev.github.io/xucaphe-media/#juego` |
| Checklist para revisar tu web | `https://xucadev.github.io/xucaphe-media/#web` |
| Kit anti-estafas para la familia | `https://xucadev.github.io/xucaphe-media/#familia` |
| Me estafaron, ¿y ahora? | `https://xucadev.github.io/xucaphe-media/#estafa` |
| Videos | `https://xucadev.github.io/xucaphe-media/#videos` |
| Redes | `https://xucadev.github.io/xucaphe-media/#redes` |
| Contacto | `https://xucadev.github.io/xucaphe-media/#contacto` |

## SmartLink de Metricool

El SmartLink (dominio `t.mtrbio.com/...`) va en el campo **Sitio web** de cada perfil; los botones apuntan a la web.
Los SmartLinks solo se crean y editan desde Metricool en el navegador de escritorio.

**Botones sugeridos, en este orden** (copiar y pegar):

1. Juega: ¿estafa o real?
   `https://xucadev.github.io/xucaphe-media/?utm_source=metricool&utm_medium=smartlink&utm_campaign=bio#juego`
2. Kit anti-estafas para la familia
   `https://xucadev.github.io/xucaphe-media/?utm_source=metricool&utm_medium=smartlink&utm_campaign=bio#familia`
3. Me estafaron, ¿qué hago?
   `https://xucadev.github.io/xucaphe-media/?utm_source=metricool&utm_medium=smartlink&utm_campaign=bio#estafa`
4. Checklist: revisa tu web en 15 minutos
   `https://xucadev.github.io/xucaphe-media/?utm_source=metricool&utm_medium=smartlink&utm_campaign=bio#web`
5. Videos largos en YouTube
   `https://www.youtube.com/channel/UCQFpMNDpNK0lT_W1X9ETfnw?sub_confirmation=1`

**Iconos de redes del SmartLink:**
YouTube `https://www.youtube.com/channel/UCQFpMNDpNK0lT_W1X9ETfnw` ·
TikTok `https://www.tiktok.com/@xucaphee` ·
Instagram `https://www.instagram.com/xucapheee/` ·
Facebook `https://www.facebook.com/1393879633819489` ·
Threads `https://www.threads.com/@xucapheee` ·
Bluesky `https://bsky.app/profile/xucaphe.bsky.social` ·
Pinterest `https://www.pinterest.com/Xucaphe/` ·
Correo `mailto:Projectsmanagers@proton.me`

**Diseño para que el SmartLink y la web se vean iguales:**
fondo `#061426`, botones `#3CC8FF` con texto `#03111F`, texto `#EAF6FF`, avatar `marca/avatar-youtube.jpg`.

**Cómo encaja todo:**
- Metricool mide los clics del SmartLink; la web no tiene analítica ni cookies (así se cumple lo de "sin rastreo").
- Al entrar desde el SmartLink, la web quita los `?utm_...` de la barra: si alguien comparte la página, el enlace sale limpio.
- Si se quiere saber qué red trae más gente, se puede clonar el SmartLink por red y cambiar `utm_source=metricool` por `instagram`, `tiktok`, etc.
- La imagen `og.jpg` y el título se usan como vista previa cuando Metricool, WhatsApp o las redes leen el enlace.

## Notas de alojamiento (GitHub Pages)

- **403:** GitHub Pages no permite páginas 403 propias (solo usa `404.html`). `403.html` queda lista para cuando la web pase a un dominio propio o a Netlify/Cloudflare Pages, donde se configura con una regla.
- **robots.txt:** los buscadores solo leen el `robots.txt` de la raíz del dominio (`xucadev.github.io/robots.txt`), no el de `/xucaphe-media/`. Con un dominio propio funcionaría directo. Mientras tanto, para Google lo importante es dar de alta la web en Search Console (propiedad de "prefijo de URL") y enviar `sitemap.xml`.
- Al cambiar de dominio: buscar y reemplazar `https://xucadev.github.io/xucaphe-media/` en `docs/` y quitar la línea `<base href="/xucaphe-media/">` de `404.html`, `403.html` y `privacidad.html`.
