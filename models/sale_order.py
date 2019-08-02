# Copyright (c) 2019, Link IT Europe Srl (http://www.linkgroup.it/)
# @author: Matteo Bilotta <mbilotta@linkgroup.it>

from odoo import _, api, fields, models

LINE_TO_INVOICE_STATUS = 'to invoice'


# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#     delivery_note_ids = fields.Many2many('stock.delivery.note', compute='_compute_delivery_note_id')
#
#     @api.multi
#     def _compute_delivery_note_id(self):
#         for note in self:
#             note.delivery_note_ids = note.mapped('line_ids.delivery_note_line_id.delivery_note_id')


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    delivery_note_line_id = fields.One2many('stock.delivery.note.line', 'sale_line_id', readonly=True)
    picking_id = fields.Many2one('stock.picking', readonly=True)

    def make_not_invoiceable(self):
        self.ensure_one()

        cache = {
            'invoice_status': self.invoice_status,
            'qty_to_invoice': self.qty_to_invoice
        }

        self.write({
            'invoice_status': 'no',
            'qty_to_invoice': 0
        })

        return cache

    @api.multi
    def retrieve_invoiceable_lines(self):
        return self.filtered(lambda l: l.invoice_status == LINE_TO_INVOICE_STATUS and l.qty_to_invoice != 0)

    @api.multi
    def retrieve_unrelated_lines(self, delivery_note):
        return self.filtered(lambda l: l.delivery_note_line_id and
                                       l.delivery_note_line_id.delivery_note_id != delivery_note)
