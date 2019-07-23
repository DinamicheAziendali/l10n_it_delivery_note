# Copyright 2014-2019 Dinamiche Aziendali srl (http://www.dinamicheaziendali.it/)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Gianmarco Conte <gconte@dinamicheaziendali.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# noinspection PyStatementEffect
{
    'name': "Easy DDT",
    'summary': "Documento di Trasporto",

    'author': "Marco Calcagni, Gianmarco Conte, Link IT Srl",
    'website': "http://www.dinamicheaziendali.it/",

    'version': '12.0.2.0.0',
    'category': "Localization",

    'depends': [
        'delivery',
        'mail',
        'sale_stock',
        'stock_account'
    ],
    'external_dependencies': {
        'python': ['openupgradelib']
    },

    'data': [
        'data/delivery_note_data.xml',
        'report/report_easy_ddt.xml',

        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'security/res_groups.xml',

        'views/account_invoice.xml',
        'views/assets.xml',
        'views/res_config_settings.xml',
        'views/res_partner.xml',
        'views/stock_delivery_note.xml',
        'views/stock_picking.xml',

        'wizard/delivery_note_create.xml',
        'wizard/delivery_note_select.xml'
    ]
}
