# -*- coding: utf-8 -*-

import base64
import logging
from pathlib import Path

from odoo import fields, http
from odoo.addons.account.controllers.terms import TermsController
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.addons.website.controllers.main import Website
from odoo.http import request


_logger = logging.getLogger(__name__)
_MODULE_ROOT = Path(__file__).resolve().parents[1]
_STATIC_ICON_PREFIX = "/latinpyme_tienda_theme/static/src/img/"

_CATEGORY_OVERRIDES = {
    1: {
        "name": "Cursos de Auditoría",
        "icon_url": "/latinpyme_tienda_theme/static/src/img/icon-auditoria.png",
    },
    2: {
        "name": "Cursos de Seguridad Vial",
        "icon_url": "/latinpyme_tienda_theme/static/src/img/icon-seguridad-vial.png",
    },
    4: {
        "name": "Diplomados",
        "icon_url": "/latinpyme_tienda_theme/static/src/img/icon-diplomado.png",
    },
    5: {
        "name": "FlashTraining",
        "url": "/shop/category/flashtraining-5",
        "icon_url": "/latinpyme_tienda_theme/static/src/img/icon-flashtraining.png",
    },
    6: {
        "name": "Talleres",
        "url": "/shop/category/talleres-6",
        "icon_url": "/latinpyme_tienda_theme/static/src/img/talleres-icon.png",
    },
}


def _category_display_name(category):
    if "lp_tienda_display_name" in category._fields and category.lp_tienda_display_name:
        return category.lp_tienda_display_name
    return _CATEGORY_OVERRIDES.get(category.id, {}).get("name") or category.name


def _category_url(category):
    return _CATEGORY_OVERRIDES.get(category.id, {}).get("url") or "/shop/category/%s" % category.id


def _category_icon_url(category):
    if "lp_tienda_icon_url" in category._fields and category.lp_tienda_icon_url:
        return category.lp_tienda_icon_url
    if _CATEGORY_OVERRIDES.get(category.id, {}).get("icon_url"):
        return "/tienda/category/%s/icon" % category.id
    return False


def _with_current_query(path):
    query_string = request.httprequest.query_string.decode("utf-8")
    return "%s?%s" % (path, query_string) if query_string else path


def _decode_image(value):
    if not value:
        return b""
    if isinstance(value, str):
        value = value.encode("ascii")
    return base64.b64decode(value)


def _guess_image_mimetype(image_data):
    if image_data.startswith(b"\x89PNG"):
        return "image/png"
    if image_data.startswith(b"\xff\xd8"):
        return "image/jpeg"
    if image_data.startswith(b"RIFF") and image_data[8:12] == b"WEBP":
        return "image/webp"
    if image_data.startswith(b"GIF"):
        return "image/gif"
    return "image/png"


def _website_matches(record):
    website = getattr(request, "website", False)
    return not record.website_id or not website or record.website_id == website


def _fallback_icon_data(category_id):
    icon_url = _CATEGORY_OVERRIDES.get(category_id, {}).get("icon_url")
    if not icon_url or not icon_url.startswith(_STATIC_ICON_PREFIX):
        return b""

    icon_path = _MODULE_ROOT / "static" / "src" / "img" / icon_url.replace(_STATIC_ICON_PREFIX, "")
    try:
        return icon_path.read_bytes()
    except OSError:
        return b""


class LatinpymeTiendaShopController(WebsiteSale):
    def _get_shop_path(self, category=None, page=0):
        category_id = getattr(category, "id", category)
        path = _CATEGORY_OVERRIDES.get(category_id, {}).get("url")
        if path:
            if page:
                path = "%s/page/%s" % (path, page)
            return path
        try:
            return super()._get_shop_path(category, page)
        except TypeError:
            return super()._get_shop_path(category)

    def _render_fixed_category(self, category_id, page=0, **post):
        category = request.env["product.public.category"].sudo().browse(category_id)
        if not category.exists():
            return request.not_found()
        return super().shop(page=page, category=category, **post)

    @http.route(
        [
            "/shop/category/webinars-6",
            "/shop/category/webinars-6/",
            "/shop/category/6",
            "/shop/category/6/",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def redirect_talleres_category(self, **post):
        return request.redirect(_with_current_query("/shop/category/talleres-6"), code=301)

    @http.route(
        [
            "/shop/category/webinars-6/page/<int:page>",
            "/shop/category/webinars-6/page/<int:page>/",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def redirect_talleres_category_page(self, page=0, **post):
        return request.redirect(_with_current_query("/shop/category/talleres-6/page/%s" % page), code=301)

    @http.route(
        [
            "/shop/category/flashtraining-gestion-estrategica-del-talento-humano-5",
            "/shop/category/flashtraining-gestion-estrategica-del-talento-humano-5/",
            "/shop/category/5",
            "/shop/category/5/",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def redirect_flashtraining_category(self, **post):
        return request.redirect(_with_current_query("/shop/category/flashtraining-5"), code=301)

    @http.route(
        [
            "/shop/category/flashtraining-gestion-estrategica-del-talento-humano-5/page/<int:page>",
            "/shop/category/flashtraining-gestion-estrategica-del-talento-humano-5/page/<int:page>/",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def redirect_flashtraining_category_page(self, page=0, **post):
        return request.redirect(_with_current_query("/shop/category/flashtraining-5/page/%s" % page), code=301)

    @http.route(
        [
            "/shop/category/talleres-6",
            "/shop/category/talleres-6/",
            "/shop/category/talleres-6/page/<int:page>",
            "/shop/category/talleres-6/page/<int:page>/",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def talleres_category(self, page=0, **post):
        return self._render_fixed_category(6, page=page, **post)

    @http.route(
        [
            "/shop/category/flashtraining-5",
            "/shop/category/flashtraining-5/",
            "/shop/category/flashtraining-5/page/<int:page>",
            "/shop/category/flashtraining-5/page/<int:page>/",
        ],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def flashtraining_category(self, page=0, **post):
        return self._render_fixed_category(5, page=page, **post)


class LatinpymeTiendaController(Website):
    def _render_tienda_page(self, template_xmlid, values):
        # Cualquier pagina "propia" que ya llama su masthead/footer a mano
        # (en vez de dejar que website.layout se los inyecte) debe pasar por
        # aca. Marca la request para que is_current_request_tienda_shell()
        # no vuelva a inyectarlos globalmente - antes esto se resolvia con
        # una lista fija de rutas excluidas que habia que actualizar a mano
        # por cada pagina nueva, y era facil de olvidar (paso con
        # /agente-ia). Con la bandera, toda pagina que use este helper queda
        # cubierta automaticamente, sin tocar ninguna lista.
        #
        # request.render() es LAZY por defecto (el render real ocurre al
        # final del dispatch, no aca) - si se dejaba lazy, el `finally` de
        # abajo apagaba la bandera ANTES de que el render real ocurriera,
        # y is_current_request_tienda_shell() la veia en False de nuevo
        # (esto fue lo que duplico el masthead/footer en home Y /agente-ia
        # al desplegar el fix). Se fuerza lazy=False para que el render
        # ocurra aca mismo, dentro del try/finally.
        request.lp_tienda_manual_shell = True
        try:
            return request.render(template_xmlid, values, lazy=False)
        finally:
            request.lp_tienda_manual_shell = False

    @http.route(["/terminos-de-uso", "/terms"], type="http", auth="public", website=True, sitemap=False)
    def tienda_terms_page(self, **kwargs):
        layout_values = request.env["latinpyme.tienda.config"].sudo().get_layout_context(getattr(request, "website", False))
        return self._render_tienda_page(
            "latinpyme_tienda_theme.lp_tienda_terms_page",
            {
                "title": "Términos de uso | Tienda LatinPyme",
                "website_meta_description": "Términos de uso de Tienda LatinPyme.",
                **layout_values,
            },
        )

    @http.route("/tienda/category/<int:category_id>/icon", type="http", auth="public", website=True, sitemap=False)
    def tienda_category_icon(self, category_id, **kwargs):
        category = request.env["product.public.category"].sudo().browse(category_id)
        if not category.exists():
            return request.not_found()

        image_data = b""
        if "lp_tienda_icon" in category._fields and category.lp_tienda_icon:
            image_data = _decode_image(category.lp_tienda_icon)
        if not image_data:
            image_data = _fallback_icon_data(category.id)
        if not image_data:
            return request.not_found()

        return request.make_response(
            image_data,
            headers=[
                ("Content-Type", _guess_image_mimetype(image_data)),
                ("Cache-Control", "no-cache, max-age=0, must-revalidate"),
            ],
        )

    @http.route(
        "/tienda/media/banner/<int:banner_id>/image",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def tienda_banner_image(self, banner_id, **kwargs):
        banner = request.env["latinpyme.tienda.banner"].sudo().browse(banner_id).exists()
        if not banner or not banner.active or not banner.image or not _website_matches(banner):
            return request.not_found()

        today = fields.Date.context_today(banner)
        if banner.date_start and banner.date_start > today:
            return request.not_found()
        if banner.date_end and banner.date_end < today:
            return request.not_found()

        image_data = _decode_image(banner.image)
        if not image_data:
            return request.not_found()

        return request.make_response(
            image_data,
            headers=[
                ("Content-Type", _guess_image_mimetype(image_data)),
                ("Cache-Control", "no-cache, max-age=0, must-revalidate"),
            ],
        )

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

    def _ensure_home_menu_item(self, menu_items):
        has_home = any(item.get("item_type") == "home" or item.get("name") == "Inicio" for item in menu_items)
        return menu_items if has_home else [self._home_menu_item()] + menu_items

    def _main_menu_items(self):
        try:
            with request.env.cr.savepoint():
                menu_items = request.env["latinpyme.tienda.menu.item"].sudo().get_header_menu(getattr(request, "website", False))
                return self._ensure_home_menu_item(menu_items or self._fallback_main_menu())
        except Exception as exc:
            _logger.info("No se pudo cargar el menu administrable de Tienda: %s", exc)
            return self._fallback_main_menu()

    def _home_product_carousels(self):
        try:
            with request.env.cr.savepoint():
                website = getattr(request, "website", False)
                Category = request.env["product.public.category"].with_context(lang=None)
                Product = request.env["product.template"]
                category_domain = []
                if "active" in Category._fields:
                    category_domain.append(("active", "=", True))
                if website and "website_id" in Category._fields:
                    category_domain.extend(["|", ("website_id", "=", False), ("website_id", "=", website.id)])

                categories = Category.search(category_domain, order="sequence asc, name asc")
                product_base_domain = []
                if "active" in Product._fields:
                    product_base_domain.append(("active", "=", True))
                if "sale_ok" in Product._fields:
                    product_base_domain.append(("sale_ok", "=", True))
                if "is_published" in Product._fields:
                    product_base_domain.append(("is_published", "=", True))
                elif "website_published" in Product._fields:
                    product_base_domain.append(("website_published", "=", True))
                if website and "website_id" in Product._fields:
                    product_base_domain.extend(["|", ("website_id", "=", False), ("website_id", "=", website.id)])

                product_order = "website_sequence asc, name asc" if "website_sequence" in Product._fields else "name asc"
                currency = getattr(website, "currency_id", False) or request.env.company.currency_id
                carousels = []
                for category in categories:
                    products = Product.search(
                        product_base_domain + [("public_categ_ids", "in", [category.id])],
                        order=product_order,
                        limit=10,
                    )
                    if not products:
                        continue
                    carousels.append(
                        {
                            "name": _category_display_name(category),
                            "url": _category_url(category),
                            "icon_url": _category_icon_url(category),
                            "products": [
                                {
                                    "name": product.name,
                                    "url": product.website_url if "website_url" in product._fields else "/shop",
                                    "image_url": "/web/image/product.template/%s/image_512" % product.id,
                                    "price": product.list_price if "list_price" in product._fields else False,
                                    "has_price": "list_price" in product._fields,
                                    "currency": currency,
                                }
                                for product in products
                            ],
                        }
                    )
                return carousels
        except Exception as exc:
            _logger.info("No se pudieron cargar carruseles nativos de Tienda: %s", exc)
            return []

    def _fallback_home_hero_banner(self, shop_url):
        return {
            "name": "Banner principal Tienda LatinPyme",
            "image_url": "https://latinpyme.com/revista/media/banner/3/image",
            "alt": "Acoso Sexual Laboral: Lo que toda empresa debe revisar antes de una sanción",
            "url": shop_url,
        }

    def _serialize_home_hero_banner(self, banner, shop_url):
        if not banner:
            return self._fallback_home_hero_banner(shop_url)
        return {
            "name": banner.name or "Banner principal Tienda LatinPyme",
            "image_url": "/tienda/media/banner/%s/image" % banner.id,
            "alt": banner.title or banner.name or "Banner principal Tienda LatinPyme",
            "url": banner.url or shop_url,
        }

    def _home_hero_banner(self, shop_url):
        try:
            with request.env.cr.savepoint():
                website = getattr(request, "website", False)
                banner = request.env["latinpyme.tienda.banner"].sudo().get_active_banner("home_hero", website=website)
                return self._serialize_home_hero_banner(banner, shop_url)
        except Exception as exc:
            _logger.info("No se pudo cargar el banner hero administrable de Tienda: %s", exc)
            return self._fallback_home_hero_banner(shop_url)

    def _serialize_home_horizontal_banner(self, banner):
        if not banner:
            return False
        return {
            "name": banner.name or "Publicidad horizontal Tienda LatinPyme",
            "image_url": "/tienda/media/banner/%s/image" % banner.id,
            "alt": banner.title or banner.name or "Publicidad horizontal Tienda LatinPyme",
            "url": banner.url or "/shop",
        }

    def _home_horizontal_banner(self):
        try:
            with request.env.cr.savepoint():
                website = getattr(request, "website", False)
                banner = request.env["latinpyme.tienda.banner"].sudo().get_active_banner("home_horizontal", website=website)
                return self._serialize_home_horizontal_banner(banner)
        except Exception as exc:
            _logger.info("No se pudo cargar el banner horizontal administrable de Tienda: %s", exc)
            return False

    def _serialize_home_side_banner(self, banner):
        if not banner:
            return False
        return {
            "name": banner.name or "Publicidad lateral Tienda LatinPyme",
            "image_url": "/tienda/media/banner/%s/image" % banner.id,
            "alt": banner.title or banner.name or "Publicidad lateral Tienda LatinPyme",
            "url": banner.url or "/shop",
        }

    def _home_side_banner(self):
        try:
            with request.env.cr.savepoint():
                website = getattr(request, "website", False)
                banner = request.env["latinpyme.tienda.banner"].sudo().get_active_banner("home_side", website=website)
                return self._serialize_home_side_banner(banner)
        except Exception as exc:
            _logger.info("No se pudo cargar el banner lateral administrable de Tienda: %s", exc)
            return False

    def _home_values(self):
        """Temporary storefront data, grouped for a future backend-managed phase."""
        shop_url = "/shop"
        whatsapp_url = "https://wa.link/i0n10b"
        layout_values = request.env["latinpyme.tienda.config"].sudo().get_layout_context(getattr(request, "website", False))
        home_blocks = layout_values.get("home_blocks") or {}
        return {
            **layout_values,
            "hero": {
                "eyebrow": "Tienda LatinPyme",
                "title": "Capacitación y soluciones empresariales para equipos que avanzan",
                "lead": "Cursos, herramientas y servicios diseñados para fortalecer gestión, tecnología, ventas y productividad en pymes latinoamericanas.",
                "primary_label": "Explorar tienda",
                "primary_url": shop_url,
                "secondary_label": "Hablar con un asesor",
                "secondary_url": whatsapp_url,
            },
            "hero_banner": self._home_hero_banner(shop_url),
            "horizontal_banner": self._home_horizontal_banner(),
            "side_banner": self._home_side_banner(),
            "product_carousels": self._home_product_carousels(),
            "training_cards": home_blocks.get("training", []),
            "technology_cards": home_blocks.get("technology", []),
            "ai_cards": home_blocks.get("ai", []),
            "allies": [
                {
                    "name": "Banco de Occidente",
                    "logo_url": "https://latinpyme.com/revista/media/ally/2/logo",
                },
                {
                    "name": "Aportes en Línea",
                    "logo_url": "https://latinpyme.com/revista/media/ally/1/logo",
                },
                {
                    "name": "Escuela Unipymes",
                    "logo_url": "https://latinpyme.com/revista/media/ally/3/logo",
                },
                {
                    "name": "Campus Virtual ACH Colombia",
                    "logo_url": "https://latinpyme.com/revista/media/ally/4/logo",
                },
                {
                    "name": "Universidad Protección",
                    "logo_url": "https://latinpyme.com/revista/media/ally/5/logo",
                },
                {
                    "name": "EduFundación Coomeva",
                    "logo_url": "https://latinpyme.com/revista/media/ally/6/logo",
                },
                {
                    "name": "Enlace",
                    "logo_url": "https://latinpyme.com/revista/media/ally/7/logo",
                },
                {
                    "name": "PorkColombia",
                    "logo_url": "https://latinpyme.com/revista/media/ally/8/logo",
                },
                {
                    "name": "Aula Asopagos",
                    "logo_url": "https://latinpyme.com/revista/media/ally/9/logo",
                },
            ],
        }

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
                    {"label": "Términos de Uso", "url": "/terminos-de-uso", "open_new_tab": False},
                    {"label": "Privacidad y datos", "url": "/terminos-de-uso", "open_new_tab": False},
                    {"label": "Aviso Legal", "url": "/terminos-de-uso", "open_new_tab": False},
                ],
            },
        ]

    def _footer_columns(self):
        try:
            website = getattr(request, "website", False)
            columns = request.env["latinpyme.tienda.footer.link"].sudo().get_footer_columns(website)
            if any(column.get("links") for column in columns):
                return columns
        except Exception as exc:
            _logger.info("No se pudieron cargar links de footer de Tienda: %s", exc)
        return self._fallback_footer_columns()

    def _is_tienda_website(self):
        website = getattr(request, "website", False)
        host = (request.httprequest.host or "").split(":", 1)[0].lower()
        website_domain = (getattr(website, "domain", "") or "").split(":", 1)[0].lower()
        website_name = (getattr(website, "name", "") or "").lower()

        if host == "tienda.latinpyme.com" or website_domain == "tienda.latinpyme.com":
            return True
        return "tienda" in website_name and "latinpyme" in website_name

    def _render_tienda_home(self):
        # El Cache-Control ya lo aplica IrHttp._post_dispatch (tienda_models.py)
        # sobre toda respuesta HTML del dominio Tienda, no hace falta repetirlo aqui.
        return self._render_tienda_page("latinpyme_tienda_theme.lp_tienda_home_page", self._home_values())

    @http.route("/", type="http", auth="public", website=True, sitemap=True)
    def index(self, **kwargs):
        if self._is_tienda_website():
            return self._render_tienda_home()
        return super().index(**kwargs)

    @http.route("/tienda", type="http", auth="public", website=True, sitemap=True)
    def tienda_home(self, **kwargs):
        return self._render_tienda_home()

    def _agente_ia_values(self):
        # /agente-ia era una website.page armada a mano en el Website Builder,
        # con su propio estilo suelto (no pasaba por tienda.scss) - se
        # reconstruye aqui como plantilla QWeb para que quede consistente con
        # el resto de Tienda y sea la primera de una familia de paginas
        # "landing" estandarizadas. El contenido (textos, links de agenda/
        # WhatsApp, logos de aliados) se preservo tal cual estaba publicado.
        appointment_url = "/appointment/9"
        whatsapp_url = "https://wa.link/bmq6tw"
        layout_values = request.env["latinpyme.tienda.config"].sudo().get_layout_context(getattr(request, "website", False))
        return {
            **layout_values,
            "title": "Agente IA | Tienda LatinPyme",
            "website_meta_description": "Atiende, vende y mide 24/7 con un Agente IA para WhatsApp, web y redes sociales.",
            "hero": {
                "eyebrow": "Agentes IA",
                "title_lead": "Atiende, vende y mide 24/7 con un ",
                "title_emphasis": "Agente IA",
                "lead": "Tu agente IA responde en WhatsApp, web y redes sociales con tu tono y tus reglas.",
                "pills": ["Soporte", "Agendamiento", "Encuestas", "Integración con CRM"],
                "primary_label": "Agendar cita aquí",
                "primary_url": appointment_url,
                "secondary_label": "Contactar un asesor",
                "secondary_url": whatsapp_url,
                "highlights": [
                    {"icon": "fa-bolt", "strong": "Respuesta inmediata:", "text": "cero esperas para tus clientes."},
                    {"icon": "fa-comments", "strong": "Marca y tono:", "text": "el agente habla como tu empresa."},
                    {"icon": "fa-bar-chart", "strong": "Data útil:", "text": "dashboard con métricas para decidir."},
                    {"icon": "fa-plug", "strong": "Integración:", "text": "CRM/ERP vía API sin fricciones."},
                ],
            },
            "appointment_url": appointment_url,
            "whatsapp_url": whatsapp_url,
            "use_cases": [
                {
                    "icon": "fa-headset",
                    "title": "Soporte",
                    "summary": "Tu agente responde consultas 24/7 con el tono de tu marca.",
                    "bullets": [
                        "Respuestas precisas y consistentes.",
                        "Escalamiento a humano con contexto.",
                        "Historial y trazabilidad.",
                    ],
                    "href": "#lp-tienda-agente-ia-agenda",
                    "button_label": "Agendar cita aquí",
                },
                {
                    "icon": "fa-bullseye",
                    "title": "Leads",
                    "summary": "Convierte visitantes en oportunidades calificadas, sin intervención manual.",
                    "bullets": [
                        "Califica leads con preguntas clave.",
                        "Agenda citas automáticamente.",
                        "Sincroniza con tu CRM o cualquier otra plataforma.",
                    ],
                    "href": "#lp-tienda-agente-ia-agenda",
                    "button_label": "Agendar cita aquí",
                },
                {
                    "icon": "fa-cogs",
                    "title": "Operación interna",
                    "summary": "Automatiza tareas repetitivas para que tu equipo se enfoque en lo importante.",
                    "bullets": [
                        "Captura y actualiza registros.",
                        "Orquesta flujos y aprobaciones.",
                        "Reportes automáticos.",
                    ],
                    "href": "#lp-tienda-agente-ia-agenda",
                    "button_label": "Agendar cita aquí",
                },
            ],
            "phases": [
                {"title": "Diagnóstico", "text": "Revisamos procesos, canales y objetivos para identificar oportunidades y mejoras."},
                {"title": "Análisis", "text": "Examinamos cómo fluye la información y se ejecutan los procesos."},
                {"title": "Desarrollo IA", "text": "Estructuramos flujos, documentos y fuentes que alimentan el sistema."},
                {"title": "Implementación", "text": "Configuramos integraciones y realizamos pruebas funcionales."},
                {"title": "Capacitación", "text": "Entrenamos al equipo y entregamos guías operativas."},
                {"title": "Administración", "text": "Monitoreo continuo y mejora basada en datos."},
            ],
            "allies": [
                {"name": "Banco de Occidente", "logo_url": "https://tienda.latinpyme.com/documents/thumbnail/GyMmex3WQZm2JalOamZSGgo2b?unique=2b3c040b&v=2"},
                {"name": "Enlace", "logo_url": "https://tienda.latinpyme.com/documents/thumbnail/8k-pLf0nRMyOyIimgTt0awo29?unique=8442d0fc&v=2"},
                {"name": "Protección", "logo_url": "https://tienda.latinpyme.com/documents/thumbnail/YJfXGw8VR-mnb3eyg9bKCgo28?unique=7c525ca1&v=2"},
                {"name": "Asopagos Jaime Torres", "logo_url": "https://tienda.latinpyme.com/documents/thumbnail/rr26jcrBSy2Pcci-R4AqIgo26?unique=a9a715e3&v=2"},
                {"name": "ACH", "logo_url": "https://tienda.latinpyme.com/web/image/249?filename=enlace.png&model=documents.document"},
                {"name": "Aporte en Línea", "logo_url": "https://tienda.latinpyme.com/documents/thumbnail/qpdl3gIvSlCXux9vfh2Yzgo24?unique=f8021906&v=2"},
            ],
        }

    @http.route("/agente-ia", type="http", auth="public", website=True, sitemap=True)
    def agente_ia_page(self, **kwargs):
        return self._render_tienda_page("latinpyme_tienda_theme.lp_tienda_agente_ia_page", self._agente_ia_values())


class LatinpymeTiendaTermsRedirect(TermsController):
    # /terms is natively owned by account/controllers/terms.py (registers its
    # own route, unrelated to website.layout, so none of the Tienda header/
    # footer fixes ever reach it) - overriding the endpoint here always wins
    # because it replaces the code behind the existing route instead of
    # trying to register a second, competing one. Render the same template
    # /terminos-de-uso uses (not a redirect) so /terms keeps its own URL
    # while showing identical content and design.
    def terms_conditions(self, **kwargs):
        website = getattr(request, "website", False)
        host = (request.httprequest.host or "").split(":", 1)[0].lower()
        website_domain = (getattr(website, "domain", "") or "").split(":", 1)[0].lower()
        website_name = (getattr(website, "name", "") or "").lower()
        is_tienda = host == "tienda.latinpyme.com" or website_domain == "tienda.latinpyme.com"
        is_tienda = is_tienda or ("tienda" in website_name and "latinpyme" in website_name)
        if is_tienda:
            layout_values = request.env["latinpyme.tienda.config"].sudo().get_layout_context(website)
            return request.render(
                "latinpyme_tienda_theme.lp_tienda_terms_page",
                {
                    "title": "Términos de uso | Tienda LatinPyme",
                    "website_meta_description": "Términos de uso de Tienda LatinPyme.",
                    **layout_values,
                },
            )
        return super().terms_conditions(**kwargs)
