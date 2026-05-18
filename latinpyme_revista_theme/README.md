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

- `__init__.py`: carga modelos y controladores del módulo.
- `__manifest__.py`: declara dependencias `website` y `website_blog`, assets y vistas QWeb.
- `models/revista_models.py`: modelos backend para configuración, secciones, aliados, publicidad y programación anual.
- `controllers/main.py`: crea rutas públicas para la Home y las secciones editoriales.
- `security/ir.model.access.csv`: permisos para administradores de Website y sistema.
- `data/revista_defaults.xml`: configuración y secciones editoriales iniciales.
- `views/backend_views.xml`: menús, acciones y vistas backend de Revista LatinPyme.
- `views/assets.xml`: placeholder documental; en Odoo 19 los assets se cargan desde `__manifest__.py`.
- `views/snippet_templates.xml`: contiene masthead, cards, sidebar, banners, bloques de Home, sección, nota, portafolio, aliados y footer editorial.
- `views/snippets.xml`: registra los snippets reutilizables del grupo `LP Revista`.
- `static/src/img/snippets/*.svg`: miniaturas propias para el selector visual de bloques de Odoo Website.
- `static/src/img/editorial/*.svg`: placeholders editoriales para snippets insertados y estados sin imagen.
- `views/home_templates.xml`: template visual dinámico para `/revista`.
- `views/section_templates.xml`: template visual dinámico para `/revista/seccion/<seccion>`.
- `views/blog_post_templates.xml`: plantilla editorial segura para nota individual, heredando `website_blog` sin crear páginas manuales.
- `static/src/scss/revista.scss`: estilos scoped bajo `.lp-revista`.
- `static/src/js/program_calendar.js`: interacción ligera del calendario anual de Programación anual.
- `docs/seo_url_inventory_template.csv`: plantilla base para inventario SEO antes de redirecciones 301.

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

### Activar o desactivar secciones

Por defecto están activas todas las secciones editoriales creadas por el módulo. Desde backend:

`Revista LatinPyme > Secciones`

El administrador puede:

- activar o desactivar secciones,
- ordenar el menú editorial,
- cambiar nombre y slug,
- asociar la etiqueta real de Odoo Blog,
- configurar descripción, cover y SEO básico.
- crear submenús usando el campo `Menu padre`,
- marcar una sección como `Solo menu desplegable` para que aparezca en el header sin enlazar a una página.

El parámetro técnico anterior `latinpyme_revista_theme.enabled_sections` queda solo como compatibilidad si no existen registros en el modelo de secciones.

Las rutas `/revista/seccion/<slug>` respetan los registros activos del backend.

## Administración backend

La Fase 4 agrega el menú:

`Revista LatinPyme`

Submenús:

- `Configuración`
- `Secciones`
- `Aliados`
- `Publicidad`

### Configuración

Permite administrar:

- nombre de la revista,
- dominio final SEO,
- dominio temporal/preproducción,
- `noindex` en preproducción,
- texto de copyright/footer,
- teléfono, ciudad y email,
- enlaces sociales,
- visibilidad de bloques en Home,
- cantidades de posts en Home,
- cantidad de posts por página en secciones,
- visibilidad de sidebar, entrevistas, portafolio y aliados en notas individuales.
- visibilidad y textos de conferencia, encuesta y publicidad del sidebar.

### Secciones

Cada sección controla:

- nombre,
- slug,
- etiqueta de Blog asociada,
- estado activo/inactivo,
- orden,
- descripción,
- imagen/cover,
- SEO title,
- SEO description,
- sitio web si aplica.

Si `tag_id` está vacío, el módulo intenta encontrar una etiqueta de Blog con el mismo nombre de la sección.

#### Menús con submenús

El menú editorial soporta hasta 3 niveles:

1. Menú principal.
2. Submenú.
3. Submenú final con enlace.

Para crear un menú padre sin página pública, como `Capacitación`:

1. Abrir `Revista LatinPyme > Secciones`.
2. Crear o editar la sección `Capacitación`.
3. Activar `Solo menu desplegable`.
4. Crear submenús desde la pestaña `Submenus` o creando secciones independientes con `Menu padre = Capacitación`.
5. Cada submenu puede usar una etiqueta de Blog propia o una `URL personalizada`.

El módulo deja preparado el menú `Capacitación` con estos submenús si no existen:

- `Programación anual`
- `Charlas`
- `Diplomados`
- `Flashtraining`

La URL `/revista/seccion/capacitacion` no debe usarse como sección pública cuando `Capacitación` está marcada como `Solo menu desplegable`. Los submenús sí pueden tener página pública, por ejemplo `/revista/seccion/programacion-anual`, siempre que estén activos y no sean `Solo menu desplegable`.

Para menús de 3 niveles, los niveles con hijos se comportan como desplegables sin URL. El módulo prepara `Portafolio` como menú desplegable con esta estructura:

- `Aprendizaje empresarial`
  - `Capacitación a la medida`
  - `Fidelización empresarial`
  - `Cursos de actualización`
- `Tecnología: Salones y Espacios`
  - `LMS - Aulas`
  - `Salón de Eventos`
- `Inteligencia Artificial`
  - `Automatización de procesos con IA`

`Portafolio` y sus submenús de segundo nivel quedan como `Solo menu desplegable`; solo los elementos de tercer nivel enlazan a `/revista/seccion/<slug>` o a la `URL personalizada` que se configure.

### Programación anual

`/revista/seccion/programacion-anual` usa una plantilla especial. No muestra el listado genérico de notas de Blog; muestra eventos administrables desde backend.

Menú backend:

`Revista LatinPyme > Programación anual`

Cada evento controla:

- nombre,
- tipo de evento,
- fecha de inicio y fin,
- hora de inicio y fin,
- zona horaria,
- modalidad,
- lugar o enlace virtual,
- descripción,
- imagen,
- enlace y texto de inscripción,
- estado activo/inactivo,
- destacado,
- orden,
- sitio web si aplica.

Tipos de evento disponibles:

- `Charlas`
- `Diplomados`
- `Flashtraining`
- `Foros`
- `Curso 50 y 20 horas`

Al actualizar el módulo, los valores antiguos se normalizan de forma segura:

- `charla` -> `charlas`
- `diplomado` -> `diplomados`
- `capacitacion` -> `charlas`
- `otro` -> `foros`

El hero superior de esta página puede administrarse desde:

`Revista LatinPyme > Publicidad`

Crear un banner con ubicación `Programacion anual hero`. Si hay banner activo, reemplaza el bloque de título/descripcion de Programación anual. Si no hay banner activo, se conserva el fallback editorial.

En la página pública este banner se renderiza como imagen limpia: no muestra breadcrumb, título, texto, botón, overlay ni estadísticas sobre la imagen. Debajo del banner aparece el título editorial `Programación Anual` y luego los controles/calendario anual.

En la página pública, la sección usa una vista anual tipo calendario editorial:

- selector de año anterior/siguiente,
- resumen del año,
- filtros por tipo de evento sincronizados con el backend,
- 12 tarjetas mensuales en grilla responsive,
- días con eventos marcados en rojo,
- panel lateral/drawer con el detalle del día seleccionado,
- bloque de próximos eventos.

Cada evento conserva:

- botón de inscripción,
- enlace para Google Calendar,
- enlace para Outlook / Microsoft 365,
- opción Apple Calendar mediante archivo `.ics`,
- descarga `.ics`.

Esta vista no usa el sidebar editorial de conferencia, encuesta ni publicidad lateral. Por eso no muestra:

- `Próxima conferencia`,
- `Encuesta`,
- banner lateral `Automatiza procesos, optimiza recursos y crece sin límites`.

Si no hay eventos activos, la página muestra un fallback editorial indicando que aún no hay programación publicada.

### Aliados

Cada aliado controla:

- nombre,
- logo,
- enlace,
- estado activo/inactivo,
- orden,
- sitio web si aplica.

El carrusel `Aliados` primero usa estos registros. Si no hay aliados activos, mantiene los placeholders visuales del snippet.

### Publicidad

Cada banner controla:

- nombre interno,
- ubicación: `home_top`, `home_horizontal`, `sidebar`, `footer`, `note`, `section`, `program_hero`,
- imagen,
- título,
- texto,
- botón,
- enlace,
- estado activo/inactivo,
- orden,
- fecha de inicio y fin,
- sitio web si aplica.

Los templates usan banners dinámicos cuando existen y conservan fallback visual cuando no hay registros.

## Cómo instalar en Odoo.sh

1. Confirmar que la carpeta del módulo esté en:
   `src/odoo/addons/latinpyme_custom/latinpyme_revista_theme`
2. Hacer commit y push hacia la rama de Odoo.sh.
3. Esperar el build.
4. En Odoo, activar modo desarrollador.
5. Ir a Apps.
6. Actualizar lista de aplicaciones.
7. Buscar `Revista LatinPyme Theme`.
8. Instalar o actualizar.
9. Verificar `/revista`.
10. Actualizar los menús existentes para que apunten a las rutas de sección.
11. Abrir `Revista LatinPyme > Configuración` y revisar dominios, noindex, footer y redes.
12. Abrir `Revista LatinPyme > Secciones` y asociar cada sección con su etiqueta de Blog.

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
10. `LP Revista - Programación anual`
11. `LP Revista - Novedades`
12. `LP Revista - Portafolio`
13. `LP Revista - Aliados`
14. `LP Revista - Footer Editorial`
15. `LP Revista - Footer con Publicidad`
16. `LP Revista - Hero Sección`
17. `LP Revista - Listado de Artículos por Sección`
18. `LP Revista - Card Artículo Horizontal`
19. `LP Revista - Sidebar Conferencia`
20. `LP Revista - Sidebar Encuesta`
21. `LP Revista - Sidebar Publicidad`
22. `LP Revista - Paginación Visual`
23. `LP Revista - Entrevistas Relacionadas`
24. `LP Revista - Portafolio Compacto`
25. `LP Revista - Cabecera de Nota`
26. `LP Revista - Autor de Nota`
27. `LP Revista - Botones Compartir`
28. `LP Revista - Cuerpo Editorial`
29. `LP Revista - Cita Destacada`
30. `LP Revista - Imagen dentro del Artículo`
31. `LP Revista - Sidebar Nota`
32. `LP Revista - Artículos Relacionados`

Notas de edición de bloques:

- `LP Revista - Aliados` es un carrusel visual. Cada aliado es una imagen editable desde Website Builder; el editor puede reemplazar logos, borrar aliados no usados o duplicar logos/slides para mostrar la cantidad necesaria.
- En Fase 4, `LP Revista - Aliados` también se alimenta desde `Revista LatinPyme > Aliados` cuando existan aliados activos.
- `LP Revista - Footer Editorial` incluye el texto `© 2026 Revista LatinPyme - Todos los derechos reservados`.
- `LP Revista - Footer con Publicidad` replica el footer editorial y agrega un banner editable a la derecha para pauta o campañas.
- En Fase 4, los banners de Home, sidebar, footer, nota y sección pueden venir de `Revista LatinPyme > Publicidad`.

## Auditoría técnica actual

| Área | Estado | Implementación |
| --- | --- | --- |
| Configuración backend | Fase 4 implementada | Modelo `latinpyme.revista.config` con dominios, noindex, contacto, redes, footer, cantidades y visibilidad de bloques. |
| Home editorial `/revista` | Dinámica y configurable | Toma destacados, recientes, novedades, entrevistas y especiales desde Odoo Blog; banners y visibilidad de bloques se controlan desde backend. |
| Secciones `/revista/seccion/<slug>` | Dinámica y administrable | Filtra `blog.post` por `blog.tag`, usa registros `latinpyme.revista.section`, cover, descripción, SEO y activación por backend. |
| Nota individual de Blog | Administrable fino | Mantiene `website_blog`; añade controles globales, por sección y por nota desde `Notas editoriales`. |
| Aliados | Fase 4 implementada | Modelo `latinpyme.revista.ally` alimenta el carrusel; si no hay registros activos, se usan placeholders. |
| Publicidad | Fase 4 implementada | Modelo `latinpyme.revista.banner` alimenta Home, sidebar, footer, nota y sección con fallback visual. |
| Sidebar editorial | Administrable fino | Modelo `latinpyme.revista.sidebar.item` permite bloques por ubicación: global, Home, sección y nota. |
| Home editorial | Administrable fino | Modelo `latinpyme.revista.home.block` controla visibilidad, orden, etiquetas, cantidad y selección manual de notas. |
| Portafolio | Administrable fino | Modelo `latinpyme.revista.portfolio.item` controla tarjetas, bullets, icono/imagen y enlaces. |
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

## Nota individual administrable

La nota individual no se construye como página manual. Sigue siendo una publicación estándar de Odoo Blog.

El editor administra desde Odoo Blog:

- título de la nota,
- subtítulo o resumen,
- imagen principal mediante el cover de Blog,
- contenido del artículo con el editor visual,
- autor,
- fecha,
- etiquetas editoriales,
- publicación/despublicación,
- slug y SEO nativo.

El módulo añade automáticamente:

- header editorial LatinPyme,
- miga de pan hacia `/revista` y la sección principal,
- etiqueta principal como kicker,
- título grande,
- metadatos de autor y fecha,
- imagen principal con el sistema `website.record_cover`,
- fallback editorial limpio si la nota aún no tiene cover configurado,
- tiempo de lectura aproximado calculado desde el contenido,
- caja de autor,
- botones de compartir,
- cuerpo editorial estilizado,
- sidebar con conferencia, encuesta y publicidad,
- artículos relacionados del mismo blog,
- entrevistas relacionadas si existe la etiqueta `Entrevistas`,
- portafolio, aliados y footer editorial.

Desde `Revista LatinPyme > Configuración`, el administrador puede mostrar u ocultar sidebar, entrevistas relacionadas, portafolio y aliados para todas las notas.

Desde `Revista LatinPyme > Secciones`, el administrador puede aplicar reglas por sección para todas las notas de una etiqueta.

Desde `Revista LatinPyme > Notas editoriales`, el editor puede crear un control específico por nota para:

- mostrar/ocultar sidebar,
- mostrar/ocultar artículos relacionados,
- mostrar/ocultar entrevistas relacionadas,
- mostrar/ocultar portafolio,
- mostrar/ocultar aliados,
- seleccionar banner específico de nota,
- configurar título SEO, descripción SEO y URL final SEO opcional.

Si no existe un control activo en `Notas editoriales`, la nota usa la regla de su sección. Si la sección tampoco define regla, usa la configuración global.

Para que una nota quede asociada a una sección, el editor debe asignar una etiqueta editorial:

`Gerencia`, `Negocios`, `IA`, `Laboral`, `Finanzas`, `Entrevistas`, `Especiales`, `Mujeres` o `Portafolio`.

## SEO y preproducción

El dominio histórico SEO es:

`https://latinpyme.com`

El dominio temporal de trabajo es:

`https://revista.latinpyme.com`

Este módulo no asume que `revista.latinpyme.com` sea el dominio final. Las rutas generadas quedan listas para producción en `latinpyme.com`.

Mientras se navegue desde el dominio temporal configurado, `.odoo.com` u `.odoo.sh`, el módulo añade si `noindex` está activo:

- `meta name="robots" content="noindex,nofollow"` en las páginas controladas por el módulo.
- `X-Robots-Tag: noindex, nofollow` en las respuestas de `/revista` y secciones.
- Meta robots en vistas nativas de Blog cuando se renderizan desde dominios de preproducción.

Canonical:

- La Home y secciones usan el dominio final configurado en `Revista LatinPyme > Configuración`.
- La nota individual no fuerza canonical hacia `latinpyme.com` por defecto mientras el dominio histórico siga en WordPress.
- Si SEO valida una URL final, `Revista LatinPyme > Notas editoriales` permite registrar la URL final por nota para inventario y metadatos sociales, sin reemplazar masivamente el canonical nativo de Odoo.
- Se mantiene el canonical nativo de Odoo Website para evitar duplicados o señales cruzadas en preproducción.
- En preproducción la defensa principal es `noindex,nofollow`; cuando `latinpyme.com` migre a Odoo se debe validar el dominio principal del Website y Search Console.
- Antes de producción, el dominio principal de Website debe quedar configurado como `latinpyme.com` y el dominio final SEO debe revisarse en la configuración de Revista.

## Estrategia de migración SEO desde WordPress

No implementar redirecciones 301 hasta tener inventario real de URLs antiguas.

Plantilla incluida:

`docs/seo_url_inventory_template.csv`

Columnas sugeridas:

| Campo | Uso |
| --- | --- |
| `url_actual` | URL histórica de WordPress o del sitio anterior. |
| `url_nueva` | URL final equivalente en Odoo. |
| `tipo_contenido` | Home, sección, nota, landing, recurso, etc. |
| `prioridad_seo` | Alta, media o baja según tráfico, enlaces y negocio. |
| `estado` | Pendiente, validada, lista para redirección, aplicada. |
| `redireccion_requerida` | Sí/no. |
| `observaciones` | Riesgos, tráfico, owner editorial o notas técnicas. |

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

## Fase 5 recomendada

- Definir si la Home final de `latinpyme.com` será `/revista` o la raíz `/`.
- Mapear URLs WordPress contra URLs Odoo reales.
- Implementar redirecciones 301.
- Evaluar rutas personalizadas para posts si se necesita una estructura más parecida a WordPress.
- Integrar encuesta real.
- Administrar conferencia/evento del sidebar desde un modelo propio o desde Eventos si se instala ese módulo.
- Integrar buscador editorial avanzado por sección, fecha y etiqueta.
- Alimentar relacionados por coincidencia de etiquetas, no solo por publicaciones recientes del mismo blog.
- Revisar y ajustar visualmente en Odoo.sh con datos reales, mobile y desktop.

## Administrabilidad fina

Esta fase agrega menús backend pensados para editores no técnicos:

- `Revista LatinPyme > Home editorial`: permite activar/desactivar bloques del Home, ordenar, cambiar títulos, elegir etiqueta fuente, definir cantidad de notas y seleccionar publicaciones manualmente.
- `Revista LatinPyme > Notas editoriales`: permite controlar bloques, banner y SEO de una nota específica sin tocar la página en Builder.
- `Revista LatinPyme > Portafolio`: permite administrar las tarjetas del bloque Portafolio sin tocar QWeb ni Builder.
- `Revista LatinPyme > Sidebar editorial`: permite crear bloques por ubicación: `Global`, `Home`, `Pagina de seccion` y `Nota individual`.
- `Revista LatinPyme > Secciones`: ahora permite overrides por sección para sidebar, relacionados, portafolio, aliados, banner de sección y banner de nota.

### Como administrar el Home

1. Abrir `Revista LatinPyme > Home editorial`.
2. Editar cada bloque:
   - `Banners superiores`
   - `Hero y destacados`
   - `Lo mas reciente`
   - `Secciones`
   - `Novedades`
   - `Entrevistas`
   - `Especiales`
   - `Banners intermedios`
   - `Portafolio`
   - `Aliados`
3. Para destacar notas manualmente, usar `Notas seleccionadas`.
4. Si no se seleccionan notas, el bloque usa la etiqueta fuente.
5. Si tampoco hay etiqueta fuente, usa las publicaciones recientes como fallback.

### Como administrar Portafolio

1. Abrir `Revista LatinPyme > Portafolio`.
2. Crear o editar tarjetas.
3. Completar titulo, icono o imagen, bullets y enlaces.
4. Ordenar con el campo `Orden`.
5. Activar/desactivar segun campaña.

### Como administrar Sidebar editorial

1. Abrir `Revista LatinPyme > Sidebar editorial`.
2. Elegir ubicacion:
   - `Global`: fallback para todo el sitio.
   - `Home`: solo portada.
   - `Pagina de seccion`: secciones.
   - `Nota individual`: notas de Blog.
3. Elegir tipo:
   - `Proxima conferencia`
   - `Encuesta`
   - `CTA entrevistas`
   - `Banner lateral`
4. Si existen bloques para una ubicacion especifica, se usan esos. Si no existen, se usa `Global`.

### Como administrar una seccion

En `Revista LatinPyme > Secciones`, cada seccion puede controlar:

- cantidad de notas por pagina,
- mostrar/ocultar sidebar,
- mostrar/ocultar relacionados,
- mostrar/ocultar portafolio,
- mostrar/ocultar aliados,
- banner especifico de seccion,
- banner especifico para notas de esa seccion,
- SEO title,
- SEO description.

El valor `Usar configuracion general` conserva el comportamiento global.

### Como administrar una nota especifica

1. Publicar o editar la nota desde Odoo Blog.
2. Abrir `Revista LatinPyme > Notas editoriales`.
3. Crear un registro y seleccionar la `Nota de Blog`.
4. En `Bloques visibles`, elegir `Usar configuracion general`, `Mostrar` u `Ocultar` para cada bloque.
5. En `Banner`, elegir un banner de ubicacion `Nota individual` si la nota necesita pauta propia.
6. En `SEO`, completar solo si esa nota necesita un override especifico.

Regla de prioridad:

1. `Notas editoriales`.
2. `Secciones`.
3. `Configuracion`.

No se recomienda llenar la URL final SEO por nota durante preproduccion salvo que SEO ya haya validado la equivalencia final.

### Snippet Programacion anual

El Website Builder incluye el snippet:

`LP Revista - Programación anual`

Este snippet se puede arrastrar a una pagina complementaria. Los eventos no se editan en el Builder; se administran desde `Revista LatinPyme > Programacion anual`.

### Checklist editorial antes de produccion

- Home configurado desde `Home editorial`.
- Banners creados por ubicacion clara.
- Portafolio cargado desde backend.
- Sidebar cargado por ubicacion.
- Secciones asociadas a etiquetas de Blog.
- Notas publicadas con titulo, subtitulo, cover, autor, etiquetas y SEO.
- Notas criticas revisadas en `Notas editoriales`.
- Programacion anual con eventos activos y links de calendario probados.
- Footer con redes sociales reales.
- Mobile revisado sin scroll horizontal.
- Preproduccion con `noindex` activo.
- Inventario SEO listo antes de redirecciones 301.

### Plan de prueba editorial en Odoo.sh

1. Crear una nota real en Odoo Blog con título, subtítulo, autor, cover, cuerpo y etiqueta de sección.
2. Verificar que la nota aparece en `/revista`, en la sección correspondiente y en su URL nativa de Blog.
3. Abrir `Revista LatinPyme > Home editorial` y probar activar/desactivar bloques, cambiar orden y seleccionar notas manuales.
4. Abrir `Revista LatinPyme > Publicidad` y probar banners por ubicación: Home, sección, nota, sidebar, footer y Programación anual.
5. Abrir `Revista LatinPyme > Notas editoriales` y crear un override para una nota crítica.
6. Validar en frontend que el override muestra/oculta sidebar, relacionados, entrevistas, portafolio, aliados y banner según lo configurado.
7. Abrir `Revista LatinPyme > Portafolio` y confirmar que las tarjetas se actualizan sin editar Builder.
8. Abrir `Revista LatinPyme > Sidebar editorial` y confirmar bloques por ubicación.
9. Crear eventos en `Revista LatinPyme > Programacion anual` y probar Google Calendar, Outlook y `.ics`/Apple Calendar.
10. Validar responsive móvil en Home, sección, nota individual y Programación anual.
11. Revisar SEO básico: noindex en preproducción, metadatos sociales, canonical si aplica e inventario de URLs.
