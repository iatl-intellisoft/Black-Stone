# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################

from odoo import api, fields, models,_
from datetime import datetime
from odoo.tools.float_utils import float_compare, float_is_zero, float_round
from dateutil.relativedelta import relativedelta
from odoo.tools import float_compare
from datetime import timedelta
from odoo.exceptions import UserError, Warning

class SalesOrder(models.Model):
    _inherit = 'sale.order'

    location_sale_id = fields.Many2one('stock.location',string="location" , domain="[('usage','=','internal')]")

class SalesOrderLine(models.Model):
    _inherit = 'sale.order.line'


    def _prepare_procurement_values(self, group_id=False):
        """ Prepare specific key for moves or other components that will be created from a stock rule
        coming from a sale order line. This method could be override in order to add other custom key that could
        be used in move/po creation.
        """
        values = super(SalesOrderLine, self)._prepare_procurement_values(group_id)
        self.ensure_one()
        # Use the delivery date if there is else use date_order and lead time
        date_deadline = self.order_id.commitment_date or (self.order_id.date_order + timedelta(days=self.customer_lead or 0.0))
        date_planned = date_deadline - timedelta(days=self.order_id.company_id.security_lead)
        values.update({
            'group_id': group_id,
            'sale_line_id': self.id,
            'date_planned': date_planned,
            'date_deadline': date_deadline,
            'route_ids': self.route_id,
            'warehouse_id': self.order_id.warehouse_id or False,
            'partner_id': self.order_id.partner_shipping_id.id,
            'product_description_variants': self.with_context(lang=self.order_id.partner_id.lang)._get_sale_order_line_multiline_description_variants(),
            'company_id': self.order_id.company_id,
            'product_packaging_id': self.product_packaging_id,
            'analytic_account_id': self.order_id.analytic_account_id or False,
            'sequence': self.sequence,
            'location_sale_id': self.order_id.location_sale_id,
        })
        return values



class StockRuleInherit(models.Model):
    _inherit = 'stock.rule'

    def _get_stock_move_values(self, product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values):
        res = super(StockRuleInherit,self)._get_stock_move_values(product_id, product_qty, product_uom, location_dest_id, name, origin, company_id, values)
        res.update({'location_id':values.get('location_sale_id').id })
        return res