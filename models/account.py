# Copyright 2014-2019 Dinamiche Aziendali srl (http://www.dinamicheaziendali.it/)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Gianmarco Conte <gconte@dinamicheaziendali.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    transport_condition_id = fields.Many2one(
        'stock.picking.transport.condition', string=_("Transport Condition"))
    goods_appearance_id = fields.Many2one(
        'stock.picking.goods.appearance', string=_("Appearance of Goods"))
    transport_reason_id = fields.Many2one(
        'stock.picking.transport.reason', string=_("Transport Reason"))
    transport_method_id = fields.Many2one(
        'stock.picking.transport.method', string=_("Transport Method"))

    number_of_packages = fields.Integer()
