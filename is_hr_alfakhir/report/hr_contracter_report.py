# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api, tools, _
import xlsxwriter
import base64
from io import StringIO, BytesIO
from odoo.exceptions import Warning as UserError


class WizardContracter(models.Model):
    _name = 'wizard.contracter'

    from_date = fields.Date('From Date', required=True)
    to_date = fields.Date('To Date', required=True)

    def print_report(self):
        for report in self:
            from_date = report.from_date
            to_date = report.to_date
            if report.from_date > report.to_date:
                raise UserError(_("You must be enter start date less than end date !"))
            file_name = _('التعاقدات الخارجية.xlsx')
            fp = BytesIO()
            workbook = xlsxwriter.Workbook(fp)
            excel_sheet = workbook.add_worksheet('التعاقدات الخارجية')

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
            report_title = 'الموضوع : التعاقدات الخارجية ' + str(from_date.month) + ' / ' + str(to_date.year)
            excel_sheet.merge_range(9, 2, 9, 9, report_title, title_format)
            report_title2 = 'ارجو من سيادتكم التكرم بالموافقة على صرف قيمة التعاقدات الخارجية التالية :-'
            excel_sheet.merge_range(10, 2, 10, 9, report_title2, title_format2)
            
            excel_sheet.set_column(col, col, 5)
            excel_sheet.write(row, col, 'الرقم', header_format)
            col += 1
            excel_sheet.set_column(col, col, 40)
            excel_sheet.write(row, col, 'الاسم', header_format)
            col += 1
            excel_sheet.set_column(col, col, 15)
            excel_sheet.write(row, col, 'الوظيفة', header_format)
            col += 1
            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'عبارة عن', header_format)
            col += 1
            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'المبلغ', header_format)
            col += 1
            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'السلفية', header_format)
            col += 1
            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'صافي التعاقدات', header_format)
            col += 1
            excel_sheet.set_column(col, col, 10)
            excel_sheet.write(row, col, 'توقيع المستلم', header_format)

            row += 1
            col = 2
            employee_ids = self.env['hr.employee'].search([('employee_type','=','contractor')])

            total = 0.0
            total_final = 0.0
            total_emps_loans = 0.0
            if employee_ids:
                for employee in employee_ids:
                    monthlyloan_ids = self.env['hr.monthlyloan'].search([
                        ('date', '>=', from_date), ('date', '<=', to_date),
                        ('employee_id','=',employee.id), 
                        ('state', '=', 'done')], order='date,id asc')
                    loan_ids = self.env['hr.loan.line'].search([
                        ('paid_date', '>=', from_date), ('paid_date', '<=', to_date), 
                        ('employee_id','=',employee.id), 
                        ('loan_id.state', '=', 'paid')], order='paid_date,id asc')
                    total_loan = 0.0

                    for loan in monthlyloan_ids:
                        total_loan += loan.loan_amount 
                    for loan in loan_ids:
                        total_loan += loan.paid_amount 

                    sequence_id += 1
                    excel_sheet.write(row, col, sequence_id, sequence_format)
                    col += 1
                    excel_sheet.write(row, col, employee.name, format2)
                    col += 1
                    excel_sheet.write(row, col, employee.job_id.name, format2)
                    col += 1
                    excel_sheet.write(row, col, 'المرتب الشهري', format2)
                    col += 1
                    excel_sheet.write(row, col, employee.contract_id.wage, format)
                    col += 1
                    excel_sheet.write(row, col, total_loan, format)
                    col += 1
                    excel_sheet.write(row, col, employee.contract_id.wage - total_loan, format)
                    col += 1
                    excel_sheet.write(row, col, '', format2)

                    total += employee.contract_id.wage
                    total_emps_loans += total_loan
                    total_final += (employee.contract_id.wage - total_loan)
                    row += 1
                    col = 2

                col = 2
                excel_sheet.merge_range(row, col, row, col + 3, 'الإجمالي', header_format2)
                excel_sheet.write(row, col + 4, total, header_format2)
                excel_sheet.write(row, col + 5, total_emps_loans, header_format2)
                excel_sheet.write(row, col + 6, total_final, header_format2)
                excel_sheet.write(row, col + 7, '', header_format2)

            workbook.close()
            file_download = base64.b64encode(fp.getvalue())
            fp.close()
            wizardmodel = self.env['contracter.report.excel']
            res_id = wizardmodel.create({'name': file_name, 'file_download': file_download})
            return {
                'name': 'Files to Download',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'contracter.report.excel',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': res_id.id,
            }


class contracter_report_excel(models.TransientModel):
    _name = 'contracter.report.excel'

    name = fields.Char('File Name', size=256, readonly=True)
    file_download = fields.Binary('File to Download', readonly=True)