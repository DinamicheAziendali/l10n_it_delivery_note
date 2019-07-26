from odoo import _, api, fields, models


class StockDeliveryNoteSelectWizard(models.TransientModel):
    _name = 'stock.delivery.note.select.wizard'
    _inherit = 'stock.delivery.note.base.wizard'
    _description = "Delivery note selector"

    delivery_note_id = fields.Many2one('stock.delivery.note', string=_("Delivery note"), required=True)

    partner_shipping_id = fields.Many2one('res.partner', related='delivery_note_id.partner_shipping_id')

    date = fields.Date(related='delivery_note_id.date')
    type_id = fields.Many2one('stock.delivery.note.type', related='delivery_note_id.type_id')

    picking_ids = fields.Many2many('stock.picking', compute='_compute_fields')

    @api.depends('selected_picking_ids', 'delivery_note_id')
    def _compute_fields(self):
        super()._compute_fields()

        if self.delivery_note_id:
            self.picking_ids += self.delivery_note_id.picking_ids

        if self.selected_picking_ids:
            self.picking_ids += self.selected_picking_ids

    def check_compliance(self, pickings):
        self._check_pickings(pickings)
        self._check_pickings_state(pickings)
        self._check_partners(pickings)
        self._check_pickings_location(pickings)

        self._check_delivery_notes(self.selected_picking_ids)

    def confirm(self):
        self.check_compliance(self.picking_ids)
        self.selected_picking_ids.write({'delivery_note_id': self.delivery_note_id.id})
