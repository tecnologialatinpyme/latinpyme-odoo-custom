# -*- coding: utf-8 -*-

{
    "name": "Revista LatinPyme Theme",
    "version": "19.0.1.0.0",
    "category": "Website",
    "summary": "Tema editorial administrable para Revista LatinPyme sobre Odoo Website y Blog",
    "description": """
Revista digital administrable para LatinPyme.

Convierte Odoo Website + Odoo Blog en una experiencia editorial con home,
secciones por etiqueta, snippets reutilizables y personalizacion visual segura
de publicaciones de Blog.
    """,
    "author": "LatinPyme",
    "website": "https://latinpyme.com",
    "license": "LGPL-3",
    "depends": [
        "website",
        "website_blog",
    ],
    "data": [
        # Odoo 19 loads frontend assets from the manifest.
        "security/ir.model.access.csv",
        "data/revista_defaults.xml",
        "views/backend_views.xml",
        "views/layout_templates.xml",
        "views/snippet_templates.xml",
        "views/snippets.xml",
        "views/home_templates.xml",
        "views/section_templates.xml",
        "views/blog_post_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "latinpyme_revista_theme/static/src/scss/revista.scss",
            "latinpyme_revista_theme/static/src/js/program_calendar.js",
            "latinpyme_revista_theme/static/src/js/mobile_nav.js",
            "latinpyme_revista_theme/static/src/js/mobile_footer.js",
            "latinpyme_revista_theme/static/src/js/revista_analytics_events.js",
            "latinpyme_revista_theme/static/src/js/poll_vote.js",
        ],
    },
    "installable": True,
    "application": False,
}
