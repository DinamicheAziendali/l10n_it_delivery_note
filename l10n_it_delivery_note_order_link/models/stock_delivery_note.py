# @author: Andrea Piovesana <andrea.m.piovesana@gmail.com>
from odoo import _, api, fields, models


class StockDeliveryNoteLine(models.Model):
    _inherit = 'stock.delivery.note.line'

    #sale_line_id = fields.Many2one('sale.order.line', related='move_id.sale_line_id', store=True, copy=False)
    purchase_line_id = fields.Many2one('purchase.order.line', related='move_id.purchase_line_id', store=True, copy=False)