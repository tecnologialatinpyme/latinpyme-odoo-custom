# Manual de administracion Revista LatinPyme

Version: 1.0  
Sitio temporal: https://revista.latinpyme.com  
Modulo: `latinpyme_revista_theme`

---

## 1. Objetivo del manual

Este manual explica como administrar la Revista LatinPyme en Odoo sin tocar codigo, HTML ni CSS.

Esta dirigido a editores, comunicadores, equipo comercial y personal no tecnico que necesita:

- Crear notas periodisticas.
- Asignar notas a secciones.
- Administrar banners y publicidad.
- Administrar menu, header y footer.
- Administrar aliados.
- Administrar portafolio.
- Administrar programacion anual.
- Usar el Website Builder con bloques ya preparados.
- Validar que el sitio se vea bien en computador y celular.

---

## 2. Reglas generales para editores

1. Las notas periodisticas se crean desde Blog.
2. No se deben crear paginas manuales para cada nota.
3. Las secciones se controlan por etiquetas de Blog y por el menu `Revista LatinPyme > Secciones`.
4. Los textos e imagenes comerciales se administran desde backend, no desde codigo.
5. El Website Builder se usa para arrastrar bloques ya disenados, no para modificar estilos avanzados.
6. Antes de publicar, siempre revisar la nota en vista escritorio y vista movil.
7. Mientras el sitio sea preproduccion, mantener `revista.latinpyme.com` como no indexable.
8. No cambiar DNS ni dominio principal hasta completar revision SEO.

---

## 3. Mapa rapido de administracion

| Necesidad | Donde se administra |
| --- | --- |
| Crear una nota | `Sitio Web > Blog` |
| Asignar nota a seccion | Etiquetas/Tags del Blog |
| Configurar menu y secciones | `Revista LatinPyme > Secciones` |
| Redes sociales, telefono, footer | `Revista LatinPyme > Configuracion` |
| Banners y publicidad | `Revista LatinPyme > Publicidad` |
| Aliados | `Revista LatinPyme > Aliados` |
| Portafolio | `Revista LatinPyme > Portafolio` |
| Sidebar editorial | `Revista LatinPyme > Sidebar editorial` |
| Home editorial | `Revista LatinPyme > Home editorial` |
| Programacion anual | `Revista LatinPyme > Programacion anual` |
| Bloques arrastrables | Website Builder, grupo `LP Revista` |

---

## 4. Flujo recomendado de trabajo editorial

Para alimentar el sitio de manera ordenada:

1. Crear o revisar la seccion.
2. Crear la nota en Blog.
3. Asignar la etiqueta correcta.
4. Subir imagen principal.
5. Revisar resumen, autor y fecha.
6. Completar SEO basico.
7. Guardar.
8. Publicar.
9. Validar en la seccion.
10. Validar en movil.
11. Si la nota debe aparecer en Home, configurar el bloque correspondiente.

---

## 5. Configuracion general del sitio

Ruta:

`Revista LatinPyme > Configuracion`

Aqui se administran datos generales del sitio:

- Nombre de la revista.
- Sitio web.
- Dominio final.
- Dominio de preproduccion.
- No indexar preproduccion.
- Texto legal del footer.
- Telefono.
- Ciudad.
- Correo.
- Redes sociales.
- Opciones globales de Home.
- Opciones globales de notas.
- Opciones globales de sidebar.

### 5.1 Redes sociales

En la pestana `Redes sociales`, completar:

- URL Facebook.
- URL LinkedIn.
- URL Instagram.
- URL YouTube.
- URL WhatsApp.

Recomendaciones:

- Usar URLs completas, por ejemplo `https://www.facebook.com/revistalatinpyme`.
- No dejar `#` si la red social ya existe.
- Probar los iconos en header y footer despues de guardar.

### 5.2 Footer

Campos importantes:

- Texto legal del footer.
- Telefono.
- Ciudad.
- Correo.
- Redes sociales.

El footer toma estos datos automaticamente.

---

## 6. Secciones y menu editorial

Ruta:

`Revista LatinPyme > Secciones`

Las secciones controlan:

- Menu principal.
- Submenus.
- Submenus de tercer nivel.
- Slug de la seccion.
- Etiqueta de Blog asociada.
- Imagen de portada.
- Descripcion.
- Visibilidad de sidebar, aliados, portafolio y banners.
- SEO por seccion.

### 6.1 Crear una seccion

1. Ir a `Revista LatinPyme > Secciones`.
2. Clic en `Nuevo`.
3. Completar:
   - Nombre.
   - Slug.
   - Etiqueta de Blog.
   - Orden.
   - Activa.
   - Descripcion.
   - Imagen de portada si aplica.
4. Guardar.

Ejemplo:

- Nombre: `Gerencia`
- Slug: `gerencia`
- Etiqueta de Blog: `Gerencia`

La URL publica sera:

`/revista/seccion/gerencia`

### 6.2 Crear menu desplegable sin URL

Usar esta opcion cuando un item debe abrir submenu, pero no debe llevar a una pagina.

1. Crear o editar seccion.
2. Activar `Solo menu sin URL`.
3. Dejar hijos configurados debajo.
4. Guardar.

Ejemplo:

`Capacitacion` puede ser menu padre sin URL y tener dentro:

- Programacion anual.
- Charlas.
- Diplomados.
- Flashtraining.

### 6.3 Crear submenu de tercer nivel

Ejemplo para Portafolio:

Portafolio

- Aprendizaje empresarial
  - Capacitacion a la medida
  - Fidelizacion empresarial
  - Cursos de actualizacion
- Tecnologia: Salones y Espacios
  - LMS - Aulas
  - Salon de Eventos
- Inteligencia Artificial
  - Automatizacion de procesos con IA

Regla:

- Nivel 1 y nivel 2 pueden ser menus sin URL.
- Nivel 3 debe tener URL si se quiere navegar.

### 6.4 Configuracion visual por seccion

En cada seccion revisar:

- Mostrar/ocultar sidebar.
- Mostrar/ocultar portafolio.
- Mostrar/ocultar aliados.
- Banner de seccion.
- Cantidad de notas por pagina.
- SEO title.
- SEO description.

---

## 7. Crear notas periodisticas por seccion

Ruta:

`Sitio Web > Blog`

o:

`Sitio Web > Blog > Publicaciones`

### 7.1 Crear una nota nueva

1. Entrar a `Sitio Web > Blog`.
2. Clic en `Nuevo`.
3. Completar:
   - Titulo.
   - Blog de Revista LatinPyme.
   - Subtitulo o resumen.
   - Contenido.
   - Imagen principal.
4. Guardar.

### 7.2 Asignar la nota a una seccion

Buscar el campo:

`Etiquetas` o `Tags`

Asignar la etiqueta de la seccion correspondiente.

Ejemplos:

| Seccion | Etiqueta |
| --- | --- |
| Gerencia | Gerencia |
| Finanzas | Finanzas |
| Empresas | Empresas |
| Tecnologia | Tecnologia |
| IA | IA |
| Mujeres | Mujeres |
| Marketing | Marketing |
| RRHH | RRHH |
| Entrevistas | Entrevistas |
| Especiales | Especiales |

Importante:

Si la nota no tiene etiqueta, no aparecera en la seccion correcta.

### 7.3 Imagen principal

Buenas practicas:

- Usar imagen horizontal.
- Usar buena calidad.
- Evitar imagenes borrosas.
- Evitar archivos demasiado pesados.
- Usar nombres claros.

Ejemplo:

`liderazgo-empresarial-2026.jpg`

### 7.4 SEO basico de la nota

Antes de publicar, revisar:

- Titulo SEO.
- Descripcion SEO.
- URL o slug.

Ejemplo:

Titulo:

`Estrategias financieras para fortalecer empresas`

Slug recomendado:

`estrategias-financieras-fortalecer-empresas`

Reglas:

- No usar tildes en el slug.
- No usar simbolos raros.
- Evitar URLs demasiado largas.
- Conservar el slug original si viene de WordPress y es importante para SEO.

### 7.5 Publicar nota

1. Guardar.
2. Revisar vista previa.
3. Activar `Publicado`.
4. Abrir la seccion correspondiente.
5. Confirmar que la nota aparece.
6. Abrir la nota individual.
7. Revisar en movil.

---

## 8. Home editorial

Ruta:

`Revista LatinPyme > Home editorial`

El Home puede administrarse por bloques.

Bloques comunes:

- Hero.
- Banners superiores.
- Notas destacadas.
- Lo mas reciente.
- Secciones.
- Entrevistas.
- Especiales.
- Novedades.
- Banners intermedios.
- Portafolio.
- Aliados.

### 8.1 Crear o editar bloque de Home

1. Ir a `Revista LatinPyme > Home editorial`.
2. Clic en `Nuevo` o abrir un bloque existente.
3. Completar:
   - Nombre interno.
   - Tipo de bloque.
   - Activo.
   - Orden.
   - Titulo visible si aplica.
   - Etiqueta fuente si aplica.
   - Notas seleccionadas manualmente si aplica.
   - Cantidad de notas.
   - Texto del enlace.
   - URL del enlace.
4. Guardar.

### 8.2 Recomendaciones para Home

- Usar pocas notas destacadas.
- Mantener imagenes de buena calidad.
- Revisar que cada bloque tenga una funcion clara.
- No saturar el Home con demasiada publicidad.
- Validar que se vea bien en movil.

---

## 9. Publicidad y banners

Ruta:

`Revista LatinPyme > Publicidad`

Los banners se administran desde backend.

Campos principales:

- Activo.
- Orden.
- Nombre.
- Ubicacion.
- Sitio web.
- Fecha de inicio.
- Fecha de fin.
- Imagen.
- Titulo.
- Texto.
- Texto del boton.
- URL.

### 9.1 Ubicaciones comunes

- Home superior.
- Home horizontal.
- Sidebar.
- Footer.
- Nota individual.
- Seccion.
- Programacion anual hero.

### 9.2 Crear banner

1. Ir a `Revista LatinPyme > Publicidad`.
2. Clic en `Nuevo`.
3. Completar nombre.
4. Elegir ubicacion.
5. Subir imagen.
6. Completar URL si debe ser clicable.
7. Activar.
8. Guardar.
9. Revisar frontend.

### 9.3 Banner de Programacion anual

Para la pagina:

`/revista/seccion/programacion-anual`

usar ubicacion:

`Programacion anual hero`

Reglas:

- El banner muestra solo la imagen.
- Si tiene URL, al hacer clic abre en nueva pestana.
- No muestra texto encima.
- No muestra boton encima.

---

## 10. Sidebar editorial

Ruta:

`Revista LatinPyme > Sidebar editorial`

El sidebar permite administrar bloques laterales como:

- Proxima conferencia.
- Encuesta.
- CTA.
- Banner lateral.

### 10.1 Crear bloque de sidebar

1. Ir a `Revista LatinPyme > Sidebar editorial`.
2. Clic en `Nuevo`.
3. Completar:
   - Nombre interno.
   - Ubicacion.
   - Tipo de bloque.
   - Activo.
   - Orden.
   - Etiqueta superior.
   - Titulo.
   - Texto.
   - Fecha, lugar y hora si aplica.
   - Boton y URL si aplica.
   - Imagen si aplica.
4. Guardar.
5. Revisar pagina donde debe aparecer.

### 10.2 Ubicaciones recomendadas

- Global.
- Home.
- Pagina de seccion.
- Nota individual.

---

## 11. Portafolio

Ruta:

`Revista LatinPyme > Portafolio`

Permite administrar las tarjetas comerciales del portafolio.

Campos principales:

- Titulo.
- Categoria.
- Icono o imagen.
- Bullet 1.
- Bullet 2.
- Bullet 3.
- Bullet 4.
- Bullet 5.
- Texto boton WhatsApp.
- URL boton WhatsApp.
- Texto boton agenda.
- URL boton agenda.
- Activo.
- Orden.

### 11.1 Crear item de portafolio

1. Ir a `Revista LatinPyme > Portafolio`.
2. Clic en `Nuevo`.
3. Escribir titulo.
4. Escribir categoria.
5. Completar bullets.
6. Configurar botones.
7. Activar.
8. Guardar.
9. Revisar frontend.

Ejemplo:

Categoria:

`Aprendizaje empresarial`

Titulo:

`Capacitacion a la medida`

Bullets:

- Programas empresariales.
- Cursos de actualizacion.
- Acompanamiento especializado.

---

## 12. Aliados

Ruta:

`Revista LatinPyme > Aliados`

Campos:

- Nombre.
- Logo.
- URL.
- Activo.
- Orden.

### 12.1 Crear aliado

1. Ir a `Revista LatinPyme > Aliados`.
2. Clic en `Nuevo`.
3. Completar nombre.
4. Subir logo.
5. Agregar URL si aplica.
6. Activar.
7. Guardar.
8. Revisar slider de aliados.

Recomendaciones:

- Usar logos en buena calidad.
- Preferir archivos PNG o SVG.
- Revisar que se vean bien sobre fondo claro.

---

## 13. Programacion anual

Ruta:

`Revista LatinPyme > Programacion anual`

Pagina publica:

`/revista/seccion/programacion-anual`

### 13.1 Crear evento

1. Ir a `Revista LatinPyme > Programacion anual`.
2. Clic en `Nuevo`.
3. Completar:
   - Nombre.
   - Tipo de evento.
   - Modalidad.
   - Fecha de inicio.
   - Fecha de fin si aplica.
   - Hora de inicio.
   - Hora de fin.
   - Zona horaria.
   - Lugar o enlace.
   - Descripcion.
   - Imagen si aplica.
   - Enlace de inscripcion.
   - Texto del boton.
   - Destacado si aplica.
   - Activo.
4. Guardar.

### 13.2 Tipos de evento

Usar:

- Charlas.
- Diplomados.
- Flashtraining.
- Foros.
- Curso 50 y 20 horas.

### 13.3 Validar evento en frontend

1. Abrir:

`/revista/seccion/programacion-anual?debug=assets`

2. Revisar que aparezca en el calendario.
3. Probar filtro por tipo.
4. Hacer clic en el dia.
5. Validar:
   - Nombre.
   - Tipo.
   - Fecha.
   - Hora.
   - Modalidad.
   - Lugar o enlace.
   - Inscripcion.
   - Google Calendar.
   - Outlook.
   - Apple Calendar / .ics.

---

## 14. Controles por nota individual

Ruta:

`Revista LatinPyme > Notas editoriales`

Esta pantalla permite configurar excepciones sobre notas especificas.

Campos posibles:

- Nota.
- Activo.
- Mostrar/ocultar sidebar.
- Mostrar/ocultar entrevistas.
- Mostrar/ocultar portafolio.
- Mostrar/ocultar aliados.
- Banner especifico de nota.
- Titulo SEO.
- Descripcion SEO.
- URL canonica.

Uso recomendado:

- Usar solo cuando una nota necesite tratamiento especial.
- Para la mayoria de notas, dejar que hereden la configuracion global o de seccion.

---

## 15. Website Builder

Ruta:

Abrir una pagina del sitio y hacer clic en `Editar`.

Grupo de snippets:

`LP Revista`

Snippets disponibles:

- LP Revista - Header Editorial.
- LP Revista - Hero Home Doble.
- LP Revista - Actualidad Destacada.
- LP Revista - Lo Mas Reciente.
- LP Revista - Grid de Cards de Articulos.
- LP Revista - Secciones Editoriales.
- LP Revista - Entrevistas.
- LP Revista - Especiales.
- LP Revista - Banner Publicitario Horizontal.
- LP Revista - Programacion anual.
- LP Revista - Novedades.
- LP Revista - Portafolio.
- LP Revista - Aliados.
- LP Revista - Footer Editorial.
- LP Revista - Footer con Publicidad.
- LP Revista - Hero Seccion.
- LP Revista - Listado de Articulos por Seccion.
- LP Revista - Sidebar Conferencia.
- LP Revista - Sidebar Encuesta.
- LP Revista - Sidebar Publicidad.
- LP Revista - Cabecera de Nota.
- LP Revista - Autor de Nota.
- LP Revista - Botones Compartir.
- LP Revista - Cuerpo Editorial.
- LP Revista - Cita Destacada.
- LP Revista - Imagen dentro del Articulo.
- LP Revista - Sidebar Nota.
- LP Revista - Articulos Relacionados.
- LP Revista - Portafolio Compacto.

### 15.1 Que debe hacer el editor en Builder

Puede:

- Arrastrar bloques ya disenados.
- Reordenar bloques.
- Probar una composicion visual.
- Editar textos simples dentro de snippets estaticos.

No debe:

- Cambiar HTML.
- Cambiar CSS.
- Crear disenos desde cero.
- Crear notas manuales como paginas.
- Romper clases del diseno.

### 15.2 Snippet de Programacion anual

El snippet `LP Revista - Programacion anual` muestra contenido dinamico.

Los eventos no se editan en el Builder.

Se editan en:

`Revista LatinPyme > Programacion anual`

---

## 16. Validacion en frontend

Cada vez que se publique o cambie contenido, revisar:

### 16.1 Home

- Header.
- Menu.
- Banners.
- Notas destacadas.
- Lo mas reciente.
- Entrevistas.
- Especiales.
- Publicidad.
- Portafolio.
- Aliados.
- Footer.

### 16.2 Seccion

- Hero de seccion.
- Listado de notas.
- Paginacion.
- Sidebar.
- Portafolio.
- Aliados.
- Footer.

### 16.3 Nota individual

- Titulo.
- Categoria.
- Imagen principal.
- Resumen.
- Autor.
- Fecha.
- Cuerpo.
- Botones compartir.
- Sidebar.
- Entrevistas relacionadas.
- Portafolio.
- Aliados.
- Footer.

### 16.4 Programacion anual

- Banner.
- Titulo.
- Filtros.
- Calendario.
- Drawer de detalle.
- Enlaces a calendarios externos.

---

## 17. Validacion en movil

Siempre revisar desde celular o modo responsive:

- No debe haber scroll horizontal.
- El menu debe abrir y cerrar.
- Los submenus deben abrir y cerrar.
- El texto no debe cortarse.
- Las imagenes deben cargar.
- El footer debe verse agrupado.
- Los botones deben ser faciles de tocar.
- Las cards deben apilarse correctamente.
- El calendario debe ser usable.

---

## 18. SEO en preproduccion

Mientras el sitio este en:

`revista.latinpyme.com`

mantener:

- Noindex activo.
- No enviar sitemap final.
- No cambiar DNS.
- No aplicar redirecciones 301 masivas.

### 18.1 Que hacer ahora

- Preparar inventario de URLs.
- Registrar URL antigua de WordPress.
- Registrar URL nueva sugerida en Odoo.
- Conservar slugs cuando sea posible.
- Revisar titulos SEO.
- Revisar descripciones SEO.
- Revisar imagenes principales.

### 18.2 Que hacer al final

Solo cuando el sitio este listo:

- Validar inventario SEO.
- Preparar redirecciones 301.
- Quitar noindex.
- Cambiar DNS.
- Validar Cloudflare.
- Enviar sitemap.
- Revisar Search Console.

---

## 19. Errores comunes y solucion

### La nota no aparece en la seccion

Posibles causas:

- No tiene etiqueta.
- Tiene etiqueta incorrecta.
- Esta en borrador.
- Pertenece a otro blog.

Solucion:

Revisar etiqueta, blog y estado publicado.

### La imagen no se ve

Posibles causas:

- Imagen no subida correctamente.
- Imagen privada.
- Imagen muy pesada.

Solucion:

Volver a subir imagen desde Odoo.

### El banner no aparece

Posibles causas:

- No esta activo.
- Tiene ubicacion incorrecta.
- Fecha de inicio/fin no aplica.
- No tiene imagen.

Solucion:

Revisar Publicidad, ubicacion, fechas y estado activo.

### Los links de redes sociales abren `#`

Posible causa:

La URL no esta configurada.

Solucion:

Ir a `Revista LatinPyme > Configuracion > Redes sociales` y completar URLs reales.

### El evento no aparece en calendario

Posibles causas:

- Evento inactivo.
- Fecha incorrecta.
- Sitio web incorrecto.
- Tipo de evento mal seleccionado.

Solucion:

Revisar `Revista LatinPyme > Programacion anual`.

---

## 20. Checklist para publicar una nota

Antes de publicar:

- [ ] Tiene titulo.
- [ ] Tiene resumen.
- [ ] Tiene imagen principal.
- [ ] Tiene etiqueta de seccion.
- [ ] Tiene autor correcto.
- [ ] Tiene fecha correcta.
- [ ] Tiene contenido revisado.
- [ ] Tiene SEO basico.
- [ ] Esta publicada.
- [ ] Aparece en la seccion correcta.
- [ ] Se ve bien en movil.

---

## 21. Checklist para configurar una seccion

- [ ] Nombre claro.
- [ ] Slug correcto.
- [ ] Etiqueta de Blog asociada.
- [ ] Activa.
- [ ] Orden correcto.
- [ ] Imagen de portada si aplica.
- [ ] Descripcion.
- [ ] SEO title.
- [ ] SEO description.
- [ ] Sidebar configurado.
- [ ] Portafolio configurado.
- [ ] Aliados configurados.
- [ ] Menu probado en desktop.
- [ ] Menu probado en movil.

---

## 22. Checklist para publicar un banner

- [ ] Nombre interno claro.
- [ ] Ubicacion correcta.
- [ ] Imagen cargada.
- [ ] URL correcta si aplica.
- [ ] Fecha de inicio correcta.
- [ ] Fecha de fin correcta.
- [ ] Activo.
- [ ] Revisado en desktop.
- [ ] Revisado en movil.

---

## 23. Checklist para programacion anual

- [ ] Evento activo.
- [ ] Tipo correcto.
- [ ] Modalidad correcta.
- [ ] Fecha correcta.
- [ ] Hora correcta.
- [ ] Zona horaria correcta.
- [ ] Lugar o enlace.
- [ ] Enlace de inscripcion.
- [ ] Google Calendar probado.
- [ ] Outlook probado.
- [ ] Apple Calendar / .ics probado.
- [ ] Vista movil revisada.

---

## 24. Recomendacion final para el equipo

El equipo editorial debe concentrarse en:

- Crear buenas notas.
- Asignar etiquetas correctamente.
- Usar imagenes de calidad.
- Mantener banners actualizados.
- Validar mobile antes de publicar.
- No tocar codigo ni estilos.

La estructura visual de la Revista LatinPyme ya esta preparada para que el contenido se alimente desde Odoo.

