# Copyright 2014-2019 Dinamiche Aziendali srl (http://www.dinamicheaziendali.it/)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Gianmarco Conte <gconte@dinamicheaziendali.it>
# Copyright (c) 2019, Link IT Europe Srl
# @author: Matteo Bilotta <mbilotta@linkeurope.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models

from .stock_delivery_note import DOMAIN_DELIVERY_NOTE_STATES
from ..mixins.picking_checker import DOMAIN_PICKING_TYPES, DONE_PICKING_STATE

CANCEL_MOVE_STATE = 'cancel'

PRICES_TO_SHOW = [
    ('unit', "Unit price"),
    ('total', "Total price"),
    ('none', "None")
]
DOMAIN_PRICES_TO_SHOW = [p[0] for p in PRICES_TO_SHOW]


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    delivery_note_id = fields.Many2one('stock.delivery.note', string=_("Delivery note"), copy=False)
    delivery_note_partner_shipping_id = fields.Many2one('res.partner', related='delivery_note_id.partner_shipping_id')

    delivery_note_carrier_id = fields.Many2one('res.partner', related='delivery_note_id.carrier_id')
    delivery_note_delivery_method_id = fields.Many2one('delivery.carrier',
                                                       related='delivery_note_id.delivery_method_id')

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
    use_advanced_behaviour = fields.Boolean(compute='_compute_boolean_flags')
    delivery_note_exists = fields.Boolean(compute='_compute_boolean_flags')
    delivery_note_readonly = fields.Boolean(compute='_compute_boolean_flags')
    delivery_note_visible = fields.Boolean(compute='_compute_boolean_flags')
    delivery_note_state = fields.Char(compute='_compute_boolean_flags')
    can_be_invoiced = fields.Boolean(compute='_compute_boolean_flags')

    @property
    def _delivery_note_fields(self):
        from collections import OrderedDict

        fields = OrderedDict({
            key: field
            for key, field in self._fields.items()
            if field.related and field.related[0] == 'delivery_note_id'
        })

        setattr(type(self), '_delivery_note_fields', fields)

        return fields

    @api.multi
    def _compute_boolean_flags(self):
        from_delivery_note = self.env.context.get('from_delivery_note')
        use_advanced_behaviour = self.env.user.user_has_groups('l10n_it_delivery_note.use_advanced_delivery_notes')

        for picking in self:
            picking.use_delivery_note = not from_delivery_note and picking.state == DONE_PICKING_STATE

            picking.delivery_note_visible = use_advanced_behaviour
            picking.use_advanced_behaviour = use_advanced_behaviour

            picking.delivery_note_readonly = True

            if picking.use_delivery_note and picking.delivery_note_id:
                picking.delivery_note_exists = True
                picking.delivery_note_readonly = (picking.delivery_note_id.state != DOMAIN_DELIVERY_NOTE_STATES[0])
                picking.delivery_note_state = picking.delivery_note_id.state
                picking.can_be_invoiced = bool(picking.delivery_note_id.sale_ids)

    def _add_delivery_cost_to_so(self):
        self.ensure_one()

        super(StockPicking, self.with_context(default_delivery_picking_id=self.id))._add_delivery_cost_to_so()

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

    def action_delivery_note_draft(self):
        self.ensure_one()

        return self.delivery_note_id.action_draft()

    def action_delivery_note_confirm(self):
        self.ensure_one()

        return self.delivery_note_id.action_confirm()

    def action_delivery_note_invoice(self):
        self.ensure_one()

        return self.delivery_note_id.action_invoice()

    @api.multi
    def action_delivery_note_done(self):
        self.ensure_one()

        return self.delivery_note_id.action_done()

    def action_delivery_note_cancel(self):
        self.ensure_one()

        return self.delivery_note_id.action_cancel()

    def action_delivery_note_print(self):
        self.ensure_one()

        return self.delivery_note_id.action_print()

    @api.multi
    def action_done(self):
        res = super().action_done()

        if self.picking_type_code != DOMAIN_PICKING_TYPES[0] and \
           not self.env.user.user_has_groups('l10n_it_delivery_note.use_advanced_delivery_notes'):
            partners = self.get_partners()

            self.delivery_note_id = self.env['stock.delivery.note'].create({
                'partner_sender_id': partners[0].id,
                'partner_id': partners[1].id,
                'partner_shipping_id': partners[1].id
            })

        return res

    @api.multi
    @api.returns('res.partner')
    def get_partners(self):
        partner_id = self.mapped('partner_id')

        if len(partner_id) != 1:
            raise ValueError("You have just called this method on an heterogeneous set of pickings.\n"
                             "All pickings should have the same 'partner_id' field value.")

        src_location_id = self.mapped('location_id')

        if len(src_location_id) != 1:
            raise ValueError("You have just called this method on an heterogeneous set of pickings.\n"
                             "All pickings should have the same 'location_id' field value.")

        dest_location_id = self.mapped('location_dest_id')

        if len(dest_location_id) != 1:
            raise ValueError("You have just called this method on an heterogeneous set of pickings.\n"
                             "All pickings should have the same 'location_dest_id' field value.")

        src_warehouse_id = src_location_id.get_warehouse()
        dest_warehouse_id = dest_location_id.get_warehouse()

        src_partner_id = src_warehouse_id.partner_id
        dest_partner_id = dest_warehouse_id.partner_id

        if not src_partner_id:
            src_partner_id = partner_id

            if not dest_partner_id:
                raise ValueError("Fields 'src_partner_id' and 'dest_partner_id' cannot be both unset.")

        elif not dest_partner_id:
            dest_partner_id = partner_id

        return src_partner_id | dest_partner_id

    def goto_delivery_note(self, **kwargs):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'stock.delivery.note',
            'res_id': self.delivery_note_id.id,
            'views': [(False, 'form')],
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            **kwargs
        }

    def update_delivery_note_fields(self, vals):
        note_fields = self._delivery_note_fields

        if any(key in note_fields for key in vals.keys()):
            delivery_note_vals = {note_fields[key].related[1]: value for key, value in vals.items() if key in note_fields}

            self.mapped('delivery_note_id').write(delivery_note_vals)

    @api.multi
    def write(self, vals):
        res = super().write(vals)

        if self.mapped('delivery_note_id'):
            self.update_delivery_note_fields(vals)

            if 'delivery_note_id' in vals:
                self.mapped('delivery_note_id').update_detail_lines()

        return res


class StockPickingTransportCondition(models.Model):
    _name = 'stock.picking.transport.condition'
    _description = "Condition of transport"
    _order = 'sequence, name, id'

    active = fields.Boolean(string=_("Active"), default=True)
    sequence = fields.Integer(string=_("Sequence"), index=True, default=10)
    name = fields.Char(string=_("Condition name"), index=True, required=True, translate=True)
    price_to_show = fields.Selection(PRICES_TO_SHOW,
                                     string=_("Price to show"),
                                     required=True,
                                     default=DOMAIN_PRICES_TO_SHOW[0])

    #
    # TODO: Capire come dev'essere utilizzato questo campo.
    #       Deve influenzare il comportamento del campo "prezzo"
    #        solo ed esclusivamente nelle stampe del DdT?
    #

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