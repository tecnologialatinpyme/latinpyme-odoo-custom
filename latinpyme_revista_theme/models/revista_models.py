# -*- coding: utf-8 -*-

from datetime import datetime, time, timedelta
import re
from urllib.parse import urlencode

from odoo import api, fields, models
from odoo.exceptions import ValidationError


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
    ("curso_50_20", "Curso 50 y 20 horas"),
]
PROGRAM_EVENT_TYPE_LEGACY_MAP = {
    "charla": "charlas",
    "diplomado": "diplomados",
    "capacitacion": "charlas",
    "otro": "foros",
}


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
            ("program_hero", "Programacion anual hero"),
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
    def _available_until_domain(self, placement, website=None):
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

    name = fields.Char(required=True)
    event_type = fields.Selection(
        PROGRAM_EVENT_TYPES,
        string="Tipo de evento",
        required=True,
        default="charlas",
    )
    date_start = fields.Date(string="Fecha de inicio", required=True, default=fields.Date.context_today)
    date_end = fields.Date(string="Fecha de fin")
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
    description = fields.Text()
    image = fields.Image(max_width=1600, max_height=900)
    registration_url = fields.Char(string="Enlace de inscripcion")
    button_label = fields.Char(default="Inscribirme")
    active = fields.Boolean(default=True)
    featured = fields.Boolean(string="Destacado")
    sequence = fields.Integer(default=10)
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
    def get_event_type_options(self):
        return list(PROGRAM_EVENT_TYPES)

    @api.model
    def get_event_type_filter_options(self):
        return [
            {"key": "type:%s" % key, "label": label}
            for key, label in self.get_event_type_options()
        ]

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
        domain = [("active", "=", True)]
        if website:
            domain.append(("website_id", "in", [False, website.id]))
        return self.search(domain, order="date_start, time_start, sequence, id")

    @api.model
    def get_public_event(self, event_id, website=None):
        domain = [("id", "=", event_id), ("active", "=", True)]
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
