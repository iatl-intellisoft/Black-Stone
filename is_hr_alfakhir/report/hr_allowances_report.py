# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, tools, _
import xlsxwriter
import base64
from io import StringIO, BytesIO
from odoo.exceptions import Warning as UserError


class WizardAllowances(models.Model):
    _name = 'wizard.allowances'

    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)

    def print_report(self):
        for report in self:
            from_date = report.from_date
            to_date = report.to_date
            if report.from_date > report.to_date:
                raise UserError(_("You must be enter start date less than end date !"))
            file_name = _('بدلات أخرى.xlsx')
            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            excel_sheet = workbook.add_worksheet('بدلات أخرى')
            header_format = workbook.add_format(
                {'bold': True, 'font_color': 'white', 'bg_color': '#696969', 'border': 1, 'num_format': '#,###'})
            header_format2 = workbook.add_format(
                {'bold': True, 'font_color': 'white', 'bg_color': '#696969', 'border': 1, 'num_format': '#,###'})
            header_format2.set_align('center')
            title_format = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': '#eeeeee', 'border': 1})
            title_format.set_align('center')
            title_format2 = workbook.add_format({'bold': True, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            title_format2.set_align('right')
            date_format = workbook.add_format({'num_format': 'dd/mm/yyyy'})
            sequence_format = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1})
            sequence_format.set_align('center')
            sequence_format.set_text_wrap()
            format = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1, 'font_size': '10', 'num_format': '#,###'})
            format.set_align('center')
            format.set_text_wrap()
            format2 = workbook.add_format(
                {'bold': False, 'font_color': 'black', 'bg_color': 'white', 'border': 1, 'font_size': '10', 'num_format': '#,###'})
            format2.set_align('right')
            format2.set_text_wrap()
            excel_sheet.right_to_left()

            sequence_id = 0
            col = 2
            row = 11
            excel_sheet.merge_range(3, 2, 3, 9, 'بسم الله الرحمن الرحيم', title_format)
            excel_sheet.merge_range(4, 2, 4, 9, 'إدارة الشؤون الإدارية / شؤون الموظفين', title_format)
            date = fields.Date.today()
            excel_sheet.merge_range(5, 2, 5, 3, '/ التاريخ ', title_format)
            excel_sheet.merge_range(5, 4, 5, 9, date, date_format)
            excel_sheet.merge_range(7, 2, 7, 9, 'السيد/ المدير العام,, المحترم', title_format2)
            excel_sheet.merge_range(8, 2, 8, 9, 'بعد السلام عليكم ورحمة الله وبركاته', title_format)
            report_title = 'الموضوع : بدلات أخرى ' + str(from_date.month) + ' / ' + str(from_date.year)
            excel_sheet.merge_range(9, 2, 9, 9, report_title, title_format)
            report_title2 = 'ارجو من سيادتكم التكرم بالموافقة على صرف البدلات ادناه وفق التصديق الشهري كالاتي :-'
            excel_sheet.merge_range(10, 2, 10, 9, report_title2, title_format2)
            
            excel_sheet.set_column(col, col, 5)
            excel_sheet.write(row, col, 'الرقم', header_format)
            col += 1
            excel_sheet.set_column(col, col, 40)
            excel_sheet.write(row, col, 'الاسم', header_format)
            col += 1
            excel_sheet.set_column(col, col, 15)
            excel_sheet.write(row, col, 'الوصف', header_format)
            col += 1
            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'المبلغ', header_format)
            col += 1
            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'سلفية', header_format)
            col += 1
            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'الفترة الزمنية', header_format)
            col += 1
            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'المبلغ النهائي', header_format)
            col += 1
            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'التوقيع', header_format)

            row += 1
            col = 2
            contract_ids = self.env['hr.contract'].search([
                ('state','=','open'),
                ('transport_allowance','>',0.0)])
            total = 0.0
            total_final = 0.0
            total_emps_loans = 0.0
            if contract_ids:
                for contract in contract_ids:
                    monthlyloan_ids = self.env['hr.monthlyloan'].search([
                        ('date', '>=', from_date), ('date', '<=', to_date),
                        ('employee_id','=',contract.employee_id.id), 
                        ('state', '=', 'done')], order='date,id asc')
                    loan_ids = self.env['hr.loan.line'].search([
                        ('paid_date', '>=', from_date), ('paid_date', '<=', to_date), 
                        ('employee_id','=',contract.employee_id.id), 
                        ('loan_id.state', '=', 'paid')], order='paid_date,id asc')
                    total_loan = 0.0

                    for loan in monthlyloan_ids:
                        total_loan += loan.loan_amount 
                    for loan in loan_ids:
                        total_loan += loan.paid_amount 

                    sequence_id += 1
                    excel_sheet.write(row, col, sequence_id, sequence_format)
                    col += 1
                    excel_sheet.write(row, col, contract.employee_id.name, format2)
                    col += 1
                    excel_sheet.write(row, col, 'بدل ترحيل', format2)
                    col += 1
                    excel_sheet.write(row, col, contract.transport_allowance, format)
                    col += 1
                    excel_sheet.write(row, col, total_loan, format)
                    col += 1
                    excel_sheet.write(row, col, 'شهر', format)
                    col += 1
                    excel_sheet.write(row, col, contract.transport_allowance - total_loan, format)
                    col += 1
                    excel_sheet.write(row, col, '', format2)

                    total += contract.transport_allowance
                    total_final += (contract.transport_allowance - total_loan)
                    total_emps_loans += total_loan
                    row += 1
                    col = 2

                col = 2
                excel_sheet.merge_range(row, col, row, col + 2, 'الإجمالي', header_format2)
                excel_sheet.write(row, col + 3, total, header_format2)
                excel_sheet.write(row, col + 4, total_emps_loans, header_format2)
                excel_sheet.write(row, col + 5, '', header_format2)
                excel_sheet.write(row, col + 6, total_final, header_format2)
                excel_sheet.write(row, col + 7, '', header_format2)
                

            workbook.close()
            file_download = base64.b64encode(fp.getvalue())
            fp.close()
            wizardmodel = self.env['allowances.report.excel']
            res_id = wizardmodel.create({'name': file_name, 'file_download': file_download})
            return {
                'name': 'Files to Download',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'allowances.report.excel',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': res_id.id,
            }


class allowances_report_excel(models.TransientModel):
    _name = 'allowances.report.excel'

    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('File to Download', readonly=True)


