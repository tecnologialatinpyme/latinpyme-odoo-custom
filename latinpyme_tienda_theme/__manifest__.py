# -*- coding: utf-8 -*-

{
    "name": "Tienda LatinPyme Theme",
    "version": "19.0.1.0.0",
    "category": "Website/eCommerce",
    "summary": "Base visual instalable para la futura tienda LatinPyme sobre Odoo Website Sale",
    "description": """
Tema base para preparar la futura experiencia de Tienda LatinPyme en Odoo 19.

Esta primera version instalable solo registra una base QWeb segura y assets
minimos para iniciar el desarrollo visual en fases posteriores.
    """,
    "author": "LatinPyme",
    "website": "https://latinpyme.com",
    "license": "LGPL-3",
    "depends": [
        "website",
        "website_sale",
    ],
    "data": [
        "views/tienda_templates.xml",
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
    "application": False,
}
