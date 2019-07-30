from odoo import _, api, models
from odoo.exceptions import ValidationError

DONE_PICKING_STATE = 'done'
INCOMING_PICKING_TYPE = 'incoming'


class StockPickingCheckerMixin(models.AbstractModel):
    _name = 'stock.picking.checker.mixin'
    _description = "Picking checker mixin"

    @api.model
    def _check_pickings(self, pickings):
        if not pickings:
            raise ValidationError(_("You shouldn't be able to launch this wizard without selecting any pickings."))

    @api.model
    def _check_pickings_state(self, pickings):
        if pickings.filtered(lambda p: p.state != DONE_PICKING_STATE):
            raise ValidationError(_("At least one picking you've selected doesn't appear to be completed."))

    @api.model
    def _check_pickings_type(self, pickings):
        if pickings.filtered(lambda p: p.picking_type_code == INCOMING_PICKING_TYPE):
            raise ValidationError(_("At least one picking you've selected appear to be incoming."))

    @api.model
    def _check_partners(self, pickings):
        partners = pickings.mapped('partner_id')

        if not partners:
            raise ValidationError(_("The pickings you've selected don't seem to have any partner."))

        if len(partners) > 1:
            raise ValidationError(_("You need to select pickings with all the same partner."))

    @api.model
    def _check_pickings_location(self, pickings):
        locations = pickings.mapped('location_dest_id')

        if not locations:
            raise ValidationError(_("The pickings you've selected don't seem to have any location of destination."))

        if len(locations) > 1:
            raise ValidationError(_("You need to select pickings with all the same location of destination."))

    @api.model
    def _check_delivery_notes(self, pickings):
        if pickings.filtered(lambda p: p.delivery_note_id):
            raise ValidationError(_("At least one picking you've selected appears to"
                                    " be already related to another delivery note."))

    @api.model
    def check_compliance(self, pickings):
        self._check_pickings(pickings)
        self._check_pickings_state(pickings)
        self._check_pickings_type(pickings)
        self._check_partners(pickings)
        self._check_pickings_location(pickings)
