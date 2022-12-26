# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta


class SellTimeOff(models.Model):
	_name = 'sell.time.off'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'sequence'

	def _get_default_company_id(self):
		return self._context.get('force_company', self.env.user.company_id.id)

	sequence = fields.Char(string='Code', readonly=True)
	request_date = fields.Date(string="Request Date",default=fields.Date.today())
	employee_id = fields.Many2one('hr.employee',string="Employee Name")
	department_id = fields.Many2one('hr.department',string="Department")
	job_id = fields.Many2one('hr.job',string="Job Title")
	address = fields.Char(string="Home Address",compute='_get_employee_data', readonly=False)
	contract_start_date = fields.Date('Contract Start Date', compute="_get_employee_data", tracking=True,
		help="Start date of the contract.")

	total_time_off = fields.Float(string="Remaining Days",compute="_compute_total_timeoff",store=True)
	days_to_sell = fields.Float(string="Days To Purchase")
	total_amount = fields.Float(string="Total Amount",compute="_compute_total_amount")
	company_id = fields.Many2one('res.company', string='Company',default=_get_default_company_id)
	state = fields.Selection([
		('draft', 'Draft'),
		('submit', 'Submit'),
		('wait_hr_approve', 'HR Manager Approval'),
		('wait_gm_approve', 'GM Approval'),
		('wait_fin_approve', 'Finance Approval'),
		('approve', 'Approved'),
		('cancel','Cancel'),],default='draft')
	paid = fields.Boolean(default=False)
	payslip_id = fields.Many2one('hr.payslip')
	debit_account = fields.Many2one('account.account', string="Debit Account")
	credit_account = fields.Many2one('account.account', string="Credit Account")
	journal_id = fields.Many2one('account.journal', string="Journal")
	move_id = fields.Many2one('account.move', string="Journal Entry", readonly=True)
	
	@api.model
	def create(self, vals):
		record = super(SellTimeOff, self).create(vals)
		record.sequence =  self.env['ir.sequence'].get('hr.leave.sell') or ' '
		return record

	@api.onchange('employee_id')
	def _get_employee_data(self):
		for rec in self:
			if rec.employee_id:
				rec.job_id = rec.employee_id.job_id
				rec.department_id = rec.employee_id.department_id
				rec.contract_start_date = rec.employee_id.contract_id.date_start
				rec.address = rec.employee_id.address_home_id.street
			else:
				rec.job_id = False
				rec.department_id = False
				rec.contract_start_date = False
				rec.address = False

	@api.depends('employee_id','days_to_sell')
	def _compute_total_amount(self):
		for rec in self:
			amount = 0.0
			if rec.employee_id and rec.days_to_sell > 0.0:
				day_wage = rec.employee_id.contract_id.wage /30
				amount =  day_wage * rec.days_to_sell
				rec.total_amount = amount
			else:
				rec.total_amount = 0

	@api.depends('employee_id')
	def _compute_total_timeoff(self):
		for rec in self:
			rec.total_time_off = 0.0
			if rec.employee_id:
				alloaction = self.env['hr.leave.allocation'].search([('employee_id','=',rec.employee_id.id),
					('holiday_status_id.is_annual','=',True)])
				if alloaction:
					for alloc in alloaction:
						rec.total_time_off += alloc.number_of_days_display - alloc.leaves_taken
				else:
					rec.total_time_off = 0.0
			else:
				rec.total_time_off = 0.0
	
	def action_submit(self):
		self.write({'state':'submit'})    

	def action_hr_approve(self):
		self.write({'state':'wait_hr_approve'})

	def action_gm_approve(self):
		self.write({'state':'wait_gm_approve'})

	def action_fin_approve(self):
		self.write({'state':'wait_fin_approve'})

	def action_draft(self):
		self.write({'state':'draft'})    

	def action_approve(self):
		line_ids = []
		debit_sum = 0.0
		credit_sum = 0.0
		move_dict = {
			'narration': 'Amount Of Purchase Time off From Employee ' + self.employee_id.name,
			'ref': '/',
			'journal_id': self.journal_id.id,
			'date': fields.Date.today(),
		}
		debit_line = (0, 0, {
			'name': 'Amount Of Purchase Time off From Employee ' + self.employee_id.name,
			'partner_id': False,
			'account_id': self.debit_account.id,
			'journal_id': self.journal_id.id,
			'date': fields.Date.today(),
			'debit': self.total_amount or 0.0,
			'credit': 0.0,
		})
		line_ids.append(debit_line)
		debit_sum += debit_line[2]['debit'] - debit_line[2]['credit']
		credit_line = (0, 0, {
			'name': 'Amount Of Purchase Time off From Employee ' + self.employee_id.name,
			'partner_id': False,
			'account_id': self.credit_account.id,
			'journal_id': self.journal_id.id,
			'date': fields.Date.today(),
			'debit': 0.0,
			'credit': self.total_amount or 0.0,
		})
		line_ids.append(credit_line)
		credit_sum += credit_line[2]['credit'] - credit_line[2]['debit']
		move_dict['line_ids'] = line_ids
		move = self.env['account.move'].create(move_dict)
		
		self.write({'state':'approve','move_id': move.id})
					

class HolidayAllocation(models.Model):
	_inherit = "hr.leave.allocation"

	@api.depends('employee_id', 'holiday_status_id', 'taken_leave_ids.number_of_days', 'taken_leave_ids.state')
	def _compute_leaves(self):
		for allocation in self:
			allocation.max_leaves = allocation.number_of_hours_display if allocation.type_request_unit == 'hour' else allocation.number_of_days
			allocation.leaves_taken = sum(taken_leave.number_of_hours_display if taken_leave.leave_type_request_unit == 'hour' else taken_leave.number_of_days\
				for taken_leave in allocation.taken_leave_ids\
				if taken_leave.state == 'validate')

			if allocation.holiday_status_id.is_annual:
				sell_leaves = self.env['sell.time.off'].search([('employee_id','=',allocation.employee_id.id),
				('state','=','approve')])

				days_to_sell = 0.0
				if sell_leaves:
					for sell in sell_leaves:
						days_to_sell += sell.days_to_sell

				allocation.leaves_taken = sum(taken_leave.number_of_hours_display if taken_leave.leave_type_request_unit == 'hour' else taken_leave.number_of_days\
					for taken_leave in allocation.taken_leave_ids\
					if taken_leave.state == 'validate')

				if days_to_sell > 0.0:
					allocation.leaves_taken = allocation.leaves_taken + days_to_sell

