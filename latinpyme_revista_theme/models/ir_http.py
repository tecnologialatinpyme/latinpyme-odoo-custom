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
