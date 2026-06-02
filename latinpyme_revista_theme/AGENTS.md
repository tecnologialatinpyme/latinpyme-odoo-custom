# LatinPyme Revista Theme - Contexto para Codex CLI

## Contexto funcional

`latinpyme_revista_theme` implementa la Revista LatinPyme en Odoo Website/Blog, con home editorial, secciones, entrevistas, banners, programación anual, sidebar, footer editorial y ajustes SEO.

La Revista debe funcionar separada de la Tienda. No mezclar headers, footers, layouts, menús ni estilos.

## Rutas principales

- `/revista`
- `/revista/seccion`
- `/revista/seccion/<slug>`
- `/revista/seccion/programacion-anual`
- `/blog/revista-latinpyme-2`
- `/blog/revista-latinpyme-2/<slug>-<id>`

## Archivos importantes

- `models/revista_models.py`
- `controllers/main.py`
- `views/backend_views.xml`
- `views/layout_templates.xml`
- `views/snippet_templates.xml`
- `views/snippets.xml`
- `views/home_templates.xml`
- `views/section_templates.xml`
- `views/blog_post_templates.xml`
- `static/src/scss/revista.scss`
- `static/src/js/mobile_nav.js`
- `static/src/js/mobile_footer.js`
- `static/src/js/program_calendar.js`

## Modelos principales

- `latinpyme.revista.config`
- `latinpyme.revista.section`
- `latinpyme.revista.home.block`
- `latinpyme.revista.home.assignment`
- `latinpyme.revista.footer.link`
- `latinpyme.revista.interview`
- `latinpyme.revista.sidebar.item`
- `latinpyme.revista.banner`
- `latinpyme.revista.program.event`
- Extensiones sobre `blog.post`
- Extensiones sobre `blog.tag`

## Home editorial

Bloques esperados:

- Actualidad
- De Interés
- Entrevistas
- Especiales
- Novedades
- Publicidad horizontal
- Portafolio
- Aliados
- Footer editorial

Reglas:

- Mantener el contenido dinámico desde modelos/controladores.
- No reemplazar bloques administrables por HTML estático.
- Respetar asignaciones manuales y vigencias.
- Evitar duplicar datos fallback al actualizar módulo.

## Asignaciones manuales

- Si hay asignaciones manuales vigentes, prevalecen sobre fallback automático.
- Si no hay manuales, puede usarse fallback por etiqueta/fecha según bloque.
- No regenerar asignaciones si el backend ya tiene configuración válida.

## Etiquetas

- Mostrar primero etiqueta de tipo `Sección editorial`.
- Si no existe, usar `Tema` o `Contenido` como fallback.
- Para Especiales aceptar alias `Especial` y `Especiales`.

## Header

- El header correcto viene de `lp_masthead`.
- El menú es dinámico desde `latinpyme.revista.section.get_masthead_nav_sections(lp_website)`.
- Mostrar solo secciones activas.
- Mostrar solo secciones del website Revista.
- Ordenar por `sequence`.
- Respetar estructura padre/hijo.

Problema histórico:

- Si reaparecen menús antiguos como `Negocios`, `IA`, `Laboral`, `Entrevistas` o `Especiales`, revisar copias website-specific/COW en `ir.ui.view`.

## Footer

El footer debe ser dinámico desde `latinpyme.revista.footer.link`.

Grupos:

- Secciones
- Portafolio
- Legal

URLs legales correctas:

- `/revista/sobre-nosotros/terminos-de-uso`
- `/revista/sobre-nosotros/politica-de-privacidad`
- `/revista/sobre-nosotros/aviso-legal`
- `/revista/sobre-nosotros/politica-de-cookies`
- `/revista/sobre-nosotros/politica-de-uso-de-imagenes`

## Regla técnica importante

No usar directamente `request.website` en snippets/assets sin fallback. En el editor ya provocó:

```text
AttributeError: 'Request' object has no attribute 'website'
```

Usar acceso defensivo cuando el contexto pueda ejecutarse en editor, assets o renderizados parciales.

## Banners

Tamaños de referencia:

- Home hero superior: `1181x161`
- Especiales: `384x169`
- Novedades: `281x127`
- Publicidad horizontal: `582x149`
- Actualidad destacada: `494x341`

## SEO

- Producción indexable: `https://latinpyme.com`.
- Canonical debe apuntar a `latinpyme.com`.
- `og:url` debe apuntar a `latinpyme.com`.
- Sitemap debe usar URLs finales.
- `revista.latinpyme.com` no debe competir; usar `noindex` o 301 según decisión.
- Evitar contenido duplicado.
- No dejar `noindex` accidental en producción.

## Pruebas comunes

```bash
python -m py_compile src/odoo/addons/latinpyme_custom/latinpyme_revista_theme/controllers/main.py
python -m py_compile src/odoo/addons/latinpyme_custom/latinpyme_revista_theme/models/revista_models.py
git diff --check
```

URLs de prueba:

- `/revista?debug=assets`
- `/revista/seccion?debug=assets`
- `/revista/seccion/especiales?debug=assets`
- `/blog/revista-latinpyme-2?debug=assets`
- Nota individual con `?debug=assets`

## Reglas de no tocar

- No tocar Tienda.
- No tocar ecommerce.
- No tocar checkout, carrito, pagos, productos ni Mercado Pago.
- No tocar módulos core de Odoo.
- No modificar Production ni configuración real de Odoo.sh sin autorización explícita.
