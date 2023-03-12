# -*- coding: utf-8 -*-
#######################################################################
#     Copyright (C) 2023 IATL IntelliSoft Business Solutions Co. Ltd. #
#     (<https://www.iatl-intellisoft.com>) all rights reserved.       #
#######################################################################

{
    'name': 'Accounting Payment - Manual Currency Rate',
    'author': 'IATL-IntelliSoft',
    'website': 'https://www.iatl-intellisoft.com',
    'summary': 'Allows to change currency of payment',
    'description': """ """,
    'category': 'Accounting',
    'version': '16.0.1.0',
    'depends': ['ii_account_journal_entry_manual_rate'],
    'data': [
        'views/account_payment.xml',
        'views/account_register_payment.xml',
    ],
    "installable": True,
    'application': False,
    'license': 'LGPL-3'
}
