# Copyright 2014-2019 Dinamiche Aziendali srl (http://www.dinamicheaziendali.it/)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Gianmarco Conte <gconte@dinamicheaziendali.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models

from .stock_delivery_note import DOMAIN_DELIVERY_NOTE_STATES
from ..mixins.picking_checker import DONE_PICKING_STATE, INCOMING_PICKING_TYPE

CANCEL_MOVE_STATE = 'cancel'


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_note_id = fields.Many2one('stock.delivery.note', string=_("Delivery note"))
    delivery_note_partner_shipping_id = fields.Many2one('res.partner', related='delivery_note_id.partner_shipping_id')
    delivery_note_type_id = fields.Many2one('stock.delivery.note.type', related='delivery_note_id.type_id')
    delivery_note_date = fields.Date(related='delivery_note_id.date')
    delivery_note_note = fields.Html(related='delivery_note_id.note')

    transport_condition_id = fields.Many2one('stock.picking.transport.condition',
                                             related='delivery_note_id.transport_condition_id')
    goods_appearance_id = fields.Many2one('stock.picking.goods.appearance',
                                          related='delivery_note_id.goods_appearance_id')
    transport_reason_id = fields.Many2one('stock.picking.transport.reason',
                                          related='delivery_note_id.transport_reason_id')
    transport_method_id = fields.Many2one('stock.picking.transport.method',
                                          related='delivery_note_id.transport_method_id')

    transport_datetime = fields.Datetime(related='delivery_note_id.transport_datetime')

    parcels = fields.Integer(related='delivery_note_id.parcels')
    delivery_note_volume = fields.Float(related='delivery_note_id.volume')
    delivery_note_volume_uom_id = fields.Many2one('uom.uom', related='delivery_note_id.volume_uom_id')
    gross_weight = fields.Float(related='delivery_note_id.gross_weight')
    gross_weight_uom_id = fields.Many2one('uom.uom', related='delivery_note_id.gross_weight_uom_id')
    net_weight = fields.Float(related='delivery_note_id.net_weight')
    net_weight_uom_id = fields.Many2one('uom.uom', related='delivery_note_id.net_weight_uom_id')

    valid_move_ids = fields.One2many('stock.move', 'picking_id', domain=[('state', '!=', CANCEL_MOVE_STATE)])
    picking_type_code = fields.Selection(related='picking_type_id.code')

    use_delivery_note = fields.Boolean(compute='_compute_boolean_flags')
    delivery_note_exists = fields.Boolean(compute='_compute_boolean_flags')
    delivery_note_validated = fields.Boolean(compute='_compute_boolean_flags')
    delivery_note_readonly = fields.Boolean(compute='_compute_boolean_flags')
    delivery_note_visible = fields.Boolean(compute='_compute_boolean_flags')
    delivery_note_done = fields.Boolean(compute='_compute_boolean_flags')

    #
    # Old DDT fields:
    #
    #     ddt_number = fields.Char()
    #     ddt_type_id = fields.Many2one('stock.delivery.note.type')
    #     ddt_date = fields.Date()
    #     ddt_notes = fields.Html()
    #
    #     carriage_condition_id = fields.Many2one('stock.picking.transport.condition')
    #     goods_description_id = fields.Many2one('stock.picking.goods.appearance')
    #     transportation_reason_id = fields.Many2one('stock.picking.transport.reason')
    #     transportation_method_id = fields.Many2one('stock.picking.transport.method')
    #
    #     date_transport_ddt = fields.Date()
    #     time_transport_ddt = fields.Float()
    #
    #     parcels = fields.Integer()
    #     gross_weight = fields.Float()
    #
    #     #
    #     # NEVER USED!
    #     #
    #     # partner_shipping_id = fields.Many2one('res.partner')
    #     # weight_manual = fields.Float()
    #     # invoice_id = fields.Many2one('account.invoice')
    #     # to_be_invoiced = fields.Boolean()
    #     # show_price = fields.Boolean()

    @property
    def _delivery_note_fields(self):
        from collections import OrderedDict

        cls = type(self)
        fields = OrderedDict({
            key: field
            for key, field in self._fields.items()
            if field.related and field.related[0] == 'delivery_note_id'
        })

        setattr(cls, '_delivery_note_fields', fields)

        return fields

    @api.multi
    def _compute_boolean_flags(self):
        from_delivery_note = self.env.context.get('from_delivery_note')
        use_advanced_behaviour = self.env.user.user_has_groups('easy_ddt.use_advanced_delivery_notes')

        for picking in self:
            picking.use_delivery_note = not from_delivery_note and \
                                        picking.state == DONE_PICKING_STATE and \
                                        picking.picking_type_code != INCOMING_PICKING_TYPE

            picking.delivery_note_visible = use_advanced_behaviour

            if picking.use_delivery_note and picking.delivery_note_id:
                picking.delivery_note_exists = True

                if picking.delivery_note_id.state == DOMAIN_DELIVERY_NOTE_STATES[1]:
                    picking.delivery_note_validated = True
                    picking.delivery_note_readonly = True
                    picking.delivery_note_visible = True

                elif picking.delivery_note_id.state == DOMAIN_DELIVERY_NOTE_STATES[2]:
                    picking.delivery_note_done = True

            else:
                picking.delivery_note_readonly = True

    @api.multi
    def action_delivery_note_create(self):
        self.ensure_one()

        return {
            'name': _("Create a new delivery note"),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.delivery.note.create.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_ids': self.ids}
        }

    @api.multi
    def action_delivery_note_select(self):
        self.ensure_one()

        return {
            'name': _("Select an existing delivery note"),
            'type': 'ir.actions.act_window',
            'res_model': 'stock.delivery.note.select.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_ids': self.ids}
        }

    @api.multi
    def action_delivery_note_validate(self):
        self.ensure_one()

        return self.delivery_note_id.action_confirm()

    @api.multi
    def action_delivery_note_print(self):
        self.ensure_one()

        return self.delivery_note_id.action_print()

    @api.multi
    def action_done(self):
        res = super().action_done()

        if self.picking_type_code != INCOMING_PICKING_TYPE and \
           not self.env.user.user_has_groups('easy_ddt.use_advanced_delivery_notes'):
            self.delivery_note_id = self.env['stock.delivery.note'].create({
                'partner_id': self.partner_id.id,
                'partner_shipping_id': self.partner_id.id
            })

        return res

    def update_delivery_note_fields(self, vals):
        fields = self._delivery_note_fields

        if any([key in fields for key in vals.keys()]):
            delivery_note_vals = {fields[key].related[1]: value for key, value in vals.items() if key in fields}

            self.mapped('delivery_note_id').write(delivery_note_vals)

    @api.multi
    def write(self, vals):
        res = super().write(vals)

        if self.mapped('delivery_note_id'):
            self.update_delivery_note_fields(vals)

            if 'delivery_note_id' in vals:
                self.mapped('delivery_note_id').update_detail_lines()

        return res

    #
    # Old DDT methods:
    #
    # @api.multi
    # def ddt_time_report(self, time_ddt):
    #     hh = int(time_ddt)
    #     mm = time_ddt - hh
    #     mms = str(int(round(mm * 60)))
    #     if len(mms) == 1:
    #         mms = '0' + mms
    #
    #     data = str(hh) + ":" + mms
    #
    #     return data
    #
    #     #
    #     # NEVER USED!
    #     #
    #     # @api.multi
    #     # def ddt_get_location(self, location_id):
    #     #     model_warehouse = self.env['stock.warehouse']
    #     #     warehouse = model_warehouse.search(
    #     #         [('lot_stock_id', '=', location_id)]
    #     #     )
    #     #     data = [warehouse.partner_id.id, warehouse.partner_id.name]
    #     #     if warehouse.partner_id:
    #     #         data = [
    #     #             warehouse.partner_id.name,
    #     #             warehouse.partner_id.street,
    #     #             (
    #     #                 warehouse.partner_id.zip + ' ' +
    #     #                 warehouse.partner_id.city + ' ' +
    #     #                 '(' + warehouse.partner_id.state_id.name + ')'
    #     #                 if warehouse.partner_id.state_id else ''
    #     #             )
    #     #         ]
    #     #
    #     #     return data


class StockPickingTransportCondition(models.Model):
    _name = 'stock.picking.transport.condition'
    _description = "Condition of transport"
    _order = 'sequence, name, id'

    active = fields.Boolean(string=_("Active"), default=True)
    sequence = fields.Integer(string=_("Sequence"), index=True, default=10)
    name = fields.Char(string=_("Condition name"), index=True, required=True, translate=True)
    note = fields.Html(string=_("Internal note"))

    _sql_constraints = [(
        'name_uniq',
        'unique(name)',
        "This condition of transport already exists!"
    )]


class StockPickingGoodsAppearance(models.Model):
    _name = 'stock.picking.goods.appearance'
    _description = "Appearance of goods"
    _order = 'sequence, name, id'

    active = fields.Boolean(string=_("Active"), default=True)
    sequence = fields.Integer(string=_("Sequence"), index=True, default=10)
    name = fields.Char(string=_("Appearance name"), index=True, required=True, translate=True)
    note = fields.Html(string=_("Internal note"))

    _sql_constraints = [(
        'name_uniq',
        'unique(name)',
        "This appearance of goods already exists!"
    )]


class StockPickingTransportReason(models.Model):
    _name = 'stock.picking.transport.reason'
    _description = "Reason of transport"
    _order = 'sequence, name, id'

    active = fields.Boolean(string=_("Active"), default=True)
    sequence = fields.Integer(string=_("Sequence"), index=True, default=10)
    name = fields.Char(string=_("Reason name"), index=True, required=True, translate=True)
    note = fields.Html(string=_("Internal note"))

    _sql_constraints = [(
        'name_uniq',
        'unique(name)',
        "This reason of transport already exists!"
    )]


class StockPickingTransportMethod(models.Model):
    _name = 'stock.picking.transport.method'
    _description = "Method of transport"
    _order = 'sequence, name, id'

    active = fields.Boolean(string=_("Active"), default=True)
    sequence = fields.Integer(string=_("Sequence"), index=True, default=10)
    name = fields.Char(string=_("Method name"), index=True, required=True, translate=True)
    note = fields.Html(string=_("Internal note"))

    _sql_constraints = [(
        'name_uniq',
        'unique(name)',
        "This method of transport already exists!"
    )]
