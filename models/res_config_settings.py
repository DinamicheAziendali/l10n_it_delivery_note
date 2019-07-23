#
# Copyright (c) 2019, Link IT srl, Italy. All rights reserved.
#

from odoo import _, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_use_advanced_delivery_notes = fields.Boolean(string=_("Use the advanced delivery notes behaviour"),
                                                       implied_group='easy_ddt.use_advanced_delivery_notes')
