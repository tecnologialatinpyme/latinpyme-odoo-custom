# -*- coding: utf-8 -*-

import json

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


def sitemap_revista_sections(env, rule, qs):
    for slug in SECTION_LABELS:
        yield {"loc": "/revista/seccion/%s" % slug}


class LatinpymeRevistaController(http.Controller):
    def _preproduction_host(self):
        host = request.httprequest.host.split(":", 1)[0].lower()
        return (
            host in PREPRODUCTION_HOSTS
            or host.endswith(".odoo.com")
            or host.endswith(".odoo.sh")
        )

    def _render(self, template, values):
        values.setdefault("sections", self._sections())
        values["lp_preproduction"] = self._preproduction_host()
        values["lp_production_url"] = "https://latinpyme.com%s" % request.httprequest.path
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
        label = SECTION_LABELS.get(section_slug)
        return self._tag_by_name(label) if label else request.env["blog.tag"].sudo().browse()

    def _sections(self):
        return [
            {
                "slug": slug,
                "name": name,
                "url": "/revista/seccion/%s" % slug,
                "tag": self._tag_by_name(name),
            }
            for slug, name in SECTION_LABELS.items()
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

    def _posts(self, blog=None, tag=None, extra_tags=None, limit=6, exclude_ids=None):
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
        return Post.search(domain, order="post_date desc, id desc", limit=limit)

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

    @http.route("/revista", type="http", auth="public", website=True, sitemap=True)
    def revista_home(self, **kwargs):
        blog = self._revista_blog()
        featured_post = self._featured_post(blog=blog)
        exclude_ids = featured_post.ids if featured_post else []
        interview_tag = self._tag_by_name("Entrevistas")
        special_tag = self._tag_by_name("Especiales")
        values = {
            "blog": blog,
            "featured_post": featured_post,
            "featured_style": self._cover_style(featured_post),
            "highlight_posts": self._posts(blog=blog, limit=3, exclude_ids=exclude_ids),
            "latest_posts": self._posts(blog=blog, limit=6, exclude_ids=exclude_ids),
            "new_posts": self._posts(blog=blog, limit=5, exclude_ids=exclude_ids),
            "interview_posts": self._posts(blog=blog, tag=interview_tag, limit=3),
            "special_posts": self._posts(blog=blog, tag=special_tag, limit=2),
        }
        return self._render("latinpyme_revista_theme.revista_home_page", values)

    @http.route(
        "/revista/seccion/<string:section_slug>",
        type="http",
        auth="public",
        website=True,
        sitemap=sitemap_revista_sections,
    )
    def revista_section(self, section_slug, **kwargs):
        if section_slug not in SECTION_LABELS:
            raise NotFound()
        blog = self._revista_blog()
        section_tag = self._section_tag(section_slug)
        empty_posts = request.env["blog.post"].sudo().browse()
        featured_post = self._featured_post(blog=blog, section_tag=section_tag) if section_tag else empty_posts
        exclude_ids = featured_post.ids if featured_post else []
        posts = self._posts(blog=blog, tag=section_tag, limit=12, exclude_ids=exclude_ids) if section_tag else empty_posts
        values = {
            "blog": blog,
            "section_slug": section_slug,
            "section_name": SECTION_LABELS[section_slug],
            "section_tag": section_tag,
            "featured_post": featured_post,
            "featured_style": self._cover_style(featured_post or blog),
            "posts": posts,
            "latest_posts": self._posts(blog=blog, limit=6, exclude_ids=exclude_ids),
        }
        return self._render("latinpyme_revista_theme.revista_section_page", values)
