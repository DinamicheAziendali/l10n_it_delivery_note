# Copyright (c) 2019, Link IT Europe Srl
# @author: Matteo Bilotta <mbilotta@linkeurope.it>

import logging

from collections import OrderedDict
from datetime import datetime, time, timedelta

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

DEFAULT_TYPE_ID = None


def init(env):
    global DEFAULT_TYPE_ID

    StockDeliveryNoteType = env['stock.delivery.note.type']

    default_type_id = StockDeliveryNoteType.search([], limit=1)
    DEFAULT_TYPE_ID = default_type_id.id


SELECT_DELIVERY_NOTES_QUERY = """
    SELECT
        "p"."id",
        "p"."ddt_number",
        "p"."ddt_type_id",
        "p"."ddt_date",
        "p"."ddt_notes",
        "p"."carriage_condition_id",
        "p"."goods_description_id",
        "p"."transportation_reason_id",
        "p"."transportation_method_id",
        "p"."date_transport_ddt",
        "p"."time_transport_ddt",
        "p"."volume",
        "p"."parcels",
        "p"."gross_weight",
        "p"."weight",
        "p"."partner_id",
        "p"."partner_shipping_id"

    FROM "stock_picking" AS "p"
        INNER JOIN "stock_picking_type" AS "t" ON ("p"."picking_type_id" = "t"."id")

    WHERE
        "p"."state" = 'done' AND
        "t"."code" != 'incoming'

    ORDER BY "p"."id";
"""


def by_index(index):
    def funct(row):
        return row[index]

    return funct


def compose_date():
    def funct(row):
        date = row[9]

        if date:
            hours = timedelta(hours=row[10])

            return datetime.combine(date, time()) + hours

    return funct


def guess_state():
    def funct(row):
        if row[1]:
            return 'confirm'

        return 'draft'

    return funct


def recover_shipping_partner():
    def funct(row):
        if row[16]:
            return row[16]

        return row[15]

    return funct


def recover_type():
    def funct(row):
        if row[2]:
            return row[2]

        return DEFAULT_TYPE_ID

    return funct


ENTRY_MAPPING = {
    'name': by_index(1),
    'state': guess_state(),
    'type_id': recover_type(),
    'date': by_index(3),
    'note': by_index(4),
    'transport_condition_id': by_index(5),
    'goods_appearance_id': by_index(6),
    'transport_reason_id': by_index(7),
    'transport_method_id': by_index(8),
    'transport_datetime': compose_date(),
    'volume': by_index(11),
    'parcels': by_index(12),
    'gross_weight': by_index(13),
    'net_weight': by_index(14),
    'partner_id': by_index(15),
    'partner_shipping_id': recover_shipping_partner()
}


def compose_entry(row):
    entry = {}

    for key, funct in ENTRY_MAPPING.items():
        value = funct(row)

        if value:
            entry[key] = value

    return entry


def parse_rows(rows):
    entries = OrderedDict()

    for row in rows:
        entries[row[0]] = compose_entry(row)

    return entries


def recover_legacy_entries(cr):
    cr.execute(SELECT_DELIVERY_NOTES_QUERY)
    rows = cr.fetchall()

    return parse_rows(rows)


def migrate(cr, version):
    if not version:
        _logger.warning("Non è presente alcuna versione precedente del modulo. Skippo la migration.")

        return

    env = api.Environment(cr, SUPERUSER_ID, {})

    StockPicking = env['stock.picking']
    StockDeliveryNote = env['stock.delivery.note'].with_context(from_migration=True)

    _logger.info("Inizializzo i dati di default per la migration...")
    init(env)

    _logger.info("Recupero i dati legacy con cui ricreare i nuovi dati...")
    entries = recover_legacy_entries(env.cr)

    _logger.info("Scrivo i dati e creo le relazioni tra modelli...")
    for id, entry in entries.items():
        picking = StockPicking.browse(id)
        delivery_note = StockDeliveryNote.create(entry)

        picking.write({'delivery_note_id': delivery_note.id})

    _logger.info("Ho terminato l'esecuzione della migration del modulo. Esco.")
