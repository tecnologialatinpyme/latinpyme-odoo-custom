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
        "views/assets.xml",
        "views/snippet_templates.xml",
        "views/snippets.xml",
        "views/home_templates.xml",
        "views/section_templates.xml",
        "views/blog_post_templates.xml",
    ],
    "installable": True,
    "application": False,
}
