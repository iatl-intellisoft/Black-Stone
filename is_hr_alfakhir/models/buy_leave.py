# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo import models, fields, api, exceptions, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError
import math


class BuyLeave(models.Model):
    _name = 'buy.leave'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    # _rec_name = 'employee_id'

    # def _default_employee(self):
    #     return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    # employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", default=_default_employee)
    # manager_id = fields.Many2one('res.users', string="Manager", required=False, )
    # remaining_leaves = fields.Float(string="Leave Balance",
    #                                 readonly=True,
    #                                 compute='calculate_buy_leave', store=True
    #                                 )
    # wage = fields.Float(string="Wage",
    #                     readonly=True,
    #                     compute='calculate_buy_leave',
    #                     store=True
    #                     )
    # days = fields.Float(string="Days", required=False, readonly=True)
    # amount = fields.Float(string="Amount", required=False,
    #                       compute='calculate_buy_leave', store=True, readonly=True
    #                       )
    # date = fields.Date(string="Date From", required=False)
    # date_to = fields.Date(string="Date To", required=True)
    # state = fields.Selection(string="State",
    #                          selection=[
    #                              ('draft', 'draft'),
    #                              ('direct_manager', 'Direct Manager Approved'),
    #                              ('admin_approve', 'Admin Approved'),
    #                              ('gm_approve', 'GM Approved'),
    #                              ('hr', 'HR Approved'),
    #                              ('done', 'Finance Approved'),
    #                          ], default='draft',
    #                          required=False, )

    # # department_approve = fields.Boolean('Approve', compute='_get_approve')
    # journal_id = fields.Many2one('account.journal', string="Journal")
    # employee_account_leave = fields.Many2one('account.account', string="Debit Account")
    # leave_account = fields.Many2one('account.account', string="Credit Account")
    # move_id = fields.Many2one('account.move', string="Journal Entry", readonly=True)


    # # @api.depends('manager_id', 'state')
    # # def _get_approve(self):
    # #     for rec in self:
    # #         rec.department_approve = False
    # #         if rec.state == 'direct_manager' and rec.manager_id.id == self.env.user.id:
    # #             rec.department_approve = True

    # def action_sent_to_direct_manager(self):
    #     self.state = 'direct_manager'

    # def action_hr_approve(self):
    #     self.state = 'hr'

    # def action_admin_approve(self):
    #     self.state = 'admin_approve'

    # def action_gm_approve(self):
    #     self.state = 'gm_approve'

    # # def action_create_finance_approve(self):
    # #     self.bntton_done()
    # #     if self.button_create_payment(self.amount, self.employee_id, self.date):
    # #         self.state = 'done'

    # def finance_approve(self):
    #     if not self.employee_account_leave or not self.leave_account or not self.journal_id:
    #         raise Warning(_("You must enter employee account & Loan account and journal to approve "))
    #     can_close = False
    #     loan_obj = self.env['buy.leave']
    #     move_obj = self.env['account.move']
    #     move_line_obj = self.env['account.move.line']
    #     currency_obj = self.env['res.currency']
    #     created_move_ids = []
    #     loan_ids = []
    #     for leave in self:
    #         line_ids = []
    #         debit_sum = 0.0
    #         credit_sum = 0.0
    #         amount = leave.amount
    #         leave_name = 'Bought Leave For' + leave.employee_id.name
    #         reference = 'Buy Leave' + leave.employee_id.name
    #         journal_id = leave.journal_id.id
    #         date = leave.date_to

    #         move_dict = {
    #             'narration': leave_name,
    #             'ref': reference,
    #             'journal_id': journal_id,
    #             'date': date,
    #         }
    #         debit_line = (0, 0, {
    #             'name': leave_name,
    #             'partner_id': False,
    #             'account_id': leave.employee_account_leave.id,
    #             'journal_id': journal_id,
    #             'date': date,
    #             'debit': amount > 0.0 and amount or 0.0,
    #             'credit': amount < 0.0 and -amount or 0.0,
    #             'analytic_account_id': False,
    #             'tax_line_id': 0.0,
    #         })
    #         line_ids.append(debit_line)
    #         debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
    #         credit_line = (0, 0, {
    #             'name': leave_name,
    #             'partner_id': False,
    #             'account_id': leave.leave_account.id,
    #             'journal_id': journal_id,
    #             'date': date,
    #             'debit': amount < 0.0 and -amount or 0.0,
    #             'credit': amount > 0.0 and amount or 0.0,
    #             'analytic_account_id': False,
    #             'tax_line_id': 0.0,
    #         })
    #         line_ids.append(credit_line)
    #         credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
    #         move_dict['line_ids'] = line_ids
    #         move = self.env['account.move'].create(move_dict)
    #         leave.write({'move_id': move.id})
    #         move.post()
    #         self.state = 'done'

    # def bntton_done(self):
    #     res = self.env['hr.leave.type'].search([('name', '=', 'Paid Time Off')])
    #     for rec in self:
    #         create_leave = self.env['hr.leave.allocation'].create({
    #             'name': 'Buy Leave',
    #             'employee_id': rec.employee_id.id,
    #             'holiday_status_id': res.id,
    #             'allocation_type': 'regular',
    #             'number_of_days': -int(rec.days)
    #         })
    #         create_leave.action_confirm()
    #         create_leave.action_validate()

    # def _get_number_of_days(self, date, date_to, employee_id):
    #     """ Returns a float equals to the timedelta between two dates given as string."""
    #     from_dt = fields.Datetime.from_string(date)
    #     to_dt = fields.Datetime.from_string(date_to)

    #     if employee_id:
    #         time_delta = to_dt - from_dt
    #         return math.ceil(time_delta.days + float(time_delta.seconds) / 86400)

    # @api.onchange('date_to')
    # def _onchange_date_to(self):
    #     """ Update the number_of_days. """
    #     date = self.date
    #     date_to = self.date_to

    #     # Compute and update the number of days
    #     if (date_to and date) and (date <= date_to):
    #         self.days = self._get_number_of_days(date, date_to, self.employee_id.id)
    #     else:
    #         self.days = 0

    # @api.depends('employee_id', 'days')
    # def calculate_buy_leave(self):
    #     for rec in self:
    #         if rec.employee_id:
    #             rec.remaining_leaves = rec.employee_id.remaining_leaves
    #             rec.wage = rec.employee_id.contract_id.wage
    #             rec.manager_id = rec.employee_id.parent_id.id
    #         if rec.days:
    #             rec.amount = (rec.wage / 30) * rec.days

    # # def button_create_payment(self, amount, employee_id, fa_date):
    # #     if amount > 0.0 and employee_id:
    # #         res = self.env['finance.approval'].create({
    # #             'request_amount': amount,
    # #             'fa_date': fa_date,
    # #             'reason': 'Buy Leave ' + employee_id.name,
    # #         })
    # #         return res
    # #     else:
    # #         raise ValidationError(_('Enter Amount ...'))


