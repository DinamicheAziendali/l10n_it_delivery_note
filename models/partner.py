##############################################################################
#
#    Copyright (C) 2015 Apulia Software s.r.l. (http://www.apuliasoftware.it)
#    @author Francesco Apruzzese <f.apruzzese@apuliasoftware.it>
#
#    License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
#
#    migrated from V8
##############################################################################

from odoo import _, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    transport_condition_id = fields.Many2one(
        'stock.picking.transport.condition', string=_("Transport Condition"))
    goods_appearance_id = fields.Many2one(
        'stock.picking.goods.appearance', string=_("Appearance of Goods"))
    transport_reason_id = fields.Many2one(
        'stock.picking.transport.reason', string=_("Transport Reason"))
    transport_method_id = fields.Many2one(
        'stock.picking.transport.method', string=_("Transport Method"))
