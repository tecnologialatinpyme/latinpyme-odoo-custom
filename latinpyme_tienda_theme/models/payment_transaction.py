# -*- coding: utf-8 -*-

from odoo import models
from odoo.tools import float_round

from odoo.addons.payment.const import CURRENCY_MINOR_UNITS
from odoo.addons.payment_mercado_pago import const as mercado_pago_const

_MERCADO_PAGO_TITLE_MAX_LENGTH = 256


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def _mercado_pago_prepare_preference_request_payload(self):
        # Odoo native behavior sends a single item with the bare transaction
        # reference (e.g. "S00224") as the title, so the customer sees no
        # hint of what they're paying for on Mercado Pago's own checkout
        # screen - and with several products in the cart, showing them all
        # joined into one title reads as a single unreadable block. Replace
        # the single item with one item per purchased product instead.
        payload = super()._mercado_pago_prepare_preference_request_payload()
        items = self._get_mercado_pago_items()
        if items:
            payload["items"] = items
        return payload

    def _get_mercado_pago_items(self):
        self.ensure_one()
        order_lines = self.sale_order_ids.order_line.filtered(
            lambda line: not line.display_type and line.price_total
        )
        lines_subtotal = sum(order_lines.mapped("price_total"))
        if not order_lines or not lines_subtotal:
            return []

        total_amount = self._mercado_pago_convert_amount()
        items = []
        allocated = 0.0
        last_index = len(order_lines) - 1
        for index, line in enumerate(order_lines):
            if index == last_index:
                # The last item absorbs the rounding remainder so the sum of
                # all items always matches the exact amount Mercado Pago
                # will charge - never let per-line rounding drift the total.
                amount = total_amount - allocated
            else:
                amount = self._mercado_pago_round_amount(
                    total_amount * (line.price_total / lines_subtotal)
                )
            allocated += amount

            quantity = line.product_uom_qty or 1
            title = line.product_id.name or line.name or self.reference
            if quantity != 1:
                title = f"{title} (x{quantity:g})"
            items.append({
                "title": title[:_MERCADO_PAGO_TITLE_MAX_LENGTH],
                "quantity": 1,
                "currency_id": self.currency_id.name,
                "unit_price": amount,
            })
        return items

    def _mercado_pago_round_amount(self, amount):
        decimal_places = mercado_pago_const.CURRENCY_DECIMALS.get(
            self.currency_id.name, CURRENCY_MINOR_UNITS.get(self.currency_id.name)
        )
        if decimal_places is not None:
            amount = float_round(amount, decimal_places, rounding_method='DOWN')
        return amount
