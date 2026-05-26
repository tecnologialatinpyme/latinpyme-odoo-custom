# -*- coding: utf-8 -*-

from datetime import datetime, time, timedelta
import re
from urllib.parse import urlencode

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.http import request as http_request


SLUG_RE = re.compile(r"^[a-z0-9-]+$")
SPANISH_MONTHS = {
    1: "enero",
    2: "febrero",
    3: "marzo",
    4: "abril",
    5: "mayo",
    6: "junio",
    7: "julio",
    8: "agosto",
    9: "septiembre",
    10: "octubre",
    11: "noviembre",
    12: "diciembre",
}
SPANISH_MONTHS_SHORT = {
    1: "ene",
    2: "feb",
    3: "mar",
    4: "abr",
    5: "may",
    6: "jun",
    7: "jul",
    8: "ago",
    9: "sep",
    10: "oct",
    11: "nov",
    12: "dic",
}
PROGRAM_EVENT_TYPES = [
    ("charlas", "Charlas"),
    ("diplomados", "Diplomados"),
    ("flashtraining", "Flashtraining"),
    ("foros", "Foros"),
]
REMOVED_PROGRAM_EVENT_TYPES = ("curso_50_20",)
PROGRAM_EVENT_TYPE_LEGACY_MAP = {
    "charla": "charlas",
    "diplomado": "diplomados",
    "capacitacion": "charlas",
    "otro": "foros",
}
DISPLAY_MODE_SELECTION = [
    ("default", "Usar configuracion general"),
    ("show", "Mostrar"),
    ("hide", "Ocultar"),
]
HOME_BLOCK_TYPES = [
    ("top_banners", "Banners superiores"),
    ("hero", "Hero y destacados"),
    ("latest", "De interes"),
    ("sections", "Secciones"),
    ("news", "Novedades"),
    ("interviews", "Entrevistas"),
    ("specials", "Especiales"),
    ("mid_banners", "Banners intermedios"),
    ("portfolio", "Portafolio"),
    ("allies", "Aliados"),
]
SIDEBAR_PLACEMENTS = [
    ("global", "Global"),
    ("home", "Home"),
    ("section", "Pagina de seccion"),
    ("note", "Nota individual"),
]
SIDEBAR_ITEM_TYPES = [
    ("conference", "Proxima conferencia"),
    ("poll", "Encuesta"),
    ("interview_cta", "CTA entrevistas"),
    ("banner", "Banner lateral"),
]


def _current_website():
    try:
        return getattr(http_request, "website", False)
    except Exception:
        return False


class LatinpymeRevistaConfig(models.Model):
    _name = "latinpyme.revista.config"
    _description = "Configuracion Revista LatinPyme"
    _order = "website_id, id"

    name = fields.Char(string="Nombre", required=True, default="Revista LatinPyme")
    website_id = fields.Many2one("website", string="Sitio web", ondelete="cascade")
    production_domain = fields.Char(string="Dominio final", default="latinpyme.com")
    preproduction_domain = fields.Char(string="Dominio de preproduccion", default="revista.latinpyme.com")
    preproduction_noindex = fields.Boolean(string="No indexar preproduccion", default=True)
    footer_text = fields.Char(string="Texto legal del footer", default="© 2026 Revista LatinPyme - Todos los derechos reservados")
    subscribe_url = fields.Char(string="URL Suscribirse", default="/suscribirse")
    interview_apply_url = fields.Char(string="URL Postúlate entrevistas", default="/contactus")
    phone = fields.Char(string="Telefono", default="+57 310 123 4567")
    city = fields.Char(string="Ciudad", default="Bogota, Colombia")
    email = fields.Char(string="Correo")
    facebook_url = fields.Char(string="URL Facebook", default="#")
    linkedin_url = fields.Char(string="URL LinkedIn", default="#")
    instagram_url = fields.Char(string="URL Instagram", default="#")
    youtube_url = fields.Char(string="URL YouTube", default="#")
    whatsapp_url = fields.Char(string="URL WhatsApp", default="#")
    show_home_banners = fields.Boolean(string="Mostrar banners en Home", default=True)
    show_home_interviews = fields.Boolean(string="Mostrar entrevistas en Home", default=True)
    show_home_specials = fields.Boolean(string="Mostrar especiales en Home", default=True)
    show_home_portfolio = fields.Boolean(string="Mostrar portafolio en Home", default=True)
    show_home_allies = fields.Boolean(string="Mostrar aliados en Home", default=True)
    home_highlight_limit = fields.Integer(string="Cantidad de destacados", default=3)
    home_latest_limit = fields.Integer(string="Cantidad de recientes", default=6)
    home_new_limit = fields.Integer(string="Cantidad de novedades", default=5)
    section_posts_per_page = fields.Integer(string="Notas por pagina de seccion", default=9)
    show_note_sidebar = fields.Boolean(string="Mostrar sidebar en notas", default=True)
    show_note_interviews = fields.Boolean(string="Mostrar entrevistas en notas", default=True)
    show_note_portfolio = fields.Boolean(string="Mostrar portafolio en notas", default=True)
    show_note_allies = fields.Boolean(string="Mostrar aliados en notas", default=True)
    show_sidebar_conference = fields.Boolean(string="Mostrar conferencia", default=True)
    show_sidebar_poll = fields.Boolean(string="Mostrar encuesta", default=True)
    show_sidebar_ad = fields.Boolean(string="Mostrar publicidad lateral", default=True)
    conference_label = fields.Char(string="Etiqueta de conferencia", default="Proxima conferencia")
    conference_title = fields.Char(string="Titulo de conferencia", default="Liderazgo y cultura organizacional: claves para el futuro")
    conference_date_text = fields.Char(string="Fecha visible", default="25 de junio de 2024")
    conference_location = fields.Char(string="Lugar", default="Bogota, Colombia")
    conference_time = fields.Char(string="Hora", default="9:00 a.m. - 12:00 m.")
    conference_button_label = fields.Char(string="Texto del boton", default="Mas informacion")
    conference_url = fields.Char(string="URL de conferencia", default="/event")
    poll_label = fields.Char(string="Etiqueta de encuesta", default="Encuesta")
    poll_question = fields.Char(string="Pregunta", default="¿Cual es el mayor desafio de tu empresa este año?")
    poll_option_1 = fields.Char(string="Opcion 1", default="Acceso a financiamiento")
    poll_option_2 = fields.Char(string="Opcion 2", default="Transformacion digital")
    poll_option_3 = fields.Char(string="Opcion 3", default="Atraccion y retencion de talento")
    poll_option_4 = fields.Char(string="Opcion 4", default="Aumento de costos")
    poll_button_label = fields.Char(string="Texto del boton encuesta", default="Votar")

    @api.constrains("home_highlight_limit", "home_latest_limit", "home_new_limit", "section_posts_per_page")
    def _check_positive_limits(self):
        for record in self:
            for field_name in ("home_highlight_limit", "home_latest_limit", "home_new_limit", "section_posts_per_page"):
                if record[field_name] < 1:
                    raise ValidationError("Las cantidades configuradas deben ser mayores que cero.")

    @api.model
    def get_active_config(self, website=None):
        website_id = website.id if website else self.env.context.get("website_id")
        request_host = False
        if not website_id:
            try:
                request_website = getattr(http_request, "website", False)
                request_host = getattr(http_request, "httprequest", False).host
            except Exception:
                request_website = False
            website_id = request_website.id if request_website else False
        elif not request_host:
            try:
                request_host = getattr(http_request, "httprequest", False).host
            except Exception:
                request_host = False
        if website_id:
            config = self.search([("website_id", "=", website_id)], limit=1)
            if config:
                return config
        request_host = self._domain_to_host(request_host) if request_host else False
        if request_host:
            for config in self.search([]):
                if request_host in (config._domain_to_host(config.production_domain), config._domain_to_host(config.preproduction_domain)):
                    return config
        return self.search([("website_id", "=", False)], limit=1)

    def _domain_to_host(self, domain):
        domain = (domain or "").strip().lower()
        domain = domain.replace("https://", "").replace("http://", "")
        domain = domain.split("/", 1)[0]
        return domain.split(":", 1)[0]

    def domain_to_host(self, domain):
        self.ensure_one()
        return self._domain_to_host(domain)

    def _normalize_url_value(self, url, fallback="/"):
        target = (url or "").strip()
        if not target or target == "#":
            return fallback
        replacements = (
            ("https://wa-link/", "https://wa.link/"),
            ("http://wa-link/", "http://wa.link/"),
            ("https:/wa.link/", "https://wa.link/"),
            ("http:/wa.link/", "http://wa.link/"),
            ("https:/wa-link/", "https://wa.link/"),
            ("http:/wa-link/", "http://wa.link/"),
            ("https/wa-link/", "https://wa.link/"),
            ("http/wa-link/", "http://wa.link/"),
            ("wa-link/", "https://wa.link/"),
        )
        for old, new in replacements:
            if target.startswith(old):
                target = target.replace(old, new, 1)
                break
        if target.startswith("https//"):
            target = target.replace("https//", "https://", 1)
        elif target.startswith("http//"):
            target = target.replace("http//", "http://", 1)
        elif target.startswith("//"):
            target = "https:" + target
        elif target.startswith("wa.link/"):
            target = "https://" + target
        return target or fallback

    def subscribe_target_url(self):
        self.ensure_one()
        return self._normalize_url_value(self.subscribe_url, fallback="/suscribirse")

    def interview_apply_target_url(self):
        self.ensure_one()
        return self._normalize_url_value(self.interview_apply_url, fallback="/contactus")

    def production_base_url(self):
        self.ensure_one()
        domain = (self.production_domain or "latinpyme.com").strip().rstrip("/")
        if not domain.startswith(("http://", "https://")):
            domain = "https://%s" % domain
        return domain.rstrip("/")

    def is_preproduction_host(self, host):
        self.ensure_one()
        if not self.preproduction_noindex:
            return False
        host = (host or "").split(":", 1)[0].lower()
        preproduction_host = self._domain_to_host(self.preproduction_domain)
        return (
            bool(preproduction_host and host == preproduction_host)
            or host.endswith(".odoo.com")
            or host.endswith(".odoo.sh")
        )

    @api.model
    def is_current_host_revista(self):
        try:
            host = getattr(http_request, "httprequest", False).host
        except Exception:
            host = False
        host = self._domain_to_host(host) if host else False
        if not host:
            return False
        for config in self.sudo().search([]):
            if host == config._domain_to_host(config.production_domain):
                return True
        return False

    @api.model
    def is_current_request_revista_shell(self):
        try:
            path = getattr(http_request, "httprequest", False).path or ""
        except Exception:
            path = ""
        return self.is_current_host_revista() and (
            path == "/revista"
            or path.startswith("/revista/")
            or path.startswith("/blog/")
        )


class LatinpymeRevistaSection(models.Model):
    _name = "latinpyme.revista.section"
    _description = "Seccion editorial Revista LatinPyme"
    _order = "sequence, name"

    name = fields.Char(string="Nombre", required=True)
    slug = fields.Char(string="Slug", required=True, index=True)
    tag_id = fields.Many2one("blog.tag", string="Etiqueta de Blog")
    parent_id = fields.Many2one("latinpyme.revista.section", string="Menu padre", ondelete="cascade")
    child_ids = fields.One2many("latinpyme.revista.section", "parent_id", string="Submenus")
    menu_only = fields.Boolean(
        string="Solo menu desplegable",
        help="Activa esta opcion para que la seccion aparezca como menu padre sin pagina propia.",
    )
    menu_url = fields.Char(
        string="URL personalizada",
        help="Opcional. Si se deja vacia, el enlace apunta a /revista/seccion/<slug>.",
    )
    active = fields.Boolean(string="Activa", default=True)
    sequence = fields.Integer(string="Orden", default=10)
    description = fields.Text(string="Descripcion")
    cover_image = fields.Image(string="Imagen de portada", max_width=1920, max_height=1080)
    cover_filename = fields.Char(string="Nombre de archivo")
    section_posts_per_page = fields.Integer(string="Notas por pagina")
    section_sidebar_mode = fields.Selection(
        DISPLAY_MODE_SELECTION,
        string="Sidebar en seccion",
        default="default",
        required=True,
    )
    section_related_mode = fields.Selection(
        DISPLAY_MODE_SELECTION,
        string="Relacionadas en seccion",
        default="default",
        required=True,
    )
    section_interviews_mode = fields.Selection(
        DISPLAY_MODE_SELECTION,
        string="Entrevistas en seccion",
        default="default",
        required=True,
    )
    section_portfolio_mode = fields.Selection(
        DISPLAY_MODE_SELECTION,
        string="Portafolio en seccion",
        default="default",
        required=True,
    )
    section_allies_mode = fields.Selection(
        DISPLAY_MODE_SELECTION,
        string="Aliados en seccion",
        default="default",
        required=True,
    )
    section_banner_id = fields.Many2one(
        "latinpyme.revista.banner",
        string="Banner especifico de seccion",
        domain=[("placement", "=", "section")],
    )
    note_sidebar_mode = fields.Selection(
        DISPLAY_MODE_SELECTION,
        string="Sidebar en notas",
        default="default",
        required=True,
    )
    note_interviews_mode = fields.Selection(
        DISPLAY_MODE_SELECTION,
        string="Entrevistas en notas",
        default="default",
        required=True,
    )
    note_portfolio_mode = fields.Selection(
        DISPLAY_MODE_SELECTION,
        string="Portafolio en notas",
        default="default",
        required=True,
    )
    note_allies_mode = fields.Selection(
        DISPLAY_MODE_SELECTION,
        string="Aliados en notas",
        default="default",
        required=True,
    )
    note_banner_id = fields.Many2one(
        "latinpyme.revista.banner",
        string="Banner especifico de nota",
        domain=[("placement", "=", "note")],
    )
    seo_title = fields.Char(string="Titulo SEO")
    seo_description = fields.Text(string="Descripcion SEO")
    website_id = fields.Many2one("website", string="Sitio web", ondelete="cascade")

    _sql_constraints = [
        ("slug_unique", "unique(slug, website_id)", "El slug de seccion debe ser unico por sitio web."),
    ]

    @api.onchange("name")
    def _onchange_name_slug(self):
        for record in self:
            if record.name and not record.slug:
                record.slug = self._slugify(record.name)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("slug"):
                vals["slug"] = vals["slug"].strip().lower()
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("slug"):
            vals["slug"] = vals["slug"].strip().lower()
        return super().write(vals)

    @api.constrains("slug")
    def _check_slug(self):
        for record in self:
            slug = (record.slug or "").strip().lower()
            if not slug or not SLUG_RE.match(slug):
                raise ValidationError("El slug solo puede usar minusculas, numeros y guiones.")

    @api.constrains("slug", "website_id")
    def _check_unique_slug(self):
        for record in self:
            domain = [("slug", "=", record.slug), ("id", "!=", record.id)]
            if record.website_id:
                domain.append(("website_id", "=", record.website_id.id))
            else:
                domain.append(("website_id", "=", False))
            if self.search_count(domain):
                raise ValidationError("Ya existe una seccion con este slug para el mismo sitio web.")

    @api.constrains("parent_id")
    def _check_parent_id(self):
        for record in self:
            current = record.parent_id
            depth = 1
            while current:
                if current == record:
                    raise ValidationError("Una seccion no puede ser submenu de si misma.")
                depth += 1
                if depth > 3:
                    raise ValidationError("El menu editorial solo permite hasta 3 niveles.")
                current = current.parent_id

    @api.model
    def _slugify(self, value):
        value = (value or "").strip().lower()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        return value.strip("-")

    @api.model
    def get_active_sections(self, website=None):
        website = website or _current_website()
        domain = [("active", "=", True)]
        if website:
            domain.append(("website_id", "in", [False, website.id]))
        return self.search(domain, order="sequence, name")

    @api.model
    def get_route_sections(self, website=None):
        return self.get_active_sections(website).filtered(lambda section: not section.menu_only)

    @api.model
    def _nav_url(self, section):
        if section.menu_only:
            return False
        return section.menu_url or "/revista/seccion/%s" % section.slug

    @api.model
    def _nav_item(self, section, children=None):
        children = children or []
        active_slugs = [section.slug]
        for child in children:
            active_slugs += child.get("active_slugs") or [child.get("slug")]
        return {
            "slug": section.slug,
            "name": section.name,
            "url": False if children else self._nav_url(section),
            "menu_only": section.menu_only or bool(children),
            "children": children,
            "active_slugs": active_slugs,
        }

    @api.model
    def _nav_tree_item(self, section, records, depth=1, max_depth=3):
        children = []
        if depth < max_depth:
            children = [
                self._nav_tree_item(child, records, depth=depth + 1, max_depth=max_depth)
                for child in records.filtered(lambda child: child.parent_id == section)
            ]
        return self._nav_item(section, children=children)

    @api.model
    def get_nav_sections(self, website=None):
        records = self.get_active_sections(website)
        if not records:
            return []
        top_sections = records.filtered(lambda section: not section.parent_id)
        return [self._nav_tree_item(section, records) for section in top_sections]

    @api.model
    def get_by_slug(self, slug, website=None, active=True, routable=False):
        website = website or _current_website()
        slug = (slug or "").strip().lower()
        domain = [("slug", "=", slug)]
        if active:
            domain.append(("active", "=", True))
        if routable:
            domain.append(("menu_only", "=", False))
        if website:
            website_record = self.search(domain + [("website_id", "=", website.id)], limit=1)
            if website_record:
                return website_record
        return self.search(domain + [("website_id", "=", False)], limit=1)

    @api.model
    def get_by_tag(self, tag, website=None):
        website = website or _current_website()
        if not tag:
            return self.browse()
        domain = [("active", "=", True), ("menu_only", "=", False), ("tag_id", "=", tag.id)]
        if website:
            website_record = self.search(domain + [("website_id", "=", website.id)], limit=1)
            if website_record:
                return website_record
        record = self.search(domain + [("website_id", "=", False)], limit=1)
        if record:
            return record
        fallback_domain = [("active", "=", True), ("menu_only", "=", False), ("name", "=ilike", tag.name)]
        if website:
            website_record = self.search(fallback_domain + [("website_id", "=", website.id)], limit=1)
            if website_record:
                return website_record
        return self.search(fallback_domain + [("website_id", "=", False)], limit=1)

    def blog_tag(self):
        self.ensure_one()
        if self.tag_id:
            return self.tag_id
        return self.env["blog.tag"].sudo().search([("name", "=ilike", self.name)], limit=1)

    def display_mode_enabled(self, field_name, default_enabled=True):
        self.ensure_one()
        value = self[field_name] or "default"
        if value == "show":
            return True
        if value == "hide":
            return False
        return bool(default_enabled)

    @api.model
    def ensure_training_menu(self):
        parent = self.search([("slug", "=", "capacitacion"), ("website_id", "=", False)], limit=1)
        if not parent:
            parent = self.create(
                {
                    "name": "Capacitación",
                    "slug": "capacitacion",
                    "sequence": 95,
                    "menu_only": True,
                    "description": "Capacitaciones, charlas y programas formativos de LatinPyme.",
                }
            )
        elif not parent.menu_only:
            parent.write({"menu_only": True})

        children = [
            ("Programación anual", "programacion-anual", 96),
            ("Charlas", "charlas", 97),
            ("Diplomados", "diplomados", 98),
            ("Flashtraining", "flashtraining", 99),
        ]
        for name, slug, sequence in children:
            child = self.search([("slug", "=", slug), ("website_id", "=", False)], limit=1)
            if child:
                values = {}
                if child.parent_id != parent:
                    values["parent_id"] = parent.id
                if child.menu_only:
                    values["menu_only"] = False
                if values:
                    child.write(values)
                continue
            self.create(
                {
                    "name": name,
                    "slug": slug,
                    "sequence": sequence,
                    "parent_id": parent.id,
                    "menu_only": False,
                    "description": "%s de Revista LatinPyme." % name,
                }
            )
        return True

    @api.model
    def ensure_portfolio_menu(self):
        parent = self.search([("slug", "=", "portafolio"), ("website_id", "=", False)], limit=1)
        if not parent:
            parent = self.create(
                {
                    "name": "Portafolio",
                    "slug": "portafolio",
                    "sequence": 90,
                    "menu_only": True,
                    "description": "Servicios, formacion, eventos y soluciones de LatinPyme.",
                }
            )
        else:
            values = {"menu_only": True}
            if not parent.sequence:
                values["sequence"] = 90
            parent.write(values)

        groups = [
            (
                "Aprendizaje empresarial",
                "aprendizaje-empresarial",
                91,
                [
                    ("Capacitación a la medida", "capacitacion-a-la-medida", 911),
                    ("Fidelización empresarial", "fidelizacion-empresarial", 912),
                    ("Cursos de actualización", "cursos-de-actualizacion", 913),
                ],
            ),
            (
                "Tecnología: Salones y Espacios",
                "tecnologia-salones-y-espacios",
                92,
                [
                    ("LMS - Aulas", "lms-aulas", 921),
                    ("Salón de Eventos", "salon-de-eventos", 922),
                ],
            ),
            (
                "Inteligencia Artificial",
                "inteligencia-artificial",
                93,
                [
                    ("Automatización de procesos con IA", "automatizacion-de-procesos-con-ia", 931),
                ],
            ),
        ]

        for group_name, group_slug, group_sequence, children in groups:
            group = self.search([("slug", "=", group_slug), ("website_id", "=", False)], limit=1)
            group_values = {
                "name": group_name,
                "sequence": group_sequence,
                "parent_id": parent.id,
                "menu_only": True,
            }
            if group:
                group.write(group_values)
            else:
                group = self.create(
                    dict(
                        group_values,
                        slug=group_slug,
                        description="%s de Portafolio LatinPyme." % group_name,
                    )
                )

            for child_name, child_slug, child_sequence in children:
                child = self.search([("slug", "=", child_slug), ("website_id", "=", False)], limit=1)
                child_values = {
                    "name": child_name,
                    "sequence": child_sequence,
                    "parent_id": group.id,
                    "menu_only": False,
                }
                if child:
                    child.write(child_values)
                    continue
                self.create(
                    dict(
                        child_values,
                        slug=child_slug,
                        description="%s de Revista LatinPyme." % child_name,
                    )
                )
        return True


class LatinpymeRevistaBlogPostOverride(models.Model):
    _name = "latinpyme.revista.blog.post.override"
    _description = "Control editorial por nota Revista LatinPyme"
    _order = "post_id"

    post_id = fields.Many2one(
        "blog.post",
        string="Nota de Blog",
        required=True,
        ondelete="cascade",
        help="Selecciona la publicacion de Odoo Blog que tendra controles editoriales propios.",
    )
    name = fields.Char(string="Nombre", related="post_id.name", store=True, readonly=True)
    active = fields.Boolean(
        string="Activo",
        default=True,
        help="Si esta desactivado, la nota usa la configuracion de su seccion o la configuracion global.",
    )
    sidebar_mode = fields.Selection(
        DISPLAY_MODE_SELECTION,
        string="Sidebar",
        default="default",
        required=True,
        help="Controla si esta nota muestra el sidebar editorial.",
    )
    related_posts_mode = fields.Selection(
        DISPLAY_MODE_SELECTION,
        string="Articulos relacionados",
        default="default",
        required=True,
        help="Controla si esta nota muestra articulos relacionados al final.",
    )
    interviews_mode = fields.Selection(
        DISPLAY_MODE_SELECTION,
        string="Entrevistas relacionadas",
        default="default",
        required=True,
        help="Controla si esta nota muestra entrevistas relacionadas.",
    )
    portfolio_mode = fields.Selection(
        DISPLAY_MODE_SELECTION,
        string="Portafolio",
        default="default",
        required=True,
        help="Controla si esta nota muestra el bloque Portafolio.",
    )
    allies_mode = fields.Selection(
        DISPLAY_MODE_SELECTION,
        string="Aliados",
        default="default",
        required=True,
        help="Controla si esta nota muestra el carrusel de aliados.",
    )
    note_banner_id = fields.Many2one(
        "latinpyme.revista.banner",
        string="Banner especifico",
        domain=[("placement", "=", "note")],
        help="Opcional. Si se selecciona, reemplaza el banner global de notas.",
    )
    seo_title = fields.Char(
        string="Titulo SEO",
        help="Opcional. Se usa para metadatos sociales de esta nota sin cambiar el titulo visible.",
    )
    seo_description = fields.Text(
        string="Descripcion SEO",
        help="Opcional. Se usa como descripcion SEO/social de esta nota.",
    )
    canonical_url = fields.Char(
        string="URL final SEO",
        help="Opcional. Usar solo cuando SEO defina una URL absoluta validada para esta nota.",
    )

    _sql_constraints = [
        ("post_unique", "unique(post_id)", "Cada nota solo puede tener un control editorial activo o inactivo."),
    ]

    @api.constrains("canonical_url")
    def _check_canonical_url(self):
        for record in self:
            url = (record.canonical_url or "").strip()
            if url and not url.startswith(("https://", "http://")):
                raise ValidationError("La URL final SEO debe iniciar con http:// o https://.")

    @api.model
    def get_for_post(self, post):
        if not post:
            return self.browse()
        post_id = post.id if hasattr(post, "id") else int(post)
        return self.search([("post_id", "=", post_id), ("active", "=", True)], limit=1)

    def display_mode_enabled(self, field_name, default_enabled=True):
        if not self:
            return default_enabled
        mode = self[:1][field_name]
        if mode == "show":
            return True
        if mode == "hide":
            return False
        return default_enabled


class LatinpymeRevistaHomeBlock(models.Model):
    _name = "latinpyme.revista.home.block"
    _description = "Bloque del Home Revista LatinPyme"
    _order = "sequence, id"

    name = fields.Char(string="Nombre interno", required=True)
    block_type = fields.Selection(HOME_BLOCK_TYPES, string="Bloque", required=True, default="hero", index=True)
    active = fields.Boolean(string="Activo", default=True)
    sequence = fields.Integer(string="Orden", default=10)
    title = fields.Char(string="Titulo visible")
    tag_id = fields.Many2one(
        "blog.tag",
        string="Etiqueta fuente",
        help="Si se configura, el bloque tomara notas de esta etiqueta.",
    )
    post_ids = fields.Many2many(
        "blog.post",
        "latinpyme_revista_home_block_post_rel",
        "block_id",
        "post_id",
        string="Notas seleccionadas",
        help="Opcional. Si se seleccionan notas, se usan antes que la regla por etiqueta.",
    )
    limit = fields.Integer(string="Cantidad de notas", default=3)
    link_label = fields.Char(string="Texto del enlace")
    link_url = fields.Char(string="URL del enlace")
    website_id = fields.Many2one("website", string="Sitio web", ondelete="cascade")

    @api.onchange("block_type")
    def _onchange_block_type(self):
        labels = dict(HOME_BLOCK_TYPES)
        for record in self:
            if record.block_type:
                label = labels.get(record.block_type)
                if not record.name:
                    record.name = label
                if not record.title:
                    record.title = label

    @api.constrains("limit")
    def _check_limit(self):
        for record in self:
            if record.limit < 1:
                raise ValidationError("La cantidad de notas debe ser mayor que cero.")

    @api.model
    def get_block(self, block_type, website=None):
        domain = [("active", "=", True), ("block_type", "=", block_type)]
        if website:
            website_record = self.search(domain + [("website_id", "=", website.id)], order="sequence, id", limit=1)
            if website_record:
                return website_record
        return self.search(domain + [("website_id", "=", False)], order="sequence, id", limit=1)

    @api.model
    def get_blocks_map(self, website=None):
        return {block_type: self.get_block(block_type, website=website) for block_type, _label in HOME_BLOCK_TYPES}

    @api.model
    def ensure_default_blocks(self):
        defaults = [
            ("top_banners", "Banners superiores", 5, 2, False, False),
            ("hero", "Hero y destacados", 10, 3, False, False),
            ("latest", "De interés", 20, 6, False, "/blog"),
            ("sections", "Secciones", 30, 1, False, False),
            ("news", "Novedades", 40, 5, False, False),
            ("interviews", "Entrevistas", 50, 3, "Entrevistas", "/revista/seccion/entrevistas"),
            ("specials", "Especiales", 60, 2, "Especiales", "/revista/seccion/especiales"),
            ("mid_banners", "Banners intermedios", 70, 3, False, False),
            ("portfolio", "Portafolio", 80, 3, False, "/revista/seccion/portafolio"),
            ("allies", "Aliados", 90, 8, False, False),
        ]
        Tag = self.env["blog.tag"].sudo()
        for block_type, title, sequence, limit, tag_name, link_url in defaults:
            block = self.search([("block_type", "=", block_type), ("website_id", "=", False)], limit=1)
            tag = Tag.search([("name", "=ilike", tag_name)], limit=1) if tag_name else False
            values = {
                "name": title,
                "title": title,
                "sequence": sequence,
                "limit": limit,
                "link_url": link_url or False,
            }
            if tag:
                values["tag_id"] = tag.id
            if block:
                missing_values = {key: value for key, value in values.items() if value and not block[key]}
                if missing_values:
                    block.write(missing_values)
                continue
            self.create(dict(values, block_type=block_type, active=True))
        return True


class LatinpymeRevistaPortfolioItem(models.Model):
    _name = "latinpyme.revista.portfolio.item"
    _description = "Item de Portafolio Revista LatinPyme"
    _order = "sequence, name"

    name = fields.Char(string="Titulo", required=True)
    category = fields.Char(string="Categoria")
    icon_class = fields.Char(string="Icono FontAwesome", default="fa fa-graduation-cap")
    image = fields.Image(string="Imagen", max_width=1024, max_height=768)
    bullet_1 = fields.Char(string="Bullet 1")
    bullet_2 = fields.Char(string="Bullet 2")
    bullet_3 = fields.Char(string="Bullet 3")
    bullet_4 = fields.Char(string="Bullet 4")
    bullet_5 = fields.Char(string="Bullet 5")
    contact_label = fields.Char(string="Texto boton WhatsApp", default="Contactanos")
    contact_url = fields.Char(string="URL boton WhatsApp", default="/contactus")
    agenda_label = fields.Char(string="Texto boton agenda", default="Agenda una cita")
    agenda_url = fields.Char(string="URL boton agenda", default="/appointment")
    active = fields.Boolean(string="Activo", default=True)
    sequence = fields.Integer(string="Orden", default=10)
    website_id = fields.Many2one("website", string="Sitio web", ondelete="cascade")

    def bullet_lines(self):
        self.ensure_one()
        return [line for line in (self.bullet_1, self.bullet_2, self.bullet_3, self.bullet_4, self.bullet_5) if line]

    @api.model
    def get_active_items(self, website=None, limit=None):
        website = website or _current_website()
        domain = [("active", "=", True)]
        if website:
            domain.append(("website_id", "in", [False, website.id]))
        return self.search(domain, order="sequence, name", limit=limit)

    @api.model
    def ensure_default_items(self):
        defaults = [
            {
                "name": "Aprendizaje empresarial",
                "sequence": 10,
                "icon_class": "fa fa-graduation-cap",
                "bullet_1": "Capacitacion a la medida",
                "bullet_2": "Fidelizacion empresarial",
                "bullet_3": "Cursos de actualizacion",
            },
            {
                "name": "Tecnologia: salones y espacios",
                "sequence": 20,
                "icon_class": "fa fa-calendar-o",
                "bullet_1": "LMS - Aulas",
                "bullet_2": "Salon de Eventos",
            },
            {
                "name": "Inteligencia artificial",
                "sequence": 30,
                "icon_class": "fa fa-microchip",
                "bullet_1": "Automatizacion de procesos con IA",
            },
        ]
        for values in defaults:
            item = self.search([("name", "=ilike", values["name"]), ("website_id", "=", False)], limit=1)
            if item:
                continue
            self.create(dict(values, active=True))
        return True


class LatinpymeRevistaInterview(models.Model):
    _name = "latinpyme.revista.interview"
    _description = "Entrevista Revista LatinPyme"
    _order = "sequence, interview_date desc, name"

    name = fields.Char(string="Titulo", required=True)
    interviewee_name = fields.Char(string="Nombre del entrevistado")
    role = fields.Char(string="Cargo")
    company = fields.Char(string="Empresa")
    summary = fields.Text(string="Resumen")
    youtube_url = fields.Char(string="URL de YouTube")
    link_url = fields.Char(
        string="URL alternativa",
        help="Opcional. Se usa si no hay URL de YouTube ni nota relacionada.",
    )
    post_id = fields.Many2one("blog.post", string="Nota relacionada", ondelete="set null")
    section_ids = fields.Many2many(
        "latinpyme.revista.section",
        "latinpyme_revista_interview_section_rel",
        "interview_id",
        "section_id",
        string="Secciones",
        help="Selecciona una o varias secciones donde debe aparecer esta entrevista. Si se deja vacio, puede mostrarse como entrevista general.",
    )
    image = fields.Image(string="Imagen", max_width=1600, max_height=900)
    interview_date = fields.Date(string="Fecha")
    active = fields.Boolean(string="Activo", default=True)
    featured = fields.Boolean(string="Destacada")
    sequence = fields.Integer(string="Orden", default=10)
    website_id = fields.Many2one("website", string="Sitio web", ondelete="cascade")

    def target_url(self):
        self.ensure_one()
        if self.youtube_url:
            return self.youtube_url
        if self.post_id and self.post_id.website_url:
            return self.post_id.website_url
        return self.link_url or "/revista/seccion/entrevistas"

    def youtube_video_id(self):
        self.ensure_one()
        url = (self.youtube_url or "").strip()
        if not url or url == "#":
            return False
        patterns = [
            r"(?:youtube\.com/watch\?[^#]*v=)([A-Za-z0-9_-]{11})",
            r"(?:youtube\.com/embed/)([A-Za-z0-9_-]{11})",
            r"(?:youtube\.com/shorts/)([A-Za-z0-9_-]{11})",
            r"(?:youtube\.com/live/)([A-Za-z0-9_-]{11})",
            r"(?:youtu\.be/)([A-Za-z0-9_-]{11})",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return False

    def youtube_thumbnail_url(self):
        self.ensure_one()
        video_id = self.youtube_video_id()
        return video_id and "https://img.youtube.com/vi/%s/hqdefault.jpg" % video_id or False

    def person_label(self):
        self.ensure_one()
        return self.interviewee_name or self.name

    def meta_label(self):
        self.ensure_one()
        parts = [value for value in (self.role, self.company) if value]
        return " - ".join(parts)

    def section_label(self):
        self.ensure_one()
        section = self.section_ids[:1]
        return section.name if section else "Entrevistas"

    @api.model
    def get_active_interviews(self, website=None, section=None, limit=None):
        website = website or _current_website()
        domain = [("active", "=", True)]
        if website:
            domain.append(("website_id", "in", [False, website.id]))
        if section:
            domain.extend(["|", ("section_ids", "=", False), ("section_ids", "in", section.id)])
        return self.search(domain, order="sequence, interview_date desc, id desc", limit=limit)


class LatinpymeRevistaSidebarItem(models.Model):
    _name = "latinpyme.revista.sidebar.item"
    _description = "Contenido del Sidebar Revista LatinPyme"
    _order = "placement, sequence, name"

    name = fields.Char(string="Nombre interno", required=True)
    placement = fields.Selection(SIDEBAR_PLACEMENTS, string="Ubicacion", required=True, default="global")
    item_type = fields.Selection(SIDEBAR_ITEM_TYPES, string="Tipo de bloque", required=True, default="conference")
    active = fields.Boolean(string="Activo", default=True)
    sequence = fields.Integer(string="Orden", default=10)
    label = fields.Char(string="Etiqueta superior")
    title = fields.Char(string="Titulo")
    text = fields.Text(string="Texto")
    date_text = fields.Char(string="Fecha visible")
    location_text = fields.Char(string="Lugar")
    time_text = fields.Char(string="Hora")
    button_label = fields.Char(string="Texto del boton")
    url = fields.Char(string="URL")
    image = fields.Image(string="Imagen", max_width=1200, max_height=900)
    banner_id = fields.Many2one(
        "latinpyme.revista.banner",
        string="Banner relacionado",
        domain=[("placement", "=", "sidebar")],
    )
    poll_option_1 = fields.Char(string="Opcion 1")
    poll_option_2 = fields.Char(string="Opcion 2")
    poll_option_3 = fields.Char(string="Opcion 3")
    poll_option_4 = fields.Char(string="Opcion 4")
    website_id = fields.Many2one("website", string="Sitio web", ondelete="cascade")

    def poll_options(self):
        self.ensure_one()
        return [option for option in (self.poll_option_1, self.poll_option_2, self.poll_option_3, self.poll_option_4) if option]

    @api.model
    def _active_domain(self, placement, website=None):
        website = website or _current_website()
        domain = [("active", "=", True), ("placement", "=", placement or "global")]
        if website:
            domain.append(("website_id", "in", [False, website.id]))
        return domain

    @api.model
    def get_active_items(self, placement="global", website=None):
        placement = placement or "global"
        items = self.search(self._active_domain(placement, website=website), order="sequence, id")
        if items or placement == "global":
            return items
        return self.search(self._active_domain("global", website=website), order="sequence, id")

    @api.model
    def get_active_item(self, placement="global", item_type=False, website=None):
        placement = placement or "global"
        domain = self._active_domain(placement, website=website)
        if item_type:
            domain.append(("item_type", "=", item_type))
        item = self.search(domain, order="sequence, id", limit=1)
        if item or placement == "global":
            return item

        fallback_domain = self._active_domain("global", website=website)
        if item_type:
            fallback_domain.append(("item_type", "=", item_type))
        return self.search(fallback_domain, order="sequence, id", limit=1)

    @api.model
    def ensure_default_items(self):
        defaults = [
            {
                "name": "Proxima conferencia",
                "placement": "global",
                "item_type": "conference",
                "sequence": 10,
                "label": "Proxima conferencia",
                "title": "Liderazgo y cultura organizacional: claves para el futuro",
                "date_text": "25 de junio de 2024",
                "location_text": "Bogota, Colombia",
                "time_text": "9:00 a.m. - 12:00 m.",
                "button_label": "Mas informacion",
                "url": "/event",
            },
            {
                "name": "Encuesta empresarial",
                "placement": "global",
                "item_type": "poll",
                "sequence": 20,
                "label": "Encuesta",
                "title": "¿Cual es el mayor desafio de tu empresa este año?",
                "poll_option_1": "Acceso a financiamiento",
                "poll_option_2": "Transformacion digital",
                "poll_option_3": "Atraccion y retencion de talento",
                "poll_option_4": "Aumento de costos",
                "button_label": "Votar",
            },
            {
                "name": "Banner lateral automatizacion",
                "placement": "global",
                "item_type": "banner",
                "sequence": 30,
                "title": "Automatiza procesos, optimiza recursos y crece sin limites.",
                "button_label": "Conoce mas",
                "url": "/contactus",
            },
        ]
        for values in defaults:
            item = self.search(
                [
                    ("name", "=ilike", values["name"]),
                    ("placement", "=", values["placement"]),
                    ("website_id", "=", False),
                ],
                limit=1,
            )
            if item:
                continue
            self.create(dict(values, active=True))
        return True


class LatinpymeRevistaAlly(models.Model):
    _name = "latinpyme.revista.ally"
    _description = "Aliado Revista LatinPyme"
    _order = "sequence, name"

    name = fields.Char(string="Nombre", required=True)
    logo = fields.Image(string="Logo", max_width=1024, max_height=512)
    url = fields.Char(string="URL")
    active = fields.Boolean(string="Activo", default=True)
    sequence = fields.Integer(string="Orden", default=10)
    website_id = fields.Many2one("website", string="Sitio web", ondelete="cascade")

    @api.model
    def get_active_allies(self, website=None):
        website = website or _current_website()
        domain = [("active", "=", True)]
        if website:
            domain.append(("website_id", "in", [False, website.id]))
        return self.search(domain, order="sequence, id")

    @api.model
    def get_active_ally_slides(self, website=None, per_slide=8):
        allies = self.get_active_allies(website)
        per_slide = max(int(per_slide or 8), 1)
        return [allies[index:index + per_slide] for index in range(0, len(allies), per_slide)]


class LatinpymeRevistaBanner(models.Model):
    _name = "latinpyme.revista.banner"
    _description = "Publicidad Revista LatinPyme"
    _order = "sequence, name"

    name = fields.Char(string="Nombre", required=True)
    placement = fields.Selection(
        [
            ("home_top", "Home hero superior"),
            ("home_horizontal", "Home publicidad horizontal 582x149"),
            ("home_news", "Home novedades publicidad 281x127"),
            ("home_specials", "Home especiales publicidad 384x169"),
            ("sidebar", "Sidebar"),
            ("footer", "Footer"),
            ("note", "Nota individual"),
            ("section", "Seccion hero superior"),
            ("program_hero", "Programacion anual hero"),
        ],
        string="Ubicacion",
        required=True,
        default="sidebar",
    )
    display_mode = fields.Selection(
        [
            ("image_only", "Solo imagen"),
            ("text_overlay", "Imagen con texto"),
        ],
        string="Modo visual",
        default="image_only",
        help="Usa Solo imagen para banners sin textos, botones ni overlays. Hero: 1181x161. Home publicidad horizontal: 582x149. Home novedades: 281x127. Home especiales: 384x169.",
    )
    image = fields.Image(string="Imagen", max_width=1920, max_height=1080)
    title = fields.Char(string="Titulo")
    text = fields.Text(string="Texto")
    button_label = fields.Char(string="Texto del boton", default="Conoce mas")
    url = fields.Char(string="URL", default="/contactus")
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
        website = website or _current_website()
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
    def _available_until_domain(self, placement, website=None):
        website = website or _current_website()
        today = fields.Date.context_today(self)
        domain = [
            ("active", "=", True),
            ("placement", "=", placement),
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
        return self.get_active_banners(placement, website=website, limit=1)

    @api.model
    def get_program_hero_banner(self, website=None):
        banner = self.get_active_banner("program_hero", website=website)
        if banner:
            return banner
        return self.search(self._available_until_domain("program_hero", website=website), order="sequence, id", limit=1)


class LatinpymeRevistaProgramEvent(models.Model):
    _name = "latinpyme.revista.program.event"
    _description = "Evento Programacion anual Revista LatinPyme"
    _order = "date_start, time_start, sequence, name"

    name = fields.Char(string="Nombre", required=True)
    event_type = fields.Selection(
        PROGRAM_EVENT_TYPES,
        string="Tipo de evento",
        required=True,
        default="charlas",
    )
    date_start = fields.Date(string="Fecha de inicio", required=True, default=fields.Date.context_today)
    date_end = fields.Date(string="Fecha de fin")
    display_days = fields.Char(
        string="Dias visibles",
        help="Usar para agendas con fechas no consecutivas. Ejemplo: 13|14|19|20|21|26|27|28.",
    )
    time_start = fields.Float(string="Hora de inicio", required=True, default=9.0)
    time_end = fields.Float(string="Hora de fin", required=True, default=10.0)
    timezone = fields.Char(string="Zona horaria", default="America/Bogota", required=True)
    modality = fields.Selection(
        [
            ("virtual", "Virtual"),
            ("presencial", "Presencial"),
            ("hibrida", "Hibrida"),
        ],
        string="Modalidad",
        required=True,
        default="virtual",
    )
    location = fields.Char(string="Lugar o enlace")
    description = fields.Text(string="Descripcion")
    image = fields.Image(string="Imagen", max_width=1600, max_height=900)
    registration_url = fields.Char(string="Enlace de inscripcion")
    button_label = fields.Char(string="Texto del boton", default="Inscribirme")
    active = fields.Boolean(string="Activo", default=True)
    featured = fields.Boolean(string="Destacado")
    sequence = fields.Integer(string="Orden", default=10)
    website_id = fields.Many2one("website", string="Sitio web", ondelete="cascade")

    @api.model
    def _normalize_event_type_value(self, value):
        return PROGRAM_EVENT_TYPE_LEGACY_MAP.get(value, value)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("event_type"):
                vals["event_type"] = self._normalize_event_type_value(vals["event_type"])
        return super().create(vals_list)

    def write(self, vals):
        if vals.get("event_type"):
            vals["event_type"] = self._normalize_event_type_value(vals["event_type"])
        return super().write(vals)

    @api.model
    def migrate_legacy_event_types(self):
        for old_value, new_value in PROGRAM_EVENT_TYPE_LEGACY_MAP.items():
            self.search([("event_type", "=", old_value)]).write({"event_type": new_value})
        return True

    @api.model
    def archive_removed_event_types(self):
        self.search([("event_type", "in", list(REMOVED_PROGRAM_EVENT_TYPES))]).write({"active": False})
        return True

    @api.model
    def get_event_type_options(self):
        return list(PROGRAM_EVENT_TYPES)

    @api.model
    def get_event_type_filter_options(self):
        return [
            {"key": "type:%s" % key, "label": label}
            for key, label in self.get_event_type_options()
        ]

    @api.model
    def ensure_program_2026_events(self):
        school_url = "https://escuela.latinpyme.com/"
        events = [
            ("diplomados", 101, "1. DIPLOMADO: Actualizacion Tributaria 2026.", "2026-01-13", "2026-01-28", "13|14|19|20|21|26|27|28", 18.5, 20.5),
            ("charlas", 102, "Charla empresarial 1: La ventaja competitiva de integrar IA sin perder el ADN empresarial.", "2026-01-14", False, "14", 9.0, 10.0),
            ("charlas", 103, "Charla empresarial 2: Contratacion y jornada laboral bajo la reforma laboral.", "2026-01-21", False, "21", 9.0, 10.0),
            ("charlas", 104, "Charla empresarial 3: Claves para Transformar la Cultura Organizacional.", "2026-01-28", False, "28", 9.0, 10.0),
            ("diplomados", 201, "1. DIPLOMADO: Reforma laboral 2025 y su impacto en la gestion empresarial.", "2026-02-09", False, "9", 18.5, 20.5),
            ("flashtraining", 202, "2. FLASH TRAINING: Declaracion de renta para empresas.", "2026-02-26", "2026-02-27", "26|27", 9.0, 10.0),
            ("charlas", 203, "Charla empresarial 1: ¿Como liquidar bien las cesantias y evitar sanciones?", "2026-02-04", False, "4", 9.0, 10.0),
            ("charlas", 204, "Charla Empresarial 2: Transforma los procesos de formacion con tecnologia amigable.", "2026-02-11", False, "11", 9.0, 10.0),
            ("charlas", 205, "Charla Empresarial 3: Ventas Agiles con IA.", "2026-02-18", False, "18", 9.0, 10.0),
            ("charlas", 206, "Charla Empresarial 4: Liderazgo colaborativo: fomentar el trabajo en equipo de alto rendimiento.", "2026-02-25", False, "25", 9.0, 10.0),
            ("diplomados", 301, "1. DIPLOMADO: Gestion de servicio al cliente y cultura de experiencia.", "2026-03-09", "2026-03-25", "9|10|11|16|17|18|24|25", 18.5, 20.5),
            ("flashtraining", 302, "2. FLASH TRAINING: Excel - Nivel Basico.", "2026-03-26", "2026-03-27", "26|27", 9.0, 10.0),
            ("charlas", 303, "Charla empresarial 1: Gestion emocional y liderazgo consciente.", "2026-03-04", False, "4", 9.0, 10.0),
            ("charlas", 304, "Charla empresarial 2: ¿Que responsabilidades tienen las empresas frente a la prevencion del riesgo psicosocial?", "2026-03-11", False, "11", 9.0, 10.0),
            ("charlas", 305, "Charla empresarial 3: Estrategias efectivas para liderar equipos efectivos.", "2026-03-18", False, "18", 9.0, 10.0),
            ("charlas", 306, "Charla empresarial 4: Como Presentar un Presupuesto Ejecutivo: Visual, Claro y Estrategico.", "2026-03-25", False, "25", 9.0, 10.0),
            ("diplomados", 401, "1. DIPLOMADO: Competencias del futuro y desarrollo del talento.", "2026-04-06", "2026-04-21", "6|7|8|13|14|15|20|21", 18.5, 20.5),
            ("foros", 402, "2. FORO: ¿Cual es el panorama economico en Colombia?", "2026-04-23", False, "23", 9.0, 10.0),
            ("charlas", 403, "Charla empresarial 1: Conecta, Inspira y Lidera con Emocion.", "2026-04-08", False, "8", 9.0, 10.0),
            ("charlas", 404, "Charla empresarial 2: Marketing emocional: conectar con personas, no con consumidores.", "2026-04-15", False, "15", 9.0, 10.0),
            ("charlas", 405, "Charla empresarial 3: Ciberseguridad: Protegiendo la Innovacion.", "2026-04-22", False, "22", 9.0, 10.0),
            ("charlas", 406, "Charla empresarial 4: Como actualizar su reglamento Interno bajo la reforma laboral.", "2026-04-29", False, "29", 9.0, 10.0),
            ("diplomados", 501, "1. DIPLOMADO: Cambios claves de la nueva Ley sobre salud mental laboral.", "2026-05-04", "2026-05-20", "4|5|6|11|12|13|19|20", 18.5, 20.5),
            ("flashtraining", 502, "2. FLASH TRAINING: Power BI - Nivel Basico.", "2026-05-21", "2026-05-22", "21|22", 9.0, 10.0),
            ("charlas", 503, "Charla empresarial 1: El futuro de las comunidades digitales: del seguidor al fan leal.", "2026-05-06", False, "6", 9.0, 10.0),
            ("charlas", 504, "Charla empresarial 2: ¿Esta mi pension segura con la reforma?", "2026-05-13", False, "13", 9.0, 10.0),
            ("charlas", 505, "Charla empresarial 3: Liderazgo Basado en la comprension y el respeto.", "2026-05-20", False, "20", 9.0, 10.0),
            ("charlas", 506, "Charla empresarial 4: Tres IA que Potencian los equipos de trabajo.", "2026-05-27", False, "27", 9.0, 10.0),
            ("diplomados", 601, "1. DIPLOMADO: Finanzas con vision estrategica.", "2026-06-09", "2026-06-24", "9|10|16|17|22|23|24", 18.5, 20.5),
            ("charlas", 602, "Charla empresarial 1: Obligaciones de la empresa en materia de seguridad social.", "2026-06-03", False, "3", 9.0, 10.0),
            ("charlas", 603, "Charla empresarial 2: El Poder de Innovar con Proposito.", "2026-06-10", False, "10", 9.0, 10.0),
            ("charlas", 604, "Charla empresarial 3: Nuevas formas de atraer, encantar y fidelizar clientes.", "2026-06-17", False, "17", 9.0, 10.0),
            ("charlas", 605, "Charla empresarial 4: IA para disenar el perfil de cargos.", "2026-06-24", False, "24", 9.0, 10.0),
            ("diplomados", 701, "1. DIPLOMADO: Economia Circular como Estrategia de Valor Sostenible.", "2026-07-06", "2026-07-22", "6|7|8|13|14|15|21|22", 18.5, 20.5),
            ("foros", 702, "2. FORO: Los retos del sector empresarial frente a la Inteligencia Artificial.", "2026-07-23", False, "23", 9.0, 10.0),
            ("charlas", 703, "Charla empresarial 1: Futuro de las ventas en redes sociales con IA.", "2026-07-01", False, "1", 9.0, 10.0),
            ("charlas", 704, "Charla empresarial 2: Conozca como aplicar la bateria de riesgo psicosocial segun la nueva ley.", "2026-07-08", False, "8", 9.0, 10.0),
            ("charlas", 705, "Charla empresarial 3: Tableros y control de gastos con IA (alertas y anomalias).", "2026-07-15", False, "15", 9.0, 10.0),
            ("charlas", 706, "Charla empresarial 4: El Rol del Feedback Continuo en el Desarrollo del Talento.", "2026-07-22", False, "22", 9.0, 10.0),
            ("charlas", 707, "Charla empresarial 5: Practicas efectivas para fomentar compromiso y pertenencia.", "2026-07-29", False, "29", 9.0, 10.0),
            ("diplomados", 801, "1. DIPLOMADO: Employee Engagement: estrategias para conectar, motivar y retener el talento humano.", "2026-08-03", "2026-08-19", "3|4|5|10|11|12|18|19", 18.5, 20.5),
            ("flashtraining", 802, "2. FLASH TRAINING: Marketing y ventas en la era de la IA.", "2026-08-20", "2026-08-21", "20|21", 9.0, 10.0),
            ("charlas", 803, "Charla empresarial 1: Auditoria interna para prevenir sanciones de la UGPP.", "2026-08-05", False, "5", 9.0, 10.0),
            ("charlas", 804, "Charla empresarial 2: Habitos Financieros para el Exito Personal y Profesional.", "2026-08-12", False, "12", 9.0, 10.0),
            ("charlas", 805, "Charla empresarial 3: Ventas 5.0: Estrategias inteligentes con IA.", "2026-08-19", False, "19", 9.0, 10.0),
            ("charlas", 806, "Charla empresarial 4: Del Problema a la Solucion: Innovacion Agil en la Practica.", "2026-08-26", False, "26", 9.0, 10.0),
            ("diplomados", 901, "1. DIPLOMADO: Transformacion Digital y Analitica de Datos.", "2026-09-07", "2026-09-22", "7|8|9|14|15|16|21|22", 18.5, 20.5),
            ("flashtraining", 902, "2. FLASH TRAINING: Responsabilidad Social (RSE).", "2026-09-24", "2026-09-25", "24|25", 9.0, 10.0),
            ("charlas", 903, "Charla empresarial 1: Como Optimizar Presupuestos Limitados en su area de trabajo.", "2026-09-02", False, "2", 9.0, 10.0),
            ("charlas", 904, "Charla empresarial 2: Promocion del bienestar mental en la empresa como lo exige la Ley.", "2026-09-09", False, "9", 9.0, 10.0),
            ("charlas", 905, "Charla empresarial 3: Equipos del futuro: liderar personas en entornos inteligentes y automatizados.", "2026-09-16", False, "16", 9.0, 10.0),
            ("charlas", 906, "Charla empresarial 4: Que decidir, que hacer, que delegar y que eliminar.", "2026-09-23", False, "23", 9.0, 10.0),
            ("charlas", 907, "Charla empresarial 5: Como liquidar bien la nomina y seguridad social.", "2026-09-30", False, "30", 9.0, 10.0),
            ("diplomados", 1001, "1. DIPLOMADO: Gestion laboral para No Abogados.", "2026-10-05", "2026-10-21", "5|6|7|13|14|19|20|21", 18.5, 20.5),
            ("flashtraining", 1002, "2. FLASH TRAINING: Obligaciones de la empresa en seguridad social.", "2026-10-22", "2026-10-23", "22|23", 9.0, 10.0),
            ("charlas", 1003, "Charla empresarial 1: Innovando para un Futuro Sostenible con IA.", "2026-10-07", False, "7", 9.0, 10.0),
            ("charlas", 1004, "Charla empresarial 2: Del servicio al cliente a la experiencia WOW.", "2026-10-14", False, "14", 9.0, 10.0),
            ("charlas", 1005, "Charla empresarial 3: Conozca como evitar fraudes financieros en la era digital.", "2026-10-21", False, "21", 9.0, 10.0),
            ("charlas", 1006, "Charla empresarial 4: Habilidades blandas en tiempos de IA.", "2026-10-28", False, "28", 9.0, 10.0),
            ("diplomados", 1101, "1. DIPLOMADO: Habilidades Gerenciales para Entornos de Cambio.", "2026-11-03", "2026-11-18", "3|4|9|10|11|17|18", 18.5, 20.5),
            ("foros", 1102, "2. FORO: Los retos del sector empresarial para la recuperacion economica.", "2026-11-26", False, "26", 9.0, 10.0),
            ("charlas", 1103, "Charla empresarial 1: El auge del trabajo hibrido y la inteligencia artificial.", "2026-11-04", False, "4", 9.0, 10.0),
            ("charlas", 1104, "Charla empresarial 2: El Debido Proceso Laboral: Como evitar errores que le cuestan sanciones a la empresa.", "2026-11-11", False, "11", 9.0, 10.0),
            ("charlas", 1105, "Charla empresarial 3: Agentes IA aplicados a Marketing.", "2026-11-18", False, "18", 9.0, 10.0),
            ("charlas", 1106, "Charla Empresarial 4: Claves para proyectar un plan de capacitacion efectivo hacia el 2027.", "2026-11-25", False, "25", 9.0, 10.0),
            ("diplomados", 1201, "1. DIPLOMADO: Human Power: el liderazgo que inspira transformacion.", "2026-12-01", "2026-12-16", "1|2|7|9|14|15|16", 18.5, 20.5),
            ("charlas", 1202, "Charla empresarial 1: Storytelling corporativo: el arte de contar historias que posicionan.", "2026-12-02", False, "2", 9.0, 10.0),
            ("charlas", 1203, "Charla empresarial 2: Finanzas con Intencion.", "2026-12-09", False, "9", 9.0, 10.0),
            ("charlas", 1204, "Charla empresarial 3: Sindrome de agotamiento laboral - Burnout.", "2026-12-16", False, "16", 9.0, 10.0),
        ]
        for event_type, sequence, name, date_start, date_end, display_days, time_start, time_end in events:
            vals = {
                "active": True,
                "featured": False,
                "sequence": sequence,
                "name": name,
                "event_type": event_type,
                "date_start": date_start,
                "date_end": date_end or date_start,
                "display_days": display_days,
                "time_start": time_start,
                "time_end": time_end,
                "timezone": "America/Bogota",
                "modality": "virtual",
                "location": school_url,
                "registration_url": school_url,
                "button_label": "Inscribirme",
                "description": "Dias exactos de programacion: %s" % display_days,
            }
            event = self.search(
                [
                    ("date_start", "=", date_start),
                    ("sequence", "=", sequence),
                ],
                limit=1,
            )
            if not event:
                event = self.search(
                    [
                        ("name", "=", name),
                        ("date_start", "=", date_start),
                    ],
                    limit=1,
                )
            if not event:
                same_day_type = self.search(
                    [
                        ("date_start", "=", date_start),
                        ("event_type", "=", event_type),
                    ]
                )
                if len(same_day_type) == 1:
                    event = same_day_type
            if event:
                event.write(vals)
            else:
                self.create(vals)
        return True

    @api.constrains("date_start", "date_end")
    def _check_dates(self):
        for record in self:
            if record.date_end and record.date_start and record.date_end < record.date_start:
                raise ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio.")

    @api.constrains("time_start", "time_end", "date_start", "date_end")
    def _check_times(self):
        for record in self:
            for field_name in ("time_start", "time_end"):
                value = record[field_name]
                if value < 0 or value > 24:
                    raise ValidationError("Las horas deben estar entre 0:00 y 24:00.")
            same_day = not record.date_end or record.date_end == record.date_start
            if same_day and record.time_end <= record.time_start:
                raise ValidationError("La hora de fin debe ser posterior a la hora de inicio.")

    @api.model
    def get_active_events(self, website=None):
        website = website or _current_website()
        domain = [
            ("active", "=", True),
            ("event_type", "in", [key for key, label in PROGRAM_EVENT_TYPES]),
        ]
        if website:
            domain.append(("website_id", "in", [False, website.id]))
        return self.search(domain, order="date_start, time_start, sequence, id")

    @api.model
    def get_public_event(self, event_id, website=None):
        website = website or _current_website()
        domain = [
            ("id", "=", event_id),
            ("active", "=", True),
            ("event_type", "in", [key for key, label in PROGRAM_EVENT_TYPES]),
        ]
        if website:
            website_record = self.search(domain + [("website_id", "=", website.id)], limit=1)
            if website_record:
                return website_record
        return self.search(domain + [("website_id", "=", False)], limit=1)

    def _split_float_hour(self, value):
        value = float(value or 0.0)
        hours = int(value)
        minutes = int(round((value - hours) * 60))
        if minutes >= 60:
            hours += 1
            minutes = 0
        return hours, minutes

    def _event_datetime(self, end=False):
        self.ensure_one()
        date_value = fields.Date.to_date(self.date_end if end and self.date_end else self.date_start)
        time_value = self.time_end if end else self.time_start
        hours, minutes = self._split_float_hour(time_value)
        if hours >= 24:
            return datetime.combine(date_value + timedelta(days=1), time(0, 0))
        return datetime.combine(date_value, time(hours, minutes))

    def _format_hour(self, value):
        hours, minutes = self._split_float_hour(value)
        suffix = "a.m." if hours < 12 else "p.m."
        display_hour = hours % 12 or 12
        if hours == 24:
            display_hour = 12
            suffix = "a.m."
        return "%s:%02d %s" % (display_hour, minutes, suffix)

    def time_label(self):
        self.ensure_one()
        return "%s - %s" % (self._format_hour(self.time_start), self._format_hour(self.time_end))

    def day_label(self):
        self.ensure_one()
        date_value = fields.Date.to_date(self.date_start)
        return "%02d" % date_value.day

    def month_short_label(self):
        self.ensure_one()
        date_value = fields.Date.to_date(self.date_start)
        return SPANISH_MONTHS_SHORT.get(date_value.month, "")

    def month_group_key(self):
        self.ensure_one()
        date_value = fields.Date.to_date(self.date_start)
        return "%04d-%02d" % (date_value.year, date_value.month)

    def month_group_label(self):
        self.ensure_one()
        date_value = fields.Date.to_date(self.date_start)
        return "%s %s" % (SPANISH_MONTHS.get(date_value.month, ""), date_value.year)

    def date_label(self):
        self.ensure_one()
        start = fields.Date.to_date(self.date_start)
        end = fields.Date.to_date(self.date_end or self.date_start)
        start_label = "%s de %s de %s" % (start.day, SPANISH_MONTHS.get(start.month, ""), start.year)
        if end == start:
            return start_label
        if end.month == start.month and end.year == start.year:
            return "%s al %s de %s de %s" % (start.day, end.day, SPANISH_MONTHS.get(start.month, ""), start.year)
        end_label = "%s de %s de %s" % (end.day, SPANISH_MONTHS.get(end.month, ""), end.year)
        return "%s al %s" % (start_label, end_label)

    def program_days_label(self):
        self.ensure_one()
        return self.display_days or self.date_label()

    def event_type_label(self):
        self.ensure_one()
        return dict(self._fields["event_type"].selection).get(self.event_type, self.event_type)

    def modality_label(self):
        self.ensure_one()
        return dict(self._fields["modality"].selection).get(self.modality, self.modality)

    def location_url(self):
        self.ensure_one()
        location = (self.location or "").strip()
        if location.startswith(("http://", "https://")):
            return location
        return False

    def _calendar_details(self):
        self.ensure_one()
        parts = []
        if self.description:
            parts.append(self.description)
        parts.append("Modalidad: %s" % self.modality_label())
        if self.location:
            parts.append("Lugar/enlace: %s" % self.location)
        if self.registration_url:
            parts.append("Inscripcion: %s" % self.registration_url)
        return "\n".join(parts)

    def calendar_links(self):
        self.ensure_one()
        start = self._event_datetime()
        end = self._event_datetime(end=True)
        if end <= start:
            end = start + timedelta(hours=1)
        details = self._calendar_details()
        google_params = {
            "action": "TEMPLATE",
            "text": self.name,
            "dates": "%s/%s" % (start.strftime("%Y%m%dT%H%M%S"), end.strftime("%Y%m%dT%H%M%S")),
            "details": details,
            "location": self.location or "",
            "ctz": self.timezone or "America/Bogota",
        }
        outlook_params = {
            "path": "/calendar/action/compose",
            "rru": "addevent",
            "subject": self.name,
            "startdt": start.isoformat(),
            "enddt": end.isoformat(),
            "body": details,
            "location": self.location or "",
        }
        return {
            "google": "https://calendar.google.com/calendar/render?%s" % urlencode(google_params),
            "outlook": "https://outlook.office.com/calendar/0/deeplink/compose?%s" % urlencode(outlook_params),
            "apple": "/revista/programacion/%s/ics?calendar=apple" % self.id,
            "ics": "/revista/programacion/%s/ics" % self.id,
        }

    def _ics_escape(self, value):
        value = (value or "").replace("\\", "\\\\")
        return value.replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")

    def ics_filename(self):
        self.ensure_one()
        slug = re.sub(r"[^a-z0-9]+", "-", (self.name or "evento").lower()).strip("-")
        return "%s.ics" % (slug or "evento")

    def ics_content(self):
        self.ensure_one()
        start = self._event_datetime()
        end = self._event_datetime(end=True)
        if end <= start:
            end = start + timedelta(hours=1)
        timezone = self.timezone or "America/Bogota"
        lines = [
            "BEGIN:VCALENDAR",
            "VERSION:2.0",
            "PRODID:-//Revista LatinPyme//Programacion//ES",
            "CALSCALE:GREGORIAN",
            "METHOD:PUBLISH",
            "BEGIN:VEVENT",
            "UID:latinpyme-revista-event-%s@latinpyme.com" % self.id,
            "DTSTAMP:%s" % datetime.utcnow().strftime("%Y%m%dT%H%M%SZ"),
            "DTSTART;TZID=%s:%s" % (timezone, start.strftime("%Y%m%dT%H%M%S")),
            "DTEND;TZID=%s:%s" % (timezone, end.strftime("%Y%m%dT%H%M%S")),
            "SUMMARY:%s" % self._ics_escape(self.name),
            "DESCRIPTION:%s" % self._ics_escape(self._calendar_details()),
            "LOCATION:%s" % self._ics_escape(self.location or ""),
        ]
        if self.registration_url:
            lines.append("URL:%s" % self._ics_escape(self.registration_url))
        lines.extend(["END:VEVENT", "END:VCALENDAR"])
        return "\r\n".join(lines) + "\r\n"
