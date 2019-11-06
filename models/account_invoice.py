# Copyright 2014-2019 Dinamiche Aziendali srl (http://www.dinamicheaziendali.it/)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Gianmarco Conte <gconte@dinamicheaziendali.it>
# Copyright (c) 2019, Link IT Europe Srl (http://www.linkgroup.it/)
# @author: Matteo Bilotta <mbilotta@linkgroup.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    delivery_note_ids = fields.Many2many('stock.delivery.note',
                                         'stock_delivery_note_account_invoice_rel',
                                         'invoice_id',
                                         'delivery_note_id',
                                         string=_("Delivery notes"))

    #
    # TODO: Confermare e tenere tutto il codice seguente oppure è possibile rimuoverlo?
    #
    delivery_note_count = fields.Integer(string=_("Delivery notes count"), compute='_compute_delivery_note_count')

    @api.multi
    def _compute_delivery_note_count(self):
        for note in self:
            note.invoice_count = len(note.invoice_ids)

    @api.multi
    def goto_delivery_notes(self):
        delivery_notes = self.mapped('delivery_note_ids')
        action = self.env.ref('easy_ddt.stock_delivery_note_tree_view').read()[0]

        if len(delivery_notes) > 1:
            action['domain'] = [('id', 'in', delivery_notes.ids)]

        elif len(delivery_notes) == 1:
            action['views'] = [(self.env.ref('easy_ddt.stock_delivery_note_form_view').id, 'form')]
            action['res_id'] = delivery_notes.id

        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action
