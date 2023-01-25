#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#    Description: Accounting Approval                                        #
#    Author: IntelliSoft Software                                            #
#    Date: Aug 2015 -  Till Now                                              #
##############################################################################


from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

from . import amount_to_ar


##################################################################
# add financial approval

########################################
class FinanceApprovalLine(models.Model):
    _name = 'finance.approval.line'
    _description = 'Finance Approval details.'

    finance_id = fields.Many2one('finance.approval', string='Finance Approval', ondelete="cascade")
    name = fields.Char('Narration', required=True)
    amount = fields.Float('Amount', required=True)
    notes = fields.Char('Notes')
    exp_account = fields.Many2one('account.account', string="Expense or Debit Account")
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    partner_id = fields.Many2one('res.partner', string='Partner')
    # payment_method_name = fields.Many2one('account.payment.method')
    # pa_name = fields.Char(related="payment_method_name.name")
    payment_method = fields.Many2one('account.payment.method')
    payment_method_name = fields.Char('Payment Method Name', related='payment_method.name')


class finance_approval(models.Model):
    _name = 'finance.approval'
    _description = 'A model for tracking finance approvals.'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    approval_no = fields.Char('Approval No.', help='Auto-generated Approval No. for finance approvals')
    custody = fields.Boolean(string='Custody')
    finance_approval_line_ids = fields.One2many('finance.approval.line', 'finance_id',
                                                string='Finance Approval Details')
    name = fields.Char('Details', compute='_get_description', store=True, readonly=True)
    requester = fields.Char('Requester', required=True, default=lambda self: self.env.user.name)
    request_amount = fields.Float('Requested Amount', required=True)
    request_currency = fields.Many2one('res.currency', 'Currency',
                                       default=lambda self: self.env.user.company_id.currency_id)
    request_amount_words = fields.Char(string='Amount in Words', readonly=True, default=False, copy=False,
                                       compute='_compute_text', translate=True)
    fa_date = fields.Date('Date')
    department_id = fields.Many2one('hr.department', string="Department")
    beneficiary = fields.Char('Beneficiary')
    reason = fields.Char('Reason')
    expense_item = fields.Char('Expense Item')
    state = fields.Selection(
        [('draft', 'Draft'), ('department_approval', 'Department Approval'), ('to_approve', 'Financial Approval'),
         ('gm_approval', 'General Manager Approval'), ('ready', 'Ready for Payment'), ('reject', 'Rejected'),
         ('validate', 'Validated')],
        string='Finance Approval Status', default='draft')
    exp_account = fields.Many2one('account.account', string="Expense or Debit Account",store=True)
    journal_id = fields.Many2one('account.journal', 'Bank/Cash Journal',
                                 help='Payment journal.',
                                 domain=[('type', 'in', ['bank', 'cash'])])
    move_id = fields.Many2one('account.move', 'Journal Entry', readonly=True)
    payment_id = fields.Many2one('account.payment', 'Account Payment', readonly=True)
    mn_remarks = fields.Text('Manager Remarks')
    auditor_remarks = fields.Text('Reviewer Remarks')
    fm_remarks = fields.Text('Finance Man. Remarks')
    gm_remarks = fields.Text('General Man. Remarks')
    view_remarks = fields.Text('View Remarks', readonly=True, compute='_get_remarks', store=True)
    user_id = fields.Many2one('res.users', string='User', default=lambda self: self.env.user)
    manager_id = fields.Many2one('res.users', string='Manager')
    ca_app_id = fields.Many2one('res.users', string="Validated By")
    partner_id = fields.Many2one('res.partner', string='Vendor',store=True)
    mn_app_id = fields.Many2one('res.users', string="Manager Approval By")
    fm_app_id = fields.Many2one('res.users', string="Finance Approval By")
    gm_app_id = fields.Many2one('res.users', string="GM Approval By")
    at_app_id = fields.Many2one('res.users', string="Validated By")
    # add company_id to allow this module to support multi-company
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id)
    # adding analytic account
    analytic_account = fields.Many2one('account.analytic.account', string='Cost/Profit Center')
    check_no = fields.Char('Check No.')
    check_bank_name = fields.Many2one('bank.bank', 'Check Bank')
    check_bank_branch = fields.Char('Check Bank Branch')
    check_date = fields.Date('Check Date')
    payment_method = fields.Many2one('account.payment.method')
    payment_method_name = fields.Char('Payment Method Name', related='payment_method.name')
    gm_approvement = fields.Boolean('Require GM Approval?', default=True)
    admin_finance = fields.Boolean('Administration Request?', default=True)

    @api.model
    def create(self, vals):
        res = super(finance_approval, self).create(vals)
        # get finance approval sequence no.
        next_seq = self.env['ir.sequence'].get('finance.approval.sequence')
        res.update({'approval_no': next_seq})
        return res

    # overriding default get
    @api.model
    def default_get(self, fields):
        res = super(finance_approval, self).default_get(fields)
        # get manager user id
        manager = self.env['res.users'].search([('id', '=', self.env.user.id)], limit=1).approval_manager.id
        if manager:
            res.update({'manager_id': manager})
        return res

    def department_approval(self):
        for rec in self:
            if rec.admin_finance == False:
                # schedule activity for manager to approve
                vals = {
                    'activity_type_id': rec.env['mail.activity.type'].sudo().search(
                        [('name', 'like', 'Financial Approval')],
                        limit=1).id,
                    'res_id': rec.id,
                    'res_model_id': rec.env['ir.model'].sudo().search([('model', 'like', 'finance.approval')], limit=1).id,
                    'user_id': rec.manager_id.id and rec.manager_id.id or 1,
                    'summary': rec.name,
                }

                # add lines
                rec.env['mail.activity'].sudo().create(vals)
                # change state
                rec.state = 'department_approval'

                # Update footer message
                message_obj = rec.env['mail.message']
                message = _("State Changed  Confirm -> <em>%s</em>.") % (rec.state)
                msg_id = rec.message_post(body=message)
            else:
                # get advisor group
                fm_group_id = rec.env['res.groups'].sudo().search([('name', 'like', 'Advisor')], limit=1).id

                # first of all get all finance managers / advisors
                if fm_group_id:
                    rec.env.cr.execute('''SELECT uid FROM res_groups_users_rel WHERE gid = %s order by uid''' % (fm_group_id))

                # schedule activity for advisor(s) to approve
                for fm in list(filter(lambda x: (
                        rec.env['res.users'].sudo().search([('id', '=', x)]).company_id == rec.company_id),
                                      rec.env.cr.fetchall())):
                    vals = {
                        'activity_type_id': rec.env['mail.activity.type'].sudo().search(
                            [('name', 'like', 'Financial Approval')],
                            limit=1).id,
                        'res_id': rec.id,
                        'res_model_id': rec.env['ir.model'].sudo().search([('model', 'like', 'finance.approval')],
                                                                           limit=1).id,
                        'user_id': fm[0] or 1,
                        'summary': rec.name,
                    }
    
                    # add lines
                    rec.env['mail.activity'].sudo().create(vals)
                # change state
                rec.state = 'to_approve'
    
                # Update footer message
                message_obj = rec.env['mail.message']
                message = _("State Changed  Confirm -> <em>%s</em>.") % (rec.state)
                msg_id = rec.message_post(body=message)

    # approval
    
    def to_approve(self):
        for rec in self :
            # schedule activity for finance manager to approve
            # get finance manager group
            fm_group_id = rec.env['res.groups'].sudo().search([('name', 'like', 'Advisor')], limit=1).id
    
            # first of all get all finance managers / advisors
            rec.env.cr.execute('''SELECT uid FROM res_groups_users_rel WHERE gid = %s order by uid''' % (fm_group_id))
    
            # schedule activity for advisor(s) to approve
            for fm in list(filter(lambda x: (
                    rec.env['res.users'].sudo().search([('id', '=', x)]).company_id == rec.company_id),
                                  rec.env.cr.fetchall())):
                vals = {
                    'activity_type_id': rec.env['mail.activity.type'].sudo().search(
                        [('name', 'like', 'Financial Approval')],
                        limit=1).id,
                    'res_id': rec.id,
                    'res_model_id': rec.env['ir.model'].sudo().search([('model', 'like', 'finance.approval')],
                                                                       limit=1).id,
                    'user_id': fm[0] or 1,
                    'summary': rec.name,
                }
    
                # add lines
                rec.env['mail.activity'].sudo().create(vals)
            # change state
            rec.state = 'to_approve'
            rec.mm_app_id = rec.env.user.id
    
            # Update footer message
            message_obj = rec.env['mail.message']
            message = _("State Changed  Confirm -> <em>%s</em>.") % (rec.state)
            msg_id = rec.message_post(body=message)
        return True

    # financial approval, i.e. actual approval step
    
    def financial_approval(self):
        for rec in self:
            self.state = 'ready'
            self.fm_app_id = self.env.user.id

        #     if rec.gm_approvement == True:
        #         # get general manager group
        #         gm_group_id = rec.env['res.groups'].sudo().search([('name', 'like', 'General Manager')], limit=1).id
        #
        #         # first of all get all general manager(s)
        #         rec.env.cr.execute(
        #             '''SELECT uid FROM res_groups_users_rel WHERE gid = %s order by uid''' % (gm_group_id))
        #
        #         # schedule activity for advisor(s) to approve
        #         for gm in list(filter(lambda x: (
        #                 rec.env['res.users'].sudo().search([('id', '=', x)]).company_id == rec.company_id),
        #                               rec.env.cr.fetchall())):
        #             vals = {
        #                 'activity_type_id': rec.env['mail.activity.type'].sudo().search(
        #                     [('name', 'like', 'Financial Approval')],
        #                     limit=1).id,
        #                 'res_id': rec.id,
        #                 'res_model_id': rec.env['ir.model'].sudo().search([('model', 'like', 'finance.approval')],
        #                                                                    limit=1).id,
        #                 'user_id': gm[0] or 1,
        #                 'summary': rec.name,
        #             }
        #             # add lines
        #             rec.env['mail.activity'].sudo().create(vals)
        #
        #         # change state
        #         rec.state = 'gm_approval'
        #         rec.fm_app_id = rec.env.user.id
        #
        #         # Update footer message
        #         message_obj = rec.env['mail.message']
        #         message = _("State Changed  Confirm -> <em>%s</em>.") % (rec.state)
        #         msg_id = rec.message_post(body=message)
        #     return True
        #
        # else:
            # get validator group
            # at_group_id = self.env['res.groups'].sudo().search([('name', 'like', 'Validator')], limit=1).id
            #
            # # first of all get all validator(s)
            # self.env.cr.execute('''SELECT uid FROM res_groups_users_rel WHERE gid = %s order by uid''' % (at_group_id))
            #
            # # schedule activity for validator(s) to validate
            # for at in list(filter(lambda x: (
            #         self.env['res.users'].sudo().search([('id', '=', x)]).company_id == self.company_id),
            #                       self.env.cr.fetchall())):
            #     vals = {
            #         'activity_type_id': self.env['mail.activity.type'].sudo().search(
            #             [('name', 'like', 'Financial Approval')],
            #             limit=1).id,
            #         'res_id': self.id,
            #         'res_model_id': self.env['ir.model'].sudo().search([('model', 'like', 'finance.approval')],
            #                                                            limit=1).id,
            #         'user_id': at[0] or 1,
            #         'summary': self.name,
            #     }
            #
            #     # add lines
            #     self.env['mail.activity'].sudo().create(vals)

            # change state

            # Update footer message
            # message_obj = self.env['mail.message']
            # message = _("State Changed  Confirm -> <em>%s</em>.") % (self.state)
            # msg_id = self.message_post(body=message)

    # general manager approval
    # @api.one
    def gm_approval(self):
        # get validator group
        for rec in self:
            at_group_id = rec.env['res.groups'].sudo().search([('name', 'like', 'Validator')], limit=1).id
    
            # first of all get all general manager(s)
            rec.env.cr.execute('''SELECT uid FROM res_groups_users_rel WHERE gid = %s order by uid''' % (at_group_id))
    
            # schedule activity for general manager(s) to approve
            for at in list(filter(lambda x: (
                    rec.env['res.users'].sudo().search([('id', '=', x)]).company_id == rec.company_id),
                                  rec.env.cr.fetchall())):
                vals = {
                    'activity_type_id': rec.env['mail.activity.type'].sudo().search(
                        [('name', 'like', 'Financial Approval')],
                        limit=1).id,
                    'res_id': rec.id,
                    'res_model_id': rec.env['ir.model'].sudo().search([('model', 'like', 'finance.approval')],
                                                                       limit=1).id,
                    'user_id': at[0] or 1,
                    'summary': rec.name,
                }
    
                # add lines
                rec.env['mail.activity'].sudo().create(vals)
    
            # change state
            rec.state = 'ready'
            rec.gm_app_id = rec.env.user.id
    
            # Update footer message
            message_obj = rec.env['mail.message']
            message = _("State Changed  Confirm -> <em>%s</em>.") % (rec.state)
            msg_id = rec.message_post(body=message)
    
        # generate name of approval automatically
   
    @api.depends('approval_no', 'requester', 'beneficiary')
    def _get_description(self):
        for rec in self :
            rec.name = (rec.approval_no and ("Approval No: " + str(rec.approval_no)) or " ") + "/" + (
                    rec.requester and ("Requester: " + rec.requester) or " ") + "/" \
                        + (rec.beneficiary and ("Beneficiary: " + rec.beneficiary) or " ") + "/" + (
                                rec.reason and ("Reason: " + rec.reason) or " ")
    
        # return request amount in words
    
    @api.depends('request_amount', 'request_currency')
    def _compute_text(self):
        for rec in self :
            rec.request_amount_words = amount_to_ar.amount_to_text_ar(rec.request_amount,
                                                                       rec.request_currency.narration_ar_un,
                                                                       rec.request_currency.narration_ar_cn)
    
        # generate remarks
    
    @api.depends('mn_remarks', 'auditor_remarks', 'fm_remarks', 'gm_remarks')
    def _get_remarks(self):
        for rec in self:
            rec.view_remarks = (rec.mn_remarks and ("Manager Remarks: " + str(rec.mn_remarks)) or " ") + "\n\n" + (
                    rec.auditor_remarks and ("Account Manager Remarks: " + str(rec.auditor_remarks)) or " ") + "\n\n" + (
                                        rec.fm_remarks and (
                                        "Financial Man. Remarks: " + rec.fm_remarks) or " ") + "\n\n" + (
                                        rec.gm_remarks and ("General Man. Remarks: " + rec.gm_remarks) or " ")

    # validation
    @api.constrains('request_amount')
    def request_amount_validation(self):
        if self.request_amount <= 0:
            raise ValidationError(_("Requested amount must be greater than zero!"))

    # validation
    @api.constrains('payment_method')
    def request_amount_validation(self):
        if self.payment_method.name == 'Checks' and not self.partner_id:
            raise ValidationError(_("Checks are only allowed for vendors!"))

    # validate debit account when vendor selected
    # @api.constrains('exp_account', 'partner_id')
    # def check_account(self):
    #     if self.partner_id and self.exp_account.user_type_id.name != 'Payable':
    #         raise ValidationError(_("Debit account must be of type 'Payable' when selecting a vendor!"))

    def cancel_button(self):
        if self.move_id:
            self.move_id.button_cancel()
            self.move_id.unlink()
        if self.payment_id:
            self.payment_id.action_draft()
        self.state = 'draft'

    # reject finance approval
    
    def reject(self):
        for rec in self:
            rec.state = 'reject'
            # Update footer message
            message_obj = rec.env['mail.message']
            message = _("State Changed  Confirm -> <em>%s</em>.") % (rec.state)
            msg_id = rec.message_post(body=message)

    # validate, i.e. post to account moves
    def move_without_check(self):
        if not self.fa_date:
            raise ValidationError(_("Please Add Date!"))
        entrys = []
        total = 0.0
        # if self.on_credit:
        #     credit_account = self.credit_account_id
        #     journal = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
        # else:
        credit_account = self.journal_id.default_account_id
        journal = self.journal_id
        if self.finance_approval_line_ids:
            for line1 in self.finance_approval_line_ids:
                if not line1.exp_account:
                    raise ValidationError(_("Please select account!"))
                total = line1.amount
                credit_vals = {
                    'name': self.reason,
                    'partner_id': False,
                    'account_id': credit_account.id,
                    'credit': total,
                    'company_id': self.company_id.id,
                }
                entrys.append((0, 0, credit_vals))
                debit_val = {
                    'name': line1.name,
                    'partner_id': self.partner_id.id,
                    'account_id': line1.exp_account.id,
                    'debit': total,
                    #'analytic_account_id': line1.analytic_account_id.id,
                    'company_id': self.company_id.id,
                }
                # print "debit val", debit_val
                entrys.append((0, 0, debit_val))
        vals = {
            'journal_id': journal.id,
            'date': self.fa_date,
            'ref': self.approval_no,
            'company_id': self.company_id.id,
            'line_ids': entrys
        }
        return vals

    def validate(self):
        self.activity_ids.unlink()
        line_ids = []
        for x in self.finance_approval_line_ids:
            line = (0, 0, {
                'name': x.name,
                'account_id': x.exp_account.id,
                #'analytic_account_id': x.analytic_account_id.id,
                'amount': x.amount,

            })
            line_ids.append(line)

        if not self.exp_account and self.custody == True:
            raise ValidationError(_("Expense or debit account must be selected!"))

        if not self.journal_id and not self.bank_journal_id and not self.on_credit:
            raise ValidationError(_("Journal must be selected!"))

        # account move entry
        if self.request_currency == self.env.user.company_id.currency_id:
            # corresponding details in account_move_line
            if self.payment_method.name == 'Manual':

            # if self.payment_method_code != 'check_printing':
                self.move_id = self.env['account.move'].create(self.move_without_check())
                self.move_id.action_post()
                self.state = 'validate'
                self.ca_app_id = self.env.user.id
            elif self.payment_method.name == 'Checks':
                self.move_check_followups()
                self.state = 'validate'
                self.ca_app_id = self.env.user.id
        elif self.request_currency != self.env.user.company_id.currency_id:
            if self.payment_method.name != 'Checks':
                entrys = []
                if self.finance_approval_line_ids:
                    total = 0
                    for line1 in self.finance_approval_line_ids:
                        total += line1.amount
                    if self.on_credit:
                        credit_account = self.credit_account_id
                        journal = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
                    else:
                        credit_account = self.journal_id.default_account_id
                        journal = self.journal_id
                    credit_vals = {
                        'name': self.reason,
                        'partner_id': self.partner_id.id,
                        'account_id': credit_account.id,
                        'currency_id': self.request_currency.id,
                        'amount_currency': -total,
                        'credit': total / self.request_currency.rate,
                        'company_id': self.company_id.id,
                    }
                    entrys.append((0, 0, credit_vals))
                    # if total != self.request_amount:
                    #     raise UserError('Request amount and sum of details amount must be equal ')
                    for line in self.finance_approval_line_ids:
                        if not line.exp_account:
                            raise ValidationError(_("Please select account!"))
                        # if line.pa_name == 'Manual':
                        debit_val = {
                            'name': line.name,
                            'partner_id': line.partner_id.id,
                            'account_id': line.exp_account.id,
                            'debit': line.amount / self.request_currency.rate,
                            'currency_id': self.request_currency.id,
                            'amount_currency': line.amount,
                            #'analytic_account_id': line.analytic_account_id.id,
                            'company_id': self.company_id.id,
                        }
                        # print "debit val", debit_val
                        entrys.append((0, 0, debit_val))
                else:
                    debit_vals = {
                        'name': self.name,
                        'partner_id': self.partner_id.id,
                        'account_id': self.exp_account.id,
                        'debit': self.request_amount > 0.0 and self.request_amount or 0.0,
                        #'analytic_account_id': self.analytic_account.id,
                        'credit': self.request_amount < 0.0 and -self.request_amount or 0.0,
                        'company_id': self.company_id.id,
                    }
                    entrys.append((0, 0, debit_vals))
                vals = {
                    'journal_id': journal.id,
                    'date': self.fa_date,
                    'ref': self.approval_no,
                    'company_id': self.company_id.id,
                    'line_ids': entrys
                    # 'line_ids': [(0, 0, debit_val), (0, 0, credit_val)]
                }
                # add lines
                self.move_id = self.env['account.move'].create(vals)
                self.move_id.action_post()
                # Change state if all went well!
                self.state = 'validate'
                self.ca_app_id = self.env.user.id
            elif self.payment_method_code == 'check_printing':
                self.move_check_followups()
                self.state = 'validate'
                self.ca_app_id = self.env.user.id
        else:
            raise Warning(_("An issue was faced when validating!"))

        # Update footer message
        message_obj = self.env['mail.message']
        message = _("State Changed  Confirm -> <em>%s</em>.") % (self.state)
        msg_id = self.message_post(body=message)
        self.env['mail.activity'].search([('user_id', '=', self.env.uid), ('res_id', '=', self.id)]).action_done()

    
    def set_to_draft(self):
        for rec in self:
            rec.state = 'draft'
            rec.mn_app_id = None
            rec.fm_app_id = None
            rec.gm_app_id = None
            rec.at_app_id = None
    
            # Update footer message
            message_obj = rec.env['mail.message']
            message = _("State Changed  Confirm -> <em>%s</em>.") % (rec.state)
            msg_id = rec.message_post(body=message)
