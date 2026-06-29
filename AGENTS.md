# LatinPyme Custom Addons - Reglas para Codex CLI

## Alcance

Esta carpeta contiene los addons personalizados de LatinPyme:

- `latinpyme_revista_theme`
- `latinpyme_tienda_theme`

Checkout operativo aprobado para trabajo y validación de custom addons:

- `D:/Odoo/_codex_tmp/latinpyme_custom_safe`

Base funcional aprobada para Tienda:

- rama `tienda-production-safe`
- baseline funcional `66d16cb7999b3ae8a36babdad8cf88d73466a4d0`

Checkout descartado para publicar cambios:

- `D:/Odoo/latinpyme-odoo/src/odoo/addons/latinpyme_custom`
- ramas que continúan la línea fallida de `59fb18f` y `fe3b6fa`

No se deben tocar módulos core de Odoo desde esta carpeta ni usar esta ruta como excusa para cambios amplios fuera del alcance solicitado.

## Separación estricta de módulos

- Si la tarea es de Revista, trabajar solo en `latinpyme_revista_theme`.
- Si la tarea es de Tienda, trabajar solo en `latinpyme_tienda_theme`.
- No tocar Tienda por una tarea de Revista.
- No tocar Revista por una tarea de Tienda.
- No mezclar headers, footers, layouts, menús, snippets ni estilos entre ambos websites.
- CSS de Revista siempre bajo `.lp-revista`.
- CSS de Tienda siempre bajo `.lp-tienda`.

## Reglas generales

- No tocar módulos base de Odoo.
- No tocar checkout, carrito, pagos, productos, ecommerce ni Mercado Pago salvo petición explícita.
- Mantener datos dinámicos de Odoo.
- No convertir vistas dinámicas en HTML estático.
- Respetar multiwebsite y `website_id`.
- Evitar cambios amplios innecesarios.
- Evitar duplicar datos fallback si ya existen datos administrables desde backend.

## Revisión previa en módulos Odoo

Antes de modificar un módulo, revisar lo que aplique:

- `__manifest__.py`: dependencias, assets, data cargada y orden de XML.
- `views`: plantillas, herencias, snippets, layouts, IDs y `xpath`.
- `security`: accesos, reglas y grupos.
- `models`: modelos, campos computados, métodos fallback y datos administrables.
- `controllers`: rutas, `website=True`, sitemap, SEO, dominios y contexto de request.
- `static/src`: SCSS, JS, imágenes y assets.
- `data`: datos iniciales, `noupdate`, duplicación y registros fallback.
- Assets: bundles, nombres de archivos, carga en website y errores en `debug=assets`.

## Multiwebsite

- Confirmar siempre qué website debe renderizar la página.
- Revisar `website_id` cuando un registro sea específico de website.
- No asumir que `request.website` siempre existe en contexto de editor o assets.
- Si hay mezcla de headers/footers, revisar herencias de `website.layout`, `website.header`, `website.footer` y copias website-specific/COW en `ir.ui.view`.

## SCSS, XML y QWeb

- En SCSS, mantener selectores acotados por `.lp-revista` o `.lp-tienda`.
- En XML/QWeb, preservar IDs estables y herencias existentes.
- No insertar HTML estático para reemplazar contenido dinámico si el módulo tiene modelos o controladores para renderizarlo.
- Después de cambios en SCSS/XML/QWeb, revisar con `?debug=assets`.
- Si Odoo mantiene assets antiguos, considerar actualización de módulo y limpieza de assets desde Odoo, no desde SQL.

## Fallbacks y datos duplicados

- Antes de crear datos fallback, comprobar si existen registros administrables desde backend.
- Si hay asignaciones manuales o registros vigentes, deben prevalecer sobre fallback automático.
- No regenerar secciones, footer, sidebar o bloques si ya se administran desde backend.
- Evitar duplicados al actualizar módulo.

## Validación mínima

## Regla operativa sobre submódulos

- Toda fase nueva de Tienda debe implementarse primero sobre esta base segura.
- No usar `origin/main` como base de deploy de Tienda mientras siga incluyendo la línea fallida iniciada por `59fb18f` y `fe3b6fa`.
- El repo principal solo debe apuntar a commits verificados de esta base segura o de una línea que la reemplace explícitamente.

Cuando haya cambios funcionales:

```bash
python -m py_compile <archivo.py>
git diff --check
```

Para cambios XML/QWeb/SCSS, además revisar la página en Odoo con `?debug=assets`.

## Ahorro de tokens en diffs

Por defecto Codex no debe imprimir el `git diff` completo. Debe usar:

- Resumen textual de cambios.
- `git diff --check`.
- `git diff --name-only`.
- `git status --short`.
- Commits creados y push realizado, si aplica.

Solo debe mostrar el diff completo si el usuario lo pide explícitamente.

## Modos de trabajo Git

### Modo por defecto: implementar sin commit ni push

- Si el usuario no autoriza explícitamente commit o push, Codex solo debe modificar archivos, validar y entregar resumen textual.
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
- Detenerse si detecta archivos fuera del alcance de la tarea.
- Decidir el alcance del `git add` según los archivos realmente modificados.
- No usar `git add .` por defecto.
- Preferir add selectivo por módulo o por archivo.
- Para Revista, el add selectivo del subrepo debe limitarse a `latinpyme_revista_theme`.
- Para Tienda, el add selectivo del subrepo debe limitarse a `latinpyme_tienda_theme`.
- Para cambios mixtos autorizados, agregar únicamente las carpetas o archivos relacionados con la tarea.
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
- `Corregir carrusel de cursos en tienda`

### Modo push Production autorizado

Solo si el usuario escribe explícitamente `AUTORIZO ADD, COMMIT Y PUSH A PRODUCTION`, Codex puede hacer add, commit y push.

- `git push origin production` despliega en Odoo.sh Production.
- Antes del push debe confirmar que `git diff --check` está OK.
- Debe confirmar que `git diff --name-only` fue revisado.
- Debe confirmar que `git status --short` fue revisado.
- Debe confirmar el estado del subrepo custom.
- Debe confirmar el estado del repo principal.
- Debe confirmar que solo hay archivos del módulo autorizado.
- Debe confirmar que no se tocó Tienda si la tarea era Revista.
- Debe confirmar que no se tocó Revista si la tarea era Tienda.
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

Flujo Tienda:

```bash
cd /d/Odoo/latinpyme-odoo

git -C src/odoo/addons/latinpyme_custom status --short
git -C src/odoo/addons/latinpyme_custom diff --check
git -C src/odoo/addons/latinpyme_custom diff --name-only

git -C src/odoo/addons/latinpyme_custom add latinpyme_tienda_theme
git -C src/odoo/addons/latinpyme_custom commit -m "MENSAJE_SUGERIDO_POR_CODEX"
git -C src/odoo/addons/latinpyme_custom push origin HEAD:main

git status --short
git add src/odoo/addons/latinpyme_custom
git commit -m "MENSAJE_SUGERIDO_POR_CODEX"
git push origin production
```

## Modos operativos para tareas diarias

Regla global: cuando el usuario escriba uno de estos modos, Codex debe aplicar automáticamente las reglas correspondientes sin pedir que se repitan en el prompt.

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

### MODO TIENDA_SAFE

Uso: tarea de Tienda sin add, sin commit y sin push.

- Trabajar solo en `latinpyme_tienda_theme`.
- No tocar `latinpyme_revista_theme`.
- No tocar módulos core de Odoo.
- No tocar Revista.
- No tocar ecommerce, checkout, carrito, pagos, productos ni Mercado Pago salvo petición explícita.
- No ejecutar SQL ni modificar datos reales.
- No hacer `git add`, commit ni push.
- Mantener SCSS bajo `.lp-tienda`.
- Respetar multiwebsite y `website_id`.
- No mostrar `git diff` completo salvo solicitud explícita.
- Al final mostrar resumen textual, archivos modificados, validaciones, `git diff --check`, `git diff --name-only`, `git status --short`, riesgos y pruebas sugeridas.

### MODO TIENDA_PUSH

Uso: tarea de Tienda con add, commit y push a Production autorizados.

- Aplicar todas las reglas de `TIENDA_SAFE`, excepto que sí está autorizado add, commit y push.
- Sugerir automáticamente el mensaje de commit según el cambio realizado.
- Usar add selectivo, no `git add .` por defecto.
- Para cambios solo de Tienda, preferir `git -C src/odoo/addons/latinpyme_custom add latinpyme_tienda_theme`.
- Si solo cambiaron archivos puntuales, puede hacer add selectivo por archivo.
- Solo usar `git add .` si confirma que todos los cambios pendientes pertenecen a la tarea.
- Si detecta archivos fuera del alcance, debe detenerse.
- Hacer commit y push del subrepo custom a `origin HEAD:main`.
- Luego actualizar el puntero del subrepo en el repo principal.
- Hacer commit y push del repo principal a `origin production`.
- Recordar que `git push origin production` despliega en Odoo.sh Production.

## Estado Git

Antes de entregar:

```bash
git -C src/odoo/addons/latinpyme_custom diff --check
git -C src/odoo/addons/latinpyme_custom diff --name-only
git -C src/odoo/addons/latinpyme_custom status --short
git diff --check
git diff --name-only
git status --short
```

No hacer commit ni push sin autorización explícita.
