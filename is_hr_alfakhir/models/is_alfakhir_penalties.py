from odoo import models, fields, api, _
from odoo.exceptions import except_orm, Warning, ValidationError
from datetime import datetime
import calendar


class PANALTIES(models.Model):
    _name = "hr.panalties"

    name = fields.Char(string="Panalty Name")
    date = fields.Date(string="Date", default=fields.Date.today())
    employee_id = fields.Many2one('hr.employee', string="Employee",required=True)
    panalty_type = fields.Selection([
        ('one_day','One Day'),
        ('half_day','Half Day'),
        ('other','Other')
    ],default="one_day")
    emp_salary = fields.Float('Basic Salary',compute='_get_basic_amount')
    amount = fields.Float('Deduct Amount',compute='_get_amount')
    state = fields.Selection(
        [('draft', 'To Submit'), ('submit', 'Submitted')],
        'Status', default='draft')
    other_amount = fields.Float('Deduct Amount')

    def act_submit(self):
        self.state = 'submit'

    @api.depends('employee_id','panalty_type')
    def _get_amount(self):
        for rec in self:
            rec.amount = 0.0
            if rec.employee_id:
                basic = rec.employee_id.contract_id.wage*0.45
                cola = rec.employee_id.contract_id.wage*0.15
                if rec.panalty_type == 'one_day':
                    rec.amount = (basic + cola)/26
                if rec.panalty_type == 'half_day':
                    rec.amount = (basic + cola)/52
                if rec.panalty_type == 'other':
                    rec.amount = 0.0

    @api.depends('employee_id')
    def _get_basic_amount(self):
        for rec in self:
            rec.emp_salary = 0.0
            if rec.employee_id:
                basic = rec.employee_id.contract_id.wage*0.45
                cola = rec.employee_id.contract_id.wage*0.15
                rec.emp_salary = basic + cola
               
