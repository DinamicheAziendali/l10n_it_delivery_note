# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Dinamiche Aziendali srl
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _default_ddt_type(self):
        return self.env['stock.ddt.type'].search([], limit=1)
        # return self.env['stock.ddt.type'].search([[('posx', '=', move_lines[0].location_id.id)]], limit=1)

    ddt_type_id = fields.Many2one(
        'stock.ddt.type', string='DdT Type', default=_default_ddt_type)
    ddt_number = fields.Char(string='DdT Number',  copy=False)
    carriage_condition_id = fields.Many2one(
        'stock.picking.carriage_condition', 'Carriage Condition')
    goods_description_id = fields.Many2one(
        'stock.picking.goods_description', 'Description of Goods')
    transportation_reason_id = fields.Many2one(
        'stock.picking.transportation_reason',
        'Reason for Transportation')
    transportation_method_id = fields.Many2one(
        'stock.picking.transportation_method',
        'Method of Transportation')
    date_transport_ddt = fields.Date(string='Delivery note Date')
    time_transport_ddt = fields.Float(string='Delivery Note Start Time')
    ddt_notes = fields.Text(string='Delivery Note Notes')

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
            if not ddt.ddt_number and ddt.ddt_type_id:
                obj_sequence = self.env["ir.sequence"]
                sequence = ddt.ddt_type_id.sequence_id
                ddt.ddt_number = obj_sequence.next_by_id(sequence.id)
            return self.env['report'].\
                get_action(self, 'easy_ddt.report_easy_ddt_main')
        return True

    @api.multi
    def ddt_get_location(self, location_id):
        model_warehouse = self.env['stock.warehouse']
        warehouse = model_warehouse.search(
            [('lot_stock_id', '=',
              location_id),
             ])
        # data=warehouse.partner_id.id
        data=(warehouse.partner_id.name + '\n' +
              warehouse.partner_id.street + '\n' +
              '('+warehouse.partner_id.zip + ') ' +
              warehouse.partner_id.city + ' ' +
              warehouse.partner_id.state_id.name)
        return data
