# -*- coding: utf-8 -*-
#######################################################################
#     Copyright (C) 2023 IATL IntelliSoft Business Solutions Co. Ltd. #
#     (<https://www.iatl-intellisoft.com>) all rights reserved.       #
#######################################################################

from odoo import fields, models, api


class Currency(models.Model):
    _inherit = "res.currency"

    @api.model
    def _get_conversion_rate(self, from_currency, to_currency, company, date):
        """override _get_conversion_rate(), to perform calculations based on custom rate
        """
        res = super(Currency, self)._get_conversion_rate(from_currency, to_currency, company, date)
        if self._context.get('custom_rate'):
            custom_rate = self._context.get('custom_rate')
            currency_rates = (from_currency + to_currency)._get_rates(company, date)
            res = currency_rates.get(to_currency.id) / custom_rate
        return res
