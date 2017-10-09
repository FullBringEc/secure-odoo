# -*- coding: utf-8 -*-
# © 2017 Savoir-faire Linux
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    'name': 'Action Access Control List',
    'version': '10.0.1.0.0',
    'author': 'Savoir-faire Linux',
    'maintainer': 'Savoir-faire Linux',
    'website': 'http://www.savoirfairelinux.com',
    'license': 'LGPL-3',
    'category': 'Security',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/ir_action_access.xml',
        'views/ir_protected_action.xml',
        'views/menu.xml',
    ],
    'application': False,
    'installable': True,
}
