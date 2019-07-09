from odoo import _, api, fields, models


class StockDeliveryNote(models.Model):
    _name = 'stock.delivery.note'
    _description = "Delivery note"

    name = fields.Char(string=_("Name"))

    # state = fields.Selection([...])  # TODO?

    transport_condition_id = fields.Many2one('stock.picking.transport.condition',
                                             string=_("Condition of transport"))
    goods_appearance_id = fields.Many2one('stock.picking.goods.appearance',
                                          string=_("Appearance of goods"))
    transport_reason_id = fields.Many2one('stock.picking.transport.reason',
                                          string=_("Reason of transport"))
    transport_method_id = fields.Many2one('stock.picking.transport.method',
                                          string=_("Method of transport"))

    date_transport_ddt = fields.Date(string=_("Delivery note Date"))
    time_transport_ddt = fields.Float(string=_("Delivery Note Start Time"))
