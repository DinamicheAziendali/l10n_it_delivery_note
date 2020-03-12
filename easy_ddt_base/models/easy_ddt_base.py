# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018  Dinamiche Aziendali srl
#    www.dinamicheaziendali.it
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


class DdtStockFree(models.Model):

    _name = 'ddt.stockfree'
    _description = 'DDT Report free of Stock'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Description', required=True, track_visibility='always')
    ddt_number = fields.Char(string='DdT Number',  copy=False,
                             track_visibility='change')
    date_ddt = fields.Date(string='Delivery note Date',
                           track_visibility='always')
    date_transport_ddt = fields.Date(string='Date of trasport',
                                     track_visibility='always')
    time_transport_ddt = fields.Float(string='Delivery Note Start Time')
    parcels = fields.Integer('Parcel')
    gross_w = fields.Float('Gross Weight')
    net_w = fields.Float('Net Weight')
    ddt_notes = fields.Text(string='Delivery Note Notes',
                            track_visibility='always')
    partner_id = fields.Many2one('res.partner',
                                 string='Destinazione del Partner',
                                 required=True)
    ddt_line_ids = fields.One2many(
        string="DDT",
        comodel_name='ddt.stockfree.line', inverse_name='ddt_line_id',
        copy=False, readonly=True)

    def _default_ddt_type(self):
        return self.env['stock.ddt.type'].search([], limit=1)

    ddt_type_id = fields.Many2one(
        'stock.ddt.type', string='DdT Type', default=_default_ddt_type)
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

    @api.multi
    def get_ddt_number(self):
        for ddt in self:
            if not ddt.ddt_number and ddt.ddt_type_id:
                sequence = ddt.ddt_type_id.sequence_id
                ddt.ddt_number = sequence.next_by_id()
            return self.env['report'].\
                get_action(self, 'easy_ddt_base.report_easy_ddt_main_base')
        return True

    @api.multi
    def ddt_time_report(self, time_ddt):
        hh = int(time_ddt)
        mm = time_ddt - hh
        mms = str(int(round(mm*60)))
        if(len(mms) == 1):
            mms = '0' + mms
        data = str(hh)+":"+mms
        return data


class DdtStockFreeLine(models.Model):
    _name = 'ddt.stockfree.line'
    _description = 'DDT Report free of Stock line'
    _inherit = ['mail.thread']
    _order = 'sequence asc'

    name = fields.Char(
        string='Description', required=True, track_visibility='always')
    quantity = fields.Integer(string='Quantity', track_visibility='always')
    sequence = fields.Integer(string='Sequence', default=10)
    ddt_line_id = fields.Many2one('ddt.stockfree',
                                  string='DDT line', ondelete='cascade',)
