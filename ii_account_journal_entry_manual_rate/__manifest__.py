# -*- coding: utf-8 -*-
#######################################################################
#     Copyright (C) 2023 IATL IntelliSoft Business Solutions Co. Ltd. #
#     (<https://www.iatl-intellisoft.com>) all rights reserved.       #
#######################################################################

{
    'name': 'Accounting Journal Entries - Manual Currency Rate',
    'author': 'IATL-IntelliSoft',
    'website': 'https://www.iatl-intellisoft.com',
    'summary': 'Allows to change currency of journal entries',
    'description': """ """,
    'category': 'Accounting',
    'version': '16.0.1.0',
    'depends': ['account'],
    'data': [
#         'data/account_currency_data.xml',
        'views/account_move.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3'
}
