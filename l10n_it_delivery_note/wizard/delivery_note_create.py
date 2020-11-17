# Copyright (c) 2019, Link IT Europe Srl
# @author: Matteo Bilotta <mbilotta@linkeurope.it>

import datetime

from odoo import api, fields, models

from ..mixins.picking_checker import PICKING_TYPES


class StockDeliveryNoteCreateWizard(models.TransientModel):
    _name = 'stock.delivery.note.create.wizard'
    _inherit = 'stock.delivery.note.base.wizard'
    _description = "Delivery Note Creator"

    def _default_date(self):
        return datetime.date.today()

    def _default_type(self):
        active_ids = self.env.context.get('active_ids', [])
        picking_ids = self.env['stock.picking'].browse(active_ids)
        if picking_ids:
            type_code = picking_ids[0].picking_type_id.code

            return self.env['stock.delivery.note.type'] \
                       .search([('code', '=', type_code)], limit=1)

        else:
            return self.env['stock.delivery.note.type'] \
                       .search([('code', '=', 'outgoing')], limit=1)

    partner_shipping_id = fields.Many2one('res.partner', required=True)

    date = fields.Date(default=_default_date)
    type_id = fields.Many2one('stock.delivery.note.type',
                              default=_default_type,
                              required=True)
    picking_type = fields.Selection(PICKING_TYPES,
                                    string="Picking type",
                                    compute='_compute_picking_type')

    @api.multi
    @api.depends('selected_picking_ids')
    def _compute_picking_type(self):
        picking_types = set(self.selected_picking_ids.mapped('picking_type_code'))
        picking_types = list(picking_types)

        if len(picking_types) != 1:
            raise ValueError(
                "You have just called this method on an "
                "heterogeneous set of pickings.\n"
                "All pickings should have the same "
                "'picking_type_code' field value.")

        self.picking_type = picking_types[0]

    @api.model
    def check_compliance(self, pickings):
        super().check_compliance(pickings)

        self._check_delivery_notes(pickings)

    @api.model
    def create_delivery_note(self, pickings,
                                   partner_sender=None,
                                   partner=None,
                                   partner_shipping=None,
                                   delivery_note_type=None,
                                   date=None):

        self.check_compliance(pickings)

        partners = pickings.get_partners()
        sale_order_ids = pickings.mapped('sale_id')
        sale_order_id = sale_order_ids and sale_order_ids[0] or False

        sender = partner_sender or partners[0]
        recipient = partner or partners[1]
        shipping = partner_shipping or partners[1]

        delivery_note = self.env['stock.delivery.note'].create({
            'partner_sender_id': sender.id,
            'partner_id': recipient.id,
            'partner_shipping_id': shipping.id,
            'type_id': delivery_note_type.id if delivery_note_type else None,
            'date': date,

            'delivery_method_id':
                recipient.property_delivery_carrier_id.id,
            'transport_condition_id':
                sale_order_id and
                sale_order_id.default_transport_condition_id.id or
                recipient.default_transport_condition_id.id or
                delivery_note_type.default_transport_condition_id.id
                    if delivery_note_type else None,
            'goods_appearance_id':
                sale_order_id and
                sale_order_id.default_goods_appearance_id.id or
                recipient.default_goods_appearance_id.id or
                delivery_note_type.default_goods_appearance_id.id
                    if delivery_note_type else None,
            'transport_reason_id':
                sale_order_id and
                sale_order_id.default_transport_reason_id.id or
                recipient.default_transport_reason_id.id or
                delivery_note_type.default_transport_reason_id.id
                    if delivery_note_type else None,
            'transport_method_id':
                sale_order_id and
                sale_order_id.default_transport_method_id.id or
                recipient.default_transport_method_id.id or
                delivery_note_type.default_transport_method_id.id
                    if delivery_note_type else None
        })

        pickings.write({'delivery_note_id': delivery_note.id})

        return delivery_note

    @api.onchange('partner_id')
    def _onchange_partner(self):
        self.partner_shipping_id = self.partner_id

    def confirm(self):
        delivery_note = self.create_delivery_note(self, self.selected_picking_ids,
            partner_sender=self.partner_sender_id,
            partner=self.partner_id,
            partner_shipping=self.partner_shipping_id,
            delivery_note_type=self.type_id,
            date=self.date)

        if self.user_has_groups('l10n_it_delivery_note.use_advanced_delivery_notes'):
            return delivery_note.goto()
