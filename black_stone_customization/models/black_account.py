from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class AccountMove(models.Model):
    _inherit = 'account.move'

    warehouse_id = fields.Many2one('stock.warehouse',string='Warehouse')
    stock_number = fields.Char(related="warehouse_id.stock_number", readonly=True, string="Stock Number")