# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL International Pvt. Ltd.
#    Copyright (C) 2020-TODAY Tech-Receptives(<http://www.iatl-sd.com>).
#
###############################################################################

from odoo import fields, models, api


class account_payment(models.Model):
    _inherit = "account.payment"

    custom_rate = fields.Float(
        'Currency Rate', default=1, help="Set new currency rate to apply on the payment")
    currency_rate = fields.Float('Currency Rate', digits='Second Currency Rate',
                                 help="Technical field used to get acctual Currency Rate As 1/custom_rate",
                                 compute="_get_currency_rate")
    # field payment_date has been deprecated in 14 so we add it here
    payment_date = fields.Date(string='Date', default=fields.Date.context_today, required=True, readonly=True,
                               states={'draft': [('readonly', False)]}, copy=False, tracking=True)

    @api.depends('custom_rate')
    def _get_currency_rate(self):
        """
        get acctual Currency Rate As 1/custom_rate
        """
        for rec in self:
            rec.currency_rate = 1 / rec.custom_rate

    def post(self):
        """Overrides post(), that Creates the journal items for the payment and
          update the payment's state to 'posted' with inclusion to custom rate
          to use in currency related calculations.
        """
        res = super(account_payment, self.with_context(
            custom_rate=self.currency_rate)).post()
        return res

    def _prepare_payment_moves(self):
        """Overrides _prepare_payment_moves(),That prepares the creation of journal entries (account.move) by creating a list of python dictionary to be passed
        to the 'create' method.
        """
        res = super(account_payment, self)._prepare_payment_moves()
        for rec in res:
            for line in rec['line_ids']:
                if line[2]:
                    line[2]['custom_rate'] = self.custom_rate
        return res

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        payments = super(account_payment, self.with_context(is_payment=True))\
            .create(vals_list)\
            .with_context(is_payment=False)
        
        for i, pay in enumerate(payments):
            to_write = {'custom_rate': pay.custom_rate}
            pay.move_id.write(to_write)

        return payments