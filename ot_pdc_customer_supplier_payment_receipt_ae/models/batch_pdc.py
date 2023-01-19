##############################################################################
#    Description: Payment and Receipt Report Customization                   #
#    Author: IntelliSoft Software/ODOOTECH FZE                               #
#    Date: Aug 2015 -  Till Now                                              #
##############################################################################

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class batch_pdc(models.Model):
    _name = 'batch.pdc'
    _description = 'Handle batch PDCs.'
    _inherit = ['mail.thread']

    name = fields.Char('Batch PDCs Summary', readonly=True, compute='_get_pdc_summary', store=True)
    partner = fields.Many2one('res.partner', string='Customer', required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.user.company_id.currency_id)
    payment_amount = fields.Monetary(string='Payment Amount', currency_field='currency_id', required=True,
                                     tracking=True)
    check_bank_name = fields.Many2one('bank.bank', 'Bank Name', required=True, tracking=True)
    check_bank_branch = fields.Char('Bank Branch', tracking=True)
    payment_date = fields.Date('Payment Date', default=datetime.today().date(), tracking=True)
    no_of_checks = fields.Integer('No. of Cheques', tracking=True)
    check_start_from_no = fields.Integer("Start from Cheque No.", tracking=True)
    check_start_from_date = fields.Date("Start from Cheque Date", tracking=True)
    batch_pdc_detail_ids = fields.One2many('batch.pdc.detail', 'batch_pdc_id', 'Cheque Details', tracking=True)
    generated_checks = fields.Boolean('Generated Cheques', default=False)
    add_checks = fields.Boolean(string='Add Cheques')
    state = fields.Selection([('draft', 'Draft'), ('done', 'Done')], string='Status', default='draft', tracking=True)
    so_id = fields.Many2one('sale.order', string='Sale Order')
    total = fields.Monetary("Total", compute='_get_total', store=True)
    check_amount_in_words = fields.Char(string="Amount In Words", compute='_get_total', readonly=True, store=True)


    # get PDC summary
    @api.depends('partner', 'payment_date', 'no_of_checks')
    def _get_pdc_summary(self):
        self.name = (self.partner and ("Partner: " + str(self.partner.name)) or " ") + "/" + (
                self.payment_date and ("Payment Date: " + str(self.payment_date)) or " ") + "/" \
                    + (self.no_of_checks and ("No. of Cheques: " + str(self.no_of_checks)) or " ")

    # generate checks based on supplied info
    def generate_checks(self):
        check_counter = self.check_start_from_no
        check_date = self.check_start_from_date
        counter = self.no_of_checks
        seq = 1
        total = 0

        while counter > 0:
            vals = {'batch_pdc_id': self.id,
                    'check_no': check_counter,
                    'payment_amount': self.payment_amount,
                    'check_due_date': check_date,
                    'sequence': seq}
            self.batch_pdc_detail_ids.create(vals)
            check_counter += 1
            check_date = check_date + relativedelta(months=+1)
            counter -= 1
            seq += 1

        # flag that checks have been generated to avoid them being generated again
        self.generated_checks = True
        message = _("PDCs to be received in batch, have been generated.")
        self.message_post(body=message)

    @api.depends('batch_pdc_detail_ids')
    def _get_total(self):
        self.total = 0
        for rec in self.batch_pdc_detail_ids:
            self.total += rec.payment_amount
            self.check_amount_in_words = rec.currency_id.amount_to_text(self.total)

    # generate payments
    def generate_payments(self):
        cuc_journal_id = self.env.user.company_id.default_checks_under_collection_journal_id.id
        if not cuc_journal_id:
            raise ValidationError(_("Please configure cheque under collection journal first!"))
        else:
            for rec in self.batch_pdc_detail_ids:
                vals = {'payment_type': 'inbound',
                        'partner_type': 'customer',
                        'partner_id': self.partner.id,
                        'amount': rec.payment_amount,
                        'journal_id': cuc_journal_id,
                        'payment_method_line_id': self.env.ref('ot_pdc_customer_supplier_payment_receipt_ae.customer_checks').id,
                        'pdc': True,
                        'check_no': rec.check_no,
                        'check_bank_name': self.check_bank_name.id,
                        'check_bank_branch': self.check_bank_branch,
                        'check_due_date': rec.check_due_date,
                        'date': self.payment_date,
                        'batch_pdc_id': self.id,
                        'so_id': self.so_id.id}
                rec.payment_id = self.env['account.payment'].create(vals)
        self.state = 'done'
        message = _("State Changed  Confirm -> <em>%s</em>. Payments have been generated.") % (self.state)
        self.message_post(body=message)

    # reset PDC
    def reset(self):
        self.state = 'draft'
        message = _("State Changed  Confirm -> <em>%s</em>.") % (self.state)
        self.message_post(body=message)


class batch_pdc_detail(models.Model):
    _name = 'batch.pdc.detail'
    _inherit = ['mail.thread']
    _description = 'Individual lines for cheques.'

    batch_pdc_id = fields.Many2one('batch.pdc', 'Batch PDCs', ondelete='cascade')
    check_no = fields.Char('Cheque No.', required=True, tracking=True)
    currency_id = fields.Many2one('res.currency', 'Currency', default=lambda self: self.env.user.company_id.currency_id)
    payment_amount = fields.Monetary(string='Payment Amount', currency_field='currency_id', required=True,
                                     tracking=True)
    check_due_date = fields.Date('Check Due Date', required=True, tracking=True)
    sequence = fields.Integer('#', readonly=True)
    payment_id = fields.Many2one('account.payment', 'Generated Payment', readonly=True)
