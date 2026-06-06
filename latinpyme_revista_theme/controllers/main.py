# -*- coding: utf-8 -*-

import base64
import calendar as pycalendar
import json
import uuid
from datetime import date, timedelta
from urllib.parse import urlencode

from odoo import fields, http
from odoo.http import request
from werkzeug.exceptions import NotFound
from werkzeug.utils import redirect as werkzeug_redirect


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

SECTION_TAG_ALIASES = {
    "especiales": ("Especiales", "Especial"),
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
PROGRAM_DISPLAY_YEAR = 2026
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
        headers = [
            ("Content-Type", mimetype),
            ("Cache-Control", "public, max-age=86400"),
        ]
        return request.make_response(content, headers=headers)

    def _website_matches(self, record):
        website = getattr(request, "website", False)
        return not record.website_id or not website or record.website_id == website

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

    def _subscribe_url(self):
        config = self._config()
        target = config.subscribe_target_url() if config else ""
        if not target or target == "/suscribirse":
            return "/"
        return target

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

    @http.route("/suscribirse", type="http", auth="public", website=True, sitemap=False)
    def revista_subscribe_redirect(self, **kwargs):
        return werkzeug_redirect(self._subscribe_url(), code=302)

    @http.route(
        "/revista/media/banner/<int:banner_id>/image",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def revista_banner_image(self, banner_id, **kwargs):
        banner = request.env["latinpyme.revista.banner"].sudo().browse(banner_id).exists()
        if not banner or not banner.active or not banner.image or not self._website_matches(banner):
            raise NotFound()
        today = fields.Date.context_today(banner)
        if banner.date_end and banner.date_end < today:
            raise NotFound()
        if banner.placement != "program_hero" and banner.date_start and banner.date_start > today:
            raise NotFound()
        return self._image_response(banner.image)

    @http.route(
        "/revista/media/ally/<int:ally_id>/logo",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def revista_ally_logo(self, ally_id, **kwargs):
        ally = request.env["latinpyme.revista.ally"].sudo().browse(ally_id).exists()
        if not ally or not ally.active or not ally.logo or not self._website_matches(ally):
            raise NotFound()
        return self._image_response(ally.logo)

    @http.route(
        "/revista/media/section/<int:section_id>/cover",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def revista_section_cover(self, section_id, **kwargs):
        section = request.env["latinpyme.revista.section"].sudo().browse(section_id).exists()
        if not section or not section.active or not section.cover_image or not self._website_matches(section):
            raise NotFound()
        return self._image_response(section.cover_image)

    @http.route(
        "/revista/media/program-event/<int:event_id>/image",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def revista_program_event_image(self, event_id, **kwargs):
        event = request.env["latinpyme.revista.program.event"].sudo().browse(event_id).exists()
        if not event or not event.active or not event.image or not self._website_matches(event):
            raise NotFound()
        return self._image_response(event.image)

    @http.route(
        "/revista/media/portfolio/<int:item_id>/image",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def revista_portfolio_item_image(self, item_id, **kwargs):
        item = request.env["latinpyme.revista.portfolio.item"].sudo().browse(item_id).exists()
        if not item or not item.active or not item.image or not self._website_matches(item):
            raise NotFound()
        return self._image_response(item.image)

    @http.route(
        "/revista/media/interview/<int:interview_id>/image",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def revista_interview_image(self, interview_id, **kwargs):
        interview = request.env["latinpyme.revista.interview"].sudo().browse(interview_id).exists()
        if not interview or not interview.active or not interview.image or not self._website_matches(interview):
            raise NotFound()
        return self._image_response(interview.image)

    @http.route(
        "/revista/media/blog-post/<int:post_id>/author-avatar",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def revista_blog_post_author_avatar(self, post_id, **kwargs):
        post = request.env["blog.post"].sudo().browse(post_id).exists()
        if not post or not post.author_avatar or not self._blog_post_is_public(post):
            raise NotFound()
        return self._image_response(post.author_avatar)

    @http.route(
        "/revista/media/sidebar/<int:item_id>/image",
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def revista_sidebar_item_image(self, item_id, **kwargs):
        item = request.env["latinpyme.revista.sidebar.item"].sudo().browse(item_id).exists()
        if not item or not item.active or not item.image or not self._website_matches(item):
            raise NotFound()
        return self._image_response(item.image)

    def _poll_session_key(self):
        session_key = request.session.get("lp_revista_poll_session_key")
        if not session_key:
            session_key = uuid.uuid4().hex
            request.session["lp_revista_poll_session_key"] = session_key
        return session_key

    def _poll_session_votes(self):
        votes = request.session.get("lp_revista_poll_votes") or []
        if isinstance(votes, str):
            votes = [vote for vote in votes.split(",") if vote]
        return set(votes)

    def _set_poll_session_votes(self, votes):
        request.session["lp_revista_poll_votes"] = sorted(votes)

    def _poll_source_data(self, source_type, source_id):
        source_type = (source_type or "config").strip()
        if source_type not in ("config", "sidebar"):
            source_type = "config"
        try:
            source_id = int(source_id or 0)
        except (TypeError, ValueError):
            source_id = 0
        website = getattr(request, "website", False)

        if source_type == "sidebar":
            item = request.env["latinpyme.revista.sidebar.item"].sudo().browse(source_id).exists()
            if not item or not item.active or item.item_type != "poll" or not self._website_matches(item):
                return False
            return {
                "source_type": "sidebar",
                "source_id": item.id,
                "config_id": False,
                "sidebar_item_id": item.id,
                "website_id": item.website_id.id if item.website_id else (website.id if website else False),
                "question": item.title or item.name,
                "options": {
                    "option_1": item.poll_option_1,
                    "option_2": item.poll_option_2,
                    "option_3": item.poll_option_3,
                    "option_4": item.poll_option_4,
                },
            }

        config = request.env["latinpyme.revista.config"].sudo().browse(source_id).exists() if source_id else self._config()
        if config and not self._website_matches(config):
            config = self._config()
        return {
            "source_type": "config",
            "source_id": config.id if config else 0,
            "config_id": config.id if config else False,
            "sidebar_item_id": False,
            "website_id": website.id if website else (config.website_id.id if config and config.website_id else False),
            "question": config.poll_question if config and config.poll_question else "¿Cuál es el mayor desafío de tu empresa este año?",
            "options": {
                "option_1": config.poll_option_1 if config and config.poll_option_1 else "Acceso a financiamiento",
                "option_2": config.poll_option_2 if config and config.poll_option_2 else "Transformación digital",
                "option_3": config.poll_option_3 if config and config.poll_option_3 else "Atracción y retención de talento",
                "option_4": config.poll_option_4 if config and config.poll_option_4 else "Aumento de costos",
            },
        }

    @http.route("/revista/poll/vote", type="jsonrpc", auth="public", website=True, csrf=False, sitemap=False)
    def revista_poll_vote(self, source_type=None, source_id=None, option_key=None, **kwargs):
        try:
            source = self._poll_source_data(source_type, source_id)
            option_key = (option_key or "").strip()
            option_label = source and source["options"].get(option_key)
            if not source or not option_label:
                return {
                    "ok": False,
                    "message": "Selecciona una opcion antes de votar.",
                }

            session_key = self._poll_session_key()
            vote_key = "%s:%s" % (source["source_type"], source["source_id"])
            session_votes = self._poll_session_votes()
            Vote = request.env["latinpyme.revista.poll.vote"].sudo()
            vote_domain = [
                ("source_type", "=", source["source_type"]),
                ("source_id", "=", source["source_id"]),
                ("session_key", "=", session_key),
            ]
            if vote_key in session_votes or Vote.search(vote_domain, limit=1):
                session_votes.add(vote_key)
                self._set_poll_session_votes(session_votes)
                return {
                    "ok": True,
                    "duplicate": True,
                    "message": "Ya registramos tu voto en esta encuesta.",
                }

            Vote.create(
                {
                    "source_type": source["source_type"],
                    "source_id": source["source_id"],
                    "config_id": source["config_id"],
                    "sidebar_item_id": source["sidebar_item_id"],
                    "website_id": source["website_id"],
                    "question": source["question"],
                    "option_key": option_key,
                    "option_label": option_label,
                    "session_key": session_key,
                    "user_id": request.env.user.id,
                }
            )
            session_votes.add(vote_key)
            self._set_poll_session_votes(session_votes)
            return {
                "ok": True,
                "message": "¡Gracias! Tu voto ha sido registrado.",
            }
        except Exception:
            return {
                "ok": False,
                "message": "No pudimos registrar tu voto en este momento. Intentalo de nuevo mas tarde.",
            }

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

    def _section_tag_names(self, section_slug, section=False):
        names = []
        if section and section.tag_id:
            names.append(section.tag_id.name)
        elif section and section.name:
            names.append(section.name)
        label = SECTION_LABELS.get(section_slug)
        if label:
            names.append(label)
        names.extend(SECTION_TAG_ALIASES.get(section_slug, ()))
        return list(dict.fromkeys(name for name in names if name))

    def _section_tag(self, section_slug):
        section = self._section_record(section_slug)
        tags = request.env["blog.tag"].sudo().browse()
        if section and section.tag_id:
            tags |= section.tag_id
        for name in self._section_tag_names(section_slug, section=section):
            tags |= self._tag_by_name(name)
        return tags

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
                        "tag": self._section_tag(record.slug),
                        "record": record,
                    }
                )
            return sections
        return [
            {
                "slug": slug,
                "name": name,
                "url": "/revista/seccion/%s" % slug,
                "tag": self._section_tag(slug),
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

    def _blog_post_is_public(self, post):
        Post = request.env["blog.post"].sudo()
        return bool(post and Post.search([("id", "=", post.id)] + self._published_domain(Post), limit=1))

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
            image_url = "/revista/media/section/%s/cover" % section.id
            return "background-image: %s, url('%s');" % (overlay, image_url)
        return self._cover_style(fallback_record)

    def _banners(self, placement, limit=1):
        return request.env["latinpyme.revista.banner"].sudo().get_active_banners(
            placement,
            website=request.website,
            limit=limit,
        )

    def _home_block(self, block_type):
        Block = request.env["latinpyme.revista.home.block"].sudo()
        domain = [("block_type", "=", block_type)]
        if request.website:
            website_block = Block.search(domain + [("website_id", "=", request.website.id)], order="sequence, id", limit=1)
            if website_block:
                return website_block
        return Block.search(domain + [("website_id", "=", False)], order="sequence, id", limit=1)

    def _home_blocks_map(self):
        return {
            block_type: self._home_block(block_type)
            for block_type, _label in request.env["latinpyme.revista.home.block"].sudo()._fields["block_type"].selection
        }

    def _home_block_enabled(self, block, default=True):
        return block.active if block else bool(default)

    def _home_block_limit(self, block, default=3):
        if block and block.limit:
            return block.limit
        return default

    def _manual_posts(self, block, blog=None, limit=6, exclude_ids=None):
        empty_posts = request.env["blog.post"].sudo().browse()
        if not block:
            return empty_posts
        Assignment = request.env["latinpyme.revista.home.assignment"].sudo()
        if block.block_type == "news":
            exclude_ids = None
        has_scheduled_posts = Assignment.has_active_assignments(block.block_type, website=request.website, content_type="post")
        scheduled_posts = Assignment.get_active_posts(
            block.block_type,
            website=request.website,
            blog=blog,
            limit=limit,
            exclude_ids=exclude_ids,
        )
        if has_scheduled_posts:
            return scheduled_posts
        if not block.post_ids:
            return empty_posts
        posts = block.post_ids.sudo()
        exclude_ids = set(exclude_ids or [])
        if blog:
            posts = posts.filtered(lambda post: post.blog_id == blog)
        if exclude_ids:
            posts = posts.filtered(lambda post: post.id not in exclude_ids)
        now = fields.Datetime.now()
        if "active" in posts._fields:
            posts = posts.filtered(lambda post: post.active)
        if "website_published" in posts._fields:
            posts = posts.filtered(lambda post: post.website_published)
        elif "is_published" in posts._fields:
            posts = posts.filtered(lambda post: post.is_published)
        if "post_date" in posts._fields:
            posts = posts.filtered(lambda post: not post.post_date or post.post_date <= now)
        if request.website and "website_id" in posts._fields:
            posts = posts.filtered(lambda post: not post.website_id or post.website_id == request.website)
        return posts[:limit]

    def _manual_interviews(self, block, section=None, limit=3):
        empty_interviews = request.env["latinpyme.revista.interview"].sudo().browse()
        if not block:
            return empty_interviews
        Assignment = request.env["latinpyme.revista.home.assignment"].sudo()
        has_scheduled_interviews = Assignment.has_active_assignments(
            block.block_type,
            website=request.website,
            content_type="interview",
        )
        scheduled_interviews = Assignment.get_active_interviews(
            block.block_type,
            website=request.website,
            section=section,
            limit=limit,
        )
        if has_scheduled_interviews:
            return scheduled_interviews
        return empty_interviews

    def _home_posts(
        self,
        block,
        blog=None,
        default_tag=None,
        default_limit=6,
        exclude_ids=None,
        min_limit=0,
        allow_fallback=False,
    ):
        limit = max(self._home_block_limit(block, default_limit), min_limit)
        manual_posts = self._manual_posts(block, blog=blog, limit=limit, exclude_ids=exclude_ids)
        if manual_posts or not allow_fallback:
            return manual_posts
        tag = block.tag_id if block and block.tag_id else default_tag
        return self._posts(blog=blog, tag=tag, limit=limit, exclude_ids=exclude_ids)

    def _home_featured_post(self, block, blog=None, allow_fallback=False):
        manual_post = self._manual_posts(block, blog=blog, limit=1)
        if manual_post or not allow_fallback:
            return manual_post
        if block and block.tag_id:
            return self._posts(blog=blog, tag=block.tag_id, limit=1)
        return self._featured_post(blog=blog)

    def _section_display_enabled(self, section, field_name, default=True):
        if section and field_name in section._fields:
            return section.display_mode_enabled(field_name, default_enabled=default)
        return bool(default)

    def _section_banners(self, section):
        if section and section.section_banner_id and section.section_banner_id.active and self._website_matches(section.section_banner_id):
            return section.section_banner_id
        return self._banners("section", limit=1)

    def _interviews(self, section=None, limit=3):
        return request.env["latinpyme.revista.interview"].sudo().get_active_interviews(
            request.website,
            section,
            limit,
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

    def _program_monthly_agenda(self, year, events):
        months = []
        for month_number in range(1, 13):
            month_events = events.filtered(
                lambda event: fields.Date.to_date(event.date_start).month == month_number
            )
            months.append(
                {
                    "number": month_number,
                    "name": PROGRAM_MONTHS[month_number],
                    "events": month_events,
                    "event_count": len(month_events),
                }
            )
        return months

    def _revista_program_section(self, section_slug, section_record, kwargs=None):
        kwargs = kwargs or {}
        blog = self._revista_blog()
        section_name = section_record.name if section_record else "Programacion anual"
        Event = request.env["latinpyme.revista.program.event"].sudo()
        program_year = PROGRAM_DISPLAY_YEAR
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
            "program_upcoming_events": upcoming_events,
            "program_type_summary": self._program_type_summary(events),
            "program_filter_options": self._program_filter_options(),
            "program_monthly_agenda": self._program_monthly_agenda(program_year, events),
            "program_hero_banner": request.env["latinpyme.revista.banner"].sudo().get_program_hero_banner(request.website),
        }
        return self._render("latinpyme_revista_theme.revista_program_page", values)

    @http.route(
        ["/revista", "/revista/"],
        type="http",
        auth="public",
        website=True,
        sitemap=False,
    )
    def revista_home_redirect(self, **kwargs):
        if request.httprequest.path == "/":
            return self._revista_home_response()
        return werkzeug_redirect("/", code=301)

    def _revista_home_response(self):
        config = self._config()
        blog = self._revista_blog()
        home_blocks = self._home_blocks_map()
        block_defaults = {
            "top_banners": config.show_home_banners if config else True,
            "hero": True,
            "latest": True,
            "sections": True,
            "news": True,
            "interviews": config.show_home_interviews if config else True,
            "specials": config.show_home_specials if config else True,
            "mid_banners": config.show_home_banners if config else True,
            "portfolio": config.show_home_portfolio if config else True,
            "allies": config.show_home_allies if config else True,
        }
        featured_post = self._home_featured_post(home_blocks.get("hero"), blog=blog)
        exclude_ids = featured_post.ids if featured_post else []
        special_tag = self._tags_by_names(("Especiales", "Especial"))
        interview_tag = self._tag_by_name("Entrevistas")
        highlight_limit = config.home_highlight_limit if config else 3
        latest_limit = config.home_latest_limit if config else 6
        new_limit = config.home_new_limit if config else 5
        home_top_banners = self._banners("home_top", limit=self._home_block_limit(home_blocks.get("top_banners"), 2))
        if not home_top_banners:
            home_top_banners = self._banners("home_horizontal", limit=self._home_block_limit(home_blocks.get("top_banners"), 2))
        home_news_banner = self._banners("home_news", limit=1)
        if not home_news_banner:
            home_news_banner = self._banners("home_horizontal", limit=1)
        home_specials_banner = self._banners("home_specials", limit=1)
        home_sidebar_items = request.env["latinpyme.revista.sidebar.item"].sudo().get_active_items("home", request.website)
        home_sections = self._sections()
        home_allies = request.env["latinpyme.revista.ally"].sudo().get_active_allies(request.website)
        interviews_block = home_blocks.get("interviews")
        interviews_limit = self._home_block_limit(interviews_block, 3)
        manual_interviews = self._manual_interviews(
            interviews_block,
            limit=interviews_limit,
        )
        manual_interview_posts = self._manual_posts(
            interviews_block,
            blog=blog,
            limit=interviews_limit,
        )
        empty_interviews = request.env["latinpyme.revista.interview"].sudo().browse()
        empty_posts = request.env["blog.post"].sudo().browse()
        values = {
            "blog": blog,
            "sections": home_sections,
            "home_section_links": home_sections[:6],
            "home_blocks": home_blocks,
            "show_home_top_banners": self._home_block_enabled(home_blocks.get("top_banners"), block_defaults["top_banners"]),
            "show_home_hero": self._home_block_enabled(home_blocks.get("hero"), block_defaults["hero"]),
            "show_home_latest": self._home_block_enabled(home_blocks.get("latest"), block_defaults["latest"]),
            "show_home_sections": self._home_block_enabled(home_blocks.get("sections"), block_defaults["sections"]),
            "show_home_news": self._home_block_enabled(home_blocks.get("news"), block_defaults["news"]),
            "show_home_interviews": self._home_block_enabled(home_blocks.get("interviews"), block_defaults["interviews"]),
            "show_home_specials": self._home_block_enabled(home_blocks.get("specials"), block_defaults["specials"]),
            "show_home_mid_banners": self._home_block_enabled(home_blocks.get("mid_banners"), block_defaults["mid_banners"]),
            "show_home_portfolio": self._home_block_enabled(home_blocks.get("portfolio"), block_defaults["portfolio"]),
            "show_home_allies": self._home_block_enabled(home_blocks.get("allies"), block_defaults["allies"]),
            "featured_post": featured_post,
            "featured_style": self._cover_style(featured_post),
            "highlight_posts": self._home_posts(home_blocks.get("hero"), blog=blog, default_limit=highlight_limit, exclude_ids=exclude_ids),
            "latest_posts": self._home_posts(home_blocks.get("latest"), blog=blog, default_limit=latest_limit, exclude_ids=exclude_ids),
            "new_posts": self._home_posts(home_blocks.get("news"), blog=blog, default_limit=new_limit, min_limit=4),
            "interviews": manual_interviews or (empty_interviews if manual_interview_posts else self._interviews(limit=interviews_limit)),
            "interview_posts": empty_posts if manual_interviews else (
                manual_interview_posts
                or self._home_posts(
                    interviews_block,
                    blog=blog,
                    default_tag=interview_tag,
                    default_limit=3,
                    allow_fallback=True,
                )
            ),
            "special_posts": self._home_posts(home_blocks.get("specials"), blog=blog, default_tag=special_tag, default_limit=2),
            "home_banners": home_top_banners,
            "home_mid_banners": self._banners("home_horizontal", limit=self._home_block_limit(home_blocks.get("mid_banners"), 3)),
            "home_news_banner": home_news_banner,
            "home_specials_banner": home_specials_banner,
            "home_allies": home_allies,
            "home_conference_item": home_sidebar_items.filtered(lambda item: item.item_type == "conference")[:1],
            "home_poll_item": home_sidebar_items.filtered(lambda item: item.item_type == "poll")[:1],
            "home_ad_item": home_sidebar_items.filtered(lambda item: item.item_type == "banner")[:1],
        }
        return self._render("latinpyme_revista_theme.revista_home_page", values)

    @http.route("/revista/seccion", type="http", auth="public", website=True, sitemap=True)
    def revista_sections_index(self, search="", **kwargs):
        query = (search or kwargs.get("q") or "").strip()
        query_lower = query.lower()
        blog = self._revista_blog()
        section_items = [
            section
            for section in self._sections()
            if not section.get("record") or section["record"].show_in_section_index
        ]
        if query_lower:
            section_items = [
                section
                for section in section_items
                if query_lower in (section.get("name") or "").lower()
                or query_lower in (section.get("slug") or "").replace("-", " ").lower()
                or (
                    section.get("record")
                    and query_lower in (section["record"].description or "").lower()
                )
            ]

        try:
            current_page = max(int(kwargs.get("page", 1) or 1), 1)
        except (TypeError, ValueError):
            current_page = 1
        per_page = 12
        total_sections = len(section_items)
        page_count = max((total_sections + per_page - 1) // per_page, 1)
        if current_page > page_count:
            current_page = page_count
        offset = (current_page - 1) * per_page
        paginated_sections = section_items[offset:offset + per_page]

        def section_page_url(page_number):
            params = {}
            if query:
                params["search"] = query
            if page_number > 1:
                params["page"] = page_number
            query_string = urlencode(params)
            return "/revista/seccion%s" % ("?%s" % query_string if query_string else "")

        section_post_counts = {}
        for section in paginated_sections:
            tag = section.get("tag")
            section_post_counts[section["slug"]] = self._posts_count(blog=blog, tag=tag) if tag else 0

        values = {
            "blog": blog,
            "section_slug": False,
            "section_search": query,
            "section_items": paginated_sections,
            "section_post_counts": section_post_counts,
            "section_current_page": current_page,
            "section_page_count": page_count,
            "section_total_count": total_sections,
            "section_prev_page_url": section_page_url(current_page - 1) if current_page > 1 else False,
            "section_next_page_url": section_page_url(current_page + 1) if current_page < page_count else False,
            "section_pagination_pages": [
                {
                    "number": page_number,
                    "url": section_page_url(page_number),
                    "active": page_number == current_page,
                }
                for page_number in range(1, page_count + 1)
            ],
            "section_seo_title": "Secciones | Revista LatinPyme",
            "section_seo_description": "Explora las secciones editoriales de Revista LatinPyme.",
        }
        return self._render("latinpyme_revista_theme.revista_section_index_page", values)

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
        per_page = section_record.section_posts_per_page if section_record and section_record.section_posts_per_page else (config.section_posts_per_page if config else 9)
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
            "section_banners": self._section_banners(section_record),
            "section_show_sidebar": self._section_display_enabled(section_record, "section_sidebar_mode", True),
            "section_show_related": self._section_display_enabled(section_record, "section_related_mode", True),
            "section_show_interviews": self._section_display_enabled(section_record, "section_interviews_mode", True),
            "section_show_portfolio": self._section_display_enabled(section_record, "section_portfolio_mode", True),
            "section_show_allies": self._section_display_enabled(section_record, "section_allies_mode", True),
            "section_interviews": self._interviews(section=section_record, limit=3) if section_record else request.env["latinpyme.revista.interview"].sudo().browse(),
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
