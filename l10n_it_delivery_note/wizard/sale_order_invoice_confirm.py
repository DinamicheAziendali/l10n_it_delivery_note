from odoo import _, api, fields, models


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    @api.multi
    def create_invoices(self):
        states = self.mapped('delivery_note_ids.state')

        import pdb; pdb.set_trace()

        return super().create_invoices()
