# LatinPyme Custom Addons - Reglas para Codex CLI

## Alcance

Esta carpeta contiene los addons personalizados de LatinPyme:

- `latinpyme_revista_theme`
- `latinpyme_tienda_theme`

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

Cuando haya cambios funcionales:

```bash
python -m py_compile <archivo.py>
git diff --check
```

Para cambios XML/QWeb/SCSS, además revisar la página en Odoo con `?debug=assets`.

## Estado Git

Antes de entregar:

```bash
git -C src/odoo/addons/latinpyme_custom status
git status
```

No hacer commit ni push sin autorización explícita.
