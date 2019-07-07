# -*- coding: utf-8 -*-
# Copyright 2014-2019 Dinamiche Aziendali srl (http://www.dinamicheaziendali.it/)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Gianmarco Conte <gconte@dinamicheaziendali.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api
from datetime import datetime


# class StockPicking(models.Model):
#     _inherit = 'stock.location'
#
#     ddt_type_id = fields.Many2one('stock.ddt.type', string='DdT Type')

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _default_ddt_type(self):
        return self.env['stock.ddt.type'].search([], limit=1)

    ddt_type_id = fields.Many2one(
        'stock.ddt.type', string='DdT Type', default=_default_ddt_type)
    ddt_number = fields.Char(string='DdT Number',  copy=False)
    ddt_date = fields.Date(string='DDT Date')
    carriage_condition_id = fields.Many2one(
        'stock.picking.carriage_condition', string='Carriage Condition')
    goods_description_id = fields.Many2one(
        'stock.picking.goods_description', string='Description of Goods')
    transportation_reason_id = fields.Many2one(
        'stock.picking.transportation_reason',
        string='Reason for Transportation')
    transportation_method_id = fields.Many2one(
        'stock.picking.transportation_method',
        string='Method of Transportation')
    date_transport_ddt = fields.Date(string='Delivery note Date')
    time_transport_ddt = fields.Float(string='Delivery Note Start Time')
    ddt_notes = fields.Text(string='Delivery Note Notes')
    picking_type_code = fields.Selection(related="picking_type_id.code")
    gross_weight = fields.Float(string="Gross Weight") #da inserire in form

    @api.onchange('partner_id', 'ddt_type_id')
    def on_change_partner(self):
        if self.ddt_type_id:
            self.carriage_condition_id = \
                self.partner_id.carriage_condition_id.id \
                if self.partner_id.carriage_condition_id else False
            self.goods_description_id = \
                self.partner_id.goods_description_id.id \
                if self.partner_id.goods_description_id else False
            self.transportation_reason_id = \
                self.partner_id.transportation_reason_id.id \
                if self.partner_id.transportation_reason_id else False
            self.transportation_method_id = \
                self.partner_id.transportation_method_id.id \
                if self.partner_id.transportation_method_id else False

    @api.multi
    def get_ddt_number(self):
        for ddt in self:
            addr = ddt.partner_id.address_get(['delivery', 'invoice'])
            if not ddt.ddt_number and ddt.ddt_type_id:
                obj_sequence = self.env["ir.sequence"]
                sequence = ddt.ddt_type_id.sequence_id
                ddt.ddt_number = sequence.next_by_id()
                ddt.min_date = datetime.now()
                # ddt.ddt_number = obj_sequence.next_by_id(sequence.id)
        # return self.env['ir.actions.report']._get_report_from_name('easy_ddt.report_easy_ddt_main')
            return self.env.ref('easy_ddt.action_report_easy_ddt').report_action(self)
        return True

    # @api.multi
    # def ddt_get_location(self, location_id):
    #     model_warehouse = self.env['stock.warehouse']
    #     # import pdb; pdb.set_trace()
    #     warehouse = model_warehouse.search(
    #         [('lot_stock_id', '=',
    #           location_id),
    #          ])
    #     data=[warehouse.partner_id.id, warehouse.partner_id.name]
    #     data= [warehouse.partner_id.name,
    #           warehouse.partner_id.street,
    #            (warehouse.partner_id.zip + ' ' +
    #           warehouse.partner_id.city + ' ' +
    #           '(' +warehouse.partner_id.state_id.name +')'),]
    #     return data

    @api.multi
    def ddt_get_location(self, location_id):
        model_warehouse = self.env['stock.warehouse']
        warehouse = model_warehouse.search(
            [('lot_stock_id', '=',
              location_id),
             ])
        data = [warehouse.partner_id.id, warehouse.partner_id.name]
        if warehouse.partner_id:
            data = [warehouse.partner_id.name,
                    warehouse.partner_id.street,
                    (warehouse.partner_id.zip + ' ' +
                     warehouse.partner_id.city + ' ' +
                     '(' + warehouse.partner_id.state_id.name + ')' if warehouse.partner_id.state_id else ''), ]
        return data

    @api.multi
    def ddt_time_report(self, time_ddt):
        hh = int(time_ddt)
        mm = time_ddt - hh
        mms = str(int(round(mm*60)))
        if(len(mms)==1):
            mms='0'+mms
        data = str(hh)+":"+mms
        return data

    # self.partner_id.address_get(['delivery', 'invoice'])
