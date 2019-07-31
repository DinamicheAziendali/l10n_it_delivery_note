# Copyright (c) 2019, Link IT Europe Srl (http://www.linkgroup.it/)
# @author: Matteo Bilotta <mbilotta@linkgroup.it>

from odoo import _, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_use_advanced_delivery_notes = fields.Boolean(string=_("Use the advanced delivery notes behaviour"),
                                                       implied_group='easy_ddt.use_advanced_delivery_notes')
