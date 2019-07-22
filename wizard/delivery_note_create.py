import datetime

from odoo import _, api, fields, models


class StockDeliveryNoteCreateWizard(models.TransientModel):
    _name = 'stock.delivery.note.create.wizard'
    _description = "Delivery note creator"

    def _default_date(self):
        return datetime.date.today()

    def _default_stock_pickings(self):
        active_ids = self.env.context['active_ids']

        return self.env['stock.picking'].browse(active_ids)

    def _default_type(self):
        return self.env['stock.delivery.note.type'].search([], limit=1)

    partner_id = fields.Many2one('res.partner', string=_("Recipient"), compute='_compute_partner_id')
    partner_shipping_id = fields.Many2one('res.partner', string=_("Shipping address"), required=True)

    date = fields.Date(string=_("Date"), default=_default_date)
    type_id = fields.Many2one('stock.delivery.note.type', string=_("Type"), default=_default_type, required=True)

    picking_ids = fields.Many2many('stock.picking',
                                   default=_default_stock_pickings,
                                   string=_("Pickings"),
                                   readonly=True)

    @api.depends('picking_ids')
    @api.onchange('picking_ids')
    def _compute_partner_id(self):
        if self.picking_ids:
            partner = self.picking_ids.mapped('partner_id')

            try:
                partner.ensure_one()

                self.partner_id = partner

            except ValueError:
                pass

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        if self.partner_id:
            return {
                'domain': {
                    'partner_shipping_id': [
                        '|', ('id', '=', self.partner_id.id),
                             ('parent_id', '=', self.partner_id.id)
                    ]
                }
            }

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
