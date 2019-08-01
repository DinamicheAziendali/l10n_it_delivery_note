# Copyright (c) 2019, Link IT Europe Srl (http://www.linkgroup.it/)
# @author: Matteo Bilotta <mbilotta@linkgroup.it>

from odoo import _, api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_transport_fee = fields.Boolean(compute='_compute_is_transport_fee')

    delivery_note_line_id = fields.One2many('stock.delivery.note.line', 'sale_line_id', readonly=True)

    @api.multi
    def _compute_is_transport_fee(self):
        delivery_category = self.env.ref('delivery.product_category_deliveries', raise_if_not_found=False)
        if not delivery_category:
            return

        for line in self:
            line.is_transport_fee = line.product_id.categ_id == delivery_category
