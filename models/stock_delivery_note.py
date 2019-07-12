import datetime

from odoo import _, api, fields, models

DATETIME_FORMAT = '%d/%m/%Y %H:%M:%S'

DELIVERY_NOTE_STATES = [
    ('draft', "Draft"),
    ('confirm', "Validated"),
    ('done', "Done"),
    ('cancel', "Cancelled")
]
DOMAIN_DELIVERY_NOTE_STATES = [s[0] for s in DELIVERY_NOTE_STATES]


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
    name = fields.Char(string=_("Name"), track_visibility='onchange')
    state = fields.Selection(DELIVERY_NOTE_STATES,
                             string=_("State"),
                             default=DOMAIN_DELIVERY_NOTE_STATES[0],
                             required=True,
                             track_visibility='onchange')

    partner_id = fields.Many2one('res.partner',
                                 string=_("Recipient"),
                                 required=True,
                                 track_visibility='onchange')
    partner_shipping_id = fields.Many2one('res.partner',
                                          string=_("Shipping address"),
                                          required=True,
                                          track_visibility='onchange')

    date = fields.Date(string=_("Date"))
    type_id = fields.Many2one('stock.delivery.note.type',
                              string=_("Type"),
                              required=True,
                              default=_default_type)

    parcels = fields.Integer(string=_("Parcels"))
    volume = fields.Float(string=_("Volume"))
    volume_uom_id = fields.Many2one('uom.uom',
                                    string=_("Volume UoM"),
                                    default=_default_volume_uom,
                                    domain=_domain_volume_uom)
    gross_weight = fields.Float(string=_("Gross weight"))
    gross_weight_uom_id = fields.Many2one('uom.uom',
                                          string=_("Gross weight UoM"),
                                          default=_default_weight_uom,
                                          domain=_domain_weight_uom)
    net_weight = fields.Float(string=_("Net weight"))
    net_weight_uom_id = fields.Many2one('uom.uom',
                                        string=_("Net weight UoM"),
                                        default=_default_weight_uom,
                                        domain=_domain_weight_uom)

    transport_condition_id = fields.Many2one('stock.picking.transport.condition', string=_("Condition of transport"))
    goods_appearance_id = fields.Many2one('stock.picking.goods.appearance', string=_("Appearance of goods"))
    transport_reason_id = fields.Many2one('stock.picking.transport.reason', string=_("Reason of transport"))
    transport_method_id = fields.Many2one('stock.picking.transport.method', string=_("Method of transport"))

    transport_datetime = fields.Datetime(string=_("Transport date"))

    picking_ids = fields.One2many('stock.picking', 'delivery_note_id', string=_("Pickings"))

    note = fields.Html(string=_("Internal note"))

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
    @api.depends('partner_id', 'partner_id.display_name')
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

            note.name = sequence.next_by_id()

    @api.multi
    def action_done(self):
        self.write({'state': DOMAIN_DELIVERY_NOTE_STATES[2]})

    @api.multi
    def action_cancel(self):
        self.write({'state': DOMAIN_DELIVERY_NOTE_STATES[3]})


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
