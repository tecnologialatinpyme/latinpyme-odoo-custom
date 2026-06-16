# -*- coding: utf-8 -*-

import base64
from datetime import date

from odoo import fields, http
from odoo.addons.website.controllers.main import Website
from odoo.http import request
from werkzeug.exceptions import NotFound
from werkzeug.utils import redirect as werkzeug_redirect


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

    def _home_values(self):
        """Storefront data with backend-managed header, menu, footer and banners."""
        shop_url = "/shop"
        website = getattr(request, "website", False)
        Config = request.env["latinpyme.tienda.config"].sudo()
        Config._refresh_module_data()
        Menu = request.env["latinpyme.tienda.menu.link"].sudo()
        Footer = request.env["latinpyme.tienda.footer.link"].sudo()
        Banner = request.env["latinpyme.tienda.banner"].sudo()
        ProductCarousel = request.env["latinpyme.tienda.product.carousel"].sudo()

        config = Config.get_active_config(website)
        whatsapp_url = config.whatsapp_url if config and config.whatsapp_url else "https://wa.link/i0n10b"
        hero_banner_record = Banner.get_active_banner("hero", website=website)
        hero_banner = {
            "name": "Banner principal Tienda LatinPyme",
            "image_url": "https://latinpyme.com/revista/media/banner/3/image",
            "alt": "Banner principal Tienda LatinPyme",
            "url": shop_url,
        }
        if hero_banner_record and hero_banner_record.image:
            hero_banner = {
                "name": hero_banner_record.name,
                "image_url": hero_banner_record.image_src(),
                "alt": hero_banner_record.alt_text or hero_banner_record.name,
                "url": hero_banner_record.url or shop_url,
            }

        return {
            "current_year": date.today().year,
            "lp_config": config,
            "menu_links": Menu.get_active_links(website),
            "social_links": config.social_link_values() if config else [],
            "hero_banner": hero_banner,
            "home_horizontal_banner": Banner.get_active_banner("home_horizontal", website=website),
            "tech_sidebar_banner": Banner.get_active_banner("tech_sidebar", website=website),
            "footer_banner": Banner.get_active_banner("footer", website=website),
            "product_carousels": ProductCarousel.get_home_carousels(website=website),
            "training_cards": [
                {
                    "title": "Cursos Online 100%",
                    "subtitle": "Cursos de actualizacion",
                    "summary": "Flexibles, disenados para adquirir nuevas habilidades.",
                    "bullets": ["Auditoria SG-SST.", "Seguridad Vial."],
                    "href": "/shop?search=online",
                    "icon": "fa-laptop",
                },
                {
                    "title": "Capacitaciones Inhouse",
                    "subtitle": "Formacion a la medida",
                    "summary": "Disenamos contenidos segun tus procesos y retos, con expertos.",
                    "bullets": ["Presencial, virtual o hibrida.", "Talento humano, IA, Finanzas y mas."],
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
                    "bullets": ["Cursos empresariales", "Seguimiento de progreso", "Certificacion"],
                    "href": "/shop?search=lms",
                    "icon": "fa-desktop",
                },
                {
                    "title": "Salones (Eventos)",
                    "summary": "Soluciones para encuentros, formaciones y experiencias corporativas.",
                    "bullets": ["Eventos presenciales", "Experiencias hibridas", "Soporte operativo"],
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
                    "title": "IA Analitica y Predictiva",
                    "summary": "Convierte datos en decisiones con modelos en tiempo real.",
                    "bullets": ["Dashboards", "Prediccion", "Decisiones automaticas"],
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
                    "name": "Aportes en Linea",
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
                    "name": "Universidad Proteccion",
                    "logo_url": "https://latinpyme.com/revista/media/ally/5/logo",
                },
                {
                    "name": "EduFundacion Coomeva",
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
                    "links": Footer.get_active_links("sections", website),
                },
                {
                    "title": "Portafolio",
                    "links": Footer.get_active_links("portfolio", website),
                },
                {
                    "title": "Legal",
                    "links": Footer.get_active_links("legal", website),
                },
            ],
            "whatsapp_url": whatsapp_url,
        }

    def _is_tienda_website(self):
        website = getattr(request, "website", False)
        host = (request.httprequest.host or "").split(":", 1)[0].lower()
        website_domain = (getattr(website, "domain", "") or "").split(":", 1)[0].lower()
        website_name = (getattr(website, "name", "") or "").lower()
        config = request.env["latinpyme.tienda.config"].sudo().get_active_config(website)

        if config and config.is_tienda_host(host):
            return True
        if host == "tienda.latinpyme.com" or website_domain == "tienda.latinpyme.com":
            return True
        return "tienda" in website_name and "latinpyme" in website_name

    def _render_tienda_home(self):
        return request.render("latinpyme_tienda_theme.lp_tienda_home_page", self._home_values())

    @http.route(
        "/latinpyme-tienda/media/banner/<int:banner_id>/image",
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

    @http.route(
        "/latinpyme-tienda/refresh-module-data",
        type="http",
        auth="user",
        website=False,
        sitemap=False,
    )
    def tienda_refresh_module_data(self, **kwargs):
        if not request.env.user.has_group("base.group_system"):
            raise NotFound()
        refreshed = request.env["latinpyme.tienda.config"].sudo()._refresh_module_data(
            force=True,
            raise_on_error=True,
        )
        message = "Tienda LatinPyme module data refreshed" if refreshed else "Tienda LatinPyme module data already current"
        return request.make_response(message, headers=[("Content-Type", "text/plain; charset=utf-8")])

    @http.route("/", type="http", auth="public", website=True, sitemap=True)
    def index(self, **kwargs):
        if self._is_tienda_website():
            return self._render_tienda_home()
        return super().index(**kwargs)

    @http.route("/tienda", type="http", auth="public", website=True, sitemap=False)
    def tienda_home(self, **kwargs):
        if self._is_tienda_website():
            return werkzeug_redirect("/", code=302)
        raise NotFound()
