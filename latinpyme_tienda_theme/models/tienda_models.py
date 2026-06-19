# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import ValidationError


_CATEGORY_URL_OVERRIDES = {
    5: "/shop/category/flashtraining-5",
    6: "/shop/category/talleres-6",
}

_CATEGORY_NAME_OVERRIDES = {
    5: "FlashTraining",
    6: "Talleres",
}


def _menu_item_display_name(item):
    category = item.product_public_category_id
    if item.item_type == "category" and category:
        return _CATEGORY_NAME_OVERRIDES.get(category.id, item.name)
    return item.name


class LatinpymeTiendaConfig(models.Model):
    _name = "latinpyme.tienda.config"
    _description = "Configuracion Tienda LatinPyme"
    _order = "website_id, id"

    name = fields.Char(string="Nombre", required=True, default="Tienda LatinPyme")
    website_id = fields.Many2one("website", string="Sitio web", ondelete="set null")
    production_domain = fields.Char(string="Dominio final", default="tienda.latinpyme.com")
    brand_label = fields.Char(string="Etiqueta de marca", default="Tienda")


class LatinpymeTiendaMenuItem(models.Model):
    _name = "latinpyme.tienda.menu.item"
    _description = "Item de menu Tienda LatinPyme"
    _order = "sequence, id"

    name = fields.Char(string="Nombre visible", required=True)
    sequence = fields.Integer(string="Orden", default=10)
    active = fields.Boolean(string="Activo", default=True)
    item_type = fields.Selection(
        [
            ("home", "Inicio"),
            ("category", "Categoria ecommerce"),
            ("group", "Grupo / dropdown"),
            ("url", "URL manual"),
        ],
        string="Tipo",
        required=True,
        default="category",
    )
    product_public_category_id = fields.Many2one(
        "product.public.category",
        string="Categoria ecommerce",
        ondelete="restrict",
    )
    parent_id = fields.Many2one(
        "latinpyme.tienda.menu.item",
        string="Padre / grupo",
        ondelete="cascade",
        index=True,
    )
    child_ids = fields.One2many("latinpyme.tienda.menu.item", "parent_id", string="Submenus")
    url = fields.Char(string="URL manual")
    computed_url = fields.Char(string="URL calculada", compute="_compute_computed_url")
    open_new_tab = fields.Boolean(string="Abrir en nueva pestaña")
    show_in_header = fields.Boolean(string="Mostrar en header", default=True)
    show_in_mobile = fields.Boolean(string="Mostrar en movil", default=True)
    css_class = fields.Char(string="Clase CSS opcional")
    website_id = fields.Many2one("website", string="Sitio web", ondelete="set null")

    @api.depends("item_type", "product_public_category_id", "url")
    def _compute_computed_url(self):
        for record in self:
            if record.item_type == "home":
                record.computed_url = "/"
            elif record.item_type == "category" and record.product_public_category_id:
                category = record.product_public_category_id
                category_url = _CATEGORY_URL_OVERRIDES.get(category.id)
                if not category_url:
                    category_url = category.website_url if "website_url" in category._fields else False
                record.computed_url = category_url or "/shop/category/%s" % category.id
            elif record.item_type == "url":
                record.computed_url = (record.url or "").strip()
            else:
                record.computed_url = False

    @api.constrains("item_type", "product_public_category_id", "url")
    def _check_required_target(self):
        for record in self:
            if record.item_type == "category" and not record.product_public_category_id:
                raise ValidationError("Los items de tipo categoria deben tener una categoria ecommerce.")
            if record.item_type == "url" and not (record.url or "").strip():
                raise ValidationError("Los items de tipo URL manual deben tener una URL.")

    @api.constrains("parent_id")
    def _check_parent_id(self):
        for record in self:
            current = record.parent_id
            depth = 0
            visited = self.browse()
            while current:
                if current == record or current in visited:
                    raise ValidationError("Un item de menu no puede ser padre de si mismo.")
                depth += 1
                if depth > 1:
                    raise ValidationError("El menu de tienda solo permite un nivel de submenu.")
                visited |= current
                current = current.parent_id

    @api.model
    def get_header_menu(self, website=None):
        domain = [("active", "=", True), ("show_in_header", "=", True)]
        if website:
            domain.extend(["|", ("website_id", "=", False), ("website_id", "=", website.id)])

        items = self.sudo().search(domain, order="sequence, id")
        if not items:
            return []

        def item_values(item):
            children = items.filtered(lambda child: child.parent_id == item)
            return {
                "name": _menu_item_display_name(item),
                "url": item.computed_url or "#",
                "item_type": item.item_type,
                "open_new_tab": item.open_new_tab,
                "show_in_mobile": item.show_in_mobile,
                "css_class": item.css_class or "",
                "children": [
                    {
                        "name": _menu_item_display_name(child),
                        "url": child.computed_url or "#",
                        "item_type": child.item_type,
                        "open_new_tab": child.open_new_tab,
                        "show_in_mobile": child.show_in_mobile,
                        "css_class": child.css_class or "",
                    }
                    for child in children
                ],
            }

        roots = items.filtered(lambda item: not item.parent_id)
        return [item_values(item) for item in roots]
