# -*- coding: utf-8 -*-

from odoo import models

_MERCADO_PAGO_TITLE_MAX_LENGTH = 250


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _mercado_pago_prepare_preference_request_payload(self):
        # Odoo native behavior only sends the bare transaction reference
        # (e.g. "S00224") as the item title, so the customer sees no hint of
        # what they're paying for on Mercado Pago's own checkout screen.
        # Prepend the purchased product name(s) while keeping the reference
        # for traceability - nothing else in the native payload is touched.
        payload = super()._mercado_pago_prepare_preference_request_payload()
        title = self._get_mercado_pago_item_title()
        if title and payload.get("items"):
            payload["items"][0]["title"] = title
        return payload

    def _get_mercado_pago_item_title(self):
        self.ensure_one()
        order_lines = self.sale_order_ids.order_line.filtered(lambda line: not line.display_type)
        product_names = list(dict.fromkeys(order_lines.mapped("product_id.name")))
        if not product_names:
            return ""

        title = ", ".join(product_names)
        suffix = f" - {self.reference}"
        max_names_length = max(_MERCADO_PAGO_TITLE_MAX_LENGTH - len(suffix), 1)
        if len(title) > max_names_length:
            title = f"{title[:max_names_length - 1]}…"
        return f"{title}{suffix}"
