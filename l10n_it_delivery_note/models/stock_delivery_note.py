# Copyright (c) 2019, Link IT Europe Srl
# @author: Matteo Bilotta <mbilotta@linkeurope.it>

import datetime

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

from ..mixins.picking_checker import DONE_PICKING_STATE, PICKING_TYPES

DATETIME_FORMAT = '%d/%m/%Y %H:%M:%S'

DELIVERY_NOTE_STATES = [
    ('draft', "Draft"),
    ('confirm', "Validated"),
    ('invoiced', "Invoiced"),
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

INVOICE_STATUSES = [
    ('no', "Nothing to invoice"),
    ('to invoice', "To invoice"),
    ('invoiced', "Fully invoiced")
]
DOMAIN_INVOICE_STATUSES = [s[0] for s in INVOICE_STATUSES]


class StockDeliveryNote(models.Model):
    _name = 'stock.delivery.note'
    _inherit = [
        'mail.thread',
        'mail.activity.mixin',
        'stock.picking.checker.mixin',
        'shipping.information.updater.mixin'
    ]
    _description = "Delivery note"
    _order = 'date DESC, id DESC'
    _rec_name = 'display_name'

    def _default_company(self):
        return self.env.user.company_id

    def _default_type(self):
        return self.env['stock.delivery.note.type'].search([], limit=1)

    def _default_volume_uom(self):
        return self.env.ref('uom.product_uom_litre', raise_if_not_found=False)

    def _domain_volume_uom(self):
        uom_category_id = self.env.ref('uom.product_uom_categ_vol',
                                       raise_if_not_found=False)

        return [('category_id', '=', uom_category_id.id)]

    def _default_weight_uom(self):
        return self.env.ref('uom.product_uom_kgm', raise_if_not_found=False)

    def _domain_weight_uom(self):
        uom_category_id = self.env.ref('uom.product_uom_categ_kgm',
                                       raise_if_not_found=False)

        return [('category_id', '=', uom_category_id.id)]

    active = fields.Boolean(string=_("Active"), default=True)
    name = fields.Char(string=_("Name"), readonly=True, index=True, copy=False, track_visibility='onchange')
    partner_ref = fields.Char(string=_("Partner Reference"), index=True, required=False, translate=True, copy=False)
    display_name = fields.Char(compute='_compute_display_name', store=True, index=True, copy=False)

    state = fields.Selection(DELIVERY_NOTE_STATES,
                             string=_("State"),
                             copy=False,
                             default=DOMAIN_DELIVERY_NOTE_STATES[0],
                             required=True,
                             track_visibility='onchange')

    partner_sender_id = fields.Many2one('res.partner',
                                        string=_("Sender"),
                                        states=DRAFT_EDITABLE_STATE,
                                        default=_default_company,
                                        readonly=True,
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
                                          states=DONE_READONLY_STATE,
                                          readonly=True,
                                          required=True,
                                          track_visibility='onchange')

    carrier_id = fields.Many2one('res.partner',
                                 string=_("Carrier"),
                                 states=DONE_READONLY_STATE,
                                 readonly=True,
                                 track_visibility='onchange')
    delivery_method_id = fields.Many2one('delivery.carrier',
                                         string=_("Delivery method"),
                                         states=DONE_READONLY_STATE,
                                         readonly=True,
                                         track_visibility='onchange')

    date = fields.Date(string=_("Date"), states=DRAFT_EDITABLE_STATE, copy=False)
    type_id = fields.Many2one('stock.delivery.note.type',
                              string=_("Type"),
                              default=_default_type,
                              states=DRAFT_EDITABLE_STATE,
                              readonly=True,
                              required=True,
                              index=True)

    type_code = fields.Selection(string=_("Type of Operation"), related='type_id.code', store=True)
    parcels = fields.Integer(string=_("Parcels"), states=DONE_READONLY_STATE, readonly=True)
    volume = fields.Float(string=_("Volume"), states=DONE_READONLY_STATE, readonly=True)

    volume_uom_id = fields.Many2one('uom.uom',
                                    string=_("Volume UoM"),
                                    default=_default_volume_uom,
                                    domain=_domain_volume_uom,
                                    states=DONE_READONLY_STATE,
                                    readonly=True)
    gross_weight = fields.Float(string=_("Gross weight"),
                                states=DONE_READONLY_STATE, readonly=True)
    gross_weight_uom_id = fields.Many2one('uom.uom',
                                          string=_("Gross weight UoM"),
                                          default=_default_weight_uom,
                                          domain=_domain_weight_uom,
                                          states=DONE_READONLY_STATE,
                                          readonly=True)
    net_weight = fields.Float(string=_("Net weight"),
                              states=DONE_READONLY_STATE, readonly=True)
    net_weight_uom_id = fields.Many2one('uom.uom',
                                        string=_("Net weight UoM"),
                                        default=_default_weight_uom,
                                        domain=_domain_weight_uom,
                                        states=DONE_READONLY_STATE,
                                        readonly=True)

    transport_condition_id = \
        fields.Many2one('stock.picking.transport.condition',
                        string=_("Condition of transport"),
                        states=DONE_READONLY_STATE,
                        readonly=True)
    goods_appearance_id = fields.Many2one('stock.picking.goods.appearance',
                                          string=_("Appearance of goods"),
                                          states=DONE_READONLY_STATE,
                                          readonly=True)
    transport_reason_id = fields.Many2one('stock.picking.transport.reason',
                                          string=_("Reason of transport"),
                                          states=DONE_READONLY_STATE,
                                          readonly=True)
    transport_method_id = fields.Many2one('stock.picking.transport.method',
                                          string=_("Method of transport"),
                                          states=DONE_READONLY_STATE,
                                          readonly=True)

    transport_datetime = fields.Datetime(string=_("Transport date"),
                                         states=DONE_READONLY_STATE,
                                         copy=False)

    line_ids = fields.One2many('stock.delivery.note.line', 'delivery_note_id',
                               string=_("Lines"))
    invoice_status = fields.Selection(INVOICE_STATUSES,
                                      string=_("Invoice status"),
                                      compute='_compute_invoice_status',
                                      default=DOMAIN_INVOICE_STATUSES[0],
                                      readonly=True,
                                      store=True,
                                      copy=False)

    picking_ids = fields.One2many('stock.picking', 'delivery_note_id',
                                  string=_("Pickings"))
    pickings_picker = fields.Many2many('stock.picking',
                                       compute='_get_pickings',
                                       inverse='_set_pickings')

    picking_type = fields.Selection(PICKING_TYPES,
                                    string=_("Picking type"),
                                    compute='_compute_picking_type',
                                    store=True)

    sale_ids = fields.Many2many('sale.order', compute='_compute_sales')
    sale_count = fields.Integer(compute='_compute_sales')
    sales_transport_check = fields.Boolean(compute='_compute_sales', default=True)

    invoice_ids = fields.Many2many('account.invoice',
                                   'stock_delivery_note_account_invoice_rel',
                                   'delivery_note_id',
                                   'invoice_id',
                                   string=_("Invoices"),
                                   copy=False)

    print_prices = fields.Boolean(string=_("Print prices on report"),
                                  related="type_id.print_prices",
                                  store=True)
    note = fields.Html(string=_("Internal note"),
                       states=DONE_READONLY_STATE)

    show_product_information = fields.Boolean(compute='_compute_boolean_flags')

    @api.multi
    @api.depends('name', 'partner_id', 'partner_id.display_name')
    def _compute_display_name(self):
        for note in self:
            if not note.name:
                partner_name = note.partner_id.display_name
                create_date = note.create_date.strftime(DATETIME_FORMAT)
                name = "{} - {}".format(partner_name, create_date)
            else:
                if note.code != 'incoming':
                    name = note.name
                else:
                    name = note.partner_ref
            note.display_name = name

    @api.multi
    @api.depends('state', 'line_ids', 'line_ids.invoice_status')
    def _compute_invoice_status(self):
        for note in self:
            lines = note.line_ids.filtered(lambda l: l.sale_line_id)

            if all(line.invoice_status == DOMAIN_INVOICE_STATUSES[2] for line in lines):
                note.invoice_status = DOMAIN_INVOICE_STATUSES[2]

            elif any(line.invoice_status == DOMAIN_INVOICE_STATUSES[1] for line in lines):
                note.invoice_status = DOMAIN_INVOICE_STATUSES[1]

            else:
                note.invoice_status = DOMAIN_INVOICE_STATUSES[0]

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
    @api.depends('picking_ids')
    def _compute_picking_type(self):
        for note in self.filtered(lambda n: n.picking_ids):
            picking_types = set(note.picking_ids.mapped('picking_type_code'))
            picking_types = list(picking_types)

            if len(picking_types) != 1:
                raise ValueError("You have just called this method on an heterogeneous set of pickings.\n"
                                 "All pickings should have the same 'picking_type_code' field value.")

            note.picking_type = picking_types[0]

    @api.multi
    def _compute_sales(self):
        for note in self:
            #
            # SMELLS: Perché solo quelli 'da fatturare'?
            #
            sales = self.mapped('picking_ids.sale_id') \
                        .filtered(lambda o: o.invoice_status == DOMAIN_INVOICE_STATUSES[1])

            note.sale_ids = sales
            note.sale_count = len(sales)

            tc = sales.mapped('default_transport_condition_id')
            ga = sales.mapped('default_goods_appearance_id')
            tr = sales.mapped('default_transport_reason_id')
            tm = sales.mapped('default_transport_method_id')
            note.sales_transport_check = all([len(x) < 2 for x in [tc, ga, tr, tm]])

    @api.multi
    def _compute_boolean_flags(self):
        show_product_information = self.user_has_groups('l10n_it_delivery_note.show_product_related_fields')

        for note in self:
            note.show_product_information = show_product_information

    @api.onchange('type_id')
    def _onchange_type(self):
        if self.type_id:
            changed = self._update_generic_shipping_information(self.type_id)

            if changed:
                return {
                    'warning': {
                        'title': _("Warning!"),
                        'message': "Some of the shipping configuration have been overwritten with"
                                   " the default ones of the selected delivery note type.\n"
                                   "Please, make sure to check this information before continuing."
                    }
                }

    @api.onchange('partner_id')
    def _onchange_partner(self):
        self.partner_shipping_id = self.partner_id

        if self.partner_id:
            pickings_picker_domain = [
                ('delivery_note_id', '=', False),
                ('state', '=', DONE_PICKING_STATE),
                ('picking_type_code', '=', self.picking_type),
                ('partner_id', '=', self.partner_id.id)
            ]

        else:
            pickings_picker_domain = [('id', '=', False)]

        return {'domain': {'pickings_picker': pickings_picker_domain}}

    @api.onchange('partner_shipping_id')
    def _onchange_partner_shipping(self):
        if self.partner_shipping_id:
            changed = self._update_partner_shipping_information(self.partner_shipping_id)

            if changed:
                return {
                    'warning': {
                        'title': _("Warning!"),
                        'message': "Some of the shipping configuration have been overwritten with"
                                   " the default ones of the selected shipping partner address.\n"
                                   "Please, make sure to check this information before continuing."
                    }
                }

        else:
            self.delivery_method_id = False

    def check_compliance(self, pickings):
        super().check_compliance(pickings)

        self._check_delivery_notes(self.pickings_picker - self.picking_ids)

    @api.multi
    def ensure_annulability(self):
        if self.mapped('invoice_ids'):
            raise UserError(_("You cannot cancel this delivery note. "
                              "There is at least one invoice"
                              " related to this delivery note."))

    @api.multi
    def action_draft(self):
        self.write({'state': DOMAIN_DELIVERY_NOTE_STATES[0]})
        self.line_ids.sync_invoice_status()

    @api.multi
    def action_confirm(self):
        for note in self:
            sequence = note.type_id.sequence_id

            #
            # TODO: Verificare che il campo "Data di trasporto" sia valorizzato?
            #       Potrebbe essere necessario rendere obbligatorio
            #        tale campo per questo passaggio di stato?
            #

            note.state = DOMAIN_DELIVERY_NOTE_STATES[1]
            if not note.date:
                note.date = datetime.date.today()

            if not note.name:
                note.name = sequence.next_by_id()

    def _fix_quantities_to_invoice(self, lines):
        cache = {}

        pickings_lines = lines.retrieve_pickings_lines(self.picking_ids)
        other_lines = lines - pickings_lines

        for line in other_lines:
            cache[line] = line.fix_qty_to_invoice()

        pickings_move_ids = self.mapped('picking_ids.move_lines')
        for line in pickings_lines.filtered(lambda l: len(l.move_ids) > 1):
            move_ids = line.move_ids & pickings_move_ids
            qty_to_invoice = sum(move_ids.mapped('quantity_done'))

            if qty_to_invoice < (line.product_uom_qty - line.qty_to_invoice):
                cache[line] = line.fix_qty_to_invoice(qty_to_invoice)

        return cache

    def action_invoice(self):
        self.ensure_one()

        orders_lines = self.mapped('sale_ids.order_line').filtered(lambda l: l.product_id)
        downpayment_lines = orders_lines.filtered(lambda l: l.is_downpayment)
        invoiceable_lines = orders_lines.filtered(lambda l: l.is_invoiceable)
        cache = self._fix_quantities_to_invoice(invoiceable_lines - downpayment_lines)

        for downpayment in downpayment_lines:
            order = downpayment.order_id
            order_lines = order.order_line.filtered(lambda l: l.product_id and not l.is_downpayment)

            if order_lines.filtered(lambda l: l.need_to_be_invoiced):
                cache[downpayment] = downpayment.fix_qty_to_invoice()

        self.sale_ids.action_invoice_create(final=True)

        for line, vals in cache.items():
            line.write(vals)

        orders_lines._get_to_invoice_qty()

        self.write({'state': DOMAIN_DELIVERY_NOTE_STATES[2]})

    @api.multi
    def action_done(self):
        self.write({'state': DOMAIN_DELIVERY_NOTE_STATES[3]})

    @api.multi
    def action_cancel(self):
        self.ensure_annulability()

        self.write({'state': DOMAIN_DELIVERY_NOTE_STATES[4]})

    @api.multi
    def action_print(self):
        return self.env.ref('l10n_it_delivery_note.delivery_note_report_action').report_action(self)

    def update_transport_datetime(self):
        self.transport_datetime = datetime.datetime.now()

    @api.multi
    def goto_sales(self, **kwargs):
        sales = self.mapped('sale_ids')
        action = self.env.ref('sale.action_orders').read()[0]
        action.update(kwargs)

        if len(sales) > 1:
            action['domain'] = [('id', 'in', sales.ids)]

        elif len(sales) == 1:
            action['views'] = [(self.env.ref('sale.view_order_form').id, 'form')]
            action['res_id'] = sales.id

        else:
            action = {'type': 'ir.actions.act_window_close'}

        return action

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

    @api.multi
    def unlink(self):
        self.ensure_annulability()

        return super().unlink()


class StockDeliveryNoteLine(models.Model):
    _name = 'stock.delivery.note.line'
    _description = "Delivery note line"
    _order = 'sequence, id'

    def _default_currency(self):
        return self.env.user.company_id.currency_id

    def _default_unit_uom(self):
        return self.env.ref('uom.product_uom_unit', raise_if_not_found=False)

    delivery_note_id = fields.Many2one('stock.delivery.note',
                                       string=_("Delivery note"),
                                       required=True,
                                       ondelete='cascade')

    sequence = fields.Integer(string=_("Sequence"), required=True, default=10, index=True)
    name = fields.Text(string=_("Description"), required=True)
    display_type = fields.Selection(LINE_DISPLAY_TYPES, string=_("Line type"), default=False)
    product_id = fields.Many2one('product.product', string=_("Product"))
    product_description = fields.Text(related='product_id.description_sale')
    product_qty = fields.Float(string=_("Quantity"), digits=dp.get_precision('Unit of Measure'), default=1.0)
    product_uom_id = fields.Many2one('uom.uom', string=_("UoM"), default=_default_unit_uom)
    price_unit = fields.Monetary(string=_("Unit price"),
                                 currency_field='currency_id',
                                 digits=dp.get_precision('Product Price'))
    currency_id = fields.Many2one('res.currency', string=_("Currency"), required=True, default=_default_currency)
    discount = fields.Float(string=_("Discount"), digits=dp.get_precision('Discount'))
    tax_ids = fields.Many2many('account.tax', string=_("Taxes"))

    move_id = fields.Many2one('stock.move', string=_("Warehouse movement"), readonly=True, copy=False)
    sale_line_id = fields.Many2one('sale.order.line', related='move_id.sale_line_id', store=True, copy=False)
    invoice_status = fields.Selection(INVOICE_STATUSES,
                                      string=_("Invoice status"),
                                      required=True,
                                      default=DOMAIN_INVOICE_STATUSES[0],
                                      copy=False)

    _sql_constraints = [(
        'move_uniq',
        'unique(move_id)',
        "You cannot assign the same warehouse movement to different delivery notes!"
    )]

    @property
    def is_invoiceable(self):
        return self.invoice_status == DOMAIN_INVOICE_STATUSES[1]

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            domain = [('category_id', '=', self.product_id.uom_id.category_id.id)]

            self.name = self.product_id.get_product_multiline_description_sale()

        else:
            domain = []

        return {'domain': {'product_uom_id': domain}}

    @api.model
    def _prepare_detail_lines(self, moves):
        lines = []
        for move in moves:
            line = {
                'move_id': move.id,
                'name': move.name,
                'product_id': move.product_id.id,
                'product_qty': move.product_uom_qty,
                'product_uom_id': move.product_uom.id
            }

            if move.sale_line_id:
                order_line = move.sale_line_id
                order = order_line.order_id

                line['price_unit'] = order_line.price_unit
                line['currency_id'] = order.currency_id.id
                line['discount'] = order_line.discount
                line['tax_ids'] = [(6, False, order_line.tax_id.ids)]
                line['invoice_status'] = DOMAIN_INVOICE_STATUSES[1]

            lines.append(line)

        return lines

    @api.model
    @api.returns('self')
    def create(self, vals):
        if vals.get('display_type'):
            vals.update({
                'product_id': False,
                'product_qty': 0.0,
                'product_uom_id': False,
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

    @api.multi
    def sync_invoice_status(self):
        for line in self.filtered(lambda l: l.sale_line_id):
            invoice_status = line.sale_line_id.invoice_status
            line.invoice_status = DOMAIN_INVOICE_STATUSES[1] if invoice_status == 'upselling' else invoice_status


class StockDeliveryNoteType(models.Model):
    _name = 'stock.delivery.note.type'
    _description = "Delivery note type"
    _order = 'sequence, name, id'

    active = fields.Boolean(string=_("Active"), default=True)
    sequence = fields.Integer(string=_("Sequence"), index=True, default=10)
    name = fields.Char(string=_("Name"), index=True, required=True, translate=True)
    print_prices = fields.Boolean(string=_("Print prices on report"), default=False)
    code = fields.Selection([('incoming', 'Incoming'), ('outgoing', 'Outgoing'), ('internal', 'Internal')],
        string='Type of Operation',
        required=True
    )
    default_transport_condition_id = fields.Many2one('stock.picking.transport.condition',
                                                     string=_("Condition of transport"))
    default_goods_appearance_id = fields.Many2one('stock.picking.goods.appearance', string=_("Appearance of goods"))
    default_transport_reason_id = fields.Many2one('stock.picking.transport.reason', string=_("Reason of transport"))
    default_transport_method_id = fields.Many2one('stock.picking.transport.method', string=_("Method of transport"))

    sequence_id = fields.Many2one('ir.sequence', required=True)
    next_sequence_number = fields.Integer(related='sequence_id.number_next_actual')
    company_id = fields.Many2one('res.company', string=_("Company"), default=lambda self: self.env.user.company_id)
    note = fields.Html(string=_("Internal note"))

    _sql_constraints = [(
        'name_uniq',
        'unique(name, company_id)',
        "This delivery note type already exists!"
    )]

    def goto_sequence(self, **kwargs):
        self.ensure_one()

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'ir.sequence',
            'res_id': self.sequence_id.id,
            'views': [(False, 'form')],
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'current',
            **kwargs
        }
