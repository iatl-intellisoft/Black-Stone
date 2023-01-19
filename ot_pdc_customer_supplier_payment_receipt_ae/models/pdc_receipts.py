#!/usr/bin/env python
# -*- coding: utf-8 -*-
##############################################################################
#    Description: Payment and Receipt Report Customization                   #
#    Author: IntelliSoft Software/ODOOTECH FZE                               #
#    Date: Aug 2015 -  Till Now                                              #
##############################################################################

from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from . import amount_to_ar


# inherited to add features to account_payment
class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    journal_type = fields.Selection('Journal Type', related='journal_id.type')
    check_journal_type = fields.Selection('Check Journal Type', related='journal_id.check_journal_type')
    pdc = fields.Boolean('Post Dated Cheque?')
    check_no = fields.Char("Check No.")
    check_bank_name = fields.Many2one('bank.bank', 'Bank Name')
    check_bank_branch = fields.Char('Bank Branch')
    check_due_date = fields.Date('Check Due Date')
    check_amount_in_words = fields.Char(string="Check Amount In Words", compute='_onchange_amount', readonly=True, store=True)
    customer_vendor = fields.Char("Received From / Paid To")
    date_from = fields.Date("Date From", compute="lambda *a,k:{}")
    date_to = fields.Date("Date To", compute="lambda *a,k:{}")
    check_cleared = fields.Boolean('Check Cleared?', copy=False)
    check_bounced = fields.Boolean('Check Bounced?', copy=False)
    clearance_id = fields.Many2one('account.move', string='Clearance Move', copy=False, readonly=True)
    bounce_id = fields.Many2one('account.move', string='Bounce Move', copy=False, readonly=True)
    check_bank_journal = fields.Many2one('account.journal', string='Cheque Bank Journal')
    so_id = fields.Many2one('sale.order', 'Sale Order')
    batch_pdc_id = fields.Many2one('batch.pdc', string='Batch PDCs', readonly=True)

    # get amount in words
    @api.depends('amount', 'currency_id')
    def _onchange_amount(self):
        for rec in self:
            rec.check_amount_in_words = rec.currency_id and rec.currency_id.amount_to_text(rec.amount) or False

    def _create_payment_vals_from_wizard(self, batch_result):
        res = super(AccountPaymentRegister, self)._create_payment_vals_from_wizard(batch_result)
        res.update({
            'pdc': self.pdc,
            'check_no': self.check_no,
            'check_bank_name': self.check_bank_name.id,
            'check_bank_branch': self.check_bank_branch,
            'check_due_date': self.check_due_date
        })
        return res


class account_payment_payment_receipt_report(models.Model):
    # _name = 'account.payment'
    _inherit = 'account.payment'

    journal_type = fields.Selection('Journal Type', related='journal_id.type')
    check_journal_type = fields.Selection('Check Journal Type', related='journal_id.check_journal_type')
    pdc = fields.Boolean('Post Dated Cheque?')
    check_no = fields.Char("Check No.")
    check_bank_name = fields.Many2one('bank.bank', 'Bank Name')
    check_bank_branch = fields.Char('Bank Branch')
    check_due_date = fields.Date('Check Due Date')
    check_amount_in_words = fields.Char(string="Check Amount in Words", compute='_onchange_amount', readonly=True, store=True)
    customer_vendor = fields.Char("Received From / Paid To")
    date_from = fields.Date("Date From", compute="lambda *a,k:{}")
    date_to = fields.Date("Date To", compute="lambda *a,k:{}")
    check_cleared = fields.Boolean('Check Cleared?', copy=False)
    check_bounced = fields.Boolean('Check Bounced?', copy=False)
    clearance_id = fields.Many2one('account.move', string='Clearance Move', copy=False, readonly=True)
    bounce_id = fields.Many2one('account.move', string='Bounce Move', copy=False, readonly=True)
    check_bank_journal = fields.Many2one('account.journal', string='Cheque Bank Journal')
    so_id = fields.Many2one('sale.order', 'Sale Order')
    batch_pdc_id = fields.Many2one('batch.pdc', string='Batch PDCs', readonly=True)
    payment_type = fields.Selection(selection_add=[('transfer', 'Internal Transfer / Other')],
                                    ondelete={'transfer': 'set default'})
    other = fields.Boolean('Other Payment')
    affect_account_id = fields.Many2one('account.account', string="Affect Account")
    from_account_id = fields.Many2one('account.account', 'From Account')
    arabic_amount_words = fields.Char(string='Arabic Amount in Words', readonly=True, default=False, copy=False,
                                      compute='_compute_text', translate=True)
    analytic_account = fields.Many2one('account.analytic.account', string='Cost/Profit Center')

    ####################################################################################################################
    # return amount in words in arabic. Please note that these 4 functions are related to check payments
    @api.depends('amount')
    def _compute_text(self):
        self.arabic_amount_words = amount_to_ar.amount_to_text_ar(self.amount,
                                                                  self.currency_id.currency_unit_label,
                                                                  self.currency_id.currency_subunit_label)

    def amount_in_word_length1(self):
        am_in_words_1 = ''
        flag = 0
        for word in str(self.arabic_amount_words).split():
            if len(am_in_words_1) < 95 and flag < 15:
                am_in_words_1 += ' ' + word
                flag += 1
        return am_in_words_1

    def amount_in_word_length2(self):
        am_in_words_1 = ''
        am_in_words_2 = ''
        flag = 0
        for word in str(self.arabic_amount_words).split():
            if len(am_in_words_1) < 95 and flag < 15:
                flag += 1
            elif flag >= 15:
                am_in_words_2 += ' ' + word
        return am_in_words_2

    def convert(self, var):
        return '#' + '{:,.2f}'.format(var) + '#'

    ####################################################################################################################
    # auto fetch check bank journal and default credit account
    @api.onchange('journal_id')
    def _get_check_bank_and_journal_and_credit_account(self):
        self.check_bank_journal = self.journal_id.bank_journal_id
        self.from_account_id = self.journal_id.default_account_id

    ####################################################################################################################
    # inherited to add general journal type
    # @api.onchange('payment_type')
    # def _onchange_payment_type(self):
    #     # if not self.invoice_ids:
    #     #     # Set default partner type for the payment type
    #     #     if self.payment_type == 'inbound':
    #     #         self.partner_type = 'customer'
    #     #     elif self.payment_type == 'outbound':
    #     #         self.partner_type = 'supplier'
    #     #     else:
    #     #         self.partner_type = False
    #     # Set payment method domain
    #     res = self._onchange_journal()
    #     # if not res.get('domain', {}):
    #     #     res['domain'] = {}
    #     # jrnl_filters = self._compute_journal_domain_and_types()
    #     # journal_types = jrnl_filters['journal_types']
    #     # journal_types.update(['bank', 'cash', 'general'])
    #     # res['domain']['journal_id'] = jrnl_filters['domain'] + [('type', 'in', list(journal_types))]
    #     return res

    # get amount in words
    @api.depends('amount', 'currency_id')
    def _onchange_amount(self):
        for rec in self:
            rec.check_amount_in_words = rec.currency_id and rec.currency_id.amount_to_text(rec.amount) or False

    ####################################################################################################################
    # select pdc if check_printing is selected in case of send money, i.e. outbound
    @api.onchange('payment_method_code', 'journal_type')
    def _onchange_payment_method_code(self):
        for rec in self:
            if rec.payment_method_code in ['check_printing', 'receivable_check']:
                rec.pdc = True
            if rec.payment_method_code in ['manual']:
                rec.pdc = False

    ####################################################################################################################
    # Change payment type to take into consideration customer checks
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # pdc = vals.get('pdc')
            # payment_type = vals.get('payment_type')
            if vals.get('pdc') and vals.get('payment_type') == 'inbound':
                vals.update({'payment_method_id': self.env['account.payment.method'].search(
                    [('code', '=', 'receivable_check')], limit=1).id})
        return super(account_payment_payment_receipt_report, self).create(vals_list)

    ####################################################################################################################
    # clear check
    def check_clear(self):
        if not self.check_bank_journal:
            raise ValidationError(_("Please choose cheque bank journal first!"))
        self.check_cleared = True
        move_line_lst = []
        # if self.journal_id.sequence_id:
        #     if not self.journal_id.sequence_id.active:
        #         raise ValidationError(
        #             _('Please activate the sequence of selected journal!'))
        #     name = self.journal_id.sequence_id.next_by_id()
        # else:
        #     raise UserError(_('Please define a sequence on the journal!'))
        debit = credit = 0.0
        if self.journal_id.type in ('purchase', 'payment'):
            credit = self.paid_amount_in_company_currency
        elif self.journal_id.type in ('sale', 'receipt'):
            debit = self.paid_amount_in_company_currency
        if debit < 0:
            credit = -debit
            debit = 0.0
        if credit < 0:
            debit = -credit
            credit = 0.0
        debit - credit < 0 and -1 or 1
        # for checks under collection
        if self.pdc and self.payment_type == 'inbound':
            for line in self.move_id.line_ids:
                if line.debit > 0.00:
                    move_line_lst.append((0, 0, {
                        'name': (' Check No.: ' + str(self.check_no) + ', ' + str(
                            self.check_bank_name.name)) or '/',
                        'debit': line.debit,
                        'credit': line.credit,
                        'account_id': self.check_bank_journal.default_account_id.id,
                        'journal_id': self.check_bank_journal.id,
                        'partner_id': self.partner_id.id,
                        'date': self.check_due_date,
                    }))
                else:
                    move_line_lst.append((0, 0, {
                        'name': (' Check No.: ' + str(self.check_no) + ', ' + str(
                            self.check_bank_name.name)) or '/',
                        'debit': line.debit,
                        'credit': line.credit,
                        'account_id': self.journal_id.default_account_id.id,
                        'journal_id': self.journal_id.id,
                        'partner_id': self.partner_id.id,
                        'date': self.check_due_date,
                    }))
            move_vals = {}
            move_vals.update({
                'journal_id': self.check_bank_journal.id,
                'date': self.check_due_date,
                'line_ids': move_line_lst,
            })

            clearance_id = self.env['account.move'].create(move_vals)
            # return back clearance id to payment
            self.clearance_id = clearance_id

        # for outstanding checks
        elif self.pdc and self.payment_type == 'outbound':
            for line in self.move_line_ids:
                if line.credit > 0.00:
                    move_line_lst.append((0, 0, {
                        'name': (self.name + ' Check No.: ' + str(self.check_no) + ', ' + str(
                            self.check_bank_journal.name)) or '/',
                        'debit': line.debit,
                        'credit': line.credit,
                        'account_id': self.check_bank_journal.default_account_id.id,
                        'journal_id': self.check_bank_journal.id,
                        'partner_id': self.partner_id.id,
                        'date': self.check_due_date,
                    }))
                else:
                    move_line_lst.append((0, 0, {
                        'name': (self.name + ' Check No.: ' + str(self.check_no) + ', ' + str(
                            self.check_bank_journal.name)) or '/',
                        'debit': line.debit,
                        'credit': line.credit,
                        'account_id': self.journal_id.default_account_id.id,
                        'journal_id': self.journal_id.id,
                        'partner_id': self.partner_id.id,
                        'date': self.check_due_date,
                    }))
            move_vals = {}
            move_vals.update({
                'name': name,
                'journal_id': self.check_bank_journal.id,
                'date': self.check_due_date,
                'line_ids': move_line_lst,
            })

            clearance_id = self.env['account.move'].create(move_vals)
            # return back clearance id to payment
            self.clearance_id = clearance_id
        ##########################
        # other payment scenarios#
        # ########################
        elif self.pdc and self.payment_type == 'transfer' and self.other and self.journal_id.check_journal_type == 'cuc':
            # same check under collection scenario
            for line in self.move_line_ids:
                if line.debit > 0.00:
                    move_line_lst.append((0, 0, {
                        'name': (self.name + ' Check No.: ' + str(self.check_no) + ', ' + str(
                            self.check_bank_name.name)) or '/',
                        'debit': line.debit,
                        'credit': line.credit,
                        'account_id': self.check_bank_journal.default_account_id.id,
                        'journal_id': self.check_bank_journal.id,
                        'partner_id': self.partner_id.id,
                        'date': self.check_due_date,
                    }))
                else:
                    move_line_lst.append((0, 0, {
                        'name': (self.name + ' Check No.: ' + str(self.check_no) + ', ' + str(
                            self.check_bank_name.name)) or '/',
                        'debit': line.debit,
                        'credit': line.credit,
                        'account_id': self.journal_id.default_account_id.id,
                        'journal_id': self.journal_id.id,
                        'partner_id': self.partner_id.id,
                        'date': self.check_due_date,
                    }))
            move_vals = {}
            move_vals.update({
                'name': name,
                'journal_id': self.check_bank_journal.id,
                'date': self.check_due_date,
                'line_ids': move_line_lst,
            })

            clearance_id = self.env['account.move'].create(move_vals)
            # return back clearance id to payment
            self.clearance_id = clearance_id

        elif self.pdc and self.payment_type == 'transfer' and self.other and self.journal_id.check_journal_type == 'osc':
            # same outstanding checks scenario
            for line in self.move_line_ids:
                if line.credit > 0.00:
                    move_line_lst.append((0, 0, {
                        'name': (self.name + ' Check No.: ' + str(self.check_no) + ', ' + str(
                            self.check_bank_journal.name)) or '/',
                        'debit': line.debit,
                        'credit': line.credit,
                        'account_id': self.check_bank_journal.default_account_id.id,
                        'journal_id': self.check_bank_journal.id,
                        'partner_id': self.partner_id.id,
                        'date': self.check_due_date,
                    }))
                else:
                    move_line_lst.append((0, 0, {
                        'name': (self.name + ' Check No.: ' + str(self.check_no) + ', ' + str(
                            self.check_bank_journal.name)) or '/',
                        'debit': line.debit,
                        'credit': line.credit,
                        'account_id': self.journal_id.default_account_id.id,
                        'journal_id': self.journal_id.id,
                        'partner_id': self.partner_id.id,
                        'date': self.check_due_date,
                    }))
            move_vals = {}
            move_vals.update({
                'name': name,
                'journal_id': self.check_bank_journal.id,
                'date': self.check_due_date,
                'line_ids': move_line_lst,
            })

            clearance_id = self.env['account.move'].create(move_vals)
            # return back clearance id to payment
            self.clearance_id = clearance_id

        # other weird case of accepting payments other than customers
        elif self.pdc and self.payment_type == 'transfer' and self.journal_type == 'general':
            # odd scenario
            for line in self.move_line_ids:
                if line.debit > 0.00:
                    move_line_lst.append((0, 0, {
                        'name': (self.name + ' Check No.: ' + str(self.check_no) + ', ' + str(
                            self.check_bank_name.name)) or '/',
                        'debit': line.debit,
                        'credit': line.credit,
                        'account_id': self.check_bank_journal.default_account_id.id,
                        'journal_id': self.check_bank_journal.id,
                        'partner_id': self.partner_id.id,
                        'date': self.check_due_date,
                    }))
                else:
                    move_line_lst.append((0, 0, {
                        'name': (self.name + ' Check No.: ' + str(self.check_no) + ', ' + str(
                            self.check_bank_name.name)) or '/',
                        'debit': line.debit,
                        'credit': line.credit,
                        'account_id': self.affect_account_id.id,
                        'journal_id': self.journal_id.id,
                        'partner_id': self.partner_id.id,
                        'date': self.check_due_date,
                    }))
            move_vals = {}
            move_vals.update({
                'name': name,
                'journal_id': self.check_bank_journal.id,
                'date': self.check_due_date,
                'line_ids': move_line_lst,
            })

            clearance_id = self.env['account.move'].create(move_vals)
            # return back clearance id to payment
            self.clearance_id = clearance_id

    ####################################################################################################################
    # cancel payment and mark as bounces
    def check_bounce(self):
        self.check_bounced = True
        move_line_lst = []
        # if self.journal_id.sequence_id:
        #     if not self.journal_id.sequence_id.active:
        #         raise ValidationError(
        #             _('Please activate the sequence of selected journal !'))
        #     name = self.journal_id.sequence_id.next_by_id()
        # else:
        #     raise UserError(_('Please define a sequence on the journal.'))
        debit = credit = 0.0
        if self.journal_id.type in ('purchase', 'payment'):
            credit = self.paid_amount_in_company_currency
        elif self.journal_id.type in ('sale', 'receipt'):
            debit = self.paid_amount_in_company_currency
        if debit < 0:
            credit = -debit
            debit = 0.0
        if credit < 0:
            debit = -credit
            credit = 0.0
        debit - credit < 0 and -1 or 1
        # for checks under collection
        if self.pdc and self.payment_type == 'inbound':
            for line in self.move_id.line_ids:
                if line.debit > 0.00:
                    move_line_lst.append((0, 0, {
                        'name': (' Bounced Check No.: ' + str(self.check_no) + ', ' + ', ' + str(
                            self.check_bank_name.name)) or '/',
                        'debit': line.debit,
                        'credit': line.credit,
                        'account_id': self.partner_id.property_account_receivable_id.id,
                        'journal_id': self.journal_id.id,
                        'partner_id': self.partner_id.id,
                        'date': self.check_due_date,
                    }))
                else:
                    move_line_lst.append((0, 0, {
                        'name': (' Bounced Check No.: ' + str(self.check_no) + ', ' + ', ' + str(
                            self.check_bank_name.name)) or '/',
                        'debit': line.debit,
                        'credit': line.credit,
                        'account_id': self.journal_id.default_account_id.id,
                        'journal_id': self.journal_id.id,
                        'partner_id': self.partner_id.id,
                        'date': self.check_due_date,
                    }))
            move_vals = {}
            move_vals.update({
                'journal_id': self.journal_id.id,
                'date': self.check_due_date,
                'line_ids': move_line_lst,
            })

            bounce_id = self.env['account.move'].create(move_vals)
            # return back bounce id to payment
            self.bounce_id = bounce_id

        # for outstanding checks
        elif self.pdc and self.payment_type == 'outbound':
            for line in self.move_line_ids:
                if line.credit > 0.00:
                    move_line_lst.append((0, 0, {
                        'name': (self.name + ' Bounced Check No.: ' + str(self.check_no) + ', ' + ', ' + str(
                            self.check_bank_journal.name)) or '/',
                        'debit': line.debit,
                        'credit': line.credit,
                        'account_id': self.partner_id.property_account_payable_id.id,
                        'journal_id': self.journal_id.id,
                        'partner_id': self.partner_id.id,
                        'date': self.check_due_date,
                    }))
                else:
                    move_line_lst.append((0, 0, {
                        'name': (self.name + ' Bounced Check No.: ' + str(self.check_no) + ', ' + ', ' + str(
                            self.check_bank_journal.name)) or '/',
                        'debit': line.debit,
                        'credit': line.credit,
                        'account_id': self.journal_id.default_account_id.id,
                        'journal_id': self.journal_id.id,
                        'partner_id': self.partner_id.id,
                        'date': self.check_due_date,
                    }))
            move_vals = {}
            move_vals.update({
                'name': name,
                'journal_id': self.journal_id.id,
                'date': self.check_due_date,
                'line_ids': move_line_lst,
            })

            bounce_id = self.env['account.move'].create(move_vals)
            # return back bounce id to payment
            self.bounce_id = bounce_id

            ##########################
            # other payment scenarios#
            # ########################
        elif self.pdc and self.payment_type == 'transfer' and self.other and self.journal_id.check_journal_type == 'osc':
            for line in self.move_line_ids:
                if line.debit > 0.00:
                    move_line_lst.append((0, 0, {
                        'name': (self.name + ' Bounced Check No.: ' + str(self.check_no) + ', ' + ', ' + str(
                            self.check_bank_name.name)) or '/',
                        'debit': line.debit,
                        'credit': line.credit,
                        'account_id': self.from_account_id.id,
                        'journal_id': self.journal_id.id,
                        'partner_id': self.partner_id.id,
                        'date': self.check_due_date,
                    }))
                else:
                    move_line_lst.append((0, 0, {
                        'name': (self.name + ' Bounced Check No.: ' + str(self.check_no) + ', ' + ', ' + str(
                            self.check_bank_name.name)) or '/',
                        'debit': line.debit,
                        'credit': line.credit,
                        'account_id': self.affect_account_id.id,
                        'journal_id': self.journal_id.id,
                        'partner_id': self.partner_id.id,
                        'date': self.check_due_date,
                    }))
            move_vals = {}
            move_vals.update({
                'name': name,
                'journal_id': self.journal_id.id,
                'date': self.check_due_date,
                'line_ids': move_line_lst,
            })

            bounce_id = self.env['account.move'].create(move_vals)
            # return back bounce id to payment
            self.bounce_id = bounce_id

        # other weird case of accepting payments other than customers - here we consider bouncing the check
        elif self.pdc and self.payment_type == 'transfer' and self.journal_type == 'general':
            # odd scenario
            for line in self.move_line_ids:
                if line.debit > 0.00:
                    move_line_lst.append((0, 0, {
                        'name': (self.name + ' Bounced Check No.: ' + str(self.check_no) + ', ' + ', ' + str(
                            self.check_bank_name.name)) or '/',
                        'debit': line.debit,
                        'credit': line.credit,
                        'account_id': self.from_account_id.id,
                        'journal_id': self.journal_id.id,
                        'partner_id': self.partner_id.id,
                        'date': self.check_due_date,
                    }))
                else:
                    move_line_lst.append((0, 0, {
                        'name': (self.name + ' Bounced Check No.: ' + str(self.check_no) + ', ' + ', ' + str(
                            self.check_bank_name.name)) or '/',
                        'debit': line.debit,
                        'credit': line.credit,
                        'account_id': self.affect_account_id.id,
                        'journal_id': self.journal_id.id,
                        'partner_id': self.partner_id.id,
                        'date': self.check_due_date,
                    }))
            move_vals = {}
            move_vals.update({
                'name': name,
                'journal_id': self.journal_id.id,
                'date': self.check_due_date,
                'line_ids': move_line_lst,
            })

            bounce_id = self.env['account.move'].create(move_vals)
            # return back bounce id to payment
            self.bounce_id = bounce_id

    ####################################################################################################################
    # created for transfer/other payment type
    def _create_other_payment_entry(self, amount):
        """ Create a journal entry corresponding to a payment of type other.
        """
        # generate move vals
        debit_vals = {
            'name': self.name,
            'account_id': self.affect_account_id.id,
            'debit': self.amount,
            'company_id': self.company_id.id,
            'payment_id': self.id
        }

        credit_vals = {
            'name': self.name,
            'account_id': self.from_account_id.id,
            'credit': self.amount,
            'company_id': self.company_id.id,
            'payment_id': self.id
        }

        vals = {
            'journal_id': self.journal_id.id,
            'date': datetime.today(),
            'ref': self.ref and ("Other payment: " + str(self.ref)) or "Other Payment",
            'company_id': self.company_id.id,
            'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
        }

        move = self.env['account.move'].create(vals)

        # validate the payment
        if not self.journal_id.post_at_bank_rec:
            move.post()

        return move

    ####################################################################################################################
    # created to accommodate for transfer/other payment type
    # def post(self):
    #     """ Create the journal items for the payment and update the payment's state to 'posted'.
    #         A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
    #         and another in the destination reconcilable account (see _compute_destination_account_id).
    #         If invoice_ids is not empty, there will be one reconcilable move line per invoice to reconcile with.
    #         If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
    #     """
    #     # raise error for other payment type and affect account not selected
    #     if self.payment_type == 'transfer' and self.other and not self.affect_account_id:
    #         raise ValidationError(_('Please select the account to be affected with your payment!'))
    #     elif self.payment_type in ['inbound', 'outbound'] and self.journal_type == 'general':
    #         raise ValidationError(_(
    #             'Sorry, you are not allowed to post an entry with a journal of type Miscellaneous for the selected payment type!'))
    #     elif self.payment_type == 'transfer' and self.journal_id.check_journal_type == 'cuc':
    #         raise ValidationError(_("For this payment type, kindly select a journal of type Miscellaneous."))

    #     for rec in self:

    #         if rec.state != 'draft':
    #             raise UserError(_("Only a draft payment can be posted."))

    #         # if any(inv.state != 'open' for inv in rec.invoice_ids):
    #         #     raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))

    #         # keep the name in case of a payment reset to draft
    #         if not rec.name:
    #             # Use the right sequence to set the name
    #             if rec.payment_type == 'transfer':
    #                 sequence_code = 'account.payment.transfer'
    #             else:
    #                 if rec.partner_type == 'customer':
    #                     if rec.payment_type == 'inbound':
    #                         sequence_code = 'account.payment.customer.invoice'
    #                     if rec.payment_type == 'outbound':
    #                         sequence_code = 'account.payment.customer.refund'
    #                 if rec.partner_type == 'supplier':
    #                     if rec.payment_type == 'inbound':
    #                         sequence_code = 'account.payment.supplier.refund'
    #                     if rec.payment_type == 'outbound':
    #                         sequence_code = 'account.payment.supplier.invoice'
    #             rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(
    #                 sequence_code)
    #             if not rec.name and rec.payment_type != 'transfer':
    #                 raise UserError(_("You have to define a sequence for %s in your company.") % (sequence_code,))

    #         # Create the journal entry
    #         amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
    #         if not self.other:
    #             move = rec._create_payment_entry(amount)
    #         elif self.other:
    #             # IntelliSoft magic ;-), user an alternative version of payment method
    #             move = rec._create_other_payment_entry(amount)
    #         persist_move_name = move.name

    #         # In case of a transfer, the first journal entry created debited the source liquidity account and credited
    #         # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
    #         if rec.payment_type == 'transfer' and not self.other:
    #             transfer_credit_aml = move.line_ids.filtered(
    #                 lambda r: r.account_id == rec.company_id.transfer_account_id)
    #             transfer_debit_aml = rec._create_transfer_entry(amount)
    #             (transfer_credit_aml + transfer_debit_aml).reconcile()
    #             persist_move_name += self._get_move_name_transfer_separator() + transfer_debit_aml.move_id.name

    #         rec.write({'state': 'posted', 'move_name': persist_move_name})

    #     # check accounts and if an alaytical account is on payment, affect debit account
    #     if self.analytic_account:
    #         for rec in self.move_line_ids:
    #             if rec.debit != 0:
    #                 rec.analytic_account_id = self.analytic_account.id

    #     return True

    ####################################################################################################################
    # notify accountants of checks due
    # check due dates and notify accountant
    @api.model
    def process_checks_due(self):
        # get all checks
        checks_obj = self.env['account.payment'].search([('pdc', '=', 'True')])
        for check in checks_obj:
            # check_due
            if check.check_due_date and not (check.check_cleared or check.check_bounced):
                check_due_days = int(
                    (datetime.strptime(str(check.check_due_date), '%Y-%m-%d') - datetime.now()).days)

                if check_due_days < check.company_id.checks_notification_days:
                    # first get all accountants
                    accountants = self.env['res.users'].search(
                        [("groups_id", "=", self.env.ref("account.group_account_user").id),
                         ('company_id', '=', check.company_id.id)])

                    # then schedule activity to notify about checks due
                    for accountant in accountants:
                        vals = {
                            'activity_type_id': self.env['mail.activity.type'].sudo().search(
                                [('name', 'like', 'Check Due')],
                                limit=1).id,
                            'res_id': check.id,
                            'res_model_id': self.env['ir.model'].sudo().search([('model', '=', 'account.payment')],
                                                                               limit=1).id,
                            'user_id': accountant.id or 1,
                            'summary': self.name,
                        }
                # add lines
                self.env['mail.activity'].sudo().create(vals)
        return True


# Banks
class Banks(models.Model):
    _name = 'bank.bank'
    _description = 'A lookup for banks.'

    name = fields.Char('Bank Name', required=True)
