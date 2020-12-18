# Copyright (c) 2019, Openindustry.it Sas
# @author: Andrea Piovesana <andrea.m.piovesana@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# noinspection PyStatementEffect
{
    'name': 'ITA - Documento di trasporto - Collegamento con ordine di vendita',
    'summary': 'Crea collegamento tra i DDT e ordine di vendita',
    'author': 'Openindustry.it Sas, Odoo Community Association (OCA), DataBooz ltd',
    'website': "https://github.com/OCA/l10n-italy/tree/12.0/"
               "l10n_it_delivery_note_order_link",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'maintainers': ['As400it', 'andreampiovesana'],
    'category': 'Localization',
    'depends': [
        'sale_stock',
        'l10n_it_delivery_note',
    ],
    'data': [
        'views/sale_order.xml',
    ],
}
