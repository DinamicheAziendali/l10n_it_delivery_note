# Copyright (c) 2019, Link IT Europe Srl (http://www.linkgroup.it/)
# @author: Matteo Bilotta <mbilotta@linkgroup.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# from odoo import _, api, fields, models
#
#
# class StockMove(models.Model):
#     _inherit = 'stock.move'
#
#     @api.multi
#     def _propagate_picking_to_sale_line(self):
#         for move in self.filtered(lambda m: m.sale_line_id and m.picking_id):
#             move.sale_line_id.picking_id = move.picking_id
#
#     @api.model
#     def create(self, vals):
#         res = super().create(vals)
#
#         if 'sale_line_id' in vals and 'picking_id' in vals:
#             res._propagate_picking_to_sale_line()
#
#         return res
#
#     @api.multi
#     def write(self, vals):
#         res = super().write(vals)
#
#         if 'sale_line_id' in vals or 'picking_id' in vals:
#             self._propagate_picking_to_sale_line()
#
#         return res
