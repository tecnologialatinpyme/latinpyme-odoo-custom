# -*- coding: utf-8 -*-

import base64
import logging
from pathlib import Path

from odoo import http
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
            "image_url": "/web/image/latinpyme.tienda.banner/%s/image" % banner.id,
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
            "image_url": "/web/image/latinpyme.tienda.banner/%s/image" % banner.id,
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
            "image_url": "/web/image/latinpyme.tienda.banner/%s/image" % banner.id,
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
            "training_cards": [
                {
                    "title": "Cursos Online 100%",
                    "subtitle": "Cursos de actualización",
                    "summary": "Flexibles, diseñados para adquirir nuevas habilidades.",
                    "bullets": ["Auditoría SG-SST.", "Seguridad Vial."],
                    "href": "/shop?search=online",
                    "icon": "fa-laptop",
                },
                {
                    "title": "Capacitaciones Inhouse",
                    "subtitle": "Formación a la medida",
                    "summary": "Diseñamos contenidos según tus procesos y retos, con expertos.",
                    "bullets": ["Presencial, virtual o híbrida.", "Talento humano, IA, Finanzas y más."],
                    "href": "/shop?search=inhouse",
                    "icon": "fa-users",
                },
                {
                    "title": "Fidelizacion empresarial",
                    "subtitle": "E-learning",
                    "summary": "Capacitaciones en gerencia, negocios y temas legales.",
                    "bullets": ["Charlas empresariales.", "Diplomados.", "Flashtraining.", "Curso 50/20 horas (SG-SST)."],
                    "href": "/shop?search=fidelizacion",
                    "icon": "fa-line-chart",
                },
            ],
            "technology_cards": [
                {
                    "title": "LMS (Aulas)",
                    "summary": "Plataformas de aprendizaje para capacitar equipos y medir avances.",
                    "bullets": ["Cursos empresariales", "Seguimiento de progreso", "Certificación"],
                    "href": "/shop?search=lms",
                    "icon": "fa-desktop",
                },
                {
                    "title": "Salones (Eventos)",
                    "summary": "Soluciones para encuentros, formaciones y experiencias corporativas.",
                    "bullets": ["Eventos presenciales", "Experiencias híbridas", "Soporte operativo"],
                    "href": "/shop?search=eventos",
                    "icon": "fa-calendar",
                },
            ],
            "ai_cards": [
                {
                    "title": "Agentes IA",
                    "summary": "Asistentes virtuales 24/7 para atencion, ventas y procesos.",
                    "bullets": ["Omnicanal", "Automatizacion", "Integracion CRM/ERP"],
                    "href": "/shop?search=agentes%20ia",
                    "icon": "fa-comments",
                },
                {
                    "title": "Telefonia IA",
                    "summary": "Llamadas inteligentes con voz natural e integracion a tus sistemas.",
                    "bullets": ["Entrantes y salientes.", "Voz natural.", "Registro en CRM."],
                    "href": "/shop?search=telefonia%20ia",
                    "icon": "fa-phone",
                },
                {
                    "title": "IA Analítica y Predictiva",
                    "summary": "Convierte datos en decisiones con modelos en tiempo real.",
                    "bullets": ["Dashboards", "Predicción", "Decisiones automáticas"],
                    "href": "/shop?search=analitica%20predictiva",
                    "icon": "fa-area-chart",
                },
            ],
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
                    {"label": "Términos de Uso", "url": "/terms", "open_new_tab": False},
                    {"label": "Privacidad y datos", "url": "/terms", "open_new_tab": False},
                    {"label": "Aviso Legal", "url": "/terms", "open_new_tab": False},
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
        response = request.render("latinpyme_tienda_theme.lp_tienda_home_page", self._home_values())
        response.headers["Cache-Control"] = "no-cache, max-age=0, must-revalidate"
        return response

    @http.route("/", type="http", auth="public", website=True, sitemap=True)
    def index(self, **kwargs):
        if self._is_tienda_website():
            return self._render_tienda_home()
        return super().index(**kwargs)

    @http.route("/tienda", type="http", auth="public", website=True, sitemap=True)
    def tienda_home(self, **kwargs):
        return self._render_tienda_home()
