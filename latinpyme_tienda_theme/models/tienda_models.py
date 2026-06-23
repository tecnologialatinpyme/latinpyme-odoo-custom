# -*- coding: utf-8 -*-

import base64
from datetime import date
from pathlib import Path

from odoo import api, fields, models
from odoo.exceptions import ValidationError


_MODULE_ROOT = Path(__file__).resolve().parents[1]

_CATEGORY_URL_OVERRIDES = {
    5: "/shop/category/flashtraining-5",
    6: "/shop/category/talleres-6",
}

_CATEGORY_NAME_OVERRIDES = {
    1: "Cursos de Auditoría",
    2: "Cursos de Seguridad Vial",
    4: "Diplomados",
    5: "FlashTraining",
    6: "Talleres",
}

_CATEGORY_ICON_FILES = {
    1: "icon-auditoria.png",
    2: "icon-seguridad-vial.png",
    4: "icon-diplomado.png",
    5: "icon-flashtraining.png",
    6: "talleres-icon.png",
}

_CATEGORY_ICON_FALLBACKS = {
    category_id: "/latinpyme_tienda_theme/static/src/img/%s" % filename
    for category_id, filename in _CATEGORY_ICON_FILES.items()
}

FOOTER_LINK_GROUPS = [
    ("sections", "Secciones"),
    ("portfolio", "Portafolio"),
    ("legal", "Legal"),
]

FOOTER_COLUMN_TITLES = {
    "sections": "SECCIONES",
    "portfolio": "PORTAFOLIO",
    "legal": "LEGAL",
}


def _category_display_name(category):
    return _CATEGORY_NAME_OVERRIDES.get(category.id, category.name)


def _category_static_icon_binary(category_id):
    icon_file = _CATEGORY_ICON_FILES.get(category_id)
    if not icon_file:
        return False

    icon_path = _MODULE_ROOT / "static" / "src" / "img" / icon_file
    try:
        with icon_path.open("rb") as file:
            return base64.b64encode(file.read())
    except OSError:
        return False


def _binary_to_text(value):
    if isinstance(value, bytes):
        return value.decode("ascii")
    return value or ""


def _image_cache_key(record):
    date_value = record.write_date or record.create_date
    return date_value.strftime("%Y%m%d%H%M%S") if date_value else str(record.id)


def _record_image_url(record, field_name):
    return "/web/image/product.public.category/%s/%s?unique=%s" % (record.id, field_name, _image_cache_key(record))


def _category_icon_route(record):
    return "/tienda/category/%s/icon?unique=%s" % (record.id, _image_cache_key(record))


def _menu_item_display_name(item):
    category = item.product_public_category_id
    if item.item_type == "category" and category:
        return _category_display_name(category)
    return item.name


class ProductPublicCategory(models.Model):
    _inherit = "product.public.category"

    lp_tienda_display_name = fields.Char(
        string="Nombre Tienda",
        compute="_compute_lp_tienda_media",
        compute_sudo=True,
    )
    lp_tienda_icon = fields.Image(
        string="Icono Tienda",
        max_width=512,
        max_height=512,
        attachment=True,
        help="Icono administrable usado en carruseles, encabezados de categoria y navegacion visual de Tienda.",
    )
    lp_tienda_icon_effective = fields.Image(
        string="Icono administrable",
        compute="_compute_lp_tienda_media",
        inverse="_inverse_lp_tienda_icon_effective",
        compute_sudo=True,
        readonly=False,
        help="Muestra el icono subido; si no existe, usa el icono estatico incluido en el modulo. Al subir uno nuevo, queda guardado como icono personalizado de la categoria.",
    )
    lp_tienda_icon_url = fields.Char(
        string="URL icono activo",
        compute="_compute_lp_tienda_media",
        compute_sudo=True,
    )
    lp_tienda_static_icon_url = fields.Char(
        string="URL icono base",
        compute="_compute_lp_tienda_media",
        compute_sudo=True,
    )
    lp_tienda_cover_image = fields.Image(
        string="Imagen de portada Tienda",
        max_width=1920,
        max_height=1080,
        attachment=True,
        help="Imagen de portada disponible para futuras landings de categoria.",
    )
    lp_tienda_cover_image_url = fields.Char(
        string="URL portada Tienda",
        compute="_compute_lp_tienda_media",
        compute_sudo=True,
    )

    @api.depends("name", "lp_tienda_icon", "lp_tienda_cover_image", "write_date")
    def _compute_lp_tienda_media(self):
        for category in self:
            category.lp_tienda_display_name = _category_display_name(category)
            category.lp_tienda_static_icon_url = _CATEGORY_ICON_FALLBACKS.get(category.id, "")
            if category.lp_tienda_icon:
                category.lp_tienda_icon_effective = category.lp_tienda_icon
            else:
                category.lp_tienda_icon_effective = _category_static_icon_binary(category.id)

            category.lp_tienda_icon_url = (
                _category_icon_route(category)
                if category.lp_tienda_icon or category.lp_tienda_static_icon_url
                else ""
            )

            category.lp_tienda_cover_image_url = (
                _record_image_url(category, "lp_tienda_cover_image")
                if category.lp_tienda_cover_image
                else ""
            )

    def _inverse_lp_tienda_icon_effective(self):
        for category in self:
            effective_icon = category.lp_tienda_icon_effective
            if not effective_icon:
                category.lp_tienda_icon = False
                continue

            fallback_icon = _category_static_icon_binary(category.id)
            if _binary_to_text(effective_icon) == _binary_to_text(fallback_icon):
                category.lp_tienda_icon = False
            else:
                category.lp_tienda_icon = effective_icon


class LatinpymeTiendaConfig(models.Model):
    _name = "latinpyme.tienda.config"
    _description = "Configuracion Tienda LatinPyme"
    _order = "website_id, id"

    name = fields.Char(string="Nombre", required=True, default="Tienda LatinPyme")
    website_id = fields.Many2one("website", string="Sitio web", ondelete="set null")
    production_domain = fields.Char(string="Dominio final", default="tienda.latinpyme.com")
    brand_label = fields.Char(string="Etiqueta de marca", default="Tienda")

    @api.model
    def _home_menu_item(self):
        return {
            "name": "Inicio",
            "url": "/",
            "item_type": "home",
            "open_new_tab": False,
            "show_in_mobile": True,
            "css_class": "",
            "children": [],
        }

    @api.model
    def _fallback_main_menu(self):
        return [
            self._home_menu_item(),
            {
                "name": "Talleres",
                "url": "/shop/category/talleres-6",
                "item_type": "category",
                "open_new_tab": False,
                "show_in_mobile": True,
                "css_class": "",
                "children": [],
            },
            {
                "name": "Cursos",
                "url": "#",
                "item_type": "group",
                "open_new_tab": False,
                "show_in_mobile": True,
                "css_class": "",
                "children": [
                    {
                        "name": "Cursos de Auditoría",
                        "url": "/shop/category/1",
                        "item_type": "category",
                        "open_new_tab": False,
                        "show_in_mobile": True,
                        "css_class": "",
                    },
                    {
                        "name": "Cursos de Seguridad Vial",
                        "url": "/shop/category/2",
                        "item_type": "category",
                        "open_new_tab": False,
                        "show_in_mobile": True,
                        "css_class": "",
                    },
                ],
            },
            {
                "name": "Diplomados",
                "url": "/shop/category/4",
                "item_type": "category",
                "open_new_tab": False,
                "show_in_mobile": True,
                "css_class": "",
                "children": [],
            },
            {
                "name": "FlashTraining",
                "url": "/shop/category/flashtraining-5",
                "item_type": "category",
                "open_new_tab": False,
                "show_in_mobile": True,
                "css_class": "",
                "children": [],
            },
        ]

    @api.model
    def _ensure_home_menu_item(self, menu_items):
        has_home = any(item.get("item_type") == "home" or item.get("name") == "Inicio" for item in menu_items)
        return menu_items if has_home else [self._home_menu_item()] + menu_items

    @api.model
    def get_main_menu(self, website=None):
        menu_items = self.env["latinpyme.tienda.menu.item"].sudo().get_header_menu(website)
        return self._ensure_home_menu_item(menu_items or self._fallback_main_menu())

    @api.model
    def get_social_links(self):
        whatsapp_url = "https://wa.link/i0n10b"
        return [
            {
                "label": "Facebook",
                "href": "https://www.facebook.com/revistalatinpyme",
                "icon": "fa-facebook",
            },
            {
                "label": "LinkedIn",
                "href": "https://co.linkedin.com/company/latinpyme/",
                "icon": "fa-linkedin",
            },
            {
                "label": "Instagram",
                "href": "https://www.instagram.com/revistalatinpyme",
                "icon": "fa-instagram",
            },
            {
                "label": "YouTube",
                "href": "https://www.youtube.com/@revistalatinpyme",
                "icon": "fa-youtube-play",
            },
            {
                "label": "WhatsApp",
                "href": whatsapp_url,
                "icon": "fa-whatsapp",
                "variant": "whatsapp",
            },
        ]

    @api.model
    def _fallback_footer_columns(self):
        return [
            {
                "title": "SECCIONES",
                "links": [
                    {"label": "Cursos", "url": "/shop?search=cursos", "open_new_tab": False},
                    {"label": "Capacitación", "url": "/shop?search=capacitacion", "open_new_tab": False},
                    {"label": "Tecnología", "url": "/shop?search=tecnologia", "open_new_tab": False},
                    {"label": "Inteligencia artificial", "url": "/shop?search=inteligencia%20artificial", "open_new_tab": False},
                ],
            },
            {
                "title": "PORTAFOLIO",
                "links": [
                    {"label": "Soluciones", "url": "/shop?search=soluciones", "open_new_tab": False},
                    {"label": "Escuela", "url": "/shop?search=escuela", "open_new_tab": False},
                    {"label": "Eventos", "url": "/shop?search=eventos", "open_new_tab": False},
                    {"label": "Curso 50 y 20 horas", "url": "/shop?search=50%2020", "open_new_tab": False},
                ],
            },
            {
                "title": "LEGAL",
                "links": [
                    {"label": "Términos de Uso", "url": "/terms", "open_new_tab": False},
                    {"label": "Privacidad y datos", "url": "/terms", "open_new_tab": False},
                    {"label": "Aviso Legal", "url": "/terms", "open_new_tab": False},
                ],
            },
        ]

    @api.model
    def get_footer_columns(self, website=None):
        columns = self.env["latinpyme.tienda.footer.link"].sudo().get_footer_columns(website)
        if any(column.get("links") for column in columns):
            return columns
        return self._fallback_footer_columns()

    @api.model
    def get_layout_context(self, website=None):
        whatsapp_url = "https://wa.link/i0n10b"
        return {
            "current_year": date.today().year,
            "social_links": self.get_social_links(),
            "main_menu": self.get_main_menu(website),
            "footer_columns": self.get_footer_columns(website),
            "whatsapp_url": whatsapp_url,
        }

    @api.model
    def is_current_request_tienda_shell(self):
        from odoo.http import request

        website = getattr(request, "website", False)
        host = (request.httprequest.host or "").split(":", 1)[0].lower()
        website_domain = (getattr(website, "domain", "") or "").split(":", 1)[0].lower()
        website_name = (getattr(website, "name", "") or "").lower()
        is_tienda = host == "tienda.latinpyme.com" or website_domain == "tienda.latinpyme.com"
        is_tienda = is_tienda or ("tienda" in website_name and "latinpyme" in website_name)
        if not is_tienda:
            return False

        path = request.httprequest.path or "/"
        normalized_path = path.rstrip("/") or "/"
        if normalized_path in ("/", "/tienda"):
            return False

        blocked_prefixes = (
            "/web",
            "/odoo",
            "/payment",
            "/shop/cart",
            "/shop/checkout",
            "/shop/payment",
            "/shop/confirm_order",
        )
        return not any(path.startswith(prefix) for prefix in blocked_prefixes)

    @api.model
    def is_current_request_shop_catalog(self):
        from odoo.http import request

        path = (request.httprequest.path or "/").rstrip("/") or "/"
        return path == "/shop" or path == "/shop/category" or path.startswith("/shop/category/")

    @api.model
    def is_current_request_shop_product(self):
        from odoo.http import request

        path = (request.httprequest.path or "/").rstrip("/") or "/"
        if not path.startswith("/shop/"):
            return False
        blocked_prefixes = (
            "/shop/category",
            "/shop/cart",
            "/shop/checkout",
            "/shop/payment",
            "/shop/confirm_order",
        )
        return not any(path.startswith(prefix) for prefix in blocked_prefixes)


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


class LatinpymeTiendaFooterLink(models.Model):
    _name = "latinpyme.tienda.footer.link"
    _description = "Link del footer Tienda LatinPyme"
    _order = "sequence, group_key, name"

    name = fields.Char(string="Texto", required=True)
    url = fields.Char(string="URL", required=True, default="#")
    group_key = fields.Selection(FOOTER_LINK_GROUPS, string="Grupo", required=True, default="sections", index=True)
    active = fields.Boolean(string="Activo", default=True)
    sequence = fields.Integer(string="Orden", default=10)
    open_new_tab = fields.Boolean(string="Abrir en nueva pestaña")
    website_id = fields.Many2one("website", string="Sitio web", ondelete="cascade")

    @api.model
    def get_active_links(self, group_key, website=None):
        domain = [("active", "=", True), ("group_key", "=", group_key)]
        if website:
            website_links = self.sudo().search(domain + [("website_id", "=", website.id)], order="sequence, name")
            if website_links:
                return website_links
        return self.sudo().search(domain + [("website_id", "=", False)], order="sequence, name")

    @api.model
    def get_footer_columns(self, website=None):
        columns = []
        for group_key, _label in FOOTER_LINK_GROUPS:
            links = self.get_active_links(group_key, website)
            columns.append(
                {
                    "key": group_key,
                    "title": FOOTER_COLUMN_TITLES[group_key],
                    "links": [
                        {
                            "label": link.name,
                            "url": link.url,
                            "open_new_tab": link.open_new_tab,
                        }
                        for link in links
                    ],
                }
            )
        return columns
