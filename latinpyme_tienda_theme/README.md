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

**Fase 1 / modulo instalable minimo.**

El modulo ya cuenta con un esqueleto instalable seguro para iniciar el desarrollo visual en fases posteriores.

## Que incluye

- `__manifest__.py` con dependencias controladas.
- Dependencias base: `website` y `website_sale`.
- Registro de assets frontend desde el manifest.
- Template QWeb base scoped para futuras personalizaciones.
- SCSS minimo bajo el scope `.lp-tienda`.
- Documentacion base y carpeta de referencias visuales.

## Que no incluye todavia

- No implementa paginas completas de tienda.
- No modifica templates de `website_sale`.
- No modifica carrito.
- No modifica checkout.
- No modifica Mercado Pago ni flujos de pago.
- No crea snippets avanzados.
- No agrega controladores ni modelos propios.

## Alcance de esta fase

Esta fase deja el modulo listo para instalarse y para iniciar, en Fase 2, el trabajo visual de tienda con cambios pequenos, medibles y seguros.
