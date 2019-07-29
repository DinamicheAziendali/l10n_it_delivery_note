from odoo import _, api, fields, models


class StockPickingSelectWizard(models.TransientModel):
    _name = 'stock.picking.select.wizard'
    _description = "Picking selector"

    def _default_delivery_notes(self):
        active_ids = self.env.context['active_ids']

        return self.env['stock.delivery.note'].browse(active_ids)

    delivery_note_ids = fields.Many2many('stock.delivery.note', default=_default_delivery_notes, readonly=True)

    picking_ids = fields.Many2many('stock.picking', string=_("Pickings"))

    def confirm(self):
        raise NotImplementedError(_("This functionality isn't ready yet. Please, come back later."))