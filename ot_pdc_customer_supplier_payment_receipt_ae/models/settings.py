# -*- coding: utf-8 -*-
##############################################################################
#
#    odoo, Open Source Management Solution
#    Copyright (C) 2015-Today ODOOTECH FZE (<http://www.odootech-fze.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
##############################################################################

from odoo import fields, models


class ExtendCompany(models.Model):
    _inherit = 'res.company'

    checks_notification_days = fields.Integer('Check Notification Before (Days)',
                                              help='No. of days to notify before check due date.', required=True,
                                              default=1)
    default_checks_under_collection_journal_id = fields.Many2one('account.journal',
                                                                 string="Default Cheques Under Collection Journal")
