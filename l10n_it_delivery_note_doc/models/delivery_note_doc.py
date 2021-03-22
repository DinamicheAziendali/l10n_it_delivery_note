# Copyright 2014-2019 Dinamiche Aziendali srl
# (http://www.dinamicheaziendali.it/)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Gianmarco Conte <gconte@dinamicheaziendali.it>
# @author: Giuseppe Borruso <gborruso@dinamicheaziendali.it>
# Copyright (c) 2020, Link IT Europe Srl
# @author: Matteo Bilotta <mbilotta@linkeurope.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields, api


class DeliveryNoteDoc(models.Model):

    _name = 'delivery.note.doc'
    _description = 'Delivery Note Document - with inventory app.'
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "ddt_number, name, id"

    def _default_type(self):
        return self.env["stock.delivery.note.type"].search(
            [("code", "=", "outgoing")], limit=1
        )

    def _default_company(self):
        return self.env.company

    active = fields.Boolean(default=True)
    name = fields.Char(
        string='Description',
        required=True,
        track_visibility='always',
    )
    ddt_number = fields.Char(string='DdT Number', copy=False,
                             track_visibility='change')
    date_ddt = fields.Date(string='Delivery note Date',
                           track_visibility='always')
    date_transport_ddt = fields.Date(string='Date of trasport',
                                     track_visibility='always')
    time_transport_ddt = fields.Float(string='Delivery Note Start Time')
    parcels = fields.Integer(string='Parcel')
    gross_w = fields.Float(string='Gross Weight')
    net_w = fields.Float(string='Net Weight')
    ddt_notes = fields.Text(string='Delivery Note Notes',
                            track_visibility='always')
    partner_id = fields.Many2one(
        'res.partner',
        string='Recipient',
        states={"draft": [("readonly", False)]},
        required=True,
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    line_ids = fields.One2many(
        "delivery.note.doc.line", "delivery_note_id", string="Lines"
    )

    type_id = fields.Many2one(
        "stock.delivery.note.type",
        string="Type",
        default=_default_type,
        states={"draft": [("readonly", False)]},
        required=True,
        index=True,
    )

    # carriage_condition_id = fields.Many2one(
    #     'stock.picking.carriage_condition', 'Carriage Condition')
    transport_condition_id = fields.Many2one(
        "stock.picking.transport.condition",
        string="Condition of transport",
        states={"done": [("readonly", True)]},
    )
    # goods_description_id = fields.Many2one(
    #     'stock.picking.goods_description', 'Description of Goods')
    goods_appearance_id = fields.Many2one(
        "stock.picking.goods.appearance",
        string="Appearance of goods",
        states={"done": [("readonly", True)]},
    )
    # transportation_reason_id = fields.Many2one(
    #     'stock.picking.transportation_reason',
    #     'Reason for Transportation')
    transport_reason_id = fields.Many2one(
        "stock.picking.transport.reason",
        string="Reason of transport",
        states={"done": [("readonly", True)]},
    )
    # transportation_method_id = fields.Many2one(
    #     'stock.picking.transportation_method',
    #     'Method of Transportation')
    transport_method_id = fields.Many2one(
        "stock.picking.transport.method",
        string="Method of transport",
        states={"done": [("readonly", True)]},
    )
    company_id = fields.Many2one("res.company",
                                 required=True, default=_default_company)

    def get_dn_number(self):
        for dn in self:
            if not dn.ddt_number and dn.type_id:
                sequence = dn.type_id.sequence_id
                dn.ddt_number = sequence.next_by_id()
            return self.env['report'].\
                get_action(
                self, 'l10n_it_delivery_note_doc.report_delivery_note_doc')
        return True

    def dn_time_report(self, time_ddt):
        hh = int(time_ddt)
        mm = time_ddt - hh
        mms = str(int(round(mm*60)))
        if(len(mms) == 1):
            mms = '0' + mms
        data = str(hh)+":"+mms
        return data


class DeliveryNoteDocLine(models.Model):
    _name = 'delivery.note.doc.line'
    _description = 'Delivery Note Document line'
    # _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'sequence asc'

    name = fields.Char(
        string='Description', required=True, track_visibility='always')
    quantity = fields.Integer(string='Quantity', track_visibility='always')
    sequence = fields.Integer(string='Sequence', default=10)
    delivery_note_id = fields.Many2one(
        'delivery.note.doc',
        string='Delivery Note line', ondelete='cascade', )
