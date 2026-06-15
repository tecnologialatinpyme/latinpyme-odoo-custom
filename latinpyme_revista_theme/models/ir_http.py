# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = "ir.http"

    @classmethod
    def _serve_page(cls):
        redirect = cls._serve_latinpyme_revista_seo_redirect()
        if redirect:
            return redirect
        return super()._serve_page()

    @classmethod
    def _register_website_track(cls, response):
        if cls._skip_latinpyme_revista_website_track():
            return False
        return super()._register_website_track(response)

    @classmethod
    def _skip_latinpyme_revista_website_track(cls):
        try:
            path = request.httprequest.path or ""
            host = (request.httprequest.host or "").split(":", 1)[0].lower()
            website = getattr(request, "website", False)
        except Exception:
            return False

        if not (
            path == "/blog/revista-latinpyme-2"
            or path.startswith("/blog/revista-latinpyme-2/")
            or path == "/revista"
            or path.startswith("/revista/")
        ):
            return False

        website_domain = ""
        website_name = ""
        if website:
            website_domain = (
                (getattr(website, "domain", "") or "").split(":", 1)[0].lower()
            )
            website_name = (getattr(website, "name", "") or "").lower()

        return (
            host in ("latinpyme.com", "revista.latinpyme.com")
            or website_domain in ("latinpyme.com", "revista.latinpyme.com")
            or "revista" in website_name
        )

    @classmethod
    def _serve_latinpyme_revista_seo_redirect(cls):
        website = getattr(request, "website", False)
        if not website:
            return False
        if (
            request.httprequest.path == "/"
            or not request.httprequest.path.endswith("/")
        ):
            return False
        Redirect = request.env["latinpyme.revista.seo.redirect"].sudo()
        old_path = Redirect.normalize_request_path(request.httprequest.path)
        if not old_path:
            return False
        record = Redirect.search([
            ("website_id", "=", website.id),
            ("old_path", "=", old_path),
            ("state", "in", ("active", "validated", "error")),
            ("rewrite_id.active", "=", True),
        ], limit=1)
        if not record or not record._rewrite_is_consistent():
            return False
        if request.env["website.page"].sudo()._get_page_info(request):
            return False
        target = record.new_path
        if request.httprequest.query_string:
            target = "%s?%s" % (
                target,
                request.httprequest.query_string.decode("utf-8"),
            )
        return request.redirect(target, code=301, local=False)
