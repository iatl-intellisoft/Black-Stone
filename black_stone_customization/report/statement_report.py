# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, tools, _
import xlsxwriter
import base64
from io import StringIO, BytesIO
from odoo.exceptions import Warning as UserError


class WizardAccount(models.Model):
    _name = 'wizard.account'
    _description = 'Print all Partners'

    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)
    account_id = fields.Many2one('account.account', 'Account', required=True)

    def print_report(self):
        for report in self:
            from_date = report.from_date
            to_date = report.to_date
            account_id = report.account_id
            if report.from_date > report.to_date:
                raise UserError(_("You must be enter start date less than end date !"))
            file_name = _('كشف حساب.xlsx')
            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            excel_sheet = workbook.add_worksheet('كشف حساب')

            header_format = workbook.add_format(
                {'bold': True, 'font_color': 'white', 'bg_color': '#696969', 'border': 1, 'num_format': '#,###'})
            header_format_sequence = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            format = workbook.add_format({'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            title_format = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'white'})
            header_format.set_align('center')
            header_format.set_align('vertical center')
            header_format.set_text_wrap()
            format = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1, 'font_size': '10', 'num_format': '#,###'})
            title_format = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            title_format.set_align('center')
            format.set_align('center')
            header_format_sequence.set_align('center')
            format.set_text_wrap()
            format_details = workbook.add_format()
            sequence_format = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            sequence_format.set_align('center')
            sequence_format.set_text_wrap()
            total_format = workbook.add_format(
                {'bold': True, 'font_color': 'black', 'bg_color': '#808080', 'border': 1, 'font_size': '10'})
            total_format.set_align('center')
            total_format.set_text_wrap()
            format_details.set_num_format('#,##0.00')
            date_format = workbook.add_format({'num_format': 'dd/mm/yy'})
            sequence_id = 0
            col = 0
            row = 11
            first_row = 13
            report_title = account_id.name + ' من ' + str(from_date) + ' إلى ' + str(to_date)
            excel_sheet.merge_range(10, 2, 10, 7, report_title, title_format)
            excel_sheet.set_column(col, col, 5)
            excel_sheet.write(row, col, '#', header_format)
            col += 1
            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'التاريخ', header_format)
            col += 1
            excel_sheet.set_column(col, col, 15)
            excel_sheet.write(row, col, 'التعليق', header_format)
            col += 1
            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'دفتر اليومية', header_format)
            # col += 1
            # excel_sheet.set_column(col, col, 15)
            # excel_sheet.write(row, col, 'Account', header_format)
            col += 1
            excel_sheet.set_column(col, col, 15)
            excel_sheet.write(row, col, 'المرجع', header_format)
            col += 1
            excel_sheet.set_column(col, col, 15)
            excel_sheet.write(row, col, 'مدين', header_format)
            col += 1
            excel_sheet.set_column(col, col, 15)
            excel_sheet.write(row, col, 'دائن', header_format)
            col += 1
            excel_sheet.set_column(col, col, 15)
            excel_sheet.write(row, col, 'الرصيد', header_format)
            col += 1
            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'العملة', header_format)
            col += 1
            # excel_sheet.set_column(col, col, 15)
            # excel_sheet.write(row, col, 'Debit', header_format)
            # col += 1
            # excel_sheet.set_column(col, col, 15)
            # excel_sheet.write(row, col, 'Credit', header_format)
            # col += 1
            # excel_sheet.set_column(col, col, 15)
            # excel_sheet.write(row, col, 'Balance', header_format)

            i_debit = 0
            i_credit = 0
            i_debit2 = 0
            i_credit2 = 0

            for initial in self.env['account.move.line'].search([('account_id', '=', account_id.id), ('date', '<', from_date), ('move_id.state', '=', 'posted')]):
                i_debit += initial.debit
                i_credit += initial.credit
            i_debit2 = i_debit2
            i_credit2 = i_credit2
            for initial2 in self.env['account.move.line'].search([('account_id', '=', account_id.id), ('date', '<', from_date), ('move_id.state', '=', 'posted'), ('amount_currency', '>', 0)]):
                # if initial.amount_currency > 0:
                i_debit2 += abs(initial2.amount_currency)
                i_credit2 += 0
            i_debit2 = i_debit2
            i_credit2 = i_credit2
            for initial3 in self.env['account.move.line'].search([('account_id', '=', account_id.id), ('date', '<', from_date), ('move_id.state', '=', 'posted'), ('amount_currency', '<', 0)]):
                # elif initial.amount_currency < 0:
                i_debit2 += 0
                i_credit2 += abs(initial3.amount_currency)
            i_debit2 = i_debit2
            i_credit2 = i_credit2
            for initial4 in self.env['account.move.line'].search([('account_id', '=', account_id.id), ('date', '<', from_date), ('move_id.state', '=', 'posted'), ('amount_currency', '=', 0)]):
            # else:
                i_debit2 += 0
                i_credit2 += 0

            i_debit2 = i_debit2
            i_credit2 = i_credit2
            i_balance2 = i_debit2 - i_credit2
            i_debit = i_debit
            i_credit = i_credit
            i_balance = i_debit - i_credit
            col = 0
            row += 1
            excel_sheet.merge_range(row, col, row, col + 4, 'الرصيد الافتتاحي', header_format)
            if i_debit:
                excel_sheet.write(row, col + 5, i_debit, header_format)
            else:
                excel_sheet.write(row, col + 5, 0.0, header_format)
            if i_credit:
                excel_sheet.write(row, col + 6, i_credit, header_format)
            else:
                excel_sheet.write(row, col + 6, 0.0, header_format)
            if i_balance:
                excel_sheet.write(row, col + 7, i_balance, header_format)
            else:
                excel_sheet.write(row, col + 7, 0.0, header_format)
            excel_sheet.write(row, col + 8, 0.0, header_format)
            # if i_debit2:
            #     excel_sheet.write(row, col + 9, i_debit2, header_format)
            # else:
            #     excel_sheet.write(row, col + 9, 0.0, header_format)
            # if i_credit2:
            #     excel_sheet.write(row, col + 10, i_credit2, header_format)
            # else:
            #     excel_sheet.write(row, col + 10, 0.0, header_format)
            # if i_balance2:
            #     excel_sheet.write(row, col + 11, i_balance2, header_format)
            # else:
            #     excel_sheet.write(row, col + 11, 0.0, header_format)
            move_ids = self.env['account.move.line'].search([('account_id', '=', account_id.id), ('date', '>=', from_date), ('date', '<=', to_date), ('move_id.state', '=', 'posted')], order='date,id asc')
            balance = i_balance
            balance2 = i_balance2
            total_debit = 0.0
            total_credit = 0.0
            total_balance = 0.0
            if move_ids:
                for move in move_ids:
                    account = move.account_id
                    # if account.user_type_id.name == 'Receivable' or account.user_type_id.name == 'Payable':
                    date = move.date
                    journal = move.journal_id.code
                    move_id = move.move_id.name
                    debit = move.debit
                    credit = move.credit
                    balance = balance + debit - credit
                    account_code = account.code
                    amount_currency = move.amount_currency
                    currency = move.currency_id.name
                    narration = move.name
                    if amount_currency > 0:
                        debit2 = abs(amount_currency)
                        credit2 = 0
                    elif amount_currency < 0:
                        debit2 = 0
                        credit2 = abs(amount_currency)
                    else:
                        debit2 = 0
                        credit2 = 0
                    balance2 = balance2 + debit2 - credit2

                    col = 0
                    row += 1
                    sequence_id += 1
                    excel_sheet.write(row, col, sequence_id, sequence_format)
                    col += 1
                    if date:
                        excel_sheet.write(row, col, date, date_format)
                    else:
                        excel_sheet.write(row, col, '', format)
                    col += 1
                    if narration:
                        excel_sheet.write(row, col, narration, format)
                    else:
                        excel_sheet.write(row, col, '', format)
                    col += 1
                    if journal:
                        excel_sheet.write(row, col, journal, format)
                    else:
                        excel_sheet.write(row, col, '', format)
                    col += 1
                    if move_id:
                        excel_sheet.write(row, col, move_id, format)
                    else:
                        excel_sheet.write(row, col, '', format)
                    col += 1
                    if debit:
                        total_debit += debit
                        excel_sheet.write(row, col, debit, format)
                    else:
                        excel_sheet.write(row, col, '0.0', format)
                    col += 1
                    if credit:
                        total_credit += credit
                        excel_sheet.write(row, col, credit, format)
                    else:
                        excel_sheet.write(row, col, '0.0', format)
                    col += 1
                    if balance:
                        total_balance += balance
                        excel_sheet.write(row, col, balance, format)
                    else:
                        excel_sheet.write(row, col, '', format)
                    col += 1
                    if currency:
                        excel_sheet.write(row, col, currency, format)
                    else:
                        excel_sheet.write(row, col, '', format)
                    col += 1
                    # if debit2:
                    #     excel_sheet.write(row, col, debit2, format)
                    # else:
                    #     excel_sheet.write(row, col, '0.0', format)
                    # col += 1
                    # if credit2:
                    #     excel_sheet.write(row, col, credit2, format)
                    # else:
                    #     excel_sheet.write(row, col, '0.0', format)
                    # col += 1
                    # if balance2:
                    #     excel_sheet.write(row, col, balance2, format)
                    # else:
                    #     excel_sheet.write(row, col, '0.0', format)
                balance = balance
                balance2 = i_balance2
            col = 0
            row += 1
            excel_sheet.merge_range(row, col, row, col + 4, 'الإجمالي', header_format)
            excel_sheet.write(row, col + 5, total_debit, header_format)
            excel_sheet.write(row, col + 6, total_credit, header_format)
            excel_sheet.write(row, col + 7, total_balance, header_format)
            excel_sheet.write(row, col + 8, '', header_format)
            # excel_sheet.write_formula(row, col + 9, 'SUM(j' + str(first_row) + ':j' + str(row) + ')', header_format)
            # excel_sheet.write_formula(row, col + 10, 'SUM(k' + str(first_row) + ':k' + str(row) + ')', header_format)
            # excel_sheet.write_formula(row, col + 11, 'j' + str(row + 1) + '-k' + str(row + 1), header_format)

            workbook.close()
            file_download = base64.b64encode(fp.getvalue())
            fp.close()
            wizardmodel = self.env['account.report.excel']
            res_id = wizardmodel.create({'name': file_name, 'file_download': file_download})
            return {
                'name': 'Files to Download',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'account.report.excel',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': res_id.id,
            }


class account_report_excel(models.TransientModel):
    _name = 'account.report.excel'

    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('File to Download', readonly=True)