from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command

class HrDepartment(models.Model):
    _inherit = 'hr.department'

    percentage = fields.Float('Incentive Percentage')



class HrJob(models.Model):
    _inherit = 'hr.job'

    percentage = fields.Float('Incentive Percentage')