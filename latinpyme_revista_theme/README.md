# Revista LatinPyme Theme

Módulo Odoo 19 para convertir Odoo Website + Odoo Blog en una revista digital administrable.

El módulo trabaja únicamente dentro de `latinpyme_revista_theme` y no depende de `lp_website_ui`, `lp_theme_tweaks`, `sendpulse_webhook` ni ecommerce.

## Objetivo

- Usar Odoo Blog como fuente editorial principal.
- Mostrar una Home editorial en `/revista`.
- Mostrar páginas de sección en `/revista/seccion/<seccion>`.
- Filtrar secciones por etiquetas de Blog.
- Mantener el diseño bajo el scope CSS `.lp-revista`.
- Evitar HTML pegado por editores.
- Preparar la transición SEO desde WordPress en `latinpyme.com` hacia Odoo.

## Archivos

- `__init__.py`: carga los controladores del módulo.
- `__manifest__.py`: declara dependencias `website` y `website_blog`, assets y vistas QWeb.
- `controllers/main.py`: crea rutas públicas para la Home y las secciones editoriales.
- `views/assets.xml`: placeholder documental; en Odoo 19 los assets se cargan desde `__manifest__.py`.
- `views/snippet_templates.xml`: contiene masthead, cards, sidebar, banners, bloques de Home, sección, nota, portafolio, aliados y footer editorial.
- `views/snippets.xml`: registra los snippets reutilizables del grupo `LP Revista`.
- `static/src/img/snippets/*.svg`: miniaturas propias para el selector visual de bloques de Odoo Website.
- `views/home_templates.xml`: template visual dinámico para `/revista`.
- `views/section_templates.xml`: template visual dinámico para `/revista/seccion/<seccion>`.
- `views/blog_post_templates.xml`: capa visual segura sobre templates nativos de `website_blog`.
- `static/src/scss/revista.scss`: estilos scoped bajo `.lp-revista`.

## Rutas disponibles

- `/revista`
- `/revista/seccion/gerencia`
- `/revista/seccion/negocios`
- `/revista/seccion/ia`
- `/revista/seccion/laboral`
- `/revista/seccion/finanzas`
- `/revista/seccion/entrevistas`
- `/revista/seccion/especiales`
- `/revista/seccion/mujeres`
- `/revista/seccion/portafolio`

Las publicaciones individuales siguen usando las URLs nativas de Odoo Blog. Esto evita romper funcionalidades internas de Blog, SEO metadata, publicación/despublicación, edición visual, tags, autores y sitemap nativo.

## Cómo instalar en Odoo.sh

1. Confirmar que la carpeta del módulo esté en:
   `src/odoo/addons/latinpyme_custom/latinpyme_revista_theme`
2. Hacer commit y push hacia la rama de Odoo.sh.
3. Esperar el build.
4. En Odoo, activar modo desarrollador.
5. Ir a Apps.
6. Actualizar lista de aplicaciones.
7. Buscar `Revista LatinPyme Theme`.
8. Instalar.
9. Verificar `/revista`.
10. Actualizar los menús existentes para que apunten a las rutas de sección.

Nota Odoo 19:

- El SCSS se declara en `__manifest__.py` dentro de `web.assets_frontend`.
- No se heredan bundles de assets desde XML; Odoo 19 usa el manifest.

## Uso editorial

Los editores no deben modificar HTML ni CSS.

El header editorial ya está incluido automáticamente en `/revista` y en las páginas de sección. También queda disponible como snippet `Header editorial` para páginas complementarias, pero no debe usarse para duplicar el encabezado en la Home dinámica.

Snippets disponibles:

1. `LP Revista - Header Editorial`
2. `LP Revista - Hero Home Doble`
3. `LP Revista - Actualidad Destacada`
4. `LP Revista - Lo Más Reciente`
5. `LP Revista - Grid de Cards de Artículos`
6. `LP Revista - Secciones Editoriales`
7. `LP Revista - Entrevistas`
8. `LP Revista - Especiales`
9. `LP Revista - Banner Publicitario Horizontal`
10. `LP Revista - Novedades`
11. `LP Revista - Portafolio`
12. `LP Revista - Aliados`
13. `LP Revista - Footer Editorial`
14. `LP Revista - Hero Sección`
15. `LP Revista - Listado de Artículos por Sección`
16. `LP Revista - Card Artículo Horizontal`
17. `LP Revista - Sidebar Conferencia`
18. `LP Revista - Sidebar Encuesta`
19. `LP Revista - Sidebar Publicidad`
20. `LP Revista - Paginación Visual`
21. `LP Revista - Entrevistas Relacionadas`
22. `LP Revista - Portafolio Compacto`
23. `LP Revista - Cabecera de Nota`
24. `LP Revista - Autor de Nota`
25. `LP Revista - Botones Compartir`
26. `LP Revista - Cuerpo Editorial`
27. `LP Revista - Cita Destacada`
28. `LP Revista - Imagen dentro del Artículo`
29. `LP Revista - Sidebar Nota`
30. `LP Revista - Artículos Relacionados`

## Auditoría técnica actual

| Área | Estado | Implementación |
| --- | --- | --- |
| Home editorial `/revista` | Dinámica parcial | Toma destacados, recientes, novedades, entrevistas y especiales desde Odoo Blog. Los banners y portafolio siguen como bloques editables. |
| Secciones `/revista/seccion/<slug>` | Dinámica | Filtra `blog.post` por `blog.tag` editorial y añade paginación por `?page=2`. |
| Nota individual de Blog | Parcial | Se mantiene `website_blog` como fuente y se añade capa visual segura; la reconstrucción completa del layout de nota queda para Fase 3. |
| Snippets Home | Completo base | Bloques reutilizables y editables desde Website Builder. |
| Snippets Sección | Completo base | Hero, listado visual, card horizontal, sidebars, paginación y relacionados. |
| Snippets Nota | Completo base | Cabecera, autor, compartir, cuerpo, cita, imagen, sidebar, relacionados. |

Flujo recomendado:

1. Crear una publicación en Odoo Blog dentro del blog `Revista LatinPyme`.
2. Subir imagen principal desde el cover de Blog.
3. Escribir título, subtítulo y contenido.
4. Asignar una etiqueta editorial: `Gerencia`, `Negocios`, `IA`, `Laboral`, `Finanzas`, `Entrevistas`, `Especiales`, `Mujeres` o `Portafolio`.
5. Configurar SEO desde las opciones nativas de Website/Blog: meta title, meta description, imagen social/Open Graph y slug.
6. Publicar o despublicar usando los controles nativos de Odoo.

Para destacar contenido en portada:

- Crear y asignar una de estas etiquetas opcionales: `Destacado Home`, `Destacado Portada`, `Portada`, `Home` o `Destacado`.
- Si no existe contenido destacado, la Home usa automáticamente las notas publicadas más recientes.

Para destacar contenido en una sección:

- Asignar la etiqueta de sección correspondiente.
- Opcionalmente añadir `Destacado Sección`, `Principal` o `Destacado`.
- Si no hay destacado, la sección usa la nota más reciente de esa etiqueta.

## SEO y preproducción

El dominio histórico SEO es:

`https://latinpyme.com`

El dominio temporal de trabajo es:

`https://revista.latinpyme.com`

Este módulo no asume que `revista.latinpyme.com` sea el dominio final. Las rutas generadas quedan listas para producción en `latinpyme.com`.

Mientras se navegue desde `revista.latinpyme.com`, `.odoo.com` u `.odoo.sh`, el módulo añade:

- `meta name="robots" content="noindex,nofollow"` en las páginas controladas por el módulo.
- `X-Robots-Tag: noindex, nofollow` en las respuestas de `/revista` y secciones.
- Meta robots en vistas nativas de Blog cuando se renderizan desde dominios de preproducción.

Canonical:

- No se genera un canonical adicional para evitar duplicados.
- Se usa el canonical nativo de Odoo Website.
- Antes de producción, el dominio principal de Website debe quedar configurado como `latinpyme.com`.

## Estrategia de migración SEO desde WordPress

No implementar redirecciones 301 hasta tener inventario real de URLs antiguas.

Fase de migración:

1. Exportar inventario completo de URLs de WordPress en `latinpyme.com`.
2. Incluir posts, páginas, categorías, tags, autores, imágenes relevantes y URLs con tráfico.
3. Exportar datos desde Google Search Console: clicks, impresiones, CTR y posición.
4. Mapear cada URL antigua a su nueva URL en Odoo.
5. Conservar slugs cuando sea viable.
6. Configurar redirecciones 301 una a una.
7. Validar que no haya cadenas de redirección.
8. Validar sitemap.xml de Odoo.
9. Validar robots.txt.
10. Configurar propiedad final en Google Search Console.
11. Revisar meta titles, meta descriptions y Open Graph.
12. Evitar duplicidad entre `latinpyme.com` y `revista.latinpyme.com`.
13. Cuando `latinpyme.com` apunte a Odoo, bloquear o desindexar el dominio temporal.

## Redirecciones 301

Pendiente hasta tener inventario. Ejemplos de mapeo esperado:

- `https://latinpyme.com/<slug-wordpress>/` -> `https://latinpyme.com/blog/revista-latinpyme-<id>/<slug-odoo>-<id>`
- `https://latinpyme.com/category/gerencia/` -> `https://latinpyme.com/revista/seccion/gerencia`
- `https://latinpyme.com/tag/<tag>/` -> revisar caso por caso para evitar thin content.

La estructura final de posts debe definirse con base en inventario SEO. Si se necesita replicar exactamente el patrón WordPress, eso debe hacerse en Fase 2 con rutas y redirecciones controladas.

## Fase 3 recomendada

- Definir si la Home final de `latinpyme.com` será `/revista` o la raíz `/`.
- Mapear URLs WordPress contra URLs Odoo reales.
- Implementar redirecciones 301.
- Evaluar rutas personalizadas para posts si se necesita una estructura más parecida a WordPress.
- Reemplazar datos placeholder de redes, contacto, aliados y eventos por configuraciones administrables.
- Crear modelo ligero de banners/editorial promos si los banners deben ser administrables sin Website Editor.
- Integrar encuesta real.
- Integrar buscador editorial avanzado por sección, fecha y etiqueta.
- Rehacer la plantilla completa de nota individual solo después de confirmar los XML IDs y estructura final de `website_blog` en Odoo.sh.
- Revisar y ajustar visualmente en Odoo.sh con datos reales, mobile y desktop.
