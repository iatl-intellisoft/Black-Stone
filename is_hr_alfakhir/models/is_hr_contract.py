# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil import relativedelta
import time
# import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.osv import osv


class HrContractLeave(models.Model):
    _inherit = 'hr.contract'

    transport_allowance = fields.Float(string='Transport + Fuel Allowance')
    taxable = fields.Boolean(string='Deduct Tax', default=True)
    eligible_si = fields.Boolean(string='Eligible For Social Insurance', default=True)
    # legal_leave = fields.Selection(
    #     [('20', '20 day'), ('25', '25 day'),
    #      ('30', '30 day')], string='Legal Leave')
    grade = fields.Selection(
        [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), ('9', '9'),
         ('10', '10')
         ], string='Grade')
    grade_class = fields.Selection([('a', 'A'), ('b', 'B'), ('c', 'C'), ('d', 'D'), ('e', 'E'), ('f', 'F')],
                                   string='Class')
    has_insurance = fields.Boolean(default=False,string='Have Medical Insurance')
    medical_insurance_ids = fields.One2many('hr.medical.insurance','contract_id')
    medical_amount = fields.Float('Amount To Deduct')
    remaining_days = fields.Float(srting="Annaul Remaining days",compute='_compute_remaining_days')

    def _compute_remaining_days(self):
        for rec in self:
            rec.remaining_days = rec.employee_id.annual_remaining_days


    # @api.onchange('legal_leave')
    # def employee_legal_leave(self):
    #     for x in self:
    #         employee = x.employee_id
    #         if x.employee_id:
    #             legal_leave = x.legal_leave
    #             employee_id = x.employee_id.id
    #             update_leave = False
    #             if legal_leave == '20':
    #                 update_leave = x._cr.execute("UPDATE hr_employee set annual_leave=%s"
    #                                              "  WHERE id= %s", (20, employee_id))
    #             elif legal_leave == '25':
    #                 update_leave = x._cr.execute("UPDATE hr_employee set annual_leave =%s"
    #                                              "  WHERE id= %s", (25, employee_id))
    #             else:
    #                 update_leave = x._cr.execute("UPDATE hr_employee set annual_leave=%s"
    #                                              "WHERE id= %s", (30, employee_id))
    #             # allocation_id = self.env['hr.holidays'].create({
    #             #     'name': 'Legal Leave',
    #             #     'employee_id': employee_id,
    #             #     'holiday_type': 'employee',
    #             #     'department_id': employee.department_id.id,
    #             #     'holiday_status_id': 1,
    #             #     'number_of_days_temp': employee.annual_leave,
    #             #     'state': 'validate'
    #             # })


class HrLeave(models.Model):
    _inherit = "hr.leave"

    @api.constrains('date_to', 'date_from')
    def _check_date(self):
        for holiday in self:
            employement_period = 0.0
            date_from = str(holiday.date_from)
            if holiday.holiday_status_id.id == 1:
                date_from = holiday.date_from
                d = date_from
                date_from = str(d.date())
                if holiday.date_from:
                    employee_id = holiday.employee_id.id
                    hr_employee = holiday.env['hr.employee'].search([('id', '=', employee_id)])
                    # if not hr_employee.hiring_date:
                    #     raise UserError(_('Please Add employee Hiring date!'))
                    # hiring = str(hr_employee.hiring_date)
                    if not hr_employee.contract_id.date_start:
                        raise UserError(_('Please Add employee Contract Start Date!'))
                    hiring = str(hr_employee.contract_id.date_start)
                    holiday_to = datetime.strptime(date_from, '%Y-%m-%d')
                    hiring_date = datetime.strptime(hiring, '%Y-%m-%d')
                    employement_period = (holiday_to - hiring_date).days
                    if employement_period < 365.25:
                        raise UserError(_('You can not request leave before you complete Year!'))


class Insurance(models.Model):
    _name = 'hr.medical.insurance'

    name = fields.Char(required=True)
    type_of_relatives = fields.Selection(selection=[('father','Father'),('mother','Mother'),('husband','Husband'),('wife','Wife')],required=True)
    birth_date = fields.Date()
    gender = fields.Selection(selection=[('male','Male'),('female','Female')],required=True)
    contract_id = fields.Many2one('hr.contract')
    employee_id = fields.Many2one('hr.employee', string="Employee", related='contract_id.employee_id',store=True)
    department_id = fields.Many2one('hr.department',string='Department',related='contract_id.department_id',store=True)