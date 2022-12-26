# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.translate import _
from odoo.tools import float_compare
from datetime import datetime

class hrLeaveAllocationInherit(models.Model):
    _inherit = 'hr.leave.allocation'

    _sql_constraints = [
        ('type_value',
         "CHECK( (holiday_type='employee' AND (employee_id IS NOT NULL OR multi_employee IS TRUE)) or "
         "(holiday_type='category' AND category_id IS NOT NULL) or "
         "(holiday_type='department' AND department_id IS NOT NULL) or "
         "(holiday_type='company' AND mode_company_id IS NOT NULL))",
         "The employee, department, company or employee category of this request is missing. Please make sure that your user login is linked to an employee."),

    ]

        # ('duration_check',
        #  "CHECK( ( number_of_days <= 0 AND allocation_type='regular') or (allocation_type != 'regular'))",
        #  "The duration must be greater than 0.")

    @api.depends('employee_id', 'holiday_status_id', 'taken_leave_ids.number_of_days', 'taken_leave_ids.state')
    def _compute_leaves(self):
        for allocation in self:
            allocation.max_leaves = allocation.number_of_hours_display if allocation.type_request_unit == 'hour' else allocation.number_of_days
            allocation.leaves_taken = sum(taken_leave.number_of_hours_display if taken_leave.leave_type_request_unit == 'hour' else taken_leave.number_of_days\
                for taken_leave in allocation.taken_leave_ids\
                if taken_leave.state == 'validate')

            if allocation.employee_id:
                sell_times = self.env['sell.time.off'].search([('employee_id','=',allocation.employee_id.id),
                    ('request_date','>=',allocation.date_from),('request_date','<=',allocation.date_to),('state','=','approve')])
                days = 0
                if sell_times:
                    for time in sell_times:
                        days += time.days_to_sell
                allocation.leaves_taken = allocation.leaves_taken + days


class HolidaysType(models.Model):
    _inherit = "hr.leave.type"

    is_annual = fields.Boolean(default=False,string="Is Annual Time Off ")

class HolidaysRequest(models.Model):
    _inherit = "hr.leave"
    _description = "Leave"

  #   state = fields.Selection([
  #       ('draft', 'To Submit'),
  #       ('cancel', 'Cancelled'),
  #       ('confirm', 'HR Approved'),
  #       ('admin_approve', 'Finance Approved'),
  #       ('gm_approve', 'GM Approved'),
  #       ('paid', 'Leave Cash Paid'),
  #       ('refuse', 'Refused'),
  # ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='draft',
  #       help="The status is set to 'To Submit', when a leave request is created." +
  #       "\nThe status is 'To Approve', when leave request is confirmed by user." +
  #       "\nThe status is 'Refused', when leave request is refused by manager." +
  #       "\nThe status is 'Approved', when leave request is approved by manager.")
    cash_alternative = fields.Float(string="Cash Alternative")
    contract_id = fields.Many2one('hr.employee', string='contract')
    leave_paid_check = fields.Boolean(string='Is Paid Leave', default=False)
    journal_id = fields.Many2one('account.journal', string="Journal")
    employee_account = fields.Many2one('account.account', string="Employee Account")
    leave_account = fields.Many2one('account.account', string="Cash Alternative Account")
    credit_account = fields.Many2one('account.account', string="Bank/Cash Account")
    move_id = fields.Many2one('account.move', string="Journal Entry", readonly=True)
    move_id2 = fields.Many2one('account.move', string="Journal Entry 2", readonly=True)


    @api.onchange('holiday_status_id')
    def check_annual(self):
        if self.holiday_status_id:
            if self.holiday_status_id.is_annual:
                self.leave_paid_check = True
            else:
                self.leave_paid_check = False

    # @api.onchange('employee_id')
    # def get_employee_account(self):
    #     if self.employee_id or len(self.employee_ids) == 1:
    #         self.employee_account = self.employee_id.

    # def action_hr_approve(self):
    #     self.state = 'confirm'

    # def action_admin_approve(self):
    #     self.state = 'admin_approve'

    # def action_gm_approve(self):
    #     self.cash_alternative_pay()
    #     self.state = 'gm_approve'

    @api.onchange('employee_id','number_of_days')
    @api.depends('number_of_days')
    def cash_alternative_leave(self):
        for rec in self:
            rec.cash_alternative = 0.0
            if rec.leave_paid_check:
                emps = rec.env['hr.employee'].search([('contract_id', '=', rec.employee_id.contract_id.id)])
                for emp in emps:
                    wage = emp.contract_id.wage
                    total_leave = wage/30
                    rec.cash_alternative = total_leave * rec.number_of_days

    def cash_alternative_pay(self):
        if not self.employee_account or not self.leave_account or not self.journal_id:
            raise ValidationError(_("You must enter debit account & credit account and journal to approve "))
        can_close = False
        loan_obj = self.env['hr.leave']
        move_obj = self.env['account.move']
        move_line_obj = self.env['account.move.line']
        currency_obj = self.env['res.currency']
        created_move_ids = []
        loan_ids = []
        for leave in self:
            line_ids = line_ids2 = []
            debit_sum = debit_sum2 = 0.0
            credit_sum = credit_sum2 = 0.0
            amount = leave.cash_alternative
            leave_name = 'Leave Cash Payment for' + leave.employee_id.name
            reference = leave.name
            journal_id = leave.journal_id.id
            date = leave.request_date_to

            move_dict = {
                'narration': leave_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': date,
            }
            debit_line = (0, 0, {
                'name': leave_name,
                'partner_id': False,
                'account_id': leave.employee_account.id,
                'journal_id': journal_id,
                'date': date,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
                'analytic_account_id': False,
                'tax_line_id': 0.0,
            })
            line_ids.append(debit_line)
            debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
            credit_line = (0, 0, {
                'name': leave_name,
                'partner_id': False,
                'account_id': leave.leave_account.id,
                'journal_id': journal_id,
                'date': date,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
                'analytic_account_id': False,
                'tax_line_id': 0.0,
            })
            line_ids.append(credit_line)
            credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
            move_dict['line_ids'] = line_ids
            move = self.env['account.move'].create(move_dict)
            leave.write({'move_id': move.id})
            move.post()

            move_dict2 = {
                'narration': leave_name,
                'ref': reference,
                'journal_id': journal_id,
                'date': date,
            }
            debit_line2 = (0, 0, {
                'name': leave_name,
                'partner_id': False,
                'account_id': leave.leave_account.id,
                'journal_id': journal_id,
                'date': date,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
                'analytic_account_id': False,
                'tax_line_id': 0.0,
            })
            line_ids2.append(debit_line2)
            debit_sum2 += debit_line2[2]['debit'] - debit_line2[2]['credit']
            credit_line2 = (0, 0, {
                'name': leave_name,
                'partner_id': False,
                'account_id': leave.credit_account.id,
                'journal_id': journal_id,
                'date': date,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
                'analytic_account_id': False,
                'tax_line_id': 0.0,
            })
            line_ids2.append(credit_line2)
            credit_sum2 += credit_line[2]['credit'] - credit_line2[2]['debit']
            move_dict2['line_ids'] = line_ids2
            move2 = self.env['account.move'].create(move_dict2)
            leave.write({'move_id': move2.id})
            move2.post()
            self.state = 'paid'


    def action_approve(self):
        # if validation_type == 'both': this method is the first approval approval
        # if validation_type != 'both': this method calls action_validate() below

        if self.leave_paid_check:
            if not (self.move_id and self.move_id2):
                raise ValidationError(_('You must pay Time Off alternative first!'))

        if any(holiday.state != 'confirm' for holiday in self):
            raise UserError(_('Time off request must be confirmed ("To Approve") in order to approve it.'))

        current_employee = self.env.user.employee_id
        self.filtered(lambda hol: hol.validation_type == 'both').write({'state': 'validate1', 'first_approver_id': current_employee.id})


        # Post a second message, more verbose than the tracking message
        for holiday in self.filtered(lambda holiday: holiday.employee_id.user_id):
            holiday.message_post(
                body=_(
                    'Your %(leave_type)s planned on %(date)s has been accepted',
                    leave_type=holiday.holiday_status_id.display_name,
                    date=holiday.date_from
                ),
                partner_ids=holiday.employee_id.user_id.partner_id.ids)

        self.filtered(lambda hol: not hol.validation_type == 'both').action_validate()
        if not self.env.context.get('leave_fast_create'):
            self.activity_update()
        return True
