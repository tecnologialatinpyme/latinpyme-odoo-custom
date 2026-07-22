# Arquitectura técnica de Revista LatinPyme y conexión con CRM

Documentación basada en el código real del módulo (`git show` sobre `origin/production`), no en supuestos. Complementa al [manual de administración](manual_administracion_revista_latinpyme.md) (que es para editores de contenido, no técnico) y a `AGENTS.md` (contexto interno para agentes de IA que trabajan en este módulo).

## 1. Cómo está construida (resumen técnico)

Revista **no es una app nueva de Odoo** — es una capa de personalización sobre dos módulos nativos:

- `website` (paginas, menús, SEO)
- `website_blog` (el motor de "notas" — cada artículo de Revista es, por debajo, un `blog.post`)

`latinpyme_revista_theme` le agrega encima un conjunto de **modelos propios de configuración editorial**, para que el equipo pueda administrar contenido sin tocar código:

| Modelo | Para qué sirve |
|---|---|
| `latinpyme.revista.config` | Configuración general del sitio: redes sociales, footer, teléfono, ciudad, URLs de "Suscribirse" y "Postúlate" (ver sección 3). |
| `latinpyme.revista.section` | Las secciones editoriales (ej. Gerencia, Tecnología) y su menú. |
| `latinpyme.revista.home.block` / `latinpyme.revista.home.assignment` | Los bloques del home (Actualidad, Entrevistas, Especiales, Novedades, Portafolio, Aliados...) y qué notas se muestran en cada uno — manual o automático por etiqueta/fecha. |
| `latinpyme.revista.footer.link` | Los links del footer, agrupados en Secciones / Portafolio / Legal. |
| `latinpyme.revista.interview` | Entrevistas destacadas. |
| `latinpyme.revista.sidebar.item` | Bloques del sidebar. |
| `latinpyme.revista.banner` | Banners publicitarios (con tamaños de referencia fijos por ubicación, ej. hero 1181×161). |
| `latinpyme.revista.program.event` | Eventos de la "Programación anual". |

Todo esto vive en `models/revista_models.py` y se administra desde el backend (`views/backend_views.xml`).

### Rutas principales (`controllers/main.py`)

- `/revista` — home editorial.
- `/revista/seccion` y `/revista/seccion/<slug>` — listado y sección individual.
- `/revista/seccion/programacion-anual` — calendario de eventos.
- `/blog/revista-latinpyme-2/<slug>-<id>` — la nota individual (ruta nativa de `website_blog`, con plantilla propia en `blog_post_templates.xml`).

### Reglas de dominio/SEO ya decididas (de `AGENTS.md`)

- El dominio indexable en producción es `latinpyme.com` (canonical y `og:url` apuntan ahí).
- `revista.latinpyme.com` no debe competir por indexación — se maneja con `noindex` o 301 según el caso.
- En entornos de preproducción, las páginas se marcan `X-Robots-Tag: noindex, nofollow` automáticamente (`_render()` en el controlador, ver `lp_preproduction`).

### Una regla técnica ya documentada que vale la pena repetir

`AGENTS.md` deja registrado un bug real ya resuelto: usar `request.website` directo (sin fallback) revienta con `AttributeError: 'Request' object has no attribute 'website'` cuando el código corre dentro del editor de Website o en render parcial de assets. Por eso el acceso a `request.website` en este módulo siempre es defensivo (`getattr`/chequeos), no directo.

## 2. Separación Revista / Tienda

Ambos módulos comparten el mismo repositorio y la misma base de datos de Odoo, pero **están deliberadamente separados**: `AGENTS.md` es explícito en que "no mezclar headers, footers, layouts, menús ni estilos" entre los dos. Cada uno tiene su propio masthead, footer y hoja de estilos (`revista.scss` vs `tienda.scss`), sin componentes compartidos entre sí.

## 3. Conexión con CRM

**No existe una integración con el módulo CRM de Odoo (`crm.lead`)**, igual que en Tienda. Verificado en código:

- `crm` no está en las dependencias del manifest (`depends`: solo `website` y `website_blog`).
- No hay ninguna referencia real a `crm.lead` en el módulo (la única coincidencia al buscar "crm" son archivos binarios de referencia — imágenes y un docx — no código).

Lo que sí existe son **dos puntos configurables que redirigen hacia afuera**, y que podrían ser lo que llevó a pensar en una conexión de CRM:

### a) "Suscribirse"

- Ruta `/suscribirse` → redirige (302) a la URL que esté configurada en `latinpyme.revista.config.subscribe_url`.
- Por defecto ese campo vale literalmente `/suscribirse` — y el código detecta ese caso especial (`_subscribe_url()`) y en vez de crear un bucle infinito, redirige al home (`/`).
- Es decir: **tal como está el código, "Suscribirse" no hace nada útil salvo que alguien configure ahí una URL real** (podría ser un formulario externo de Mailchimp, HubSpot, un CRM, o cualquier otra herramienta — el código no impone cuál). Cuál es el valor configurado *hoy* en la base de datos no lo pude verificar sin acceso al backend.

### b) "Postúlate" (entrevistas)

- `latinpyme.revista.config.interview_apply_url`, por defecto `/contactus` — la página nativa de "Contáctenos" de Odoo Website.
- Esa página nativa, tal cual la instala Odoo, normalmente solo **envía un correo** (no crea un registro en ningún lado) — a menos que el módulo `crm` esté instalado en la base de datos como aplicación aparte (no por este tema, sino instalado independientemente) y el formulario esté configurado para generar oportunidades ahí. **No pude confirmar si `crm` está instalado a nivel de base de datos** porque estos dos módulos (Tienda y Revista) no lo requieren y no tengo acceso al backend en esta sesión para revisarlo directamente en Ajustes → Aplicaciones.

### En resumen

| Pregunta | Respuesta |
|---|---|
| ¿Hay código que cree oportunidades de CRM automáticamente? | No, en ningún módulo (ni Tienda ni Revista). |
| ¿"Suscribirse" guarda el correo en algún lado dentro de Odoo? | No directamente — es una redirección configurable a una URL externa. |
| ¿"Postúlate" podría terminar en CRM? | Solo si `crm` está instalado aparte en la base de datos Y el formulario de Contáctenos está configurado para generar leads ahí — no verificado. |
| ¿Se necesita acceso al backend para completar esto? | Sí — para ver el valor real de `subscribe_url` hoy, y para confirmar si la app CRM está instalada. |

## 4. Limitaciones de este documento

Igual que la documentación equivalente de Tienda (`latinpyme_tienda_theme/docs/PAGOS_CORREOS_CRM.md`): todo lo anterior está verificado leyendo el código real del repositorio. Lo que requiere entrar al backend (valor actual de `subscribe_url`, si `crm` está instalado, configuración de `/contactus`) no se pudo confirmar en esta sesión por falta de una sesión iniciada en Odoo. "Cómo se trabajó" en el sentido de historial de decisiones día a día no está cubierto aquí tampoco — ese contexto vive en conversaciones previas de este proyecto que esta sesión no tuvo acceso; este documento describe el estado **actual** del código, no la cronología de cómo se llegó a él.
