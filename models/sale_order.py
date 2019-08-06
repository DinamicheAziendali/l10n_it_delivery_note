# Copyright (c) 2019, Link IT Europe Srl (http://www.linkgroup.it/)
# @author: Matteo Bilotta <mbilotta@linkgroup.it>

from odoo import _, api, fields, models

LINE_TO_INVOICE_STATUS = 'to invoice'
LINE_INVOICED_STATUS = 'invoiced'


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
    delivery_picking_id = fields.Many2one('stock.picking', readonly=True)

    @property
    def has_picking(self):
        return self.move_ids or (self.is_delivery and self.delivery_picking_id)

    @property
    def is_invoiceable(self):
        return self.invoice_status == LINE_TO_INVOICE_STATUS and self.qty_to_invoice != 0

    @property
    def already_invoiced(self):
        return self.invoice_status == LINE_INVOICED_STATUS and \
               self.product_uom_qty == self.qty_invoiced and \
               self.qty_to_invoice == 0

    def fix_qty_to_invoice(self, new_qty_to_invoice=0):
        self.ensure_one()

        cache = {
            'invoice_status': self.invoice_status,
            'qty_to_invoice': self.qty_to_invoice
        }

        self.write({
            'invoice_status': 'to invoice' if new_qty_to_invoice else 'no',
            'qty_to_invoice': new_qty_to_invoice
        })

        return cache

    def is_pickings_related(self, picking_ids):
        if self.is_delivery:
            return self.delivery_picking_id in picking_ids

        return bool(self.move_ids & picking_ids.mapped('move_lines'))

    @api.multi
    def retrieve_pickings_lines(self, picking_ids):
        return self.filtered(lambda l: l.has_picking) \
                   .filtered(lambda l: l.is_pickings_related(picking_ids))
