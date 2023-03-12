# -*- coding: utf-8 -*-
#######################################################################
#     Copyright (C) 2023 IATL IntelliSoft Business Solutions Co. Ltd. #
#     (<https://www.iatl-intellisoft.com>) all rights reserved.       #
#######################################################################

from odoo import models, fields, api, _


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    custom_rate = fields.Float(
        'Currency Rate', default=1, help="Set new currency rate to apply on the payment")

    @api.onchange('custom_rate')
    def _onchange_currency_rate(self):

        for wizard in self:
            if not(wizard.source_currency_id == wizard.currency_id or wizard.currency_id == wizard.company_id.currency_id):
                wizard.amount = wizard.source_amount * wizard.custom_rate

    def _create_payment_vals_from_wizard(self, batch_result):
        payment_vals = super(AccountPaymentRegister,
                             self)._create_payment_vals_from_wizard(batch_result)
        payment_vals['custom_rate'] = self.custom_rate

        return payment_vals

    def _create_payments(self):
        payments = super(AccountPaymentRegister, self)._create_payments()
        for payment in payments:
            payment.custom_rate = self.custom_rate
        return payments


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        ''' draft -> posted '''
        for line in self.move_id.line_ids:
            line.custom_rate = self.custom_rate
        return super(AccountPayment, self).action_post()
