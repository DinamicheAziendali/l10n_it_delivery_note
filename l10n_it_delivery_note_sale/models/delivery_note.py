# Copyright (c) 2020, DataBooz ltd - Luigi Di Naro
# @author: Luigi Di Naro <luigi.dinaro@databooz.com>

from odoo import api, fields, models


class StockDeliveryNote(models.Model):
    _inherit = 'stock.delivery.note'

    sale_ids = fields.Many2many('sale.order', compute='_compute_sales')
    sale_count = fields.Integer(compute='_compute_sales')
    sales_transport_check = fields.Boolean(compute='_compute_sales',
                                           default=True)

    @api.multi
    def _compute_sales(self):
        for note in self:
            sales = note.mapped('picking_ids.sale_id')

            note.sale_ids = sales
            note.sale_count = len(sales)

            tc = sales.mapped('default_transport_condition_id')
            ga = sales.mapped('default_goods_appearance_id')
            tr = sales.mapped('default_transport_reason_id')
            tm = sales.mapped('default_transport_method_id')
            note.sales_transport_check = all([
                len(x) < 2 for x in [tc, ga, tr, tm]
            ])
