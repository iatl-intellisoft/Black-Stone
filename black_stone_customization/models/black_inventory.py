# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class StockWarehouse(models.Model):
    _inherit = "stock.warehouse"
    
    stock_number = fields.Char('Stock Number')


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def _employee_get(self):
        record = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)], limit=1)
        return record


    accountant_signature = fields.Many2one('hr.employee',string="Accountant Signature")
    inventory_manager_signature = fields.Many2one('hr.employee',string="Inventory Manager Signature")
    inventory_user_signature = fields.Many2one('hr.employee',
                                               default=_employee_get,
                                               string="Inventory User Signature")
    note = fields.Char('Note',default="company not responsible to deliver same product after 48 hour from printing delivery order, Goods are not returned or exchanged after being withdrawn from the warehouse ")



class ProductTemplate(models.Model):
    _inherit = "product.template"


    incentive = fields.Boolean('Incentive?')


