##############################################################################
#    Description: Payment and Receipt Report Customization                   #
#    Author: IntelliSoft Software/ODOOTECH FZE                               #
#    Date: Aug 2015 -  Till Now                                              #
##############################################################################

from odoo import fields, models, api


class AccountJournal(models.Model):
    _inherit = "account.journal"

    bank_journal_id = fields.Many2one('account.journal', 'Journal',
                                      help='If check gets cleared, payment entry will be done in this journal.')
    check_journal_type = fields.Selection(selection=[('na', 'Not Applicable'), ('cuc', 'Cheques Under Collection'),
                                        ('osc', 'Outstanding Cheques')], string='Cheque Journal Type',
                                        default='na', help="Choose the cheque journal type if applicable.")


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['receivable_check'] = {'mode': 'multi', 'domain': [('type', '=', 'bank')]}
        return res

################################################################################################################
