# -*- coding: utf-8 -*-

import logging
import base64
from datetime import date

from werkzeug.exceptions import NotFound

from odoo import fields, http
from odoo.addons.website.controllers.main import Website
from odoo.http import request


_logger = logging.getLogger(__name__)


class LatinpymeTiendaController(Website):
    def _image_response(self, image):
        if not image:
            raise NotFound()
        content = base64.b64decode(image)
        mimetype = "image/png"
        if content.startswith(b"\xff\xd8"):
            mimetype = "image/jpeg"
        elif content.startswith(b"\x89PNG\r\n\x1a\n"):
            mimetype = "image/png"
        elif content.startswith(b"GIF"):
            mimetype = "image/gif"
        elif content.startswith(b"RIFF") and content[8:12] == b"WEBP":
            mimetype = "image/webp"
        return request.make_response(
            content,
            headers=[
                ("Content-Type", mimetype),
                ("Cache-Control", "public, max-age=86400"),
            ],
        )

    def _website_matches(self, record):
        website = getattr(request, "website", False)
        return not record.website_id or not website or record.website_id == website

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
                            "name": category.name,
                            "url": "/shop/category/%s" % category.id,
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

    def _home_banner(self, placement):
        try:
            with request.env.cr.savepoint():
                return request.env["latinpyme.tienda.banner"].sudo().get_active_banner(
                    placement,
                    getattr(request, "website", False),
                )
        except Exception as exc:
            _logger.info("No se pudo cargar banner de Tienda %s: %s", placement, exc)
            return False

    def _home_values(self):
        """Temporary storefront data, grouped for a future backend-managed phase."""
        shop_url = "/shop"
        whatsapp_url = "https://wa.link/i0n10b"
        social_links = [
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
        return {
            "current_year": date.today().year,
            "social_links": social_links,
            "hero": {
                "eyebrow": "Tienda LatinPyme",
                "title": "Capacitación y soluciones empresariales para equipos que avanzan",
                "lead": "Cursos, herramientas y servicios diseñados para fortalecer gestión, tecnología, ventas y productividad en pymes latinoamericanas.",
                "primary_label": "Explorar tienda",
                "primary_url": shop_url,
                "secondary_label": "Hablar con un asesor",
                "secondary_url": whatsapp_url,
            },
            "hero_banner": {
                "name": "Banner principal Tienda LatinPyme",
                "image_url": "https://latinpyme.com/revista/media/banner/3/image",
                "alt": "Acoso Sexual Laboral: Lo que toda empresa debe revisar antes de una sanción",
                "url": shop_url,
            },
            "product_carousels": self._home_product_carousels(),
            "home_horizontal_banner": self._home_banner("home_horizontal"),
            "home_side_banner": self._home_banner("home_side"),
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
            "footer_columns": [
                {
                    "title": "Secciones",
                    "links": [
                        ("Cursos", "/shop?search=cursos"),
                        ("Capacitación", "/shop?search=capacitacion"),
                        ("Tecnología", "/shop?search=tecnologia"),
                        ("Inteligencia artificial", "/shop?search=inteligencia%20artificial"),
                    ],
                },
                {
                    "title": "Portafolio",
                    "links": [
                        ("Soluciones", "/shop?search=soluciones"),
                        ("Escuela", "/shop?search=escuela"),
                        ("Eventos", "/shop?search=eventos"),
                        ("Curso 50 y 20 horas", "/shop?search=50%2020"),
                    ],
                },
                {
                    "title": "Legal",
                    "links": [
                        ("Términos de Uso", "/terms"),
                        ("Privacidad y datos", "/terms"),
                        ("Aviso Legal", "/terms"),
                    ],
                },
            ],
            "whatsapp_url": whatsapp_url,
        }

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

    @http.route(
        "/tienda/media/banner/<int:banner_id>/image",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def tienda_banner_image(self, banner_id, **kwargs):
        banner = request.env["latinpyme.tienda.banner"].sudo().browse(banner_id).exists()
        if not banner or not banner.active or not banner.image or not self._website_matches(banner):
            raise NotFound()
        today = fields.Date.context_today(banner)
        if banner.date_start and banner.date_start > today:
            raise NotFound()
        if banner.date_end and banner.date_end < today:
            raise NotFound()
        return self._image_response(banner.image)
