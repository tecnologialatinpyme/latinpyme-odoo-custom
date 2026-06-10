# -*- coding: utf-8 -*-

from datetime import date

from odoo import http
from odoo.http import request


class LatinpymeTiendaController(http.Controller):
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
                "Proteccion",
                "Coomeva Fundacion",
                "Enlace Operativo",
                "Ceniporcino",
                "Asopagos",
                "Banco de Occidente",
            ],
            "footer_columns": [
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
                    "title": "Capacitación",
                    "links": [
                        ("Cursos online", "/shop?search=online"),
                        ("Inhouse", "/shop?search=inhouse"),
                        ("Inteligencia artificial", "/shop?search=inteligencia%20artificial"),
                        ("Seguridad vial", "/shop?search=seguridad%20vial"),
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

    @http.route("/tienda", type="http", auth="public", website=True, sitemap=True)
    def tienda_home(self, **kwargs):
        return request.render("latinpyme_tienda_theme.lp_tienda_home_page", self._home_values())

