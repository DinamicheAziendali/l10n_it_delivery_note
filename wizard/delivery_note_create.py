from odoo import _, api, fields, models


class DeliveryNoteCreateWizard(models.TransientModel):
    _name = 'stock.picking.delivery.note.create.wizard'
    _description = "Delivery Note creator"

    def _default_stock_pickings(self):
        active_ids = self.env.context['active_ids']

        return self.env['stock.picking'].browse(active_ids)

    picking_ids = fields.Many2many('stock.picking',
                                   default=_default_stock_pickings,
                                   string=_("Pickings"),
                                   readonly=True)

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
