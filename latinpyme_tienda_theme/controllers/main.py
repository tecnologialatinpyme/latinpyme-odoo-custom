# -*- coding: utf-8 -*-

from datetime import date

from odoo import http
from odoo.addons.website.controllers.main import Website
from odoo.http import request


class LatinpymeTiendaController(Website):
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
            "course_categories": [
                {
                    "title": "Cursos de Auditor en SG-SST",
                    "summary": "Fórmate para evaluar y mejorar sistemas de gestión.",
                    "href": "/shop?search=SG-SST",
                    "icon": "fa-shield",
                },
                {
                    "title": "Cursos de Seguridad Vial",
                    "summary": "Capacítate en prevención y cultura de seguridad vial.",
                    "href": "/shop?search=seguridad%20vial",
                    "icon": "fa-road",
                },
                {
                    "title": "Cursos de IA",
                    "summary": "Impulsa tu futuro. Aprende IA aplicada a tu trabajo y tu empresa.",
                    "href": "/shop?search=inteligencia%20artificial",
                    "icon": "fa-cogs",
                },
                {
                    "title": "Diplomados",
                    "summary": "Programas especializados para avanzar en tu carrera.",
                    "href": "/shop?search=diplomado",
                    "icon": "fa-graduation-cap",
                },
                {
                    "title": "Talleres",
                    "summary": "Formación práctica con resultados inmediatos.",
                    "href": "/shop?search=taller",
                    "icon": "fa-book",
                },
            ],
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
        return request.render("latinpyme_tienda_theme.lp_tienda_home_page", self._home_values())

    @http.route("/", type="http", auth="public", website=True, sitemap=True)
    def index(self, **kwargs):
        if self._is_tienda_website():
            return self._render_tienda_home()
        return super().index(**kwargs)

    @http.route("/tienda", type="http", auth="public", website=True, sitemap=True)
    def tienda_home(self, **kwargs):
        return self._render_tienda_home()

