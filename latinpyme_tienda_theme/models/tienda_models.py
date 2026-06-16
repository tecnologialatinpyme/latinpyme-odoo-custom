# -*- coding: utf-8 -*-

from urllib.parse import quote

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.http import request as http_request


FOOTER_LINK_GROUPS = [
    ("sections", "Secciones"),
    ("portfolio", "Portafolio"),
    ("legal", "Legal"),
]

BANNER_PLACEMENTS = [
    ("hero", "Home principal"),
    ("home_horizontal", "Home publicidad horizontal"),
    ("tech_sidebar", "Home tecnologia lateral"),
    ("footer", "Footer"),
]

DEFAULT_PRODUCT_CAROUSELS = [
    {
        "sequence": 10,
        "name": "Talleres",
        "description": "Formacion practica para equipos y empresarios.",
        "search_name": "Taller",
    },
    {
        "sequence": 20,
        "name": "Cursos de Auditoría",
        "description": "Cursos especializados en auditoria y gestion.",
        "search_name": "Auditor",
    },
    {
        "sequence": 30,
        "name": "Cursos de Seguridad Vial",
        "description": "Capacitaciones enfocadas en prevencion y seguridad vial.",
        "search_name": "Seguridad Vial",
    },
    {
        "sequence": 40,
        "name": "Diplomados",
        "description": "Programas especializados de mayor profundidad.",
        "search_name": "Diplomado",
    },
    {
        "sequence": 50,
        "name": "FlashTraining",
        "description": "Capacitaciones cortas para actualizacion rapida.",
        "search_name": "FlashTraining",
    },
    {
        "sequence": 60,
        "name": "Cursos Gratis",
        "description": "Contenidos gratuitos disponibles en la tienda.",
        "search_name": "Gratis",
    },
]


def _current_website():
    try:
        return getattr(http_request, "website", False)
    except Exception:
        return False


class LatinpymeTiendaConfig(models.Model):
    _name = "latinpyme.tienda.config"
    _description = "Configuracion Tienda LatinPyme"
    _order = "website_id, id"

    name = fields.Char(string="Nombre", required=True, default="Tienda LatinPyme")
    website_id = fields.Many2one("website", string="Sitio web", ondelete="cascade")
    production_domain = fields.Char(string="Dominio final", default="tienda.latinpyme.com")
    brand_label = fields.Char(string="Etiqueta marca", default="Tienda")
    brand_name = fields.Char(string="Nombre marca", default="LatinPyme")
    anniversary_title = fields.Char(string="Titulo aniversario", default="25 anos")
    anniversary_text = fields.Char(
        string="Texto aniversario",
        default="Impulsando empresarios en Latinoamerica",
    )
    search_placeholder = fields.Char(
        string="Placeholder buscador",
        default="Buscar soluciones, cursos, herramientas y mas",
    )
    footer_summary = fields.Char(
        string="Texto footer",
        default="Soluciones, capacitacion y herramientas para pymes en Latinoamerica.",
    )
    footer_text = fields.Char(
        string="Texto legal footer",
        default="(c) 2026 Tienda LatinPyme - Todos los derechos reservados",
    )
    phone = fields.Char(string="Telefono", default="+57 3162336085")
    city = fields.Char(string="Ciudad", default="Bogota, Colombia")
    facebook_url = fields.Char(string="URL Facebook", default="https://www.facebook.com/revistalatinpyme")
    linkedin_url = fields.Char(string="URL LinkedIn", default="https://co.linkedin.com/company/latinpyme/")
    instagram_url = fields.Char(string="URL Instagram", default="https://www.instagram.com/revistalatinpyme")
    youtube_url = fields.Char(string="URL YouTube", default="https://www.youtube.com/@revistalatinpyme")
    whatsapp_url = fields.Char(string="URL WhatsApp", default="https://wa.link/i0n10b")

    @api.model
    def _domain_to_host(self, value):
        value = (value or "").strip().lower()
        if not value:
            return False
        value = value.replace("https://", "").replace("http://", "")
        value = value.split("/", 1)[0]
        return value.split(":", 1)[0]

    @api.model
    def get_active_config(self, website=None):
        website = website or _current_website()
        if website:
            config = self.search([("website_id", "=", website.id)], limit=1)
            if config:
                return config

        request_host = False
        try:
            request_host = getattr(http_request, "httprequest", False).host
        except Exception:
            request_host = False
        request_host = self._domain_to_host(request_host)

        if request_host:
            configs = self.search([])
            for config in configs:
                website_host = (
                    self._domain_to_host(config.website_id.domain)
                    if config.website_id and "domain" in config.website_id._fields
                    else False
                )
                if request_host in (website_host, self._domain_to_host(config.production_domain)):
                    return config

        return self.search([("website_id", "=", False)], limit=1)

    def is_tienda_host(self, host):
        self.ensure_one()
        host = self._domain_to_host(host)
        website_host = (
            self._domain_to_host(self.website_id.domain)
            if self.website_id and "domain" in self.website_id._fields
            else False
        )
        return host in (self._domain_to_host(self.production_domain), website_host)

    def social_link_values(self):
        if not self:
            return []
        self.ensure_one()
        links = [
            ("Facebook", self.facebook_url, "fa-facebook", False),
            ("LinkedIn", self.linkedin_url, "fa-linkedin", False),
            ("Instagram", self.instagram_url, "fa-instagram", False),
            ("YouTube", self.youtube_url, "fa-youtube-play", False),
            ("WhatsApp", self.whatsapp_url, "fa-whatsapp", "whatsapp"),
        ]
        return [
            {
                "label": label,
                "href": href,
                "icon": icon,
                "variant": variant,
            }
            for label, href, icon, variant in links
            if href and href != "#"
        ]


class LatinpymeTiendaMenuLink(models.Model):
    _name = "latinpyme.tienda.menu.link"
    _description = "Link del menu Tienda LatinPyme"
    _order = "sequence, name"

    name = fields.Char(string="Texto", required=True)
    url = fields.Char(string="URL", required=True, default="#")
    active = fields.Boolean(string="Activo", default=True)
    sequence = fields.Integer(string="Orden", default=10)
    open_new_tab = fields.Boolean(string="Abrir en nueva pestana")
    website_id = fields.Many2one("website", string="Sitio web", ondelete="cascade")

    @api.model
    def get_active_links(self, website=None):
        website = website or _current_website()
        domain = [("active", "=", True)]
        if website:
            website_links = self.search(domain + [("website_id", "=", website.id)], order="sequence, name")
            if website_links:
                return website_links
        return self.search(domain + [("website_id", "=", False)], order="sequence, name")


class LatinpymeTiendaFooterLink(models.Model):
    _name = "latinpyme.tienda.footer.link"
    _description = "Link del footer Tienda LatinPyme"
    _order = "sequence, group_key, name"

    name = fields.Char(string="Texto", required=True)
    url = fields.Char(string="URL", required=True, default="#")
    group_key = fields.Selection(FOOTER_LINK_GROUPS, string="Grupo", required=True, default="sections", index=True)
    active = fields.Boolean(string="Activo", default=True)
    sequence = fields.Integer(string="Orden", default=10)
    open_new_tab = fields.Boolean(string="Abrir en nueva pestana")
    website_id = fields.Many2one("website", string="Sitio web", ondelete="cascade")

    @api.model
    def get_active_links(self, group_key, website=None):
        website = website or _current_website()
        domain = [("active", "=", True), ("group_key", "=", group_key)]
        if website:
            website_links = self.search(domain + [("website_id", "=", website.id)], order="sequence, name")
            if website_links:
                return website_links
        return self.search(domain + [("website_id", "=", False)], order="sequence, name")


class LatinpymeTiendaBanner(models.Model):
    _name = "latinpyme.tienda.banner"
    _description = "Banner Tienda LatinPyme"
    _order = "sequence, name"

    name = fields.Char(string="Nombre", required=True)
    placement = fields.Selection(BANNER_PLACEMENTS, string="Ubicacion", required=True, default="hero")
    image = fields.Image(string="Imagen", max_width=1920, max_height=1080)
    alt_text = fields.Char(string="Texto alternativo")
    url = fields.Char(string="URL", default="/shop")
    active = fields.Boolean(string="Activo", default=True)
    sequence = fields.Integer(string="Orden", default=10)
    date_start = fields.Date(string="Fecha de inicio")
    date_end = fields.Date(string="Fecha de fin")
    website_id = fields.Many2one("website", string="Sitio web", ondelete="cascade")

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for record in self:
            if record.date_start and record.date_end and record.date_start > record.date_end:
                raise ValidationError("La fecha de inicio no puede ser posterior a la fecha final.")

    @api.model
    def _active_domain(self, placement):
        today = fields.Date.context_today(self)
        return [
            ("active", "=", True),
            ("placement", "=", placement),
            "|",
            ("date_start", "=", False),
            ("date_start", "<=", today),
            "|",
            ("date_end", "=", False),
            ("date_end", ">=", today),
        ]

    @api.model
    def get_active_banners(self, placement, website=None, limit=1):
        website = website or _current_website()
        domain = self._active_domain(placement)
        if website:
            website_banners = self.search(domain + [("website_id", "=", website.id)], order="sequence, id", limit=limit)
            if website_banners:
                return website_banners
        return self.search(domain + [("website_id", "=", False)], order="sequence, id", limit=limit)

    @api.model
    def get_active_banner(self, placement, website=None):
        return self.get_active_banners(placement, website=website, limit=1)

    def image_src(self):
        self.ensure_one()
        if not self.image:
            return ""
        return "/latinpyme-tienda/media/banner/%s/image" % self.id


class LatinpymeTiendaProductCarousel(models.Model):
    _name = "latinpyme.tienda.product.carousel"
    _description = "Carrusel de productos Tienda LatinPyme"
    _order = "sequence, name"

    name = fields.Char(string="Nombre", required=True)
    active = fields.Boolean(string="Activo", default=True)
    sequence = fields.Integer(string="Orden", default=10)
    description = fields.Char(string="Descripcion")
    category_id = fields.Many2one(
        "product.public.category",
        string="Categoria de tienda",
        ondelete="restrict",
        help="Categoria publica de ecommerce usada para listar productos del carrusel.",
    )
    internal_category_id = fields.Many2one(
        "product.category",
        string="Categoria interna",
        ondelete="restrict",
        help="Fallback opcional si los productos todavia no tienen categoria publica de ecommerce.",
    )
    category_search_name = fields.Char(
        string="Buscar categoria por nombre",
        help="Fallback para datos iniciales: si no hay categoria asignada, se buscan categorias publicas por este texto.",
    )
    website_id = fields.Many2one("website", string="Sitio web", ondelete="cascade")
    product_ids = fields.Many2many(
        "product.template",
        compute="_compute_product_ids",
        string="Productos relacionados",
    )
    product_count = fields.Integer(string="Productos", compute="_compute_product_ids")

    @api.depends("category_id", "internal_category_id", "category_search_name", "website_id")
    def _compute_product_ids(self):
        for carousel in self:
            products = carousel._get_related_products()
            carousel.product_ids = products
            carousel.product_count = len(products)

    def _get_related_categories(self):
        self.ensure_one()
        Category = self.env["product.public.category"].sudo()
        if self.category_id:
            return self.category_id

        search_name = (self.category_search_name or "").strip()
        if not search_name:
            return Category.browse()
        return Category.search([("name", "ilike", search_name)])

    def _get_related_internal_categories(self, search_name=None):
        self.ensure_one()
        Category = self.env["product.category"].sudo()
        if self.internal_category_id:
            return self.internal_category_id

        search_name = (search_name or self.category_search_name or "").strip()
        if not search_name:
            return Category.browse()
        return Category.search([("name", "ilike", search_name)])

    def _base_product_domain(self, Product, website=None):
        domain = []
        if "active" in Product._fields:
            domain.append(("active", "=", True))
        if "sale_ok" in Product._fields:
            domain.append(("sale_ok", "=", True))
        if "is_published" in Product._fields:
            domain.append(("is_published", "=", True))
        elif "website_published" in Product._fields:
            domain.append(("website_published", "=", True))
        if website and "website_id" in Product._fields:
            domain.extend(["|", ("website_id", "=", False), ("website_id", "=", website.id)])
        return domain

    @api.model
    def _product_order(self, Product):
        order_fields = []
        for field_name in ("website_sequence", "sequence", "name"):
            if field_name in Product._fields:
                order_fields.append("%s asc" % field_name)
        return ", ".join(order_fields) or "name asc"

    def _get_related_products(self, website=None, search_name=None):
        self.ensure_one()
        Product = self.env["product.template"].sudo()
        Category = self.env["product.public.category"].sudo()
        domain_base = self._base_product_domain(Product, website=website)
        order = self._product_order(Product)

        categories = self._get_related_categories()
        search_name = (search_name or self.category_search_name or self.name or "").strip()
        category_ids = Category.search([("id", "child_of", categories.ids)]).ids
        if category_ids:
            products = Product.search(domain_base + [("public_categ_ids", "in", category_ids)], order=order)
            if products:
                return products

        internal_categories = self._get_related_internal_categories(search_name=search_name)
        if internal_categories and "categ_id" in Product._fields:
            products = Product.search(domain_base + [("categ_id", "child_of", internal_categories.ids)], order=order)
            if products:
                return products

        if search_name:
            products = Product.search(domain_base + [("name", "ilike", search_name)], order=order)
            if products:
                return products
        return Product.browse()

    @api.model
    def _get_products_by_search_name(self, search_name, website=None):
        search_name = (search_name or "").strip()
        Product = self.env["product.template"].sudo()
        PublicCategory = self.env["product.public.category"].sudo()
        InternalCategory = self.env["product.category"].sudo()
        domain_base = self._base_product_domain(Product, website=website)
        order = self._product_order(Product)
        if not search_name:
            return Product.browse()

        public_categories = PublicCategory.search([("name", "ilike", search_name)])
        public_category_ids = PublicCategory.search([("id", "child_of", public_categories.ids)]).ids
        if public_category_ids:
            products = Product.search(domain_base + [("public_categ_ids", "in", public_category_ids)], order=order)
            if products:
                return products

        internal_categories = InternalCategory.search([("name", "ilike", search_name)])
        if internal_categories and "categ_id" in Product._fields:
            products = Product.search(domain_base + [("categ_id", "child_of", internal_categories.ids)], order=order)
            if products:
                return products

        return Product.search(domain_base + [("name", "ilike", search_name)], order=order)

    def _category_url(self):
        self.ensure_one()
        category = self.category_id or self._get_related_categories()[:1]
        if category and "website_url" in category._fields and category.website_url:
            return category.website_url
        search_text = self.category_search_name or self.name
        return "/shop?search=%s" % quote(search_text)

    @api.model
    def _product_frontend_values(self, product, website=None):
        currency = self.env.company.currency_id
        if website and "currency_id" in website._fields and website.currency_id:
            currency = website.currency_id
        product_url = "/shop"
        if "website_url" in product._fields and product.website_url:
            product_url = product.website_url
        category_label = ""
        if "public_categ_ids" in product._fields and product.public_categ_ids:
            category_label = product.public_categ_ids[:1].name
        return {
            "name": product.name,
            "url": product_url,
            "image_url": "/web/image/product.template/%s/image_512" % product.id,
            "price": product.list_price if "list_price" in product._fields else False,
            "currency": currency,
            "category_label": category_label,
        }

    @api.model
    def get_home_carousels(self, website=None):
        domain = [("active", "=", True)]
        if website:
            domain.extend(["|", ("website_id", "=", False), ("website_id", "=", website.id)])
        else:
            domain.append(("website_id", "=", False))

        values = []
        for carousel in self.search(domain, order="sequence, name"):
            products = carousel._get_related_products(website)
            if not products:
                continue
            values.append(
                {
                    "name": carousel.name,
                    "description": carousel.description,
                    "category_url": carousel._category_url(),
                    "products": [
                        carousel._product_frontend_values(product, website=website)
                        for product in products
                    ],
                }
            )
        if values:
            return values

        for spec in DEFAULT_PRODUCT_CAROUSELS:
            products = self._get_products_by_search_name(spec["search_name"], website=website)
            if not products:
                continue
            values.append(
                {
                    "name": spec["name"],
                    "description": spec["description"],
                    "category_url": "/shop?search=%s" % quote(spec["search_name"]),
                    "products": [
                        self._product_frontend_values(product, website=website)
                        for product in products
                    ],
                }
            )
        return values
