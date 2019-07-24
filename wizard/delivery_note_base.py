from odoo import _, api, fields, models


class StockDeliveryNoteCreateWizard(models.AbstractModel):
    _name = 'stock.delivery.note.base.wizard'
    _description = "Delivery note base"

    error_message = fields.Html(readonly=True, store=False)

    partner_id = fields.Many2one('res.partner', string=_("Recipient"))
    partner_shipping_id = fields.Many2one('res.partner', string=_("Shipping address"))

    date = fields.Date(string=_("Date"))
    type_id = fields.Many2one('stock.delivery.note.type', string=_("Type"))

    picking_ids = fields.Many2many('stock.picking', string=_("Pickings"), readonly=True)

    def check_compliance(self):
        #
        # TODO #1: Stesso partner.
        # TODO #2: Stesso magazzino di partenza.
        # TODO #3: Stesso periodo di fatturazione (?).
        # [...]
        # TODO #N: Altro?
        #

        raise NotImplementedError(_("This functionality isn't yet ready. Please, come back later."))

    @api.multi
    def confirm(self):
        self.check_compliance()
        #
        # TODO: Something, something...
        #

        raise NotImplementedError(_("This functionality isn't yet ready. Please, come back later."))
