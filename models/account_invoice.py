# Copyright 2014-2019 Dinamiche Aziendali srl (http://www.dinamicheaziendali.it/)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Gianmarco Conte <gconte@dinamicheaziendali.it>
# Copyright (c) 2019, Link IT Europe Srl (http://www.linkgroup.it/)
# @author: Matteo Bilotta <mbilotta@linkgroup.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    delivery_note_ids = fields.Many2many('stock.delivery.note', ...)
    delivery_note_count = fields.Integer(...)
