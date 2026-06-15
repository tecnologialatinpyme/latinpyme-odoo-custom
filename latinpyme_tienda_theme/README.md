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

**Fase 4 / home administrable de tienda.**

El modulo ya cuenta con home publico en `/`, backend administrable para header, menu, footer y banners, y estilos frontend acotados sin alterar checkout, pagos ni productos.

## Que incluye

- `__manifest__.py` con dependencias controladas.
- Dependencias base: `website` y `website_sale`.
- Registro de assets frontend desde el manifest.
- Templates QWeb scoped para home, header, menu, footer y banners de Tienda.
- Ruta publica `/` para el home de `tienda.latinpyme.com`.
- Redireccion de compatibilidad desde `/tienda` hacia `/` solo en el website de Tienda.
- Modelos backend para configuracion, menu, footer y banners.
- SCSS minimo bajo el scope `.lp-tienda`.
- Documentacion base y carpeta de referencias visuales.

## Que no incluye todavia

- No inserta automaticamente el bloque en `/shop`.
- No modifica carrito.
- No modifica checkout.
- No modifica Mercado Pago ni flujos de pago.
- No modifica productos reales, precios, categorias ni `website_id`.

## Alcance de esta fase

Esta fase mantiene el home de Tienda separado de Revista y de `/shop`. Las imagenes de publicidad se administran como banners de imagen desde backend.
