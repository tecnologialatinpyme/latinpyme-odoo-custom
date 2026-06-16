# -*- coding: utf-8 -*-

{
    "name": "Tienda LatinPyme",
    "version": "19.0.1.5.1",
    "category": "Website/eCommerce",
    "summary": "Administracion personalizada de Tienda LatinPyme",
    "description": """
Aplicacion administrable para la experiencia de Tienda LatinPyme en Odoo 19.

Incluye configuracion de header, menu, footer, banners y home de tienda,
manteniendo separacion con Revista LatinPyme y sin tocar checkout ni pagos.
    """,
    "author": "LatinPyme",
    "website": "https://latinpyme.com",
    "license": "LGPL-3",
    "depends": [
        "website",
        "website_sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/tienda_defaults.xml",
        "views/backend_views.xml",
        "views/tienda_templates.xml",
        "views/shop_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "latinpyme_tienda_theme/static/src/scss/tienda.scss",
        ],
        "web.assets_frontend_lazy": [
            "latinpyme_tienda_theme/static/src/js/address_guard.js",
        ],
    },
    "installable": True,
    "application": True,
}
