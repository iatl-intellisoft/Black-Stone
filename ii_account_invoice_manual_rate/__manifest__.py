# -*- coding: utf-8 -*-
#######################################################################
#     Copyright (C) 2023 IATL IntelliSoft Business Solutions Co. Ltd. #
#     (<https://www.iatl-intellisoft.com>) all rights reserved.       #
#######################################################################

{
    'name': 'Accounting Invoice - Manual Currency Rate',
    'author': 'IATL-IntelliSoft',
    'website': 'https://www.iatl-intellisoft.com',
    'summary': 'Allows to change currency of invoice',
    'description': """ """,
    'category': 'Accounting',
    'version': '16.0.1.0',
    'depends': ['ii_account_journal_entry_manual_rate'],
    'data': [
        'views/account_invoice.xml',
    ],
    "installable": True,
    'application': False,
    'license': 'LGPL-3'
}
