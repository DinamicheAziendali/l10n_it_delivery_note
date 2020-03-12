# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017
#    Marco Calcagni (<mcalcagni@dinamicheaziendali.it>)
#    Gianmarco Conte (<gconte@dinamicheaziendali.it>)
#
#    same parts :
#    Copyright (C) 2015 Apulia Software s.r.l. (http://www.apuliasoftware.it)
#    @author Francesco Apruzzese <f.apruzzese@apuliasoftware.it>
#
#    All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
#

{
    'name': 'Easy DDT',
    'version': '10.0.1.0.0',
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
