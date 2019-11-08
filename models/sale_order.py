# Copyright (c) 2019, Link IT Europe Srl (http://www.linkgroup.it/)
# @author: Matteo Bilotta <mbilotta@linkgroup.it>

from odoo import _, api, fields, models

from .stock_delivery_note import DOMAIN_INVOICE_STATUSES


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.multi
    def _assign_delivery_notes_invoices(self, invoice_ids):
        order_lines = self.mapped('order_line').filtered(lambda l: l.is_invoiced and l.delivery_note_line_ids)
        delivery_note_lines = order_lines.mapped('delivery_note_line_ids').filtered(lambda l: l.is_invoiceable)
        delivery_note_lines.write({'invoice_status': DOMAIN_INVOICE_STATUSES[2]})

        #
        # TODO #1: È necessario gestire il caso di fatturazione splittata
        #           di una stessa riga d'ordine associata ad una sola
        #           picking (e di conseguenza, ad un solo DdT)?
        #          Può essere, invece, un caso "borderline"
        #           da lasciar gestire all'operatore?
        #
        # TODO #2: È necessario controllare che il DdT associato alle
        #           righe sia stato validato prima di fatturare?
        #

        delivery_notes = delivery_note_lines.mapped('delivery_note_id')
        delivery_notes.write({'invoice_ids': [(4, invoice_id) for invoice_id in invoice_ids]})

    @api.multi
    def _generate_delivery_note_lines(self, invoice_ids):
        invoices = self.env['account.invoice'].browse(invoice_ids)
        invoices.update_delivery_note_lines()

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        invoice_ids = super().action_invoice_create(grouped=grouped, final=final)

        self._assign_delivery_notes_invoices(invoice_ids)
        self._generate_delivery_note_lines(invoice_ids)

        return invoice_ids


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    delivery_note_line_ids = fields.One2many('stock.delivery.note.line', 'sale_line_id', readonly=True)
    delivery_picking_id = fields.Many2one('stock.picking', readonly=True, copy=False)

    @property
    def has_picking(self):
        return self.move_ids or (self.is_delivery and self.delivery_picking_id)

    @property
    def is_invoiceable(self):
        return self.invoice_status == DOMAIN_INVOICE_STATUSES[1] and self.qty_to_invoice != 0

    @property
    def is_invoiced(self):
        return self.invoice_status != DOMAIN_INVOICE_STATUSES[1] and self.qty_invoiced != 0

    @property
    def need_to_be_invoiced(self):
        return self.product_uom_qty != (self.qty_to_invoice + self.qty_invoiced)

    def fix_qty_to_invoice(self, new_qty_to_invoice=0):
        self.ensure_one()

        cache = {
            'invoice_status': self.invoice_status,
            'qty_to_invoice': self.qty_to_invoice
        }

        self.write({
            'invoice_status': 'to invoice' if new_qty_to_invoice else 'no',
            'qty_to_invoice': new_qty_to_invoice
        })

        return cache

    def is_pickings_related(self, picking_ids):
        if self.is_delivery:
            return self.delivery_picking_id in picking_ids

        return bool(self.move_ids & picking_ids.mapped('move_lines'))

    @api.multi
    def retrieve_pickings_lines(self, picking_ids):
        return self.filtered(lambda l: l.has_picking) \
                   .filtered(lambda l: l.is_pickings_related(picking_ids))
