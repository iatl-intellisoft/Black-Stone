###############################################################################
#
#    IATL International Pvt. Ltd.
#    Copyright (C) 2018-TODAY Tech-Receptives(<http://www.iatl-sd.com>).
#
###############################################################################
import re
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.misc import format_date


class StockScrap(models.Model):
    _inherit = 'stock.scrap'


    partner_id = fields.Many2one('res.partner','Customer')

    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('sale_order','Sale Order')
    ],string='Status', default="draft", readonly=True, tracking=True)

    def action_sale_order(self):
        he_obj = self.env['sale.order']
        he_vals = {
            'partner_id': self.partner_id.id,
            'date_order': self.date_done,
        }
        order_id = he_obj.create(he_vals)
        for line in self:
            self.env['sale.order.line'].create({
                'product_id': line.product_id.id,
                'product_uom_qty': line.scrap_qty,
                'product_uom':line.product_uom_id.id,
                'order_id':order_id.id,
            })
        self.write({'state': "sale_order"})




class StockLandedCostLines(models.Model):
    _inherit = 'stock.landed.cost'

    currency_id = fields.Many2one('res.currency')



class StockMove(models.Model):
    _inherit = 'stock.move'

    num_krtona = fields.Float(string='NO Of  Sale Krtona',related='sale_line_id.product_packaging_qty')
    num_krtona_purchase = fields.Float(string='NO Of Purchase Krtona',related='purchase_line_id.product_packaging_qty')


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    num_krtona = fields.Float(string='Krtona')










