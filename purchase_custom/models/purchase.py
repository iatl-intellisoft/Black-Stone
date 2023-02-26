# -*- coding: utf-8 -*-
###############################################################################
#
#    IATL-Intellisoft International Pvt. Ltd.
#    Copyright (C) 2021 Tech-Receptives(<http://www.iatl-intellisoft.com>).
#
###############################################################################

from odoo import api, fields, models,_

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    location_id = fields.Many2one('stock.location',string="location", domain="[('usage','=','internal')]")


class PurchaseOrderInherit(models.Model):
    _inherit = 'purchase.order'

    def _prepare_picking(self):
        res = super(PurchaseOrderInherit,self)._prepare_picking()
        res.update({'location_id':self.location_id.id})
        return res


