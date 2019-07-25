from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from ..models.stock_picking import DONE_PICKING_STATE


class StockDeliveryNoteCreateWizard(models.AbstractModel):
    _name = 'stock.delivery.note.base.wizard'
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

    def _check_pickings(self):
        if not self.selected_picking_ids:
            raise ValidationError(_("You shouldn't be able to launch this wizard without selecting any pickings."))

    def _check_pickings_state(self):
        if self.selected_picking_ids.filtered(lambda p: not p.state == DONE_PICKING_STATE):
            raise ValidationError(_("At least one picking you've selected doesn't appear to be completed."))

    def _check_delivery_notes(self):
        if self.selected_picking_ids.filtered(lambda p: p.delivery_note_id):
            raise ValidationError(_("At least one picking you've selected appears to"
                                    " be already related to another delivery note."))

    def _check_partners(self):
        partners = self.selected_picking_ids.mapped('partner_id')

        if not partners:
            raise ValidationError(_("The pickings you've selected don't seem to have any partner."))

        if len(partners) > 1:
            raise ValidationError(_("You need to select pickings with all the same partner."))

    def _check_pickings_location(self):
        locations = self.selected_picking_ids.mapped('location_dest_id')

        if not locations:
            raise ValidationError(_("The pickings you've selected don't seem to have any location of destination."))

        if len(locations) > 1:
            raise ValidationError(_("You need to select pickings with all the same location of destination."))

    def _get_validation_errors(self):
        validators = [
            (self._check_pickings, True),
            (self._check_pickings_state, False),
            (self._check_partners, False),
            (self._check_pickings_location, False),
            (self._check_delivery_notes, False)
        ]

        errors = []
        for validator, interrupt in validators:
            try:
                validator()

            except ValidationError as exc:
                errors.append(exc.name)

                if interrupt:
                    break

        return errors

    @api.depends('selected_picking_ids')
    def _compute_fields(self):
        try:
            self.check_compliance()

        except ValidationError:
            values = {
                'title': _("Warning!"),
                'errors': self._get_validation_errors()
            }

            self.error_message = self.env['ir.ui.view'] \
                .render_template('easy_ddt.stock_delivery_note_wizard_error_message_template', values)

        else:
            self.partner_id = self.selected_picking_ids.mapped('partner_id')

    def check_compliance(self):
        self._check_pickings()
        self._check_pickings_state()
        self._check_partners()
        self._check_pickings_location()
        self._check_delivery_notes()

    def confirm(self):
        raise NotImplementedError(_("This functionality isn't ready yet. Please, come back later."))
