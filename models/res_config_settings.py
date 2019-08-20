# Copyright (c) 2019, Link IT Europe Srl (http://www.linkgroup.it/)
# @author: Matteo Bilotta <mbilotta@linkgroup.it>

from odoo import _, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_use_advanced_delivery_notes = fields.Boolean(string=_("Use the advanced delivery notes behaviour"),
                                                       implied_group='easy_ddt.use_advanced_delivery_notes')
    group_show_product_related_fields = fields.Boolean(string=_("Show product information in the delivery note lines"),
                                                       implied_group='easy_ddt.show_product_related_fields')
