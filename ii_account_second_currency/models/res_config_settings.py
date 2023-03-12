# -*- coding: utf-8 -*-
#######################################################################
#     Copyright (C) 2023 IATL IntelliSoft Business Solutions Co. Ltd. #
#     (<https://www.iatl-intellisoft.com>) all rights reserved.       #
#######################################################################

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    second_currency_id = fields.Many2one(
        'res.currency', string="Secondary Currency", default=lambda self: self.env.ref('base.USD'), required=True)


class ConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    second_currency_id = fields.Many2one('res.currency', string="Secondary Currency",
                                         related='company_id.second_currency_id', required=True, readonly=False)
