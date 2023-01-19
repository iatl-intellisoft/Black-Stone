# -*- coding:utf-8 -*-
#######################################################################
#    IntelliSoft Software & ODOOTECH FZE                              #
#    Copyright (C) 2018 (<http://intellisoft.sd>) all rights reserved.#
#######################################################################
{
    'name': 'Post Dated Checks with Payment and Receipt Vouchers (A/E)',
    'version': '16.0.1.0',
    'price': 25,
    'author': 'IntelliSoft Software/ODOOTECH FZE (UAE)',
    'website': 'www.intellisoft.sd',
    'currency': 'EUR',
    'license': 'Other proprietary',
    'category': 'Account',
    'support': 'mustafa@intellisoft.sd',
    'summary': 'This module provides basic management of post dated checks as well as printnig of '
               'payment and receipt vouchers.',
    'description': """
	This module prints customer and vendor payment vouchers from payments.
	Print customer payment receipts.
	Print vendor payment receipts.
	Customer payment receipts.
	Vendor payment receipts.
	Payment receipts.
	Payment vouchers.
	Customer payment vouchers.
	Vendor payment vouchers.
	This module customer and vendor payment receipt.
	This module customer and vendor payment receipts.
	Print customer payment receipt.
	Print vendor payment receipt.
	Customer payment receipt.
	Vendor payment receipt.
	Payment receipt.
	Payment voucher.
	Customer payment voucher.
	Vendor payment voucher.
	Payment voucher.
	Voucher payment.
	Receipt voucher.
	Voucher Receipts.
	Post dated checks.
	Post dated cheques.
	Cheque management.
	Check management.
	Management checks.
	Management cheques.
    """,
    'depends': ['account', 'account_check_printing', 'sale'],
    'data': [
        'data/load.xml',
        'data/pdc_scheduled_actions.xml',
        'security/ir.model.access.csv',
        'reports/reports_registration.xml',
        'reports/report_voucher_receipt.xml',
        'reports/report_voucher_payment.xml',
        'reports/report_batch_pdc_voucher_receipt.xml',
        'reports/report_check.xml',
        'views/settings_view.xml',
        'views/account_view.xml',
        'views/account_payment_view.xml',
        'views/batch_pdc_view.xml',
    ],
    "images": ['static/description/banner.png'],
    'installable': True,
    'auto_install': False,
}
