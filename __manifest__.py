# -*- coding: utf-8 -*-
# Copyright 2014-2019 Dinamiche Aziendali srl (http://www.dinamicheaziendali.it/)
# @author: Marco Calcagni <mcalcagni@dinamicheaziendali.it>
# @author: Gianmarco Conte <gconte@dinamicheaziendali.it>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': 'Easy DDT',
    'version': '12.0.1.0.0',
    'category': 'Localization/Italy',
    'summary': 'Documento di Trasporto',
    'author': 'Marco Calcagni, Odoo Community Association (OCA),',
    'website': 'http://www.dinamicheaziendali.it/',
    'license': 'AGPL-3',
    'depends': [
        'delivery',
        'sale_stock',
        'stock_account',
        ],
    'data': [
        'security/ir.model.access.csv',
        'data/ddt_data.xml',
        'views/account.xml',
        'views/easy_ddt_add.xml',
        'views/easy_ddt.xml',
        'views/partner.xml',
        'views/report_easy_ddt.xml',
        ],
    'installable': True,
}
