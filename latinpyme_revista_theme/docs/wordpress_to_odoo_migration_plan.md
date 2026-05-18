# Plan de carga inicial WordPress -> Odoo

Este documento define la forma segura de montar contenido de `https://latinpyme.com/` en el sitio temporal `https://revista.latinpyme.com/` sin migrar todavia el dominio principal.

## Estado recomendado

- Mantener `revista.latinpyme.com` como preproduccion con `noindex`.
- No cambiar DNS todavia.
- No implementar redirecciones 301 masivas sin inventario aprobado.
- Usar Odoo Blog como fuente principal de notas.
- No crear paginas manuales para cada nota.
- Cargar primero una base editorial suficiente para validar home, secciones, notas, mobile, header, footer y bloques administrables.

## Informacion que se puede obtener del WordPress publico

Desde el sitio publico normalmente se puede obtener:

- Navegacion visible y estructura editorial.
- URLs publicas de notas y secciones.
- Titulos, resumen visible, fechas y contenido HTML renderizado.
- Imagenes visibles en las paginas.
- Algunos metadatos si el REST API de WordPress esta habilitado.

Para una migracion limpia y completa, no conviene depender solo del scraping publico. La fuente preferida es exportacion WordPress.

## Exportaciones solicitadas

Pedir al administrador de WordPress:

1. `Herramientas > Exportar > Todo el contenido` en XML.
2. Export de medios o acceso a URLs publicas de `wp-content/uploads`.
3. Lista de usuarios/autores si no vienen completos en el XML.
4. Sitemap XML actual.
5. Export de Search Console con paginas con trafico organico.
6. Lista manual de URLs prioritarias para negocio.
7. Mapa editorial deseado: seccion destino, prioridad y si debe aparecer en home.

## Mapeo WordPress -> Odoo

| WordPress | Odoo |
| --- | --- |
| Categoria principal | `latinpyme.revista.section` y/o `blog.tag` |
| Tags | `blog.tag` |
| Post | `blog.post` |
| Titulo | Titulo de `blog.post` |
| Slug | Slug de la URL Odoo cuando sea posible |
| Excerpt | Resumen/subtitulo editorial |
| Content rendered | Cuerpo de la nota |
| Featured media | Imagen principal de la nota |
| Author | Autor editorial / contacto relacionado |
| Date | Fecha de publicacion |
| URL original | Inventario SEO |

## Secciones base sugeridas

- Inicio
- Gerencia
- Finanzas
- Empresas
- Tecnologia
- IA
- Mujeres
- Marketing
- RRHH
- Entrevistas
- Especiales
- Capacitacion
- Portafolio

La seccion `Portafolio` puede mantener jerarquia de hasta tres niveles. Los niveles 1 y 2 pueden funcionar como menus sin URL, y el nivel 3 como destino navegable.

## Carga inicial recomendada

1. Crear secciones y tags base.
2. Importar entre 30 y 80 notas prioritarias.
3. Priorizar notas con trafico organico, actualidad y valor editorial.
4. Importar imagen destacada cuando haya URL publica estable.
5. Mantener fecha original.
6. Mantener autor si viene identificado; si no, usar autor editorial generico.
7. Poblar home con reglas por seccion y algunos destacados manuales.
8. Poblar banners, portafolio, aliados y sidebar con registros administrables.
9. Validar visualmente home, seccion y nota individual.

## Automatizable

- Crear secciones.
- Crear tags.
- Crear posts de blog.
- Asignar categorias/tags.
- Cargar fechas, autores, resumen y cuerpo HTML.
- Registrar URLs origen y destino en inventario SEO.
- Descargar o enlazar imagenes principales si son publicas.

## Mejor cargar manualmente o revisar editoralmente

- Home hero y destacados principales.
- Banners comerciales.
- Sidebar editorial.
- Encuestas.
- CTAs.
- Portafolio comercial.
- Aliados.
- Ajustes finos de imagenes y textos largos.
- Posts con maquetacion compleja o shortcodes de WordPress.

## SEO en preproduccion

Hacer ahora:

- Mantener `revista.latinpyme.com` en `noindex`.
- Preparar inventario SEO URL antigua -> URL Odoo.
- Conservar slugs cuando sea viable.
- Documentar cambios de categoria y estructura.
- Validar canonicals y sitemap de Odoo en entorno temporal.
- No publicar sitemap final en Search Console.

No hacer todavia:

- No cambiar DNS.
- No apuntar `latinpyme.com` a Odoo.
- No aplicar redirecciones 301 masivas.
- No enviar sitemap final a Search Console.
- No retirar WordPress de produccion.

## Criterio para pasar a migracion final

- Inventario SEO aprobado.
- Contenido prioritario cargado y revisado.
- Home, secciones y notas validadas en desktop y mobile.
- Noindex listo para retirarse el dia de salida.
- Redirecciones 301 preparadas y probadas en staging.
- DNS y Cloudflare planificados con ventana de cambio.
- Search Console lista para validar dominio final.

