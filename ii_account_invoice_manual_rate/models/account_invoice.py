# -*- coding: utf-8 -*-
#######################################################################
#     Copyright (C) 2023 IATL IntelliSoft Business Solutions Co. Ltd. #
#     (<https://www.iatl-intellisoft.com>) all rights reserved.       #
#######################################################################

from odoo import fields, models, api


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    custom_rate = fields.Float('Currency Rate', default=1, help="Set new currency rate to apply on the invoice")
    currency_rate = fields.Float('Currency Rate', digits='Second Currency Rate', help="Technical field used to get acctual Currency Rate As 1/custom_rate", compute="_get_currency_rate")

    @api.depends('custom_rate')
    def _get_currency_rate(self):
        """
        get acctual Currency Rate As 1/custom_rate
        """
        for rec in self:
            rec.currency_rate = 1/rec.custom_rate
            # rec.currency_rate = rec.currency_id.round(1/rec.custom_rate)

    def action_post(self):
        """Overrides post(), that Creates the journal items for the payment and
          update the move state to 'posted' with inclusion to custom rate
          to use in currency related calculations.
        """
        res = super(AccountInvoice, self.with_context(custom_rate=self.currency_rate)).action_post()
        return res

    @api.onchange('currency_id', 'invoice_date')
    def _onchange_currency_date(self):
        # Update custom rate value onchange of date value
        today = fields.Date.today()
        self.custom_rate = self.currency_id._get_conversion_rate(self.currency_id, self.company_id.currency_id, self.company_id, self.invoice_date or today)
        self._onchange_custom_rate()

    @api.onchange('custom_rate', 'currency_rate')
    def _onchange_custom_rate(self):
        for rec in self:
            for line in rec.line_ids:
                line.custom_rate = rec.custom_rate
                line.with_context(custom_rate=rec.currency_rate)._recompute_debit_credit_from_amount_currency()


# class AccountMoveLine(models.Model):
#     _inherit = "account.move.line"

    # def _get_fields_onchange_subtotal(self, price_subtotal=None, move_type=None, currency=None, company=None, date=None):
    #     """Overrides _get_fields_onchange_subtotal(),Witch used to recompute the values of 'quantity', 'discount', 'price_unit' due to a change made
    #     in some accounting fields such as 'balance' ,with inclusion to custom rate
    #     to use in currency related calculations. 
    #     """
    #     res = super(AccountMoveLine, self.with_context(custom_rate=self.currency_rate)
    #                 )._get_fields_onchange_subtotal(price_subtotal, move_type, currency, company, date)
    #     return res
