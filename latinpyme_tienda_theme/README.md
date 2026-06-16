# Tienda LatinPyme Theme

Modulo base para la futura experiencia **Tienda LatinPyme Theme** sobre Odoo 19.

El objetivo del modulo sera construir una experiencia premium de tienda sobre Odoo Website y eCommerce, orientada a:

- `website_sale`
- eCommerce
- productos
- cursos
- soluciones empresariales
- carrito
- checkout
- Mercado Pago
- diseno premium de tienda

## Estado actual

**Fase 3 / pagina dedicada de tienda.**

El modulo ya cuenta con un esqueleto instalable, un primer bloque visual reutilizable y una pagina dedicada `/tienda` para montarlo sin alterar `/shop`.

## Que incluye

- `__manifest__.py` con dependencias controladas.
- Dependencias base: `website` y `website_sale`.
- Registro de assets frontend desde el manifest.
- Template QWeb base scoped para futuras personalizaciones.
- Template QWeb `lp_tienda_storefront_intro` como primer bloque visual de tienda.
- Ruta publica `/tienda` que renderiza el bloque mediante un controlador propio.
- SCSS minimo bajo el scope `.lp-tienda`.
- Documentacion base y carpeta de referencias visuales.

## Que no incluye todavia

- No implementa paginas completas de tienda.
- No inserta automaticamente el bloque en `/shop`.
- No modifica templates de `website_sale`.
- No modifica carrito.
- No modifica checkout.
- No modifica Mercado Pago ni flujos de pago.
- No crea snippets avanzados.
- No agrega controladores ni modelos propios.

## Alcance de esta fase

Esta fase monta el bloque en una pagina dedicada y reversible. La insercion en `/shop`, si se decide mas adelante, debera hacerse mediante una herencia controlada y documentada.
