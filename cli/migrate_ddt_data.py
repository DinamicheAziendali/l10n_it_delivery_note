# Copyright (c) 2019, Link IT Europe Srl
# @author: Matteo Bilotta <mbilotta@linkeurope.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import argparse
import functools
import logging
import odoo

from odoo import SUPERUSER_ID
from odoo.cli import Command
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

STATES_MAPPING = {
    'draft': 'draft',
    'cancel': 'cancel',
    'in_pack': 'draft',
    'done': 'confirm'
}


def environment(funct=None, parser_args_method=None):
    if not funct:
        return functools.partial(environment, parser_args_method=parser_args_method)

    @functools.wraps(funct)
    def env_enabler(self, args):
        command_args = unknown_args = args

        if parser_args_method:
            command_args, unknown_args = parser_args_method(self, args)

        odoo.tools.config._parse_config(unknown_args)
        odoo.netsvc.init_logger()

        config = odoo.tools.config

        with odoo.api.Environment.manage():
            cr = odoo.registry(config['db_name']).cursor()
            env = odoo.api.Environment(cr, SUPERUSER_ID, {})

            funct(self, command_args, env)

    return env_enabler


# noinspection PyPep8Naming
class Migrate_Ddt_Data(Command):
    __is_debugging = None

    _carriage_conditions = None
    _goods_descriptions = None
    _transportation_reasons = None
    _transportation_methods = None
    _document_types = None

    env = None

    def __init__(self):
        self.__is_debugging = False

        self._carriage_conditions = {}
        self._goods_descriptions = {}
        self._transportation_reasons = {}
        self._transportation_methods = {}
        self._document_types = {}

    @property
    def _default_volume_uom(self):
        return self.env.ref('uom.product_uom_litre', raise_if_not_found=False)

    @property
    def _default_weight_uom(self):
        return self.env.ref('uom.product_uom_kgm', raise_if_not_found=False)

    # noinspection PyMethodMayBeStatic
    def _map_create(self, map_dict, old_records, Model, vals_getter=None):
        if not old_records:
            return

        def default_getter(record):
            return {
                'name': record.name,
                'note': record.note
            }

        if not vals_getter:
            vals_getter = default_getter

        for old_record in old_records:
            vals = vals_getter(old_record)
            new_record = Model.create(vals)

            map_dict[old_record] = new_record

    def _map_ref(self, map_dict, old_ext_id, new_ext_id):
        l10n_it_ddt_record = self.env.ref('l10n_it_ddt.{}'.format(old_ext_id))
        easy_ddt_record = self.env.ref('easy_ddt.{}'.format(new_ext_id))

        map_dict[l10n_it_ddt_record] = easy_ddt_record

        return l10n_it_ddt_record

    # noinspection PyMethodMayBeStatic
    def _parse_args(self, args):
        args_parser = argparse.ArgumentParser()
        args_parser.add_argument('--debug', action='store_true', default=False)

        return args_parser.parse_known_args(args)

    def check_database_integrity(self):
        _logger.info("Checking database integrity before run data migration...")

        self.env.cr.execute("""SELECT "id", "state" FROM "ir_module_module" WHERE "name" = 'l10n_it_ddt';""")
        l10n_it_ddt = self.env.cr.fetchone()
        if not l10n_it_ddt or l10n_it_ddt[1] != 'installed':
            raise UserError("Module `l10n_it_ddt` isn't installed on this database. "
                            "You don't need to run this command.")

        l10n_it_ddt_sequence = self.env.ref('l10n_it_ddt.seq_ddt')
        if l10n_it_ddt_sequence.number_next_actual == 1:
            raise UserError("It seems that there are no documents to migrate. "
                            "You don't need to run this command.")

        easy_ddt_sequence = self.env.ref('easy_ddt.delivery_note_sequence_ddt')
        if easy_ddt_sequence.number_next_actual > 1:
            raise ValidationError("It seems that at least one delivery note has been already created. "
                                  "You can't migrate any data on an already used database.")

        _logger.info("Database integrity check successfully passed.")

    def initialize(self, args, env):
        self.__is_debugging = args.debug

        self.env = env

    def migrate_carriage_conditions(self):
        _logger.info("Migrating carriage conditions data...")

        CarriageCondition = self.env['stock.picking.carriage_condition']
        TransportCondition = self.env['stock.picking.transport.condition']

        pf = self._map_ref(self._carriage_conditions, 'carriage_condition_PF', 'transport_condition_PF')
        pa = self._map_ref(self._carriage_conditions, 'carriage_condition_PA', 'transport_condition_PA')
        paf = self._map_ref(self._carriage_conditions, 'carriage_condition_PAF', 'transport_condition_PAF')

        records = CarriageCondition.search([('id', 'not in', [pf.id, pa.id, paf.id])], order='id ASC')

        self._map_create(self._carriage_conditions, records, TransportCondition)

        _logger.info("Carriage conditions data successfully migrated.")

    def migrate_goods_descriptions(self):
        _logger.info("Migrating goods descriptions data...")

        GoodsDescription = self.env['stock.picking.goods_description']
        GoodsAppearance = self.env['stock.picking.goods.appearance']

        car = self._map_ref(self._goods_descriptions, 'goods_description_CAR', 'goods_appearance_CAR')
        ban = self._map_ref(self._goods_descriptions, 'goods_description_BAN', 'goods_appearance_BAN')
        sfu = self._map_ref(self._goods_descriptions, 'goods_description_SFU', 'goods_appearance_SFU')
        cba = self._map_ref(self._goods_descriptions, 'goods_description_CBA', 'goods_appearance_CBA')

        records = GoodsDescription.search([('id', 'not in', [car.id, ban.id, sfu.id, cba.id])], order='id ASC')

        self._map_create(self._goods_descriptions, records, GoodsAppearance)

        _logger.info("Goods descriptions data successfully migrated.")

    def migrate_transportation_reasons(self):
        _logger.info("Migrating transportation reasons data...")

        TransportationReason = self.env['stock.picking.transportation_reason']
        TransportReason = self.env['stock.picking.transport.reason']

        ven = self._map_ref(self._transportation_reasons, 'transportation_reason_VEN', 'transport_reason_VEN')
        vis = self._map_ref(self._transportation_reasons, 'transportation_reason_VIS', 'transport_reason_VIS')
        res = self._map_ref(self._transportation_reasons, 'transportation_reason_RES', 'transport_reason_RES')

        records = TransportationReason.search([('id', 'not in', [ven.id, vis.id, res.id])], order='id ASC')

        self._map_create(self._transportation_reasons, records, TransportReason)

        _logger.info("Transportation reasons data successfully migrated.")

    def migrate_transportation_methods(self):
        _logger.info("Migrating transportation methods data...")

        TransportationMethod = self.env['stock.picking.transportation_method']
        TransportMethod = self.env['stock.picking.transport.method']

        mit = self._map_ref(self._transportation_methods, 'transportation_method_MIT', 'transport_method_MIT')
        des = self._map_ref(self._transportation_methods, 'transportation_method_DES', 'transport_method_DES')
        cor = self._map_ref(self._transportation_methods, 'transportation_method_COR', 'transport_method_COR')

        records = TransportationMethod.search([('id', 'not in', [mit.id, des.id, cor.id])], order='id ASC')

        self._map_create(self._transportation_methods, records, TransportMethod)

        _logger.info("Transportation methods data successfully migrated.")

    def migrate_document_types(self):
        _logger.info("Migrating document types data...")

        DocumentType = self.env['stock.ddt.type']
        DeliveryNoteType = self.env['stock.delivery.note.type']

        l10n_it_ddt_type = self.env.ref('l10n_it_ddt.ddt_type_ddt')
        easy_ddt_type = self.env.ref('easy_ddt.delivery_note_type_ddt')
        easy_ddt_type.write({'sequence_id': l10n_it_ddt_type.sequence_id.id})

        self.env.cr.execute("""DELETE FROM "ir_model_data" WHERE "module" = 'l10n_it_ddt' AND "name" = 'seq_ddt';""")

        self._document_types[l10n_it_ddt_type] = easy_ddt_type

        records = DocumentType.search([('id', 'not in', [l10n_it_ddt_type.id])], order='id ASC')

        self._map_create(self._document_types, records, DeliveryNoteType, lambda r: {

            'name': r.name,
            'sequence_id': r.sequence_id.id,
            'default_goods_appearance_id': self._goods_descriptions[r.default_goods_description_id].id,
            'default_transport_reason_id': self._transportation_reasons[r.default_transportation_reason_id].id,
            'default_transport_condition_id': self._carriage_conditions[r.default_carriage_condition_id].id,
            'default_transport_method_id': self._transportation_methods[r.default_transportation_method_id].id,
            'note': r.note
        })

        _logger.info("Document types data successfully migrated.")

    def migrate_documents(self):
        def vals_getter(record):
            return {

                'state': STATES_MAPPING[record.state],
                'name': record.ddt_number,
                'partner_sender_id': record.company_id.id,
                'partner_id': record.partner_id.id,
                'partner_shipping_id': record.partner_shipping_id.id,
                'type_id': self._document_types[record.ddt_type_id].id,
                'date': record.date,
                'carrier_id': record.carrier_id.id,
                'delivery_method_id': record.partner_id.property_delivery_carrier_id.id,
                'transport_datetime': record.date_done,
                'parcels': record.parcels,
                'volume': record.volume,
                'volume_uom_id': record.volume_uom_id.id or self._default_volume_uom.id,
                'gross_weight': record.gross_weight or record.weight,
                'gross_weight_uom_id': record.gross_weight_uom_id.id or self._default_weight_uom.id,
                'net_weight': record.weight_manual or record.weight,
                'net_weight_uom_id': record.weight_manual_uom_id.id or self._default_weight_uom.id,
                'goods_appearance_id': self._goods_descriptions[record.goods_description_id].id,
                'transport_reason_id': self._transportation_reasons[record.transportation_reason_id].id,
                'transport_condition_id': self._carriage_conditions[record.carriage_condition_id].id,
                'transport_method_id': self._transportation_methods[record.transportation_method_id].id,
                'picking_ids': [(4, p.id) for p in record.picking_ids],
                'invoice_ids': [(4, record.invoice_id.id)] if record.invoice_id else [],
                'note': record.note
            }

        _logger.info("Migrating documents data...")

        Document = self.env['stock.picking.package.preparation']
        DeliveryNote = self.env['stock.delivery.note']

        documents = Document.search([], order='id ASC')
        for document in documents:
            DeliveryNote.create(vals_getter(document))

        _logger.info("Documents data successfully migrated.")

    @environment(parser_args_method=_parse_args)
    def run(self, args, env):
        try:
            self.initialize(args, env)
            self.check_database_integrity()
            self.migrate_carriage_conditions()
            self.migrate_goods_descriptions()
            self.migrate_transportation_reasons()
            self.migrate_transportation_methods()
            self.migrate_document_types()
            self.migrate_documents()

            _logger.info("Execution completed successfully! Committing...")

            env.cr.commit()

        except:
            _logger.exception("Something went wrong during command execution. Rolling back...")

            env.cr.rollback()

        finally:
            env.cr.close()
