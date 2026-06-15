# -*- coding: utf-8 -*-

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
