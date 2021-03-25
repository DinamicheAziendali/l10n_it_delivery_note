# Copyright 2014-2019 Dinamiche Aziendali srl
# (http://www.dinamicheaziendali.it/)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Gianmarco Conte <gconte@dinamicheaziendali.it>
# @author: Giuseppe Borruso <gborruso@dinamicheaziendali.it>
# Copyright (c) 2020, Link IT Europe Srl
# @author: Matteo Bilotta <mbilotta@linkeurope.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import datetime

from odoo import api, fields, models


class DeliveryNoteDoc(models.Model):
    _name = "delivery.note.doc"
    _description = "Delivery Note Document - without inventory app"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "ddt_number, name, id"

    def _default_type(self):
        return self.env["stock.delivery.note.type"].search(
            [("code", "=", "outgoing")], limit=1
        )

    def _default_company(self):
        return self.env.company

    active = fields.Boolean(default=True)
    name = fields.Char(
        string="Description",
        required=True,
        track_visibility="always",
    )
    ddt_number = fields.Char(
        string="DdT Number",
        copy=False,
        track_visibility="change",
    )
    date_ddt = fields.Date(string="Date", copy=False, track_visibility="always")
    date_transport_ddt = fields.Datetime(string="Transport date", rack_visibility="always")
    packages = fields.Integer(string="Packages")
    gross_weight = fields.Float(string="Gross Weight")
    net_weight = fields.Float(string="Net Weight")
    ddt_notes = fields.Html(string="Delivery Note Notes", track_visibility="always")
    partner_id = fields.Many2one(
        "res.partner",
        string="Recipient",
        # states={"draft": [("readonly", False)]},
        required=True,
        index=True,
        track_visibility="always",
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
    )
    line_ids = fields.One2many(
        "delivery.note.doc.line", "delivery_note_doc_id", string="Lines"
    )

    type_id = fields.Many2one(
        "stock.delivery.note.type",
        string="Type",
        default=_default_type,
        # states={"draft": [("readonly", False)]},
        required=True,
        index=True,
    )
    transport_condition_id = fields.Many2one(
        "stock.picking.transport.condition",
        string="Condition of transport",
        # states={"done": [("readonly", True)]},
    )
    goods_appearance_id = fields.Many2one(
        "stock.picking.goods.appearance",
        string="Appearance of goods",
        # states={"done": [("readonly", True)]},
    )
    transport_reason_id = fields.Many2one(
        "stock.picking.transport.reason",
        string="Reason of transport",
        # states={"done": [("readonly", True)]},
    )
    transport_method_id = fields.Many2one(
        "stock.picking.transport.method",
        string="Method of transport",
        # states={"done": [("readonly", True)]},
    )
    company_id = fields.Many2one("res.company", required=True, default=_default_company)

    def _valid_field_parameter(self, field, name):
        return name == "track_visibility" or super()._valid_field_parameter(field, name)

    def get_dn_number(self):
        # for dn in self:
        #     if not dn.ddt_number and dn.type_id:
        #         sequence = dn.type_id.sequence_id
        #         dn.ddt_number = sequence.next_by_id()
        #     return self.env["report"].\
        #         get_action(
        #         self, "l10n_it_delivery_note_doc.report_delivery_note_doc")
        return True

    def dn_time_report(self, time_ddt):
        # hh = int(time_ddt)
        # mm = time_ddt - hh
        # mms = str(int(round(mm*60)))
        # if(len(mms) == 1):
        #     mms = "0" + mms
        # data = str(hh)+":"+mms
        # return data
        return True

    def update_date_transport_ddt(self):
        self.date_transport_ddt = datetime.datetime.now()


class DeliveryNoteDocLine(models.Model):
    _name = "delivery.note.doc.line"
    _description = "Delivery Note Document line"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "sequence asc"

    name = fields.Text(string="Description", required=True, track_visibility="always")
    quantity = fields.Float(
        string="Quantity",
        digits="Product Unit of Measure",
        default=1.0,
        track_visibility="always",
    )
    sequence = fields.Integer(string="Sequence", required=True, default=10, index=True)
    delivery_note_doc_id = fields.Many2one(
        "delivery.note.doc",
        string="Delivery Note line",
        required=True,
        ondelete="cascade",
    )
