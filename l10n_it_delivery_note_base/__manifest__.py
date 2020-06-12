# Copyright 2014-2019 Dinamiche Aziendali srl (http://www.dinamicheaziendali.it/)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Gianmarco Conte <gconte@dinamicheaziendali.it>
# Copyright (c) 2019, Link IT Europe Srl
# @author: Matteo Bilotta <mbilotta@linkeurope.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# noinspection PyStatementEffect
{
    'name': "ITA - Documento di Trasporto Base",
    'summary': "Crea, gestisci e fattura i DdT partendo dalle Consegne",

    'author': "Marco Calcagni, Gianmarco Conte, Link IT Europe Srl",
    'website': "http://www.dinamicheaziendali.it/",

    'version': '12.0.1.0.0',
    'category': "Localization",

    'depends': ['mail'],

    'data': [
        'data/delivery_note_data.xml',
        # 'report/report_delivery_note.xml',

        'views/stock_delivery_note_type.xml',
        'views/stock_picking_goods_appearance.xml',
        'views/stock_picking_transport_condition.xml',
        'views/stock_picking_transport_method.xml',
        'views/stock_picking_transport_reason.xml'
    ]
}
