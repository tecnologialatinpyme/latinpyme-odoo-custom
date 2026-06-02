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

## Ahorro de tokens en diffs

Por defecto Codex no debe imprimir el `git diff` completo. En tareas de Revista debe entregar:

- Resumen textual de cambios.
- `git diff --check`.
- `git diff --name-only`.
- `git status --short`.
- Commits creados y push realizado, si aplica.

Solo debe mostrar el diff completo si el usuario lo pide explícitamente.

## Modos de trabajo Git

### Modo por defecto: implementar sin commit ni push

- Si el usuario no autoriza explícitamente commit o push, Codex solo debe modificar archivos de Revista, validar y entregar resumen textual.
- No debe hacer commit.
- No debe hacer push.
- Debe mostrar resumen textual, archivos modificados, `git diff --name-only`, `git diff --check` y `git status --short`.

### Modo commit autorizado

Solo si el usuario escribe claramente `autorizar commit` o `hacer commit`, Codex puede crear commit.

Antes del commit debe ejecutar:

```bash
git diff --check
git status --short
git -C src/odoo/addons/latinpyme_custom status --short
git -C src/odoo/addons/latinpyme_custom diff --name-only
```

Reglas:

- No mostrar `git diff` completo salvo solicitud explícita.
- Detenerse si detecta archivos fuera de `latinpyme_revista_theme` para una tarea de Revista.
- Decidir el alcance del `git add` según los archivos realmente modificados.
- No usar `git add .` por defecto.
- Para cambios solo de Revista, usar preferentemente `git -C src/odoo/addons/latinpyme_custom add latinpyme_revista_theme`.
- Solo usar `git add .` si Codex confirma antes que todos los cambios pendientes pertenecen a la tarea autorizada y no existen archivos ajenos, temporales, logs, pruebas locales ni cambios no relacionados.
- El usuario no está obligado a proporcionar el mensaje de commit al inicio.
- Codex debe sugerir automáticamente un mensaje de commit corto, claro y funcional al finalizar los cambios, basado en los archivos modificados y el objetivo de la tarea.
- El mensaje debe estar en español, en infinitivo o estilo funcional.
- Si el usuario proporciona mensaje de commit, usar ese mensaje.
- Si no lo proporciona, proponer uno y pedir confirmación antes de commitear.
- El mismo mensaje puede usarse en el subrepo custom y en el repo principal.

Ejemplos de mensaje:

- `Corregir encuadre de imágenes en home revista`
- `Ajustar enlaces legales del footer revista`
- `Separar estilos de tienda y revista`

### Modo push Production autorizado

Solo si el usuario escribe explícitamente `AUTORIZO ADD, COMMIT Y PUSH A PRODUCTION`, Codex puede hacer add, commit y push.

- `git push origin production` despliega en Odoo.sh Production.
- Antes del push debe confirmar que `git diff --check` está OK.
- Debe confirmar que `git diff --name-only` fue revisado.
- Debe confirmar que `git status --short` fue revisado.
- Debe confirmar el estado del subrepo custom.
- Debe confirmar el estado del repo principal.
- Debe confirmar que solo hay archivos de `latinpyme_revista_theme` o archivos Markdown de contexto autorizados.
- Debe confirmar que no se tocó Tienda.
- Debe confirmar que no se tocaron módulos core de Odoo.
- Debe confirmar que no se tocó ecommerce, checkout, carrito, pagos, productos ni Mercado Pago salvo petición explícita.
- Debe confirmar que no se ejecutó SQL ni se modificaron datos reales.
- Si detecta cambios fuera del alcance, debe detenerse.

Flujo Revista:

```bash
cd /d/Odoo/latinpyme-odoo

git -C src/odoo/addons/latinpyme_custom status --short
git -C src/odoo/addons/latinpyme_custom diff --check
git -C src/odoo/addons/latinpyme_custom diff --name-only

git -C src/odoo/addons/latinpyme_custom add latinpyme_revista_theme
git -C src/odoo/addons/latinpyme_custom commit -m "MENSAJE_SUGERIDO_POR_CODEX"
git -C src/odoo/addons/latinpyme_custom push origin HEAD:main

git status --short
git add src/odoo/addons/latinpyme_custom
git commit -m "MENSAJE_SUGERIDO_POR_CODEX"
git push origin production
```

## Modos operativos para tareas diarias

Regla global: cuando el usuario escriba uno de estos modos, Codex debe aplicar automáticamente las reglas correspondientes sin pedir que se repitan en el prompt. En este AGENTS específico de Revista se detallan los modos de Revista; los modos `TIENDA_SAFE` y `TIENDA_PUSH` se gobiernan desde el AGENTS padre y el documento de contexto general.

### MODO REVISTA_SAFE

Uso: tarea de Revista sin add, sin commit y sin push.

- Trabajar solo en `latinpyme_revista_theme`.
- No tocar `latinpyme_tienda_theme`.
- No tocar módulos core de Odoo.
- No tocar ecommerce, checkout, carrito, pagos, productos ni Mercado Pago.
- No ejecutar SQL ni modificar datos reales.
- No hacer `git add`, commit ni push.
- Mantener SCSS bajo `.lp-revista`.
- Respetar multiwebsite y `website_id`.
- No mostrar `git diff` completo salvo solicitud explícita.
- Al final mostrar resumen textual, archivos modificados, validaciones, `git diff --check`, `git diff --name-only`, `git status --short`, riesgos y pruebas sugeridas.

### MODO REVISTA_PUSH

Uso: tarea de Revista con add, commit y push a Production autorizados.

- Aplicar todas las reglas de `REVISTA_SAFE`, excepto que sí está autorizado add, commit y push.
- Sugerir automáticamente el mensaje de commit según el cambio realizado.
- Usar add selectivo, no `git add .` por defecto.
- Para cambios solo de Revista, preferir `git -C src/odoo/addons/latinpyme_custom add latinpyme_revista_theme`.
- Si solo cambiaron archivos puntuales, puede hacer add selectivo por archivo.
- Solo usar `git add .` si confirma que todos los cambios pendientes pertenecen a la tarea.
- Si detecta archivos fuera del alcance, debe detenerse.
- Hacer commit y push del subrepo custom a `origin HEAD:main`.
- Luego actualizar el puntero del subrepo en el repo principal.
- Hacer commit y push del repo principal a `origin production`.
- Recordar que `git push origin production` despliega en Odoo.sh Production.

## Reglas de no tocar

- No tocar Tienda.
- No tocar ecommerce.
- No tocar checkout, carrito, pagos, productos ni Mercado Pago.
- No tocar módulos core de Odoo.
- No modificar Production ni configuración real de Odoo.sh sin autorización explícita.
