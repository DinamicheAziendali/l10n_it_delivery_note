# Copyright (c) 2019, Link IT Europe Srl (http://www.linkgroup.it/)
# @author: Matteo Bilotta <mbilotta@linkgroup.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import argparse
import functools
import logging
import odoo

from odoo import SUPERUSER_ID
from odoo.cli import Command
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


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
    _goods_appearances = None
    _transportation_reasons = None
    _transportation_methods = None
    _document_types = None

    env = None

    def __init__(self):
        self.__is_debugging = False

        self._carriage_conditions = {}
        self._goods_appearances = {}
        self._transportation_reasons = {}
        self._transportation_methods = {}
        self._document_types = {}

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
        CarriageCondition = self.env['stock.picking.carriage_condition']
        TransportCondition = self.env['stock.picking.transport.condition']

        pf = self._map_ref(self._carriage_conditions, 'carriage_condition_PF', 'transport_condition_PF')
        pa = self._map_ref(self._carriage_conditions, 'carriage_condition_PA', 'transport_condition_PA')
        paf = self._map_ref(self._carriage_conditions, 'carriage_condition_PAF', 'transport_condition_PAF')

        records = CarriageCondition.search([('id', 'not in', [pf.id, pa.id, paf.id])], order='id ASC')

        self._map_create(self._carriage_conditions, records, TransportCondition)

    def migrate_goods_descriptions(self):
        GoodsDescription = self.env['stock.picking.goods_description']
        GoodsAppearance = self.env['stock.picking.goods.appearance']

        car = self._map_ref(self._goods_appearances, 'goods_description_CAR', 'goods_appearance_CAR')
        ban = self._map_ref(self._goods_appearances, 'goods_description_BAN', 'goods_appearance_BAN')
        sfu = self._map_ref(self._goods_appearances, 'goods_description_SFU', 'goods_appearance_SFU')
        cba = self._map_ref(self._goods_appearances, 'goods_description_CBA', 'goods_appearance_CBA')

        records = GoodsDescription.search([('id', 'not in', [car.id, ban.id, sfu.id, cba.id])], order='id ASC')

        self._map_create(self._goods_appearances, records, GoodsAppearance)

    def migrate_transportation_reasons(self):
        TransportationReason = self.env['stock.picking.transportation_reason']
        TransportReason = self.env['stock.picking.transport.reason']

        ven = self._map_ref(self._transportation_reasons, 'transportation_reason_VEN', 'transport_reason_VEN')
        vis = self._map_ref(self._transportation_reasons, 'transportation_reason_VIS', 'transport_reason_VIS')
        res = self._map_ref(self._transportation_reasons, 'transportation_reason_RES', 'transport_reason_RES')

        records = TransportationReason.search([('id', 'not in', [ven.id, vis.id, res.id])], order='id ASC')

        self._map_create(self._transportation_reasons, records, TransportReason)

    def migrate_transportation_methods(self):
        TransportationMethod = self.env['stock.picking.transportation_method']
        TransportMethod = self.env['stock.picking.transport.method']

        mit = self._map_ref(self._transportation_methods, 'transportation_method_MIT', 'transport_method_MIT')
        des = self._map_ref(self._transportation_methods, 'transportation_method_DES', 'transport_method_DES')
        cor = self._map_ref(self._transportation_methods, 'transportation_method_COR', 'transport_method_COR')

        records = TransportationMethod.search([('id', 'not in', [mit.id, des.id, cor.id])], order='id ASC')

        self._map_create(self._transportation_methods, records, TransportMethod)

    def migrate_document_types(self):
        DocumentType = self.env['stock.ddt.type']
        DeliveryNoteType = self.env['stock.delivery.note.type']

        type = self._map_ref(self._document_types, 'ddt_type_ddt', 'delivery_note_type_ddt')

        records = DocumentType.search([('id', 'not in', [type.id])], order='id ASC')

        self._map_create(self._document_types, records, DeliveryNoteType, lambda r: {

            'name': r.name,
            'sequence_id': r.sequence_id.id,
            #
            # FIXME: Una volta introdotti i campi con i valori di default,
            #         integrare questa importazione con tali informazioni.
            #
            # 'default_carriage_condition_id': [...],
            # 'default_goods_description_id': [...],
            # 'default_transportation_reason_id': [...],
            # 'default_transportation_method_id': [...],
            #
            'note': r.note
        })

        DocumentType = self.env['stock.ddt.type']
        DeliveryNoteType = self.env['stock.delivery.note.type']

        l10n_it_ddt_type = self.env.ref('l10n_it_ddt.ddt_type_ddt')
        easy_ddt_type = self.env.ref('easy_ddt.delivery_note_type_ddt')
        self._document_types[l10n_it_ddt_type] = easy_ddt_type

        old_types = DocumentType.search([('id', '!=', l10n_it_ddt_type.id)], order='id ASC')
        for old_type in old_types:
            new_type = DeliveryNoteType.create()

            self._document_types[old_type] = new_type


    def migrate_documents(self):
        import pdb; pdb.set_trace()

        Document = self.env['stock.picking.package.preparation']

        documents = Document.search([], order='id ASC')
        for document in documents:
            vals = {
                'partner_id': document.partner_id,
                'partner_shipping_id': document.partner_shipping_id,

            }

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
