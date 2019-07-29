import datetime

from odoo import _, api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError

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

CANCEL_MOVE_STATE = 'cancel'


class StockDeliveryNote(models.Model):
    _name = 'stock.delivery.note'
    _inherit = ['mail.thread', 'mail.activity.mixin']
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

    note = fields.Html(string=_("Internal note"), states=DONE_READONLY_STATE)

    @api.onchange('partner_id')
    def _onchange_partner(self):
        domain = []

        if self.partner_id:
            domain = [
                '|', ('id', '=', self.partner_id.id),
                     ('parent_id', '=', self.partner_id.id)
            ]

        return {
            'domain': {'partner_shipping_id': domain}
        }

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
        raise NotImplementedError(_("This functionality isn't yet ready. Please, come back later."))

    @api.model
    def _compose_detail_lines_vals(self, vals):
        picking_ids = []
        if 'picking_ids' not in vals:
            return vals

        for tuple in vals['picking_ids']:
            if tuple[0] == 4:
                picking_ids.append(tuple[1])

            elif tuple[0] == 6:
                picking_ids.extend(tuple[2])

        detail_lines = self.env['stock.delivery.note.line']._prepare_detail_lines(picking_ids)
        if detail_lines:
            pass

    @api.model
    @api.returns('self')
    def create(self, vals):
        composed_vals = self._compose_detail_lines_vals(vals)

        return super().create(composed_vals)

    @api.multi
    def update_detail_lines(self):
        for note in self:
            #
            # TODO: Something, something...
            #
            pass

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

    move_id = fields.Many2one('stock.move', string=_("Stock movement"), readonly=True)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            domain = [('category_id', '=', self.product_id.uom_id.category_id.id)]

            self.name = self.product_id.get_product_multiline_description_sale()

        else:
            domain = []

        return {'domain': {'product_uom': domain}}

    def _prepare_detail_lines(self, picking_ids):
        lines = []
        if not picking_ids:
            return lines

        pickings = self.env['stock.picking'].browse(picking_ids)
        for move in pickings.mapped('move_lines').filtered(lambda m: m.state != CANCEL_MOVE_STATE):
            if self.search_count([('move_id', '=', move.id)]):
                raise UserError(_("The stock movement named \"{}\" seems to be"
                                  " already related to another delivery note.\n"
                                  "You can't add this stock movement to this delivery note."))
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
