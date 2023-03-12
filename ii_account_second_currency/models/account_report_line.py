# -*- coding: utf-8 -*-
#######################################################################
#     Copyright (C) 2023 IATL IntelliSoft Business Solutions Co. Ltd. #
#     (<https://www.iatl-intellisoft.com>) all rights reserved.       #
#######################################################################

import re
from odoo import fields, models

DOMAIN_REGEX = re.compile(r'(-?sum)\((.*)\)')


class AccountReportLine(models.Model):
    _inherit = "account.report.line"

    def _create_report_expression(self, engine):
        # create account.report.expression for each report line based on the formula provided to each
        # engine-related field. This makes xmls a bit shorter
        vals_list = []
        for report_line in self:
            if engine == 'domain' and report_line.domain_formula:
                subformula, formula = DOMAIN_REGEX.match(report_line.domain_formula or '').groups()
                # Resolve the calls to ref(), to mimic the fact those formulas are normally given with an eval="..." in XML
                formula = re.sub(r'''\bref\((?P<quote>['"])(?P<xmlid>.+?)(?P=quote)\)''', lambda m: str(self.env.ref(m['xmlid']).id), formula)
            elif engine == 'account_codes' and report_line.account_codes_formula:
                subformula, formula = None, report_line.account_codes_formula
            elif engine == 'aggregation' and report_line.aggregation_formula:
                subformula, formula = None, report_line.aggregation_formula
            else:
                continue

            vals = {
                'report_line_id': report_line.id,
                'label': 'balance',
                'engine': engine,
                'formula': formula.lstrip(' \t\n'),  # Avoid IndentationError in evals
                'subformula': subformula
            }

            if self.env.context.get('install_module') and self.env.context.get('install_module') == 'ii_account_second_currency':
                vals = {
                'report_line_id': report_line.id,
                'label': 'second_currency_balance',
                'engine': engine,
                'formula': formula.lstrip(' \t\n'),  # Avoid IndentationError in evals
                'subformula': subformula
            }

            if report_line.expression_ids:
                # expressions already exists, update the first expression with the right engine
                # since syntactic sugar aren't meant to be used with multiple expressions
                for expression in report_line.expression_ids:
                    if expression.engine == engine:
                        expression.write(vals)
                        break
            else:
                # else prepare batch creation
                vals_list.append(vals)

        if vals_list:
            self.env['account.report.expression'].create(vals_list)