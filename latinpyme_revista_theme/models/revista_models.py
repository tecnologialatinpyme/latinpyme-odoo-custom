# -*- coding: utf-8 -*-

import re

from odoo import api, fields, models
from odoo.exceptions import ValidationError


SLUG_RE = re.compile(r"^[a-z0-9-]+$")


class LatinpymeRevistaConfig(models.Model):
    _name = "latinpyme.revista.config"
    _description = "Configuracion Revista LatinPyme"
    _order = "website_id, id"

    name = fields.Char(required=True, default="Revista LatinPyme")
    website_id = fields.Many2one("website", string="Sitio web", ondelete="cascade")
    production_domain = fields.Char(default="latinpyme.com")
    preproduction_domain = fields.Char(default="revista.latinpyme.com")
    preproduction_noindex = fields.Boolean(default=True)
    footer_text = fields.Char(default="© 2026 Revista LatinPyme - Todos los derechos reservados")
    phone = fields.Char(default="+57 310 123 4567")
    city = fields.Char(default="Bogota, Colombia")
    email = fields.Char()
    facebook_url = fields.Char(default="#")
    linkedin_url = fields.Char(default="#")
    instagram_url = fields.Char(default="#")
    youtube_url = fields.Char(default="#")
    whatsapp_url = fields.Char(default="#")
    show_home_banners = fields.Boolean(default=True)
    show_home_interviews = fields.Boolean(default=True)
    show_home_specials = fields.Boolean(default=True)
    show_home_portfolio = fields.Boolean(default=True)
    show_home_allies = fields.Boolean(default=True)
    home_highlight_limit = fields.Integer(default=3)
    home_latest_limit = fields.Integer(default=6)
    home_new_limit = fields.Integer(default=5)
    section_posts_per_page = fields.Integer(default=9)
    show_note_sidebar = fields.Boolean(default=True)
    show_note_interviews = fields.Boolean(default=True)
    show_note_portfolio = fields.Boolean(default=True)
    show_note_allies = fields.Boolean(default=True)
    show_sidebar_conference = fields.Boolean(default=True)
    show_sidebar_poll = fields.Boolean(default=True)
    show_sidebar_ad = fields.Boolean(default=True)
    conference_label = fields.Char(default="Proxima conferencia")
    conference_title = fields.Char(default="Liderazgo y cultura organizacional: claves para el futuro")
    conference_date_text = fields.Char(default="25 de junio de 2024")
    conference_location = fields.Char(default="Bogota, Colombia")
    conference_time = fields.Char(default="9:00 a.m. - 12:00 m.")
    conference_button_label = fields.Char(default="Mas informacion")
    conference_url = fields.Char(default="/event")
    poll_label = fields.Char(default="Encuesta")
    poll_question = fields.Char(default="¿Cual es el mayor desafio de tu empresa este año?")
    poll_option_1 = fields.Char(default="Acceso a financiamiento")
    poll_option_2 = fields.Char(default="Transformacion digital")
    poll_option_3 = fields.Char(default="Atraccion y retencion de talento")
    poll_option_4 = fields.Char(default="Aumento de costos")
    poll_button_label = fields.Char(default="Votar")

    @api.constrains("home_highlight_limit", "home_latest_limit", "home_new_limit", "section_posts_per_page")
    def _check_positive_limits(self):
        for record in self:
            for field_name in ("home_highlight_limit", "home_latest_limit", "home_new_limit", "section_posts_per_page"):
                if record[field_name] < 1:
                    raise ValidationError("Las cantidades configuradas deben ser mayores que cero.")

    @api.model
    def get_active_config(self, website=None):
        if website:
            config = self.search([("website_id", "=", website.id)], limit=1)
            if config:
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


class LatinpymeRevistaSection(models.Model):
    _name = "latinpyme.revista.section"
    _description = "Seccion editorial Revista LatinPyme"
    _order = "sequence, name"

    name = fields.Char(required=True)
    slug = fields.Char(required=True, index=True)
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
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    description = fields.Text()
    cover_image = fields.Image(max_width=1920, max_height=1080)
    cover_filename = fields.Char()
    seo_title = fields.Char()
    seo_description = fields.Text()
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
            while current:
                if current == record:
                    raise ValidationError("Una seccion no puede ser submenu de si misma.")
                current = current.parent_id

    @api.model
    def _slugify(self, value):
        value = (value or "").strip().lower()
        value = re.sub(r"[^a-z0-9]+", "-", value)
        return value.strip("-")

    @api.model
    def get_active_sections(self, website=None):
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
    def _nav_item(self, section):
        return {
            "slug": section.slug,
            "name": section.name,
            "url": self._nav_url(section),
            "menu_only": section.menu_only,
            "children": [],
        }

    @api.model
    def get_nav_sections(self, website=None):
        records = self.get_active_sections(website)
        if not records:
            return []
        top_sections = records.filtered(lambda section: not section.parent_id)
        nav_sections = []
        for section in top_sections:
            item = self._nav_item(section)
            children = records.filtered(lambda child: child.parent_id == section)
            item["children"] = [self._nav_item(child) for child in children]
            nav_sections.append(item)
        return nav_sections

    @api.model
    def get_by_slug(self, slug, website=None, active=True, routable=False):
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


class LatinpymeRevistaAlly(models.Model):
    _name = "latinpyme.revista.ally"
    _description = "Aliado Revista LatinPyme"
    _order = "sequence, name"

    name = fields.Char(required=True)
    logo = fields.Image(max_width=1024, max_height=512)
    url = fields.Char()
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    website_id = fields.Many2one("website", string="Sitio web", ondelete="cascade")

    @api.model
    def get_active_allies(self, website=None):
        domain = [("active", "=", True)]
        if website:
            domain.append(("website_id", "in", [False, website.id]))
        return self.search(domain, order="sequence, name")

    @api.model
    def get_active_ally_slides(self, website=None, per_slide=8):
        allies = self.get_active_allies(website)
        per_slide = max(int(per_slide or 8), 1)
        return [allies[index:index + per_slide] for index in range(0, len(allies), per_slide)]


class LatinpymeRevistaBanner(models.Model):
    _name = "latinpyme.revista.banner"
    _description = "Publicidad Revista LatinPyme"
    _order = "sequence, name"

    name = fields.Char(required=True)
    placement = fields.Selection(
        [
            ("home_horizontal", "Home horizontal"),
            ("sidebar", "Sidebar"),
            ("footer", "Footer"),
            ("note", "Nota individual"),
            ("section", "Seccion"),
        ],
        required=True,
        default="sidebar",
    )
    image = fields.Image(max_width=1920, max_height=1080)
    title = fields.Char()
    text = fields.Text()
    button_label = fields.Char(default="Conoce mas")
    url = fields.Char(default="/contactus")
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)
    date_start = fields.Date()
    date_end = fields.Date()
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
        return self.get_active_banners(placement, website=website, limit=1)
