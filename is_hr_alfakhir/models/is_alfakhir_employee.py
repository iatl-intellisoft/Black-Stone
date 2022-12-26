# -*- coding: utf-8 -*-
###########

from odoo import api, fields, models, _
import xlsxwriter
import base64
import datetime
from io import StringIO, BytesIO
from datetime import *
from datetime import datetime, timedelta
from odoo.exceptions import UserError
from dateutil import relativedelta


class HrEmployeePublic(models.Model):
    _inherit = "hr.employee.public"

    # bank_acc = fields.Char(readonly=True)
    # employee_account = fields.Many2one(readonly=True)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    # employee_account = fields.Many2one('account.account', string="Debit Account")
    # bank_acc = fields.Char("Bank Account")
    annual_remaining_days = fields.Integer(string="Annual Remaining Days",compute="_calc_remaining_days")

    @api.depends('remaining_leaves')
    def _calc_remaining_days(self):
        for rec in self:
            alloaction = self.env['hr.leave.allocation'].search([('employee_id','=',rec.id),
                ('holiday_status_id.is_annual','=',True)])
            if alloaction:
                for alloc in alloaction:
                    rec.annual_remaining_days += alloc.number_of_days_display - alloc.leaves_taken
            else:
                rec.annual_remaining_days = 0.0

# class FinanceApproval(models.Model):
#     _inherit = 'finance.approval'
#     requester = fields.Many2one('hr.employee', 'Requester', required=True)
#
#     exp_account = fields.Many2one('account.account', string="Expense or Debit Account",
#                                   related="requester.employee_account")
#
#     @api.depends('approval_no', 'requester', 'beneficiary')
#     def _get_description(self):
#         for rec in self:
#             rec.name = (rec.approval_no and ("Approval No: " + str(rec.approval_no)) or " ") + "/" + (
#                     rec.requester and ("Requester: " + rec.requester.name) or " ") + "/" \
#                        + (rec.beneficiary and ("Beneficiary: " + rec.beneficiary) or " ") + "/" + (
#                                rec.reason and ("Reason: " + rec.reason) or " ")


class HrApplicant(models.Model):
    _inherit = 'hr.applicant'
    state = fields.Selection([('draft', 'Draft '),
                              ('interviewed', 'Interviewed'),
                              ('short_list', 'Short list'),
                              ('offer', 'Offer '),
                              ('employee_approval', 'Employee Approval'),
                              ('done', 'Done')
                              ], "State", readonly=True, default="draft")
    is_short_list = fields.Boolean(default=False)

    def set_short_list(self):
        self.state = 'short_list'
        self.is_short_list = True
        # next_seq = self.env['ir.sequence'].get('stage.stage_id.sequence')
        next_seq = self.stage_id.id +1
        print("next_seq before", self.stage_id.sequence)
        self.stage_id.id = next_seq
        print("next_seq after", self.stage_id.sequence)

    def set_offer(self):
        self.state = 'offer'

    def set_employee_approval(self):
        self.state = 'employee_approval'

    def set_done(self):
        self.state = 'done'

    def set_interviewed(self):
        self.state = 'interviewed'

    @api.onchange('stage_id')
    @api.depends('stage_id')
    def set_short_(self):

        for rec in self:

            if rec.stage_id.is_short:

                rec.is_short_list = True


            else:
                rec.is_short_list = False
        # return True



class HrJob(models.Model):
    _inherit = 'hr.job'
    state = fields.Selection([
        ('recruit', 'draft'),
        ('interviewed', 'Interviewed'),
        ('request', 'Department Request'),
        ('confirm', 'HR Confirm'),
        ('advertised', 'Advertised'),
        ('applicant', 'Applicant'),
        ('refuse', 'Refuse'),
        ('open', 'Not Recruiting')
    ], string='Status', readonly=True, required=True, tracking=True, copy=False, default='recruit',
        help="Set whether the recruitment process is open or closed for this job position.")
    short_list_count = fields.Integer(compute='_compute_short_list_count', string="Short List")




    def set_advertised(self):
        self.state = 'advertised'

    def set_applicant(self):
        self.state = 'applicant'

    def set_refuse(self):
        self.state = 'open'


    def _compute_short_list_count(self):


        for job in self:
            job.short_list_count = self.env["hr.applicant"].search_count(
                [("job_id", "=", job.id), ("is_short_list", "=", True)]
            )



class Stage(models.Model):
    _inherit = 'hr.recruitment.stage'

    is_short =fields.Boolean("Is short list",default=False)
