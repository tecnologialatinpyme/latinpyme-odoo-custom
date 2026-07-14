# -*- coding: utf-8 -*-

{
    "name": "Tienda LatinPyme",
    "version": "19.0.1.7.2",
    "category": "Website/eCommerce",
    "summary": "Administracion minima de Tienda LatinPyme",
    "description": """
Base visual y acceso backend minimo para Tienda LatinPyme en Odoo 19.

Esta fase conecta el home a categorias publicas nativas de ecommerce para
mostrar carruseles de productos sin crear modelos nuevos.
    """,
    "author": "LatinPyme",
    "website": "https://tienda.latinpyme.com",
    "license": "LGPL-3",
    "depends": [
        "website",
        "website_sale",
        "account",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/tienda_config.xml",
        "data/tienda_home_blocks.xml",
        "data/res_company_branding.xml",
        "views/backend_views.xml",
        "views/tienda_templates.xml",
        "views/shop_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "latinpyme_tienda_theme/static/src/scss/tienda.scss",
            "latinpyme_tienda_theme/static/src/js/product_terms_link.js",
            "latinpyme_tienda_theme/static/src/js/product_cupos.js",
            "latinpyme_tienda_theme/static/src/js/mobile_nav.js",
        ],
        "web.assets_frontend_lazy": [
            "latinpyme_tienda_theme/static/src/js/address_guard.js",
            "latinpyme_tienda_theme/static/src/js/quick_reorder_guard.js",
        ],
    },
    "installable": True,
    "application": True,
}
