# -*- coding: utf-8 -*-

{
    "name": "Tienda LatinPyme",
    "version": "19.0.1.4.0",
    "category": "Website/eCommerce",
    "summary": "Administracion minima de Tienda LatinPyme",
    "description": """
Base visual y acceso backend minimo para Tienda LatinPyme en Odoo 19.

Esta fase usa categorias publicas nativas de ecommerce como base administrable
para futuros carruseles, sin crear modelos ni tocar el home.
    """,
    "author": "LatinPyme",
    "website": "https://tienda.latinpyme.com",
    "license": "LGPL-3",
    "depends": [
        "website",
        "website_sale",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/tienda_config.xml",
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
