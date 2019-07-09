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
    _description = "Condition of transport"
    _order = 'sequence, name, id'

    active = fields.Boolean(string=_("Active"), default=True)
    sequence = fields.Integer(string=_("Sequence"), index=True, default=10)
    name = fields.Char(string=_("Condition name"), index=True, required=True, translate=True)
    note = fields.Html(string=_("Internal note"))

    _sql_constraints = [(
        'name_uniq',
        'unique(name)',
        "This condition of transport name is already used!"
    )]


class StockPickingGoodsAppearance(models.Model):
    _name = 'stock.picking.goods.appearance'
    _description = "Appearance of goods"
    _order = 'sequence, name, id'

    active = fields.Boolean(string=_("Active"), default=True)
    sequence = fields.Integer(string=_("Sequence"), index=True, default=10)
    name = fields.Char(string=_("Appearance name"), index=True, required=True, translate=True)
    note = fields.Html(string=_("Internal note"))

    _sql_constraints = [(
        'name_uniq',
        'unique(name)',
        "This appearance of goods name is already used!"
    )]


class StockPickingTransportReason(models.Model):
    _name = 'stock.picking.transport.reason'
    _description = "Reason of transport"
    _order = 'sequence, name, id'

    active = fields.Boolean(string=_("Active"), default=True)
    sequence = fields.Integer(string=_("Sequence"), index=True, default=10)
    name = fields.Char(string=_("Reason name"), index=True, required=True, translate=True)
    note = fields.Html(string=_("Internal note"))

    _sql_constraints = [(
        'name_uniq',
        'unique(name)',
        "This reason of transport name is already used!"
    )]


class StockPickingTransportMethod(models.Model):
    _name = 'stock.picking.transport.method'
    _description = "Method of transport"
    _order = 'sequence, name, id'

    active = fields.Boolean(string=_("Active"), default=True)
    sequence = fields.Integer(string=_("Sequence"), index=True, default=10)
    name = fields.Char(string=_("Method name"), index=True, required=True, translate=True)
    note = fields.Html(string=_("Internal note"))

    _sql_constraints = [(
        'name_uniq',
        'unique(name)',
        "This method of transport name is already used!"
    )]


class StockDdtType(models.Model):
    _name = 'stock.ddt.type'
    _inherit = 'mail.thread'
    _description = "Transport note type"
    _order = 'sequence, name, id'

    active = fields.Boolean(string=_("Active"), default=True)
    sequence = fields.Integer(string=_("Sequence"), index=True, default=10)
    name = fields.Char(string=_(""), index=True, required=True, translate=True)
    sequence_id = fields.Many2one('ir.sequence', required=True)
    company_id = fields.Many2one('res.company', string=_("Company"), default=lambda self: self.env.user.company_id)
    note = fields.Html(string=_("Internal note"))
