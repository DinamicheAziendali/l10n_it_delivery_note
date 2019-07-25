import datetime

from odoo import fields, models


class StockDeliveryNoteCreateWizard(models.TransientModel):
    _name = 'stock.delivery.note.create.wizard'
    _inherit = 'stock.delivery.note.base.wizard'
    _description = "Delivery note creator"

    def _default_date(self):
        return datetime.date.today()

    def _default_type(self):
        return self.env['stock.delivery.note.type'].search([], limit=1)

    partner_shipping_id = fields.Many2one('res.partner', required=True)

    date = fields.Date(default=_default_date)
    type_id = fields.Many2one('stock.delivery.note.type', default=_default_type, required=True)
