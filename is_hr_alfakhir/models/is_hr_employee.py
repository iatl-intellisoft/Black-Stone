from odoo import api, fields, models, _
import datetime
from odoo.exceptions import UserError


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    contract_id = fields.Many2one(readonly=True)
#    hiring_date = fields.Date(readonly=True)


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    @api.model
    def _compute_loans(self):
        for x in self:
            count = 0
            loan_remain_amount = 0.00
            loan_ids = x.env['hr.loan'].search([('employee_id', '=', x.id)])
            for loan in loan_ids:
                loan_remain_amount += loan.balance_amount
                count += 1
            x.loan_count = count
            x.loan_amount = loan_remain_amount

    is_manager = fields.Boolean(string="Is Manager", groups="hr.group_hr_user")
    loan_amount = fields.Float(string="loan Amount", compute='_compute_loans', groups="hr.group_hr_user")
    loan_count = fields.Integer(string="Loan Count", compute='_compute_loans', groups="hr.group_hr_user")
    # hiring_date = fields.Date(string="Date of Joining", groups="hr.group_hr_user")
    # quit_date = fields.Date(string="Date of Quit", groups="hr.group_hr_user")
    # leave_balance = fields.Float(string='Leave Balance', compute='_compute_leave_balance', groups="hr.group_hr_user")
    # remaining_leaves = fields.Float(compute='_compute_remaining_leaves', string='Leave Balance', store=True,
    #                                 inverse='_inverse_remaining_leaves',
    #                                 help='Total number of legal leaves allocated to this employee, change this value to create allocation/leave request.'
    #                                      'Total based on all the leave types without overriding limit.')
    # annual_leave = fields.Selection([('20', '20 days'), ('25', '25 days'),('30', '30 days')])
    # annual_leave = fields.Float(string="Annual Leave", groups="hr.group_hr_user")
    blood = fields.Selection([('o1', 'O+'), ('o2', 'O-'), ('a1', 'A+'),('a2', 'A-'),('b1', 'B+'),('b2', 'B-'),
                              ('ab1', 'AB+'), ('ab2', 'AB-')], groups="hr.group_hr_user")
    mother_name = fields.Char(string='Mother Name', groups="hr.group_hr_user")
    code = fields.Char(string='Employee Code', groups="hr.group_hr_user")
    # remaining_leaves_date = fields.Date(string='Remaining Leaves Date')
    national_service_from = fields.Date(string='Date From', groups="hr.group_hr_user")
    national_service_to = fields.Date(string='Date To', groups="hr.group_hr_user")
    graduation_year = fields.Date(string='Graduation Year', groups="hr.group_hr_user")
    signature = fields.Binary(string='Signature', groups="hr.group_hr_user")
    year_experience = fields.Integer(string='Years of Experience', groups="hr.group_hr_user")
    month_experience = fields.Integer(string='Months of Experience', groups="hr.group_hr_user")
    age_in_years = fields.Integer(string='Age In Years', compute='_calculate_age', groups="hr.group_hr_user")
    family_member = fields.Integer(string='No Of Family Members', groups="hr.group_hr_user")
    edu_level_id = fields.Many2one('educational.level', string='Degree', groups="hr.group_hr_user")
    edu_section_id = fields.Many2one('education.section', string='Section',
                                     domain="[('education_level_id', '=', edu_level_id)]", groups="hr.group_hr_user")
    age = fields.Char(compute='_calculate_age', string='Age', groups="hr.group_hr_user")
    loan_id = fields.Many2one('hr.loan')

    # @api.depends('remaining_leaves')
    # def _compute_leave_balance(self):
    #     for leave in self:
    #         leave.leave_balance = 0
    #         if leave.remaining_leaves:
    #             remaining_leaves = leave.remaining_leaves
    #             leave.leave_balance = remaining_leaves

    from datetime import datetime

    @api.depends('birthday')
    def _calculate_age(self):
        str_now = datetime.datetime.now().date()
        age = ''
        employee_years = 0
        for employee in self:
            if employee.birthday:
                date_start = datetime.datetime.strptime(str(employee.birthday), '%Y-%m-%d').date()
                total_days = (str_now - date_start).days
                employee_years = int(total_days / 365)
                remaining_days = total_days - 365 * employee_years
                employee_months = int(12 * remaining_days / 365)
                employee_days = int(0.5 + remaining_days - 365 * employee_months / 12)
                age = str(employee_years) + ' Year(s) ' + str(employee_months) + ' Month(s) ' + str(
                    employee_days) + ' day(s)'
                # raise UserError(_(total_days))
            employee.age = age
            employee.age_in_years = employee_years

    # @api.depends('contract_id.legal_leave', 'hiring_date')
    # def employee_legal_leave(self):
    #     for rec in self:
    #         if rec.contract_id:
    #             legal_leave = rec.contract_id.legal_leave
    #             remaining_leaves = rec.remaining_leaves
    #             old_leave = rec.leave_balance
    #             hiring_date = rec.hiring_date
    #             if not hiring_date:
    #                 raise UserError(_('Please Add employee Hiring date!'))
    #             if hiring_date:
    #                 hiring_date = rec.hiring_date
    #                 print hiring_date
    #             date_now = fields.Date.today()
    #             today_date = datetime.datetime.strptime(date_now, '%Y-%m-%d')
    #             hiring_date = datetime.datetime.strptime(hiring_date, '%Y-%m-%d')
    #             employement_period = (today_date - hiring_date).days
    #             print employement_period
    #             print old_leave
    #             if legal_leave == '20':
    #                 if employement_period < 365.25:
    #                     rec.leave_balance = remaining_leaves - old_leave + 20
    #                     print rec.leave_balance
    #                 else:
    #                     rec.leave_balance = legal_leave
    #                     print "++++++++++++++++++++++++++++"
    #                     print rec.leave_balance
    #                 rec.annual_leave = 20
    #                 rec.remaining_leaves_date = date_now
    #             if legal_leave == '25':
    #                 if employement_period < 365.25:
    #                     rec.leave_balance = remaining_leaves - old_leave + 25
    #                     print "++++++++++++++++++++++++++++"
    #                     print remaining_leaves - old_leave + 25
    #                 else:
    #                     rec.leave_balance = legal_leave
    #                     print "++++++++++++++++++++++++++++"
    #                     print rec.leave_balance
    #                 rec.annual_leave = 25
    #
    #                 # self.remaining_leaves = remaining_leaves + 25
    #                 rec.remaining_leaves_date = date_now
    #             if legal_leave == '30':
    #                 if employement_period < 365.25:
    #                     print old_leave
    #                     rec.leave_balance = remaining_leaves - old_leave + 30
    #                     print "++++++++++++++++++++++++++++"
    #                     print rec.leave_balance
    #                 else:
    #                     print "++++++++++++++++++++++++++++"
    #                     print rec.leave_balance
    #                     rec.leave_balance = legal_leave
    #                 # self.remaining_leaves = remaining_leaves + 30
    #                 rec.annual_leave = 30
    #                 rec.remaining_leaves_date = date_now


class EduactionSection(models.Model):
    _name = 'education.section'
    name = fields.Char(string='Section')
    education_level_id = fields.Many2one('educational.level',string='Level')


class EducationalLevel(models.Model):
    _name = 'educational.level'
    name = fields.Char(string='Educational Level')
    edu_section_ids = fields.One2many('education.section','education_level_id', string='Section')


class smtDepartment(models.Model):
    _inherit = 'hr.department'
    analytic_debit_account_id = fields.Many2one('account.analytic.account', string="Department Debit Analytic Account")
