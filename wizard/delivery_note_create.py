import datetime

from odoo import _, api, fields, models


class StockDeliveryNoteCreateWizard(models.TransientModel):
    _name = 'stock.delivery.note.create.wizard'
    _inherit = 'stock.delivery.note.base.wizard'
    _description = "Delivery note creator"

    def _default_date(self):
        return datetime.date.today()

    def _default_stock_pickings(self):
        active_ids = self.env.context['active_ids']

        return self.env['stock.picking'].browse(active_ids)

    def _default_type(self):
        return self.env['stock.delivery.note.type'].search([], limit=1)

    picking_ids = fields.Many2many('stock.picking', default=_default_stock_pickings)

    partner_id = fields.Many2one('res.partner', compute='_compute_fields')
    partner_shipping_id = fields.Many2one('res.partner', required=True)

    date = fields.Date(default=_default_date)
    type_id = fields.Many2one('stock.delivery.note.type', default=_default_type, required=True)

    error_message = fields.Html(compute='_compute_fields')

    def _init_partner_id(self):
        partner = self.picking_ids.mapped('partner_id')
        partner.ensure_one()

        self.partner_id = partner

    @api.depends('picking_ids')
    def _compute_fields(self):
        errors = {}

        if self.picking_ids:
            try:
               self._init_partner_id()

            except ValueError:
                errors['invalid_partners'] = True

        else:
            errors['no_pickings'] = True

        if errors:
            errors['title'] = _("Warning!")

            self.error_message = self.env['ir.ui.view'] \
                .render_template('easy_ddt.stock_delivery_note_wizard_error_message_template', errors)
