import logging

_logger = logging.getLogger(__name__)

RENAME_TABLE_QUERY = """ALTER TABLE "%s" RENAME TO "%s";"""
TABLES_TO_RENAME = (
    ('stock_picking_carriage_condition', 'stock_picking_transport_condition'),
    ('stock_picking_goods_description', 'stock_picking_goods_appearance'),
    ('stock_picking_transportation_reason', 'stock_picking_transport_reason'),
    ('stock_picking_transportation_method', 'stock_picking_transport_method')
)

RENAME_FIELDS_QUERY = """ALTER TABLE "%s" RENAME COLUMN "%s" TO "%s";"""
FIELDS_TO_RENAME = (
    ('carriage_condition_id', 'transport_condition_id'),
    ('goods_description_id', 'goods_appearance_id'),
    ('transportation_reason_id', 'transport_reason_id'),
    ('transportation_method_id', 'transport_method_id')
)
TABLES_WITH_FIELDS_TO_RENAME = (
    'account_invoice',
    'res_partner',
    'stock_picking'
)

RENAME_MODEL_QUERY = """UPDATE "ir_model_data" SET "model" = %s WHERE "model" = %s;"""
MODELS_TO_RENAME = (
    ('stock.picking.carriage_condition', 'stock.picking.transport.condition'),
    ('stock.picking.goods_description', 'stock.picking.goods.appearance'),
    ('stock.picking.transportation_reason', 'stock.picking.transport.reason'),
    ('stock.picking.transportation_method', 'stock.picking.transport.method')
)

RENAME_EXT_ID_QUERY = """UPDATE "ir_model_data" SET "name" = %s WHERE "name" = %s;"""
EXT_ID_TO_RENAME = (
    ('carriage_condition_PF', 'transport_condition_PF'),
    ('carriage_condition_PA', 'transport_condition_PA'),
    ('carriage_condition_PAF', 'transport_condition_PAF'),
    ('goods_description_CAR', 'goods_appearance_CAR'),
    ('goods_description_BAN', 'goods_appearance_BAN'),
    ('goods_description_SFU', 'goods_appearance_SFU'),
    ('goods_description_CBA', 'goods_appearance_CBA'),
    ('transportation_reason_VEN', 'transport_reason_VEN'),
    ('transportation_reason_VIS', 'transport_reason_VIS'),
    ('transportation_reason_RES', 'transport_reason_RES'),
    ('transportation_method_MIT', 'transport_method_MIT'),
    ('transportation_method_DES', 'transport_method_DES'),
    ('transportation_method_COR', 'transport_method_COR')
)


def migrate(cr, version):
    if not version:
        _logger.warning("Non è presente alcuna versione precedente del modulo. Skippo la migration.")

        return

    _logger.info("Rinomino le tabelle dei vecchi modelli...")
    for old, new in TABLES_TO_RENAME:
        cr.execute(RENAME_TABLE_QUERY % (old, new))

    _logger.info("Rinomino i campi dei vecchi modelli...")
    for table in TABLES_WITH_FIELDS_TO_RENAME:
        for old, new in FIELDS_TO_RENAME:
            cr.execute(RENAME_FIELDS_QUERY % (table, old, new))

    _logger.info("Aggiorno i modelli dei vecchi dati...")
    for old, new in MODELS_TO_RENAME:
        cr.execute(RENAME_MODEL_QUERY, (new, old))

    _logger.info("Aggiorno gli external IDs dei vecchi dati...")
    for old, new in EXT_ID_TO_RENAME:
        cr.execute(RENAME_EXT_ID_QUERY, (new, old))

    _logger.info("Ho terminato l'esecuzione della migration del modulo. Esco.")
