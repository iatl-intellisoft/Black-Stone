{
    'name': 'Hr Alfakhir Customization Module',
    'author': 'IntelliSoft Software',
    'website': 'http://www.intellisoft.sd',
    'category': 'Human Resources',
    'description': """alfakhir hr customization """,

    'depends': ['base', 'hr', 'hr_payroll', 'hr_payroll_account', 'hr_attendance', 'hr_recruitment', 'account', 'hr_holidays'],
    'data': [
        # security
        'security/alfakhir_security.xml',
        'security/ir.model.access.csv',

        # date
        'data/hr_loan_sequence.xml',
        'data/payroll_rule_data.xml',
        'data/is_alfakhir_hr_recruitment_data.xml',
        # 'data/hr_holiday_data.xml',

        # Views
        'wizard/delay_loan_view.xml',
        'views/is_hr_alfakhir_loan_view.xml',
        'views/is_hr_alfakhir_view.xml',
        'views/is_hr_alfakhir_recruitment.xml',
        'views/is_hr_alfakhir_overtime_view.xml',
        'views/is_hr_alfakhir_trip.xml',
        # 'views/buy_leave_view.xml',
        'views/is_hr_leave_views.xml',
        # 'views/end_service_view.xml',
        'views/sale_time_off_view.xml',
        
        'views/is_hr_alfakhir_payslip_view.xml',
        'views/is_alfakhir_penalties.xml',

        'wizard/lta_transport_batch_view.xml',
        'views/is_alfakhir_lta_transport_view.xml',
        'views/is_alfakhir_employee_view.xml',

        # reports
        'report/alfakhir_hr_report.xml',
        # 'report/is_smt_payslip.xml',
        'report/alfakhir_hr_trip_report.xml',
        'report/hr_contracter_report.xml',
        'report/hr_allowances_report.xml',

        # wizard
        'wizard/pay_sheet_view.xml',
        'wizard/wizard_overtime_view.xml',
        'wizard/wizard_lta_transport_view.xml',
        'wizard/pay_sheet_view_custom.xml',

    ],
    'application': True,
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
