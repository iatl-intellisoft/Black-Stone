# -*- coding: utf-8 -*-
#######################################################################
#     Copyright (C) 2023 IATL IntelliSoft Business Solutions Co. Ltd. #
#     (<https://www.iatl-intellisoft.com>) all rights reserved.       #
#######################################################################

{
    'name': "Secondary Currency",
    'author': 'IATL-IntelliSoft',
    'website': 'https://www.iatl-intellisoft.com',
    'summary': """""",
    'description': """Enables the monitoring and reporting of all financial processes in a secondary currency.""",
    'category': 'Accounting',
    'version': '16.0.0.1',
    'depends': ['account_accountant', 'account_reports'],
    'data': [
        'views/ii_accounting_view.xml',
        'views/res_config_settings_view.xml',
        'report/second_currency_balance_sheet.xml',
        'report/second_currency_general_ledger.xml',
        'report/second_currency_profit_and_loss.xml',
        'report/second_currency_trial_balance.xml',
        'report/report_registration.xml',
        'report/menuitems.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
