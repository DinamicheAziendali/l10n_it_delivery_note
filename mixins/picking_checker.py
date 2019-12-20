# Copyright (c) 2019, Link IT Europe Srl (http://www.linkgroup.it/)
# @author: Matteo Bilotta <mbilotta@linkgroup.it>

from odoo import _, api, models
from odoo.exceptions import ValidationError

DONE_PICKING_STATE = 'done'

PICKING_TYPES = [
    ('incoming', "Vendors"),
    ('outgoing', "Customers"),
    ('internal', "Internal")
]
DOMAIN_PICKING_TYPES = [t[0] for t in PICKING_TYPES]


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
    def _check_pickings_types(self, pickings):
        types = set(pickings.mapped('picking_type_code'))

        if not types:
            raise ValidationError(_("The pickings you've selected don't seem to have any type."))

        if len(types) > 1:
            raise ValidationError(_("You need to select pickings with all the same type."))

    @api.model
    def _check_pickings_partners(self, pickings):
        partners = pickings.mapped('partner_id')

        if not partners:
            raise ValidationError(_("The pickings you've selected don't seem to have any partner."))

        if len(partners) > 1:
            raise ValidationError(_("You need to select pickings with all the same recipient."))

    @api.model
    def _check_pickings_src_locations(self, pickings):
        src_locations = pickings.mapped('location_id')

        if not src_locations:
            raise ValidationError(_("The pickings you've selected don't seem to have any location of departure."))

        if len(src_locations) > 1:
            raise ValidationError(_("You need to select pickings with all the same location of departure."))

    @api.model
    def _check_pickings_dest_locations(self, pickings):
        dest_locations = pickings.mapped('location_dest_id')

        if not dest_locations:
            raise ValidationError(_("The pickings you've selected don't seem to have any location of destination."))

        if len(dest_locations) > 1:
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
        self._check_pickings_types(pickings)
        self._check_pickings_partners(pickings)
        self._check_pickings_src_locations(pickings)
        self._check_pickings_dest_locations(pickings)