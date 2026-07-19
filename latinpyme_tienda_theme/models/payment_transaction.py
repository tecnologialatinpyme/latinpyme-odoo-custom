# -*- coding: utf-8 -*-

from odoo import models

_MERCADO_PAGO_TITLE_MAX_LENGTH = 256


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _mercado_pago_prepare_preference_request_payload(self):
        # Odoo native behavior sends a single item with the bare transaction
        # reference (e.g. "S00224") as the title, so the customer sees no
        # hint of what they're paying for on Mercado Pago's own checkout
        # screen. Mercado Pago's own payment summary only ever renders a
        # title when the preference has exactly one item - as soon as there
        # are two or more it collapses the whole list to a generic
        # "Productos" label (confirmed live, not something the payload can
        # change). So keep a single item, matching Mercado Pago's own
        # requirement for the title to actually show, and put a clean,
        # human-readable product list in it instead of the bare reference.
        payload = super()._mercado_pago_prepare_preference_request_payload()
        title = self._get_mercado_pago_item_title()
        if title and payload.get("items"):
            payload["items"][0]["title"] = title
        return payload

    def _get_mercado_pago_item_title(self):
        self.ensure_one()
        order_lines = self.sale_order_ids.order_line.filtered(lambda line: not line.display_type)
        names = []
        for line in order_lines:
            name = line.product_id.name or line.name
            if not name:
                continue
            quantity = line.product_uom_qty
            if quantity and quantity != 1:
                name = f"{name} (x{quantity:g})"
            names.append(name)

        if not names:
            return ""

        if len(names) == 1:
            title = names[0]
        elif len(names) == 2:
            title = f"{names[0]} y {names[1]}"
        else:
            title = f"{len(names)} productos: {', '.join(names[:-1])} y {names[-1]}"

        return title[:_MERCADO_PAGO_TITLE_MAX_LENGTH]
