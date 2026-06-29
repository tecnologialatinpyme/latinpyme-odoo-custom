# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


BANNER_PLACEMENTS = [
    ("home_hero", "Home banner principal"),
    ("home_horizontal", "Home publicidad horizontal"),
    ("home_side", "Home publicidad lateral"),
]


class LatinpymeTiendaConfig(models.Model):
    _name = "latinpyme.tienda.config"
    _description = "Configuracion Tienda LatinPyme"
    _order = "website_id, id"

    name = fields.Char(string="Nombre", required=True, default="Tienda LatinPyme")
    website_id = fields.Many2one("website", string="Sitio web", ondelete="set null")
    production_domain = fields.Char(string="Dominio final", default="tienda.latinpyme.com")
    brand_label = fields.Char(string="Etiqueta de marca", default="Tienda")


class LatinpymeTiendaBanner(models.Model):
    _name = "latinpyme.tienda.banner"
    _description = "Publicidad Tienda LatinPyme"
    _order = "sequence, name"

    name = fields.Char(string="Nombre", required=True)
    placement = fields.Selection(
        BANNER_PLACEMENTS,
        string="Ubicacion",
        required=True,
        default="home_hero",
    )
    image = fields.Image(string="Imagen", max_width=1920, max_height=1080)
    title = fields.Char(string="Titulo")
    text = fields.Text(string="Texto")
    button_label = fields.Char(string="Texto del boton", default="Ver mas")
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
    def _active_domain(self, placement, website=None):
        today = fields.Date.context_today(self)
        domain = [
            ("active", "=", True),
            ("placement", "=", placement),
            "|",
            ("date_start", "=", False),
            ("date_start", "<=", today),
            "|",
            ("date_end", "=", False),
            ("date_end", ">=", today),
        ]
        if website:
            domain.append(("website_id", "in", [False, website.id]))
        return domain

    @api.model
    def get_active_banners(self, placement, website=None, limit=1):
        return self.search(self._active_domain(placement, website=website), order="sequence, id", limit=limit)

    @api.model
    def get_active_banner(self, placement, website=None):
        if website:
            banner = self.search(
                self._active_domain(placement, website=False) + [("website_id", "=", website.id)],
                order="sequence, id",
                limit=1,
            )
            if banner:
                return banner
        return self.search(
            self._active_domain(placement, website=False) + [("website_id", "=", False)],
            order="sequence, id",
            limit=1,
        )
