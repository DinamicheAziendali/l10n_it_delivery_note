from datetime import datetime

from odoo import _, api, fields, models

DELIVERY_NOTE_STATES = [
    ('draft', "Draft"),
    ('done', "Done"),
    ('cancel', "Cancelled")
]
DOMAIN_DELIVERY_NOTE_STATES = [s[0] for s in DELIVERY_NOTE_STATES]


class StockDeliveryNote(models.Model):
    _name = 'stock.delivery.note'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Delivery note"

    active = fields.Boolean(string=_("Active"), default=True)
    name = fields.Char(string=_("Name"), required=True, track_visibility='onchange')

    partner_id = fields.Many2one('res.partner',
                                 string=_("Recipient"),
                                 required=True,
                                 track_visibility='onchange')
    partner_shipping_id = fields.Many2one('res.partner',
                                          string=_("Shipping address"),
                                          required=True,
                                          track_visibility='onchange')

    state = fields.Selection(DELIVERY_NOTE_STATES,
                             string=_("State"),
                             default=DOMAIN_DELIVERY_NOTE_STATES[0],
                             required=True,
                             track_visibility='onchange')

    transport_condition_id = fields.Many2one('stock.picking.transport.condition', string=_("Condition of transport"))
    goods_appearance_id = fields.Many2one('stock.picking.goods.appearance', string=_("Appearance of goods"))
    transport_reason_id = fields.Many2one('stock.picking.transport.reason', string=_("Reason of transport"))
    transport_method_id = fields.Many2one('stock.picking.transport.method', string=_("Method of transport"))

    transport_datetime = fields.Datetime(string=_("Transport date"), default=datetime.now())

    picking_ids = fields.One2many('stock.picking', 'delivery_note_id', string=_("Pickings"))

    note = fields.Html(string=_("Internal note"))

    @api.onchange('partner_id')
    def _onchange_partner(self):
        domain = []

        if self.partner_id:
            domain = [
                '|', ('id', '=', self.partner_id.id),
                     ('parent_id', '=', self.partner_id.id)
            ]

        return {
            'domain': {'partner_shipping_id': domain}
        }

    @api.multi
    def action_draft(self):
        self.write({'state': DOMAIN_DELIVERY_NOTE_STATES[0]})

    @api.multi
    def action_done(self):
        self.write({'state': DOMAIN_DELIVERY_NOTE_STATES[1]})

    @api.multi
    def action_cancel(self):
        self.write({'state': DOMAIN_DELIVERY_NOTE_STATES[2]})
