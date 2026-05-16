# -*- coding: utf-8 -*-

import calendar as pycalendar
import json
from datetime import date, timedelta

from odoo import fields, http
from odoo.http import request
from werkzeug.exceptions import NotFound


REVISTA_BLOG_NAME = "Revista LatinPyme"

SECTION_LABELS = {
    "gerencia": "Gerencia",
    "negocios": "Negocios",
    "ia": "IA",
    "laboral": "Laboral",
    "finanzas": "Finanzas",
    "entrevistas": "Entrevistas",
    "especiales": "Especiales",
    "mujeres": "Mujeres",
    "portafolio": "Portafolio",
}

ENABLED_SECTIONS_PARAM = "latinpyme_revista_theme.enabled_sections"

HOME_FEATURE_TAGS = (
    "Destacado Home",
    "Destacado Portada",
    "Portada",
    "Home",
    "Destacado",
)

SECTION_FEATURE_TAGS = (
    "Destacado Seccion",
    "Destacado Sección",
    "Principal",
    "Destacado",
)

PREPRODUCTION_HOSTS = {
    "revista.latinpyme.com",
}

PROGRAM_SECTION_SLUG = "programacion-anual"
PROGRAM_WEEKDAYS = ("L", "M", "M", "J", "V", "S", "D")
PROGRAM_MONTHS = {
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


def enabled_section_slugs(env):
    sections = env["latinpyme.revista.section"].sudo().get_route_sections()
    if sections:
        return [section.slug for section in sections if section.slug]
    configured = env["ir.config_parameter"].sudo().get_param(ENABLED_SECTIONS_PARAM, "")
    slugs = [slug.strip().lower() for slug in configured.split(",") if slug.strip()]
    valid_slugs = [slug for slug in slugs if slug in SECTION_LABELS]
    return valid_slugs or list(SECTION_LABELS)


def sitemap_revista_sections(env, rule, qs):
    for slug in enabled_section_slugs(env):
        yield {"loc": "/revista/seccion/%s" % slug}


class LatinpymeRevistaController(http.Controller):
    def _config(self):
        return request.env["latinpyme.revista.config"].sudo().get_active_config(request.website)

    def _production_base_url(self):
        config = self._config()
        return config.production_base_url() if config else "https://latinpyme.com"

    def _preproduction_host(self):
        config = self._config()
        host = request.httprequest.host.split(":", 1)[0].lower()
        if config:
            return config.is_preproduction_host(host)
        return (
            host in PREPRODUCTION_HOSTS
            or host.endswith(".odoo.com")
            or host.endswith(".odoo.sh")
        )

    def _render(self, template, values):
        config = self._config()
        values.setdefault("sections", self._sections())
        values["lp_config"] = config
        values["lp_preproduction"] = self._preproduction_host()
        values["lp_production_url"] = "%s%s" % (self._production_base_url(), request.httprequest.path)
        response = request.render(template, values)
        if values["lp_preproduction"]:
            response.headers["X-Robots-Tag"] = "noindex, nofollow"
        return response

    def _website_domain(self, model):
        if request.website and "website_id" in model._fields:
            return [("website_id", "in", [False, request.website.id])]
        return []

    def _revista_blog(self):
        Blog = request.env["blog.blog"].sudo()
        domain = []
        if "active" in Blog._fields:
            domain.append(("active", "=", True))
        website_domain = self._website_domain(Blog)
        blog = Blog.search(domain + [("name", "=", REVISTA_BLOG_NAME)] + website_domain, limit=1)
        if not blog:
            blog = Blog.search(domain + website_domain, limit=1)
        return blog

    def _tag_by_name(self, name):
        return request.env["blog.tag"].sudo().search([("name", "=ilike", name)], limit=1)

    def _tags_by_names(self, names):
        tags = request.env["blog.tag"].sudo().browse()
        for name in names:
            tags |= self._tag_by_name(name)
        return tags

    def _section_tag(self, section_slug):
        section = self._section_record(section_slug)
        if section:
            return section.blog_tag()
        label = SECTION_LABELS.get(section_slug)
        return self._tag_by_name(label) if label else request.env["blog.tag"].sudo().browse()

    def _section_record(self, section_slug):
        return request.env["latinpyme.revista.section"].sudo().get_by_slug(
            section_slug,
            website=request.website,
            routable=True,
        )

    def _sections(self):
        Section = request.env["latinpyme.revista.section"].sudo()
        records = Section.get_route_sections(request.website)
        if records:
            website_id = request.website.id if request.website else False
            ordered = sorted(
                records,
                key=lambda record: (
                    0 if website_id and record.website_id.id == website_id else 1,
                    record.sequence,
                    record.name,
                ),
            )
            seen = set()
            sections = []
            for record in ordered:
                if not record.slug or record.slug in seen:
                    continue
                seen.add(record.slug)
                sections.append(
                    {
                        "slug": record.slug,
                        "name": record.name,
                        "url": "/revista/seccion/%s" % record.slug,
                        "tag": record.blog_tag(),
                        "record": record,
                    }
                )
            return sections
        return [
            {
                "slug": slug,
                "name": name,
                "url": "/revista/seccion/%s" % slug,
                "tag": self._tag_by_name(name),
                "record": False,
            }
            for slug, name in SECTION_LABELS.items()
            if slug in enabled_section_slugs(request.env)
        ]

    def _published_domain(self, Post):
        domain = []
        if "active" in Post._fields:
            domain.append(("active", "=", True))
        if "website_published" in Post._fields:
            domain.append(("website_published", "=", True))
        elif "is_published" in Post._fields:
            domain.append(("is_published", "=", True))
        if "post_date" in Post._fields:
            domain.append(("post_date", "<=", fields.Datetime.now()))
        domain += self._website_domain(Post)
        return domain

    def _posts_domain(self, blog=None, tag=None, extra_tags=None, exclude_ids=None):
        Post = request.env["blog.post"].sudo()
        domain = self._published_domain(Post)
        if blog:
            domain.append(("blog_id", "=", blog.id))
        if tag:
            domain.append(("tag_ids", "in", tag.ids))
        if extra_tags:
            domain.append(("tag_ids", "in", extra_tags.ids))
        if exclude_ids:
            domain.append(("id", "not in", exclude_ids))
        return domain

    def _posts(self, blog=None, tag=None, extra_tags=None, limit=6, exclude_ids=None, offset=0):
        Post = request.env["blog.post"].sudo()
        domain = self._posts_domain(blog=blog, tag=tag, extra_tags=extra_tags, exclude_ids=exclude_ids)
        return Post.search(domain, order="post_date desc, id desc", limit=limit, offset=offset)

    def _posts_count(self, blog=None, tag=None, extra_tags=None, exclude_ids=None):
        Post = request.env["blog.post"].sudo()
        domain = self._posts_domain(blog=blog, tag=tag, extra_tags=extra_tags, exclude_ids=exclude_ids)
        return Post.search_count(domain)

    def _featured_post(self, blog=None, section_tag=None):
        feature_tags = self._tags_by_names(SECTION_FEATURE_TAGS if section_tag else HOME_FEATURE_TAGS)
        featured = self._posts(blog=blog, tag=section_tag, extra_tags=feature_tags, limit=1)
        if not featured:
            featured = self._posts(blog=blog, tag=section_tag, limit=1)
        return featured

    def _cover_style(self, record):
        default = "background-image: linear-gradient(90deg, rgba(12, 14, 18, .94), rgba(12, 14, 18, .72));"
        if not record or "cover_properties" not in record._fields:
            return default
        try:
            cover_properties = json.loads(record.cover_properties or "{}")
        except ValueError:
            return default
        background = cover_properties.get("background-image")
        if not background or background == "none":
            return default
        overlay = "linear-gradient(90deg, rgba(5, 7, 12, .88), rgba(5, 7, 12, .46) 58%, rgba(5, 7, 12, .18))"
        return "background-image: %s, %s;" % (overlay, background)

    def _section_cover_style(self, section, fallback_record):
        if section and section.cover_image:
            overlay = "linear-gradient(90deg, rgba(5, 7, 12, .88), rgba(5, 7, 12, .44) 58%, rgba(5, 7, 12, .14))"
            image_url = "/web/image/latinpyme.revista.section/%s/cover_image" % section.id
            return "background-image: %s, url('%s');" % (overlay, image_url)
        return self._cover_style(fallback_record)

    def _banners(self, placement, limit=1):
        return request.env["latinpyme.revista.banner"].sudo().get_active_banners(
            placement,
            website=request.website,
            limit=limit,
        )

    def _program_event_groups(self, events):
        groups = []
        current_key = False
        for event in events:
            month_key = event.month_group_key()
            if month_key != current_key:
                groups.append(
                    {
                        "key": month_key,
                        "label": event.month_group_label(),
                        "events": [],
                    }
                )
                current_key = month_key
            groups[-1]["events"].append(event)
        return groups

    def _program_year(self, kwargs):
        Event = request.env["latinpyme.revista.program.event"].sudo()
        today = fields.Date.context_today(Event)
        try:
            year = int(kwargs.get("year") or today.year)
        except (TypeError, ValueError):
            year = today.year
        return max(min(year, 2100), 2000)

    def _event_intersects_year(self, event, year):
        start = fields.Date.to_date(event.date_start)
        end = fields.Date.to_date(event.date_end or event.date_start)
        return start <= date(year, 12, 31) and end >= date(year, 1, 1)

    def _program_events_by_day(self, events, year):
        grouped = {}
        year_start = date(year, 1, 1)
        year_end = date(year, 12, 31)
        for event in events:
            current = max(fields.Date.to_date(event.date_start), year_start)
            end = min(fields.Date.to_date(event.date_end or event.date_start), year_end)
            while current <= end:
                grouped.setdefault(current.isoformat(), []).append(event)
                current += timedelta(days=1)
        return grouped

    def _program_day_label(self, day):
        return "%s de %s de %s" % (day.day, PROGRAM_MONTHS.get(day.month, ""), day.year)

    def _program_calendar_months(self, year, events, today):
        grouped = self._program_events_by_day(events, year)
        calendar = pycalendar.Calendar(firstweekday=0)
        months = []
        for month_number in range(1, 13):
            weeks = []
            for week in calendar.monthdatescalendar(year, month_number):
                days = []
                for day in week:
                    day_events = grouped.get(day.isoformat(), [])
                    days.append(
                        {
                            "date": day.isoformat(),
                            "label": self._program_day_label(day),
                            "number": day.day,
                            "in_month": day.month == month_number,
                            "is_today": day == today,
                            "events": day_events,
                            "event_count": len(day_events),
                            "featured": any(event.featured for event in day_events),
                            "event_types": " ".join(sorted(set(event.event_type for event in day_events))),
                            "modalities": " ".join(sorted(set(event.modality for event in day_events))),
                        }
                    )
                weeks.append(days)
            months.append(
                {
                    "number": month_number,
                    "name": PROGRAM_MONTHS[month_number],
                    "weeks": weeks,
                    "event_count": sum(1 for event in events if fields.Date.to_date(event.date_start).month == month_number),
                }
            )
        return months

    def _program_type_summary(self, events):
        Event = request.env["latinpyme.revista.program.event"].sudo()
        selection = dict(Event._fields["event_type"].selection)
        summary = []
        for key, label in selection.items():
            count = len(events.filtered(lambda event: event.event_type == key))
            if count:
                summary.append({"key": key, "label": label, "count": count})
        return summary

    def _program_filter_options(self):
        Event = request.env["latinpyme.revista.program.event"].sudo()
        return [{"key": "all", "label": "Todos"}] + Event.get_event_type_filter_options()

    def _revista_program_section(self, section_slug, section_record, kwargs=None):
        kwargs = kwargs or {}
        blog = self._revista_blog()
        section_name = section_record.name if section_record else "Programacion anual"
        Event = request.env["latinpyme.revista.program.event"].sudo()
        program_year = self._program_year(kwargs)
        today = fields.Date.context_today(Event)
        events = Event.get_active_events(request.website).filtered(
            lambda event: self._event_intersects_year(event, program_year)
        )
        upcoming_events = events.filtered(
            lambda event: fields.Date.to_date(event.date_end or event.date_start) >= today
        )[:5]
        values = {
            "blog": blog,
            "section_slug": section_slug,
            "section_name": section_name,
            "section_record": section_record,
            "section_description": section_record.description if section_record else False,
            "section_seo_title": section_record.seo_title if section_record else False,
            "section_seo_description": section_record.seo_description if section_record else False,
            "featured_style": self._section_cover_style(section_record, blog),
            "program_events": events,
            "program_groups": self._program_event_groups(events),
            "program_calendar_months": self._program_calendar_months(program_year, events, today),
            "program_weekdays": PROGRAM_WEEKDAYS,
            "program_year": program_year,
            "program_prev_year_url": "/revista/seccion/%s?year=%s" % (section_slug, program_year - 1),
            "program_next_year_url": "/revista/seccion/%s?year=%s" % (section_slug, program_year + 1),
            "program_upcoming_events": upcoming_events,
            "program_type_summary": self._program_type_summary(events),
            "program_filter_options": self._program_filter_options(),
            "program_hero_banner": self._banners("program_hero", limit=1),
        }
        return self._render("latinpyme_revista_theme.revista_program_page", values)

    @http.route("/revista", type="http", auth="public", website=True, sitemap=True)
    def revista_home(self, **kwargs):
        config = self._config()
        blog = self._revista_blog()
        featured_post = self._featured_post(blog=blog)
        exclude_ids = featured_post.ids if featured_post else []
        interview_tag = self._tag_by_name("Entrevistas")
        special_tag = self._tag_by_name("Especiales")
        highlight_limit = config.home_highlight_limit if config else 3
        latest_limit = config.home_latest_limit if config else 6
        new_limit = config.home_new_limit if config else 5
        values = {
            "blog": blog,
            "featured_post": featured_post,
            "featured_style": self._cover_style(featured_post),
            "highlight_posts": self._posts(blog=blog, limit=highlight_limit, exclude_ids=exclude_ids),
            "latest_posts": self._posts(blog=blog, limit=latest_limit, exclude_ids=exclude_ids),
            "new_posts": self._posts(blog=blog, limit=new_limit, exclude_ids=exclude_ids),
            "interview_posts": self._posts(blog=blog, tag=interview_tag, limit=3),
            "special_posts": self._posts(blog=blog, tag=special_tag, limit=2),
            "home_banners": self._banners("home_horizontal", limit=2),
        }
        return self._render("latinpyme_revista_theme.revista_home_page", values)

    @http.route(
        "/revista/seccion/<string:section_slug>",
        type="http",
        auth="public",
        website=True,
        sitemap=sitemap_revista_sections,
    )
    def revista_section(self, section_slug, page=1, **kwargs):
        section_slug = (section_slug or "").strip().lower()
        section_record = self._section_record(section_slug)
        if section_slug not in enabled_section_slugs(request.env):
            raise NotFound()
        if section_slug == PROGRAM_SECTION_SLUG:
            return self._revista_program_section(section_slug, section_record, kwargs)
        section_name = section_record.name if section_record else SECTION_LABELS.get(section_slug)
        if not section_name:
            raise NotFound()
        config = self._config()
        blog = self._revista_blog()
        section_tag = self._section_tag(section_slug)
        empty_posts = request.env["blog.post"].sudo().browse()
        featured_post = self._featured_post(blog=blog, section_tag=section_tag) if section_tag else empty_posts
        exclude_ids = featured_post.ids if featured_post else []
        try:
            current_page = max(int(page or kwargs.get("page", 1) or 1), 1)
        except (TypeError, ValueError):
            current_page = 1
        per_page = config.section_posts_per_page if config else 9
        total_posts = self._posts_count(blog=blog, tag=section_tag, exclude_ids=exclude_ids) if section_tag else 0
        page_count = max((total_posts + per_page - 1) // per_page, 1)
        if current_page > page_count:
            current_page = page_count
        offset = (current_page - 1) * per_page
        posts = self._posts(blog=blog, tag=section_tag, limit=per_page, exclude_ids=exclude_ids, offset=offset) if section_tag else empty_posts
        section_url = "/revista/seccion/%s" % section_slug
        values = {
            "blog": blog,
            "section_slug": section_slug,
            "section_name": section_name,
            "section_record": section_record,
            "section_description": section_record.description if section_record else False,
            "section_seo_title": section_record.seo_title if section_record else False,
            "section_seo_description": section_record.seo_description if section_record else False,
            "section_tag": section_tag,
            "featured_post": featured_post,
            "featured_style": self._section_cover_style(section_record, featured_post or blog),
            "posts": posts,
            "latest_posts": self._posts(blog=blog, limit=6, exclude_ids=exclude_ids),
            "current_page": current_page,
            "page_count": page_count,
            "total_posts": total_posts,
            "prev_page_url": "%s?page=%s" % (section_url, current_page - 1) if current_page > 1 else False,
            "next_page_url": "%s?page=%s" % (section_url, current_page + 1) if current_page < page_count else False,
            "section_banners": self._banners("section", limit=1),
        }
        return self._render("latinpyme_revista_theme.revista_section_page", values)

    @http.route(
        "/revista/programacion/<int:event_id>/ics",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def revista_program_event_ics(self, event_id, **kwargs):
        event = request.env["latinpyme.revista.program.event"].sudo().get_public_event(
            event_id,
            website=request.website,
        )
        if not event:
            raise NotFound()
        headers = [
            ("Content-Type", "text/calendar; charset=utf-8"),
            ("Content-Disposition", 'attachment; filename="%s"' % event.ics_filename()),
        ]
        return request.make_response(event.ics_content(), headers=headers)
