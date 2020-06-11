# Copyright (c) 2019, Link IT Europe Srl
# @author: Matteo Bilotta <mbilotta@linkeurope.it>

from odoo import _, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_use_advanced_delivery_notes = fields.Boolean(
        string=_("Use the advanced delivery notes behaviour"),
        implied_group='l10n_it_delivery_note.use_advanced_delivery_notes')
    group_show_product_related_fields = fields.Boolean(
        string=_("Show product information in the delivery note lines"),
        implied_group='l10n_it_delivery_note.show_product_related_fields')
