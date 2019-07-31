# Copyright (c) 2019, Link IT Europe Srl (http://www.linkgroup.it/)
# @author: Matteo Bilotta <mbilotta@linkgroup.it>

from odoo import _, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    transport_condition_id = fields.Many2one('stock.picking.transport.condition', string=_("Condition of transport"))
    goods_appearance_id = fields.Many2one('stock.picking.goods.appearance', string=_("Appearance of goods"))
    transport_reason_id = fields.Many2one('stock.picking.transport.reason', string=_("Reason of transport"))
    transport_method_id = fields.Many2one('stock.picking.transport.method', string=_("Method of transport"))
