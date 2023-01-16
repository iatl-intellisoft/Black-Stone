{
    'name': 'Black Loan Customization Module',
    'author': 'IntelliSoft Software',
    'website': 'http://www.intellisoft.sd',
    'category': 'Human Resources',
    'description': """alfakhir hr customization """,

    'depends': ['base', 'hr', 'hr_payroll', 'hr_payroll_account', 'hr_attendance', 'hr_recruitment', 'account', 'hr_holidays','is_accounting_approval_15'],
    'data': [
        # security
        'security/black_security.xml',
        'security/ir.model.access.csv',

        # date
        'data/hr_loan_sequence.xml',
        # 'data/payroll_rule_data.xml',
      
        # Views
        'views/is_black_loan_view.xml',
        'wizard/delay_loan_view.xml',


    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
