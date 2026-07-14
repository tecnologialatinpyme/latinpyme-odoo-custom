# -*- coding: utf-8 -*-

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _update_address(self, partner_id, fnames=None):
        # Bug nativo de website_sale: al editar el contacto principal (ej. desde
        # el enlace "editar datos" del checkout), Odoo reenvia address_type=
        # 'billing' por defecto, lo que fuerza partner_id y partner_invoice_id
        # al mismo valor y borra silenciosamente una direccion de facturacion
        # distinta que el cliente ya habia guardado (con su propia ciudad).
        # Si ya existe una direccion de facturacion separada y valida (con
        # ciudad), no la pisamos solo porque se este tocando el contacto
        # principal.
        if fnames and "partner_id" in fnames and "partner_invoice_id" in fnames:
            invoice_partner = self.partner_invoice_id
            if invoice_partner and invoice_partner.id != partner_id and invoice_partner.city:
                fnames = fnames - {"partner_invoice_id"}
        return super()._update_address(partner_id, fnames)
