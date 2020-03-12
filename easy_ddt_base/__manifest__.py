# -*- coding: utf-8 -*-
# Copyright (C) 2018-Today:
#     Dinamiche Aziendali srl (<http://www.dinamicheaziendali.it/>)
# @author: Gianmarco Conte (gconte@dinamicheaziendali.it)
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).


{
    'name': 'Easy DDT Base',
    'version': '10.0.1.0.0',
    'category': 'Localization/Italy',
    'summary': 'Documento di Trasporto',
    'author': 'Gianmarco Conte, Odoo Community Association (OCA),',
    'website': 'http://www.dinamicheaziendali.it/',
    'license': 'AGPL-3',
    'depends': [
        'base',
        'sale',
        'l10n_it',
        'mail',
        'report',
    ],
    'data': [
        'security/ddt_group.xml',
        'security/ir.model.access.csv',
        'data/ddt_data.xml',
        'views/easy_ddt_base.xml',
        'views/easy_ddt_add.xml',
        'views/report_easy_ddt.xml',
    ],
    'installable': True,
}
