# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request


class LatinpymeTiendaController(http.Controller):
    @http.route("/tienda", type="http", auth="public", website=True, sitemap=True)
    def tienda_home(self, **kwargs):
        return request.render("latinpyme_tienda_theme.lp_tienda_home_page", {})

