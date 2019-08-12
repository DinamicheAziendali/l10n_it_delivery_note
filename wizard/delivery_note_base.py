# Copyright (c) 2019, Link IT Europe Srl (http://www.linkgroup.it/)
# @author: Matteo Bilotta <mbilotta@linkgroup.it>

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class StockDeliveryNoteBaseWizard(models.AbstractModel):
    _name = 'stock.delivery.note.base.wizard'
    _inherit = 'stock.picking.checker.mixin'
    _description = "Delivery note base"

    def _default_stock_pickings(self):
        active_ids = self.env.context['active_ids']

        return self.env['stock.picking'].browse(active_ids)

    selected_picking_ids = fields.Many2many('stock.picking', default=_default_stock_pickings, readonly=True)

    partner_id = fields.Many2one('res.partner', string=_("Recipient"), compute='_compute_fields')
    partner_shipping_id = fields.Many2one('res.partner', string=_("Shipping address"))

    date = fields.Date(string=_("Date"))
    type_id = fields.Many2one('stock.delivery.note.type', string=_("Type"))

    error_message = fields.Html(compute='_compute_fields')

    def _get_validation_errors(self, pickings):
        validators = [
            (self._check_pickings, True),
            (self._check_pickings_state, False),
            (self._check_pickings_type, False),
            (self._check_partners, False),
            (self._check_pickings_location, False),
            (self._check_delivery_notes, False)
        ]

        errors = []
        for validator, interrupt in validators:
            try:
                validator(pickings)

            except ValidationError as exc:
                errors.append(exc.name)

                if interrupt:
                    break

        return errors

    @api.depends('selected_picking_ids')
    def _compute_fields(self):
        try:
            self.check_compliance(self.selected_picking_ids)

        except ValidationError:
            values = {
                'title': _("Warning!"),
                'errors': self._get_validation_errors(self.selected_picking_ids)
            }

            self.error_message = self.env['ir.ui.view'] \
                .render_template('easy_ddt.stock_delivery_note_wizard_error_message_template', values)

        else:
            self.partner_id = self.mapped('selected_picking_ids.partner_id')

    def confirm(self):
        raise NotImplementedError(_("This functionality isn't ready yet. Please, come back later."))
