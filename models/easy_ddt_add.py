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
    _name = 'stock.picking.transport.condition'
    _description = "Transport Condition"

    name = fields.Char(
        string=_("Condition name"), required=True, translate=True)
    note = fields.Text(string=_("Internal note"))


class StockPickingGoodsAppearance(models.Model):
    _name = 'stock.picking.goods.appearance'
    _description = "Appearance of Goods"

    name = fields.Char(
        string=_("Appearance of Goods name"), required=True, translate=True)
    note = fields.Text(string=_("Internal note"))


class StockPickingTransportReason(models.Model):
    _name = 'stock.picking.transport.reason'
    _description = "Transport Reason"

    name = fields.Char(
        string=_("Reason name"), required=True, translate=True)
    note = fields.Text(string=_("Internal note"))


class StockPickingTransportMethod(models.Model):
    _name = 'stock.picking.transport.method'
    _description = "Transport Method"

    name = fields.Char(
        string=_("Method name"), required=True, translate=True)
    note = fields.Text(string=_("Internal note"))


class StockDdtType(models.Model):
    _name = 'stock.ddt.type'
    _inherit = 'mail.thread'
    _description = "Stock DdT Type"

    name = fields.Char(required=True)
    sequence_id = fields.Many2one('ir.sequence', required=True)
    note = fields.Text(string=_("Internal note"))
    company_id = fields.Many2one(
        'res.company',
        string=_("Company"),
        default=lambda self: self.env.user.company_id)
