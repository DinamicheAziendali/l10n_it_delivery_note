# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017 Dinamiche Aziendali srl
#    @author Gianmarco Conte <gconte@dinamicheaziendali.it>
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


from odoo import models, fields


class StockPickingCarriageCondition(models.Model):

    _name = "stock.picking.carriage_condition"
    _description = "Carriage Condition"

    name = fields.Char(
        string='Carriage Condition', required=True, translate=True)
    note = fields.Text(string='Note', translate=True)


class StockPickingGoodsDescription(models.Model):

    _name = 'stock.picking.goods_description'
    _description = "Description of Goods"

    name = fields.Char(
        string='Description of Goods', required=True, translate=True)
    note = fields.Text(string='Note', translate=True)


class StockPickingTransportationReason(models.Model):

    _name = 'stock.picking.transportation_reason'
    _description = 'Reason for Transportation'

    name = fields.Char(
        string='Reason For Transportation', required=True, translate=True)
    note = fields.Text(string='Note', translate=True)


class StockPickingTransportationMethod(models.Model):

    _name = 'stock.picking.transportation_method'
    _description = 'Method of Transportation'

    name = fields.Char(
        string='Method of Transportation', required=True, translate=True)
    note = fields.Text(string='Note', translate=True)


class StockDdtType(models.Model):

    _name = 'stock.ddt.type'
    _description = 'Stock DdT Type'
    _inherit = ['mail.thread']

    name = fields.Char(required=True)
    sequence_id = fields.Many2one('ir.sequence', required=True)
    note = fields.Text(string='Note')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id, )
