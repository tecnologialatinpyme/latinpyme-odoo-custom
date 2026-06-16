# -*- coding: utf-8 -*-

from odoo import fields, models


class LatinpymeTiendaConfig(models.Model):
    _name = "latinpyme.tienda.config"
    _description = "Configuracion Tienda LatinPyme"
    _order = "website_id, id"

    name = fields.Char(string="Nombre", required=True, default="Tienda LatinPyme")
    website_id = fields.Many2one("website", string="Sitio web", ondelete="set null")
    production_domain = fields.Char(string="Dominio final", default="tienda.latinpyme.com")
    brand_label = fields.Char(string="Etiqueta de marca", default="Tienda")


class LatinpymeTiendaProductCarousel(models.Model):
    _name = "latinpyme.tienda.product.carousel"
    _description = "Carrusel de productos Tienda LatinPyme"
    _order = "sequence, name"

    name = fields.Char(string="Nombre", required=True)
    active = fields.Boolean(string="Activo", default=True)
    sequence = fields.Integer(string="Secuencia", default=10)
    website_id = fields.Many2one("website", string="Sitio web", ondelete="set null")
    category_id = fields.Many2one(
        "product.public.category",
        string="Categoria de tienda",
        ondelete="restrict",
        help="Categoria publica de ecommerce usada para alimentar el carrusel.",
    )
    description = fields.Char(string="Descripcion")
    product_limit = fields.Integer(string="Limite de productos", default=12)
