from odoo import _, api, fields, models

from ..models.stock_delivery_note import DOMAIN_DELIVERY_NOTE_STATES


class StockDeliveryNoteSelectWizard(models.TransientModel):
    _name = 'stock.delivery.note.select.wizard'
    _description = "Delivery note selector"

    def _default_stock_picking(self):
        active_ids = self.env.context['active_ids']

        return self.env['stock.picking'].browse(active_ids)

    selected_picking_id = fields.Many2one('stock.picking', default=_default_stock_picking)
    selected_partner_id = fields.Many2one('res.partner', related='selected_picking_id.partner_id')

    delivery_note_id = fields.Many2one('stock.delivery.note', string=_("Delivery note"), required=True)

    partner_id = fields.Many2one('res.partner', string=_("Recipient"), related='delivery_note_id.partner_id')
    partner_shipping_id = fields.Many2one('res.partner',
                                          string=_("Shipping address"),
                                          related='delivery_note_id.partner_shipping_id')

    date = fields.Date(string=_("Date"), related='delivery_note_id.date')
    type_id = fields.Many2one('stock.delivery.note.type', string=_("Type"), related='delivery_note_id.type_id')

    picking_ids = fields.Many2many('stock.picking',
                                   string=_("Pickings"),
                                   compute='_compute_picking_ids')

    @api.depends('selected_picking_id', 'delivery_note_id')
    def _compute_picking_ids(self):
        self.picking_ids = None

        if self.delivery_note_id:
            self.picking_ids += self.delivery_note_id.picking_ids

        if self.selected_picking_id:
            self.picking_ids += self.selected_picking_id

    def check_compliance(self):
        #
        # TODO #1: Stesso partner.
        # TODO #2: Stesso magazzino di partenza.
        # TODO #3: Stesso periodo di fatturazione (?).
        # [...]
        # TODO #N: Altro?
        #

        pass

    @api.multi
    def confirm(self):
        self.check_compliance()
        #
        # TODO: Something, something...
        #

        pass
