# Copyright 2014-2019 Dinamiche Aziendali srl (http://www.dinamicheaziendali.it/)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Gianmarco Conte <gconte@dinamicheaziendali.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from datetime import datetime


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _default_ddt_type(self):
        return self.env['stock.ddt.type'].search([], limit=1)

    ddt_type_id = fields.Many2one(
        'stock.ddt.type', string='DdT Type', default=_default_ddt_type)
    ddt_number = fields.Char(string='DdT Number', copy=False)
    ddt_date = fields.Date(string='DDT Date')
    transport_condition_id = fields.Many2one(
        'stock.picking.transport.condition', string=_("Transport Condition"))
    goods_appearance_id = fields.Many2one(
        'stock.picking.goods.appearance', string=_("Appearance of Goods"))
    transport_reason_id = fields.Many2one(
        'stock.picking.transport.reason', string=_("Transport Reason"))
    transport_method_id = fields.Many2one(
        'stock.picking.transport.method', string=_("Transport Method"))
    date_transport_ddt = fields.Date(string='Delivery note Date')
    time_transport_ddt = fields.Float(string='Delivery Note Start Time')
    ddt_notes = fields.Html(string='Delivery Note Notes')
    picking_type_code = fields.Selection(related="picking_type_id.code")
    gross_weight = fields.Float(string="Gross Weight")

    partner_shipping_id = fields.Many2one(
        'res.partner', string="Shipping Address")
    parcels = fields.Integer('Parcels')
    invoice_id = fields.Many2one(
        'account.invoice', string='Invoice', readonly=True, copy=False)
    to_be_invoiced = fields.Boolean(
        string='To be Invoiced',
        help="This depends on 'To be Invoiced' field of the Reason for "
             "Transportation of this TD")
    show_price = fields.Boolean(string='Show prices on report')
    weight_manual = fields.Float(
        string="Force Net Weight",
        help="Fill this field with the value you want to be used as weight. "
             "Leave empty to let the system to compute it")

    @api.onchange('partner_id', 'ddt_type_id')
    def on_change_partner(self):
        if self.ddt_type_id:
            self.transport_condition_id = \
                self.partner_id.transport_condition_id.id \
                if self.partner_id.transport_condition_id else False
            self.goods_appearance_id = \
                self.partner_id.goods_appearance_id.id \
                if self.partner_id.goods_appearance_id else False
            self.transport_reason_id = \
                self.partner_id.transport_reason_id.id \
                if self.partner_id.transport_reason_id else False
            self.transport_method_id = \
                self.partner_id.transport_method_id.id \
                if self.partner_id.transport_method_id else False

    @api.multi
    def get_ddt_number(self):
        for ddt in self:
            if not ddt.ddt_number and ddt.ddt_type_id:
                sequence = ddt.ddt_type_id.sequence_id
                ddt.ddt_number = sequence.next_by_id()
                if not ddt.ddt_date:
                    ddt.ddt_date = datetime.now().date()
            return self.env.ref('easy_ddt.action_report_easy_ddt').report_action(self)
        return True

    @api.multi
    def ddt_get_location(self, location_id):
        model_warehouse = self.env['stock.warehouse']
        warehouse = model_warehouse.search(
            [('lot_stock_id', '=', location_id)]
        )
        data = [warehouse.partner_id.id, warehouse.partner_id.name]
        if warehouse.partner_id:
            data = [
                warehouse.partner_id.name,
                warehouse.partner_id.street,
                (
                    warehouse.partner_id.zip + ' ' +
                    warehouse.partner_id.city + ' ' +
                    '(' + warehouse.partner_id.state_id.name + ')'
                    if warehouse.partner_id.state_id else ''
                )
            ]

        return data

    @api.multi
    def ddt_time_report(self, time_ddt):
        hh = int(time_ddt)
        mm = time_ddt - hh
        mms = str(int(round(mm * 60)))
        if len(mms) == 1:
            mms = '0' + mms

        data = str(hh) + ":" + mms

        return data
