from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command

class HrDepartment(models.Model):
    _inherit = 'hr.department'

    percentage = fields.Float('Incentive Percentage')



class HrJob(models.Model):
    _inherit = 'hr.job'

    percentage = fields.Float('Incentive Percentage')


class HrContract(models.Model):
    _inherit = 'hr.contract'

    currency_id = fields.Many2one('res.currency', string="Currency")
    foreign = fields.Boolean('foreign')


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    long_loan = fields.Float(compute="get_long_loan", store=True, string="Long Loan")
    short_loan = fields.Float(compute="get_short_loan", store=True, string="Long Loan")
    incentive = fields.Float(string="Incentive")
    payroll_rate = fields.Float('Payroll rate')

    @api.depends('employee_id', 'date_to', 'date_from')
    def get_long_loan(self):
        for rec in self:
            if rec.employee_id:
                loan_ids = self.env['hr.loan.line'].search(
                    [('employee_id', '=', rec.employee_id.id), ('paid', '=', False),
                     ('date', '<=', rec.date_to), ('date', '>=', rec.date_from),
                     ('loan_id.state', '=', 'done')])
                rec.long_loan = sum(loan_ids.mapped('amount'))

    @api.depends('employee_id', 'date_to', 'date_from')
    def get_short_loan(self):
        for x in self:
            if x.employee_id:
                amount = 0.00
                loan_ids = x.env['hr.monthlyloan'].search(
                    [('employee_id', '=', x.employee_id.id), ('state', '=', 'done'), ('date', '>=', x.date_from),
                     ('date', '<=', x.date_to)])
                for loan in loan_ids:
                    amount += loan.loan_amount
                x.short_loan = amount
