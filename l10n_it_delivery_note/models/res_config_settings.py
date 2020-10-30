# Copyright (c) 2019, Link IT Europe Srl
# @author: Matteo Bilotta <mbilotta@linkeurope.it>

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_use_advanced_delivery_notes = fields.Boolean(
        string="Use Advanced DN Features",
        implied_group='l10n_it_delivery_note.'
                      'use_advanced_delivery_notes')

    group_draft_delivery_note_invoicing_notify = fields.Boolean(
        string="Notify if delivery note isn't validated",
        implied_group='l10n_it_delivery_note.'
                      'draft_delivery_note_invoicing_notify')
