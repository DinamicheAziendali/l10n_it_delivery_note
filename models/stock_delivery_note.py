# Copyright (c) 2019, Link IT Europe Srl (http://www.linkgroup.it/)
# @author: Matteo Bilotta <mbilotta@linkgroup.it>

import datetime

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

from ..mixins.picking_checker import DONE_PICKING_STATE, INCOMING_PICKING_TYPE

DATETIME_FORMAT = '%d/%m/%Y %H:%M:%S'

DELIVERY_NOTE_STATES = [
    ('draft', "Draft"),
    ('confirm', "Validated"),
    ('done', "Done"),
    ('cancel', "Cancelled")
]
DOMAIN_DELIVERY_NOTE_STATES = [s[0] for s in DELIVERY_NOTE_STATES]

LINE_DISPLAY_TYPES = [
    ('line_section', "Section"),
    ('line_note', "Note")
]
DOMAIN_LINE_DISPLAY_TYPES = [t[0] for t in LINE_DISPLAY_TYPES]

DRAFT_EDITABLE_STATE = {'draft': [('readonly', False)]}
DONE_READONLY_STATE = {'done': [('readonly', True)]}


class StockDeliveryNote(models.Model):
    _name = 'stock.delivery.note'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'stock.picking.checker.mixin']
    _description = "Delivery note"
    _rec_name = 'display_name'

    def _default_type(self):
        return self.env['stock.delivery.note.type'].search([], limit=1)

    def _default_volume_uom(self):
        return self.env.ref('uom.product_uom_litre', raise_if_not_found=False)

    def _domain_volume_uom(self):
        uom_category_id = self.env.ref('uom.product_uom_categ_vol', raise_if_not_found=False)

        return [('category_id', '=', uom_category_id.id)]

    def _default_weight_uom(self):
        return self.env.ref('uom.product_uom_kgm', raise_if_not_found=False)

    def _domain_weight_uom(self):
        uom_category_id = self.env.ref('uom.product_uom_categ_kgm', raise_if_not_found=False)

        return [('category_id', '=', uom_category_id.id)]

    active = fields.Boolean(string=_("Active"), default=True)
    name = fields.Char(string=_("Name"), readonly=True, index=True, track_visibility='onchange')
    display_name = fields.Char(compute='_compute_display_name', store=True, index=True)
    state = fields.Selection(DELIVERY_NOTE_STATES,
                             string=_("State"),
                             default=DOMAIN_DELIVERY_NOTE_STATES[0],
                             required=True,
                             track_visibility='onchange')

    partner_id = fields.Many2one('res.partner',
                                 string=_("Recipient"),
                                 states=DRAFT_EDITABLE_STATE,
                                 readonly=True,
                                 required=True,
                                 index=True,
                                 track_visibility='onchange')
    partner_shipping_id = fields.Many2one('res.partner',
                                          string=_("Shipping address"),
                                          states=DRAFT_EDITABLE_STATE,
                                          readonly=True,
                                          required=True,
                                          track_visibility='onchange')

    date = fields.Date(string=_("Date"), states=DONE_READONLY_STATE)
    type_id = fields.Many2one('stock.delivery.note.type',
                              string=_("Type"),
                              default=_default_type,
                              states=DRAFT_EDITABLE_STATE,
                              readonly=True,
                              required=True,
                              index=True)

    parcels = fields.Integer(string=_("Parcels"), states=DRAFT_EDITABLE_STATE, readonly=True)
    volume = fields.Float(string=_("Volume"), states=DRAFT_EDITABLE_STATE, readonly=True)
    volume_uom_id = fields.Many2one('uom.uom',
                                    string=_("Volume UoM"),
                                    default=_default_volume_uom,
                                    domain=_domain_volume_uom,
                                    states=DRAFT_EDITABLE_STATE,
                                    readonly=True)
    gross_weight = fields.Float(string=_("Gross weight"), states=DRAFT_EDITABLE_STATE, readonly=True)
    gross_weight_uom_id = fields.Many2one('uom.uom',
                                          string=_("Gross weight UoM"),
                                          default=_default_weight_uom,
                                          domain=_domain_weight_uom,
                                          states=DRAFT_EDITABLE_STATE,
                                          readonly=True)
    net_weight = fields.Float(string=_("Net weight"), states=DRAFT_EDITABLE_STATE, readonly=True)
    net_weight_uom_id = fields.Many2one('uom.uom',
                                        string=_("Net weight UoM"),
                                        default=_default_weight_uom,
                                        domain=_domain_weight_uom,
                                        states=DRAFT_EDITABLE_STATE,
                                        readonly=True)

    transport_condition_id = fields.Many2one('stock.picking.transport.condition',
                                             string=_("Condition of transport"),
                                             states=DRAFT_EDITABLE_STATE,
                                             readonly=True)
    goods_appearance_id = fields.Many2one('stock.picking.goods.appearance',
                                          string=_("Appearance of goods"),
                                          states=DRAFT_EDITABLE_STATE,
                                          readonly=True)
    transport_reason_id = fields.Many2one('stock.picking.transport.reason',
                                          string=_("Reason of transport"),
                                          states=DRAFT_EDITABLE_STATE,
                                          readonly=True)
    transport_method_id = fields.Many2one('stock.picking.transport.method',
                                          string=_("Method of transport"),
                                          states=DRAFT_EDITABLE_STATE,
                                          readonly=True)

    transport_datetime = fields.Datetime(string=_("Transport date"), states=DONE_READONLY_STATE)

    line_ids = fields.One2many('stock.delivery.note.line', 'delivery_note_id', string=_("Lines"))

    picking_ids = fields.One2many('stock.picking', 'delivery_note_id', string=_("Pickings"))
    pickings_picker = fields.Many2many('stock.picking', compute='_get_pickings', inverse='_set_pickings')

    sale_ids = fields.Many2many('sale.order', compute='_compute_sale_ids')

    note = fields.Html(string=_("Internal note"), states=DONE_READONLY_STATE)

    @api.onchange('partner_id')
    def _onchange_partner(self):
        result = {}

        if self.partner_id:
            skipped = False

            if not self.transport_condition_id:
                self.transport_condition_id = self.partner_id.transport_condition_id
            elif self.partner_id.transport_condition_id:
                skipped = True

            if not self.goods_appearance_id:
                self.goods_appearance_id = self.partner_id.goods_appearance_id
            elif self.partner_id.goods_appearance_id:
                skipped = True

            if not self.transport_reason_id:
                self.transport_reason_id = self.partner_id.transport_reason_id
            elif self.partner_id.transport_reason_id:
                skipped = True

            if not self.transport_method_id:
                self.transport_method_id = self.partner_id.transport_method_id
            elif self.partner_id.transport_method_id:
                skipped = True

            if skipped:
                result['warning'] = {
                    'title': _("Warning!"),
                    'message': "Some of the shipping configuration have not"
                               " been overwritten with the default ones of"
                               " the partner due of fields already valorized. "
                               "Check this shipping information.\n"
                               "If you wish to be sure to overwrite all shipping information"
                               " be sure you make the fields blank before changing the partner."
                }

            pickings_picker_domain = [
                ('delivery_note_id', '=', False),
                ('state', '=', DONE_PICKING_STATE),
                ('picking_type_code', '!=', INCOMING_PICKING_TYPE),
                ('partner_id', '=', self.partner_id.id)
            ]
            shipping_partner_domain = [
                '|', ('id', '=', self.partner_id.id),
                     ('parent_id', '=', self.partner_id.id)
            ]

        else:
            pickings_picker_domain = [('id', '=', False)]
            shipping_partner_domain = [('id', '=', False)]

        result['domain'] = {
            'pickings_picker': pickings_picker_domain,
            'partner_shipping_id': shipping_partner_domain
        }

        return result

    @api.multi
    @api.depends('name', 'partner_id', 'partner_id.display_name')
    def _compute_display_name(self):
        for note in self:
            if not note.name:
                partner_name = note.partner_id.display_name
                create_date = note.create_date.strftime(DATETIME_FORMAT)

                name = "{} - {}".format(partner_name, create_date)

            else:
                name = note.name

            note.display_name = name

    @api.multi
    def _get_pickings(self):
        for note in self:
            note.pickings_picker = note.picking_ids

    @api.multi
    def _set_pickings(self):
        for note in self:
            if note.pickings_picker:
                self.check_compliance(note.pickings_picker)

            note.picking_ids = note.pickings_picker

    @api.multi
    def _compute_sale_ids(self):
        for note in self:
            note.sale_ids = self.mapped('picking_ids.sale_id')

    def check_compliance(self, pickings):
        super().check_compliance(pickings)

        self._check_delivery_notes(self.pickings_picker - self.picking_ids)

    @api.multi
    def action_draft(self):
        self.write({'state': DOMAIN_DELIVERY_NOTE_STATES[0]})

    @api.multi
    def action_confirm(self):
        for note in self:
            sequence = note.type_id.sequence_id

            note.state = DOMAIN_DELIVERY_NOTE_STATES[1]
            if not note.date:
                note.date = datetime.date.today()

            if not note.name:
                note.name = sequence.next_by_id()

    @api.multi
    def action_done(self):
        self.write({'state': DOMAIN_DELIVERY_NOTE_STATES[2]})

    @api.multi
    def action_cancel(self):
        self.write({'state': DOMAIN_DELIVERY_NOTE_STATES[3]})

    @api.multi
    def action_print(self):
        return self.env.ref('easy_ddt.delivery_note_report_action').report_action(self)

    def _fix_quantities_to_invoice(self, lines):
        cache = {}

        picking_lines = lines.retrieve_pickings_lines(self.picking_ids)
        other_lines = lines - picking_lines

        for line in other_lines:
            cache[line] = line.fix_qty_to_invoice()

        valid_move_ids = self.mapped('picking_ids.move_lines')

        for line in picking_lines.filtered(lambda l: len(l.move_ids) > 1):
            qty_to_invoice = sum(line.move_ids.filtered(lambda m: m in valid_move_ids).mapped('quantity_done'))

            cache[line] = line.fix_qty_to_invoice(qty_to_invoice)

        return cache

    def action_invoice(self):
        self.ensure_one()

        orders_lines = self.mapped('sale_ids.order_line').filtered(lambda l: l.product_id)
        downpayment_lines = orders_lines.filtered(lambda l: l.is_downpayment)
        invoiceable_lines = orders_lines.filtered(lambda l: l.is_invoiceable)
        cache = self._fix_quantities_to_invoice(invoiceable_lines - downpayment_lines)

        self.sale_ids.action_invoice_create()

        for line, vals in cache.items():
            line.write(vals)

    def _create_detail_lines(self, move_ids):
        if not move_ids:
            return

        moves = self.env['stock.move'].browse(move_ids)
        lines_vals = self.env['stock.delivery.note.line']._prepare_detail_lines(moves)

        self.write({'line_ids': [(0, False, vals) for vals in lines_vals]})

    def _delete_detail_lines(self, move_ids):
        if not move_ids:
            return

        lines = self.env['stock.delivery.note.line'].search([('move_id', 'in', move_ids)])

        self.write({'line_ids': [(2, line.id, False) for line in lines]})

    @api.multi
    def update_detail_lines(self):
        for note in self:
            lines_move_ids = note.mapped('line_ids.move_id').ids
            pickings_move_ids = note.mapped('picking_ids.valid_move_ids').ids

            move_ids_to_create = [l for l in pickings_move_ids if l not in lines_move_ids]
            move_ids_to_delete = [l for l in lines_move_ids if l not in pickings_move_ids]

            note._create_detail_lines(move_ids_to_create)
            note._delete_detail_lines(move_ids_to_delete)

    @api.model
    @api.returns('self')
    def create(self, vals):
        res = super().create(vals)

        if 'picking_ids' in vals:
            res.update_detail_lines()

        return res

    @api.multi
    def write(self, vals):
        res = super().write(vals)

        if 'picking_ids' in vals:
            self.update_detail_lines()

        return res


class StockDeliveryNoteLine(models.Model):
    _name = 'stock.delivery.note.line'
    _description = "Delivery note line"

    def _default_unit_uom(self):
        return self.env.ref('uom.product_uom_unit', raise_if_not_found=False)

    delivery_note_id = fields.Many2one('stock.delivery.note', string=_("Delivery note"), required=True)

    sequence = fields.Integer(string=_("Sequence"), required=True, default=10, index=True)
    name = fields.Text(string=_("Description"), required=True)
    display_type = fields.Selection(LINE_DISPLAY_TYPES, string=_("Line type"), default=False)
    product_id = fields.Many2one('product.product', string=_("Product"))
    product_description = fields.Text(related='product_id.description_sale')
    product_qty = fields.Float(string=_("Quantity"), digits=dp.get_precision('Unit of Measure'), default=1.0)
    product_uom = fields.Many2one('uom.uom', string=_("UoM"), default=_default_unit_uom)
    price_unit = fields.Float(string=_("Unit price"), digits=dp.get_precision('Product Price'))
    discount = fields.Float(string=_("Discount"), digits=dp.get_precision('Discount'))
    tax_ids = fields.Many2many('account.tax', string=_("Taxes"))

    move_id = fields.Many2one('stock.move', string=_("Warehouse movement"), readonly=True)
    sale_line_id = fields.Many2one('sale.order.line', related='move_id.sale_line_id', store=True)

    _sql_constraints = [(
        'move_uniq',
        'unique(move_id)',
        "You cannot assign the same warehouse movement to different delivery notes!"
    )]

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            domain = [('category_id', '=', self.product_id.uom_id.category_id.id)]

            self.name = self.product_id.get_product_multiline_description_sale()

        else:
            domain = []

        return {'domain': {'product_uom': domain}}

    @api.model
    def _prepare_detail_lines(self, moves):
        lines = []
        for move in moves:
            lines.append({
                'name': move.name,
                'product_id': move.product_id.id,
                'product_qty': move.product_uom_qty,
                'product_uom': move.product_uom.id,
                'price_unit': 0.0,
                'discount': 0.0,
                'tax_ids': [(5, False, False)],
                'move_id': move.id
            })

        return lines

    @api.model
    @api.returns('self')
    def create(self, vals):
        if vals.get('display_type'):
            vals.update({
                'product_id': False,
                'product_qty': 0.0,
                'product_uom': False,
                'price_unit': 0.0,
                'discount': 0.0,
                'tax_ids': [(5, False, False)]
            })

        return super().create(vals)

    @api.multi
    def write(self, vals):
        if 'display_type' in vals and self.filtered(lambda l: l.display_type != vals['display_type']):
            raise UserError(_("You cannot change the type of a delivery note line. "
                              "Instead you should delete the current line"
                              " and create a new line of the proper type."))

        return super().write(vals)


class StockDeliveryNoteType(models.Model):
    _name = 'stock.delivery.note.type'
    _description = "Delivery note type"
    _order = 'sequence, name, id'

    active = fields.Boolean(string=_("Active"), default=True)
    sequence = fields.Integer(string=_("Sequence"), index=True, default=10)
    name = fields.Char(string=_("Name"), index=True, required=True, translate=True)
    sequence_id = fields.Many2one('ir.sequence', required=True)
    next_sequence_number = fields.Integer(related='sequence_id.number_next_actual')
    company_id = fields.Many2one('res.company', string=_("Company"), default=lambda self: self.env.user.company_id)
    note = fields.Html(string=_("Internal note"))

    _sql_constraints = [(
        'name_uniq',
        'unique(name, company_id)',
        "This delivery note type already exists!"
    )]
