import logging

from odoo import api, SUPERUSER_ID
from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)

TABLES_TO_RENAME = [
    ('stock_ddt_type', 'stock_delivery_note_type'),
    ('stock_picking_carriage_condition', 'stock_picking_transport_condition'),
    ('stock_picking_goods_description', 'stock_picking_goods_appearance'),
    ('stock_picking_transportation_reason', 'stock_picking_transport_reason'),
    ('stock_picking_transportation_method', 'stock_picking_transport_method')
]
MODELS_TO_RENAME = (
    ('stock.ddt.type', 'stock.delivery.note.type'),
    ('stock.picking.carriage_condition', 'stock.picking.transport.condition'),
    ('stock.picking.goods_description', 'stock.picking.goods.appearance'),
    ('stock.picking.transportation_reason', 'stock.picking.transport.reason'),
    ('stock.picking.transportation_method', 'stock.picking.transport.method')
)

FIELDS_TO_RENAME = [
    ('account.invoice', 'account_invoice', 'carriage_condition_id', 'transport_condition_id'),
    ('account.invoice', 'account_invoice', 'goods_description_id', 'goods_appearance_id'),
    ('account.invoice', 'account_invoice', 'transportation_reason_id', 'transport_reason_id'),
    ('account.invoice', 'account_invoice', 'transportation_method_id', 'transport_method_id'),

    ('res.partner', 'res_partner', 'carriage_condition_id', 'transport_condition_id'),
    ('res.partner', 'res_partner', 'goods_description_id', 'goods_appearance_id'),
    ('res.partner', 'res_partner', 'transportation_reason_id', 'transport_reason_id'),
    ('res.partner', 'res_partner', 'transportation_method_id', 'transport_method_id'),

    ('stock.picking', 'stock_picking', 'carriage_condition_id', 'transport_condition_id'),
    ('stock.picking', 'stock_picking', 'goods_description_id', 'goods_appearance_id'),
    ('stock.picking', 'stock_picking', 'transportation_reason_id', 'transport_reason_id'),
    ('stock.picking', 'stock_picking', 'transportation_method_id', 'transport_method_id')
]

XMLIDS_TO_RENAME = (
    ('easy_ddt.stock_ddt_type_comp_rule', 'easy_ddt.stock_delivery_note_type_company_rule'),

    ('easy_ddt.seq_ddt', 'easy_ddt.delivery_note_sequence_ddt'),
    ('easy_ddt.ddt_type_ddt', 'easy_ddt.delivery_note_type_ddt'),
    ('easy_ddt.carriage_condition_PF', 'easy_ddt.transport_condition_PF'),
    ('easy_ddt.carriage_condition_PA', 'easy_ddt.transport_condition_PA'),
    ('easy_ddt.carriage_condition_PAF', 'easy_ddt.transport_condition_PAF'),
    ('easy_ddt.goods_description_CAR', 'easy_ddt.goods_appearance_CAR'),
    ('easy_ddt.goods_description_BAN', 'easy_ddt.goods_appearance_BAN'),
    ('easy_ddt.goods_description_SFU', 'easy_ddt.goods_appearance_SFU'),
    ('easy_ddt.goods_description_CBA', 'easy_ddt.goods_appearance_CBA'),
    ('easy_ddt.transportation_reason_VEN', 'easy_ddt.transport_reason_VEN'),
    ('easy_ddt.transportation_reason_VIS', 'easy_ddt.transport_reason_VIS'),
    ('easy_ddt.transportation_reason_RES', 'easy_ddt.transport_reason_RES'),
    ('easy_ddt.transportation_method_MIT', 'easy_ddt.transport_method_MIT'),
    ('easy_ddt.transportation_method_DES', 'easy_ddt.transport_method_DES'),
    ('easy_ddt.transportation_method_COR', 'easy_ddt.transport_method_COR')
)


def _adjust_database_structure(env):
    _logger.info("Rinomino le tabelle dei vecchi modelli...")
    openupgrade.rename_tables(env.cr, TABLES_TO_RENAME)
    _logger.info("Aggiorno i modelli dei vecchi dati...")
    openupgrade.rename_models(env.cr, MODELS_TO_RENAME)

    _logger.info("Rinomino i campi dei vecchi modelli...")
    openupgrade.rename_fields(env, FIELDS_TO_RENAME)

    _logger.info("Aggiorno gli XML IDs dei vecchi dati...")
    openupgrade.rename_xmlids(env.cr, XMLIDS_TO_RENAME)


def migrate(cr, version):
    if not version:
        _logger.warning("Non è presente alcuna versione precedente del modulo. Skippo la migration.")

        return

    env = api.Environment(cr, SUPERUSER_ID, {})

    _logger.info("Adatto la struttura del database al nuovo codice...")
    _adjust_database_structure(env)

    _logger.info("Ho terminato l'esecuzione della migration del modulo. Esco.")
