##############################################################################
#
#    part of file stock_picking_package_preparation.py
#    migrated from V8
#    Copyright (C) 2015 Apulia Software s.r.l. (http://www.apuliasoftware.it)
#    @author Francesco Apruzzese <f.apruzzese@apuliasoftware.it>
#
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
##############################################################################

from odoo import _, fields, models


class StockPickingCarriageCondition(models.Model):
    _name = "stock.picking.transport.condition"
    _description = "Transport Condition"

    name = fields.Char(
        string=_("Condition name"), required=True, translate=True)
    note = fields.Text(string='Note', translate=True)


class StockPickingGoodsDescription(models.Model):
    _name = 'stock.picking.goods_description'
    _description = "Description of Goods"

    name = fields.Char(
        string='Description of Goods', required=True, translate=True)
    note = fields.Text(string='Note', translate=True)


class StockPickingTransportationReason(models.Model):
    _name = 'stock.picking.transport.reason'
    _description = "Transport Reason"

    name = fields.Char(
        string=_("Reason name"), required=True, translate=True)
    note = fields.Text(string='Note', translate=True)


class StockPickingTransportationMethod(models.Model):
    _name = 'stock.picking.transport.method'
    _description = "Transport Method"

    name = fields.Char(
        string=_("Method name"), required=True, translate=True)
    note = fields.Text(string='Note', translate=True)


class StockDdtType(models.Model):
    _name = 'stock.ddt.type'
    _description = 'Stock DdT Type'
    _inherit = ['mail.thread']

    name = fields.Char(required=True)
    sequence_id = fields.Many2one('ir.sequence', required=True)
    note = fields.Text(string='Note')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id)
