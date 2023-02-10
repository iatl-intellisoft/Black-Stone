# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL International Pvt. Ltd.
#    Copyright (C) 2020-TODAY Tech-Receptives(<http://www.iatl-sd.com>).
#
###############################################################################

from functools import lru_cache
from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    custom_rate = fields.Float(
        'Currency Rate', default=1, help="Set new currency rate to apply on the payment")
    c_currency_rate = fields.Float(
        'Currency Rate', digits='Second Currency Rate', help="Technical field used to get acctual Currency Rate As 1/custom_rate", compute="_get_currency_rate")

    @api.depends('custom_rate')
    def _get_currency_rate(self):
        """
        get acctual Currency Rate As 1/custom_rate
        """
        for rec in self:
            rec.c_currency_rate = 1/rec.custom_rate

    @api.depends('currency_id', 'company_id', 'move_id.date', 'custom_rate')
    def _compute_currency_rate(self):
        @lru_cache()
        def get_rate(from_currency, to_currency, company, date):
            return self.env['res.currency']._get_conversion_rate(
                from_currency=from_currency,
                to_currency=to_currency,
                company=company,
                date=date,
            )
        for line in self:
            currency_rate = 1
            if line.currency_id and self.env.company.currency_id and line.currency_id != self.env.company.currency_id:
                currency_rate = 1 / line.custom_rate
            line.currency_rate = currency_rate

    # @api.onchange('debit')
    # def _inverse_debit(self):
    #     res = super(AccountMoveLine, self.with_context(
    #         custom_rate=self.currency_rate))._inverse_debit()
    #     return res

    # @api.onchange('credit')
    # def _inverse_credit(self):
    #     res = super(AccountMoveLine, self.with_context(
    #         custom_rate=self.currency_rate))._inverse_credit()
    #     return res

    # @api.onchange('amount_currency', 'custom_rate', 'currency_rate')
    # def _onchange_amount_currency(self):
    #     """Overrides _onchange_amount_currency(), That Recompute the debit/credit
    #     based on amount_currency/currency_id and date to include custom rate in
    #     currency related calculations represented in the context
    #     """
    #     res = super(AccountMoveLine, self.with_context(custom_rate=self.currency_rate))._onchange_amount_currency()
    #     return res

    @api.onchange('amount_currency', 'currency_id', 'custom_rate', 'c_currency_rate')
    def _inverse_amount_currency(self):
        """Overrides _inverse_amount_currency() ,Update custom rate value on change of 
        currency_id/custom_rate values
        """
        # res = super(AccountMoveLine, self.with_context(
        #         custom_rate=self.c_currency_rate))._inverse_amount_currency()
        # return res

        move_type = self._context.get('default_type')
        for rec in self:
            res = super(AccountMoveLine, rec.with_context(
                custom_rate=rec.currency_rate))._inverse_amount_currency()
            today = fields.Date.today()

            if rec.currency_id and move_type == 'entry':
                rec.custom_rate = rec.currency_id._get_conversion_rate(
                    rec.currency_id, rec.move_id.company_id.currency_id, rec.move_id.company_id, rec.move_id.date or today)
            return res

    def _recompute_debit_credit_from_amount_currency(self):
        """Overrides _recompute_debit_credit_from_amount_currency(), That Recompute the debit/credit
        based on amount_currency/currency_id and date to include custom rate in
        currency related calculations represented in the context
        """
        """" in upgrading to 14 this function has been deprecated so we copy it here"""
        for line in self:
            # Recompute the debit/credit based on amount_currency/currency_id and date.
            company_currency = line.account_id.company_id.currency_id
            balance = line.amount_currency
            if line.currency_id and company_currency and line.currency_id != company_currency:
                balance = line.currency_id._convert(balance, company_currency, line.account_id.company_id,
                                                    line.move_id.date or fields.Date.today())
                line.debit = balance > 0 and balance or 0.0
                line.credit = balance < 0 and -balance or 0.0

    @api.onchange('custom_rate')
    def _onchange_custom_rate(self):
        for rec in self:
            rec.with_context(
                custom_rate=rec.c_currency_rate)._recompute_debit_credit_from_amount_currency()
