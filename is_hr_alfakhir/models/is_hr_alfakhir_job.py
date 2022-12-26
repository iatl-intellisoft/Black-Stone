from odoo import api, fields, models


class smtJob(models.Model):
    _inherit = "hr.job"
    _description = "Job Position States"

    hr_comment = fields.Text('Hr Comments')
    gm_comment = fields.Text('General Manager Comments')
    # state = fields.Selection([
    #     ('recruit', 'draft'),
    #     ('advertised', 'Advertised'),
    #     ('applicant', 'Applicant'),
    #     ('open', 'Not Recruiting')
    # ], string='Status', readonly=True, required=True, tracking=True, copy=False, default='recruit',
    #     help="Set whether the recruitment process is open or closed for this job position.")

    # state = fields.Selection([
    #     ('draft', 'Draft'),
    #     ('advertised', 'Advertised'),
    #     ('applicant', 'Applicant')
    # ], string='Status', readonly=True, required=True, track_visibility='always', copy=False, default='draft',
    #     help="Set whether the recruitment process is open or closed for this job position.")

    def department_job_position(self):
        for rec in self:
            rec.state = 'request'

    def reset_draft(self):
        for rec in self:
            rec.state = 'recruit'

    def hr_confirmation(self):
        for rec in self:
            rec.state = 'confirm'

    def set_open(self):
        for rec in self:
            return rec.write({
                'state': 'refuse',
                'no_of_recruitment': 0,
                'no_of_hired_employee': 0
            })


class WizardRecruitment(models.Model):
    _name = 'wizard.recruitment'
    _description = 'recruitment reason'
    job_id = fields.Many2one('hr.job', 'Job', required=True)
    comment = fields.Text('Comments')

    def refuse_recruitment(self):
        for rec in self:
            rec.job_id.set_open()
