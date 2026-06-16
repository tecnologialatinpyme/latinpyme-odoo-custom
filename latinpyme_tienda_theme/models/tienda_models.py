# -*- coding: utf-8 -*-

from urllib.parse import quote

from odoo import api, fields, models
from odoo.fields import Domain


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
    description = fields.Char(string="Descripcion")
    category_id = fields.Many2one(
        "product.public.category",
        string="Categoria de tienda",
        ondelete="restrict",
        help="Categoria publica de ecommerce usada para listar productos del carrusel.",
    )
    category_search_name = fields.Char(
        string="Buscar categoria por nombre",
        help="Fallback inicial mientras se asignan categorias publicas exactas.",
    )
    website_id = fields.Many2one("website", string="Sitio web", ondelete="cascade")
    product_ids = fields.Many2many(
        "product.template",
        string="Productos relacionados",
        compute="_compute_product_ids",
    )
    product_count = fields.Integer(string="Productos", compute="_compute_product_ids")

    @api.depends("category_id", "category_search_name", "website_id", "active")
    def _compute_product_ids(self):
        for carousel in self:
            products = carousel._get_related_products()
            carousel.product_ids = products
            carousel.product_count = len(products)

    @api.model
    def _base_product_domain(self, Product, website=None):
        if website and hasattr(website, "sale_product_domain"):
            domain = Domain(website.sale_product_domain())
        else:
            domain = Domain.TRUE
        if "active" in Product._fields:
            domain &= Domain("active", "=", True)
        if "sale_ok" in Product._fields:
            domain &= Domain("sale_ok", "=", True)
        if "is_published" in Product._fields:
            domain &= Domain("is_published", "=", True)
        elif "website_published" in Product._fields:
            domain &= Domain("website_published", "=", True)
        if "service_tracking" in Product._fields and hasattr(Product, "_get_saleable_tracking_types"):
            domain &= Domain("service_tracking", "in", Product._get_saleable_tracking_types())
        return domain

    @api.model
    def _product_order(self, Product):
        order_fields = []
        for field_name in ("website_sequence", "sequence", "name"):
            if field_name in Product._fields:
                order_fields.append("%s asc" % field_name)
        return ", ".join(order_fields) or "name asc"

    def _get_related_categories(self, website=None):
        self.ensure_one()
        Category = self.env["product.public.category"]
        domain = Domain.TRUE
        if website and hasattr(website, "website_domain"):
            domain &= Domain(website.website_domain())
        if self.category_id:
            return Category.search(domain & Domain("id", "child_of", self.category_id.id))

        search_name = (self.category_search_name or self.name or "").strip()
        if not search_name:
            return Category.browse()
        categories = Category.search(domain & Domain("name", "ilike", search_name))
        return Category.search(domain & Domain("id", "child_of", categories.ids)) if categories else categories

    def _get_related_products(self, website=None):
        self.ensure_one()
        Product = self.env["product.template"]
        domain_base = self._base_product_domain(Product, website=website)
        order = self._product_order(Product)
        search_name = (self.category_search_name or self.name or "").strip()

        categories = self._get_related_categories(website=website)
        if categories and "public_categ_ids" in Product._fields:
            products = Product.search(domain_base & Domain("public_categ_ids", "in", categories.ids), order=order)
            if products:
                return products

        if search_name and "categ_id" in Product._fields:
            internal_categories = self.env["product.category"].search([("name", "ilike", search_name)])
            if internal_categories:
                products = Product.search(domain_base & Domain("categ_id", "child_of", internal_categories.ids), order=order)
                if products:
                    return products

        if search_name:
            products = Product.search(domain_base & Domain("name", "ilike", search_name), order=order)
            if products:
                return products
        return Product.browse()

    def _category_url(self, website=None):
        self.ensure_one()
        category = self.category_id or self._get_related_categories(website=website)[:1]
        if category and "website_url" in category._fields and category.website_url:
            return category.website_url
        if category:
            return "/shop/category/%s" % category.id
        search_text = self.category_search_name or self.name
        return "/shop?search=%s" % quote(search_text or "")

    @api.model
    def _product_frontend_values(self, product, website=None):
        currency = self.env.company.currency_id
        if website and "currency_id" in website._fields and website.currency_id:
            currency = website.currency_id
        product_url = "/shop"
        if "website_url" in product._fields and product.website_url:
            product_url = product.website_url
        return {
            "name": product.name,
            "url": product_url,
            "image_url": "/web/image/product.template/%s/image_512" % product.id,
            "price": product.list_price if "list_price" in product._fields else False,
            "has_price": "list_price" in product._fields,
            "currency": currency,
        }

    @api.model
    def get_home_carousels(self, website=None):
        domain = [("active", "=", True)]
        if website:
            domain.extend(["|", ("website_id", "=", False), ("website_id", "=", website.id)])
        else:
            domain.append(("website_id", "=", False))

        carousels = []
        for carousel in self.search(domain, order="sequence, name"):
            products = carousel._get_related_products(website=website)
            if not products:
                continue
            carousels.append(
                {
                    "name": carousel.name,
                    "description": carousel.description,
                    "category_url": carousel._category_url(website=website),
                    "products": [
                        carousel._product_frontend_values(product, website=website)
                        for product in products
                    ],
                }
            )
        return carousels
