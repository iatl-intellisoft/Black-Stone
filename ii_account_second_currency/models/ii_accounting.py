# -*- coding: utf-8 -*-
#######################################################################
#     Copyright (C) 2023 IATL IntelliSoft Business Solutions Co. Ltd. #
#     (<https://www.iatl-intellisoft.com>) all rights reserved.       #
#######################################################################

from odoo import fields, models, api


class AccountMove(models.Model):
    _inherit = 'account.move'

    second_currency_id = fields.Many2one(
        'res.currency', string="Secondary Currency", related='company_id.second_currency_id')
    second_currency_rate = fields.Float(
        related='second_currency_id.rate', string="Currency Rate", required=True)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    second_currency_id = fields.Many2one(
        'res.currency', related='move_id.second_currency_id', string="Secondary Currency", store=True, invisible=True)
    second_currency_debit = fields.Float(
        string="Secondary Currency Debit", compute='second_currency_equivalent', store=True, digits=(12,2))
    second_currency_credit = fields.Float(
        string="Secondary Currency Credit", compute='second_currency_equivalent', store=True, digits=(12,2))
    second_currency_balance = fields.Float(
        string="Secondary Currency Balance", compute='second_currency_equivalent', store=True, digits=(12,2))
    second_currency_amount_residual = fields.Float(
        string="Secondary Currency Amount Residual", compute='second_currency_equivalent', store=True)
    second_currency_amount_currency = fields.Float(
        string="Secondary Amount Currency", compute='second_currency_equivalent', store=True, digits=(12,2))

    @api.depends('debit', 'credit', 'balance', 'amount_residual', 'move_id.second_currency_rate', 'move_id.second_currency_id')
    def second_currency_equivalent(self):
        for rec in self:
            rec.second_currency_debit = rec.debit * rec.move_id.second_currency_rate
            rec.second_currency_credit = rec.credit * rec.move_id.second_currency_rate
            rec.second_currency_balance = rec.balance * rec.move_id.second_currency_rate
            rec.second_currency_amount_residual = rec.amount_residual * \
                rec.move_id.second_currency_rate
            if rec.move_id.currency_id != rec.move_id.second_currency_id or rec.move_id.currency_id == rec.company_id.currency_id:
                rec.second_currency_amount_currency = (
                    rec.debit or rec.credit) * rec.move_id.second_currency_rate
            if rec.move_id.currency_id == rec.move_id.second_currency_id:
                rec.second_currency_amount_currency = rec.amount_currency
