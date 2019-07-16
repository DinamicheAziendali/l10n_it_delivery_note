import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)

SELECT_DELIVERY_NOTES_QUERY = """
    SELECT
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
        "p"."gross_weight"

    FROM "stock_picking" AS "p"
        INNER JOIN "stock_picking_type" AS "t" ON ("p"."picking_type_id" = "t"."id")

    WHERE
        "p"."state" = 'done' AND
        "t"."code" != 'incoming'

    ORDER BY "p"."id";
"""


def migrate(cr, version):
    if not version:
        _logger.warning("Non è presente alcuna versione precedente del modulo. Skippo la migration.")

        return

    env = api.Environment(cr, SUPERUSER_ID, {})

    _logger.info("Adatto la struttura del database al nuovo codice...")

    cr.execute(SELECT_DELIVERY_NOTES_QUERY)
    results = cr.fetchall()

    import pdb; pdb.set_trace()

    _logger.info("Ho terminato l'esecuzione della migration del modulo. Esco.")
