# -*- coding: utf-8 -*-
#######################################################################
#     Copyright (C) 2023 IATL IntelliSoft Business Solutions Co. Ltd. #
#     (<https://www.iatl-intellisoft.com>) all rights reserved.       #
#######################################################################

from odoo import models, fields, _
from odoo.tools import get_lang
from collections import defaultdict


class GeneralLedgerCustomHandler(models.AbstractModel):
    _inherit = 'account.general.ledger.report.handler'

    def _dynamic_lines_generator(self, report, options, all_column_groups_expression_totals):
        lines = []
        date_from = fields.Date.from_string(options['date']['date_from'])
        company_currency = self.env.company.currency_id

        totals_by_column_group = defaultdict(lambda: {'debit': 0, 'credit': 0, 'balance': 0,
                                    'second_currency_debit': 0, 'second_currency_credit': 0, 'second_currency_balance': 0})
        for account, column_group_results in self._query_values(report, options):
            eval_dict = {}
            has_lines = False
            for column_group_key, results in column_group_results.items():
                account_sum = results.get('sum', {})
                account_un_earn = results.get('unaffected_earnings', {})

                account_debit = account_sum.get('debit', 0.0) + account_un_earn.get('debit', 0.0)
                account_credit = account_sum.get('credit', 0.0) + account_un_earn.get('credit', 0.0)
                account_balance = account_sum.get('balance', 0.0) + account_un_earn.get('balance', 0.0)

                account_sc_debit = account_sum.get('second_currency_debit', 0.0) + account_un_earn.get('second_currency_debit', 0.0)
                account_sc_credit = account_sum.get('second_currency_credit', 0.0) + account_un_earn.get('second_currency_credit', 0.0)
                account_sc_balance = account_sum.get('second_currency_balance', 0.0) + account_un_earn.get('second_currency_balance', 0.0)

                eval_dict[column_group_key] = {
                    'amount_currency': account_sum.get('amount_currency', 0.0) + account_un_earn.get('amount_currency', 0.0),
                    'debit': account_debit,
                    'credit': account_credit,
                    'balance': account_balance,
                }

                if self.env.context.get('account_second_currency_report'):
                    eval_dict[column_group_key] = {
                        'second_currency_amount_currency': account_sum.get('second_currency_amount_currency', 0.0) + account_un_earn.get('second_currency_amount_currency', 0.0),
                        'second_currency_debit': account_sc_debit,
                        'second_currency_credit': account_sc_credit,
                        'second_currency_balance': account_sc_balance,
                    }

                max_date = account_sum.get('max_date')
                has_lines = has_lines or (max_date and max_date >= date_from)

                totals_by_column_group[column_group_key]['debit'] += account_debit
                totals_by_column_group[column_group_key]['credit'] += account_credit
                totals_by_column_group[column_group_key]['balance'] += account_balance

                totals_by_column_group[column_group_key]['second_currency_debit'] += account_sc_debit
                totals_by_column_group[column_group_key]['second_currency_credit'] += account_sc_credit
                totals_by_column_group[column_group_key]['second_currency_balance'] += account_sc_balance

            lines.append(self._get_account_title_line(report, options, account, has_lines, eval_dict))

        # Report total line.
        for totals in totals_by_column_group.values():
            totals['balance'] = company_currency.round(totals['balance'])
            if self.env.context.get('account_second_currency_report'):
                totals['second_currency_balance'] = company_currency.round(totals['second_currency_balance'])

        # Tax Declaration lines.
        journal_options = report._get_options_journals(options)
        if len(options['column_groups']) == 1 and len(journal_options) == 1 and journal_options[0]['type'] in ('sale', 'purchase'):
            lines += self._tax_declaration_lines(report, options, journal_options[0]['type'])

        # Total line
        lines.append(self._get_total_line(report, options, totals_by_column_group))

        return [(0, line) for line in lines]

    def _get_query_sums(self, report, options):
        """ Construct a query retrieving all the aggregated sums to build the report. It includes:
        - sums for all accounts.
        - sums for the initial balances.
        - sums for the unaffected earnings.
        - sums for the tax declaration.
        :return:                    (query, params)
        """
        options_by_column_group = report._split_options_per_column_group(options)

        params = []
        queries = []

        # Create the currency table.
        # As the currency table is the same whatever the comparisons, create it only once.
        ct_query = self.env['res.currency']._get_query_currency_table(options)

        # ============================================
        # 1) Get sums for all accounts.
        # ============================================
        for column_group_key, options_group in options_by_column_group.items():
            if not options.get('general_ledger_strict_range'):
                options_group = self._get_options_sum_balance(options_group)

            # Sum is computed including the initial balance of the accounts configured to do so, unless a special option key is used
            # (this is required for trial balance, which is based on general ledger)
            sum_date_scope = 'strict_range' if options_group.get('general_ledger_strict_range') else 'normal'

            query_domain = []

            if options.get('filter_search_bar'):
                query_domain.append(('account_id', 'ilike', options['filter_search_bar']))

            if options_group.get('include_current_year_in_unaff_earnings'):
                query_domain += [('account_id.include_initial_balance', '=', True)]

            tables, where_clause, where_params = report._query_get(options_group, sum_date_scope, domain=query_domain)
            params.append(column_group_key)
            params += where_params
            queries.append(f"""
                SELECT
                    account_move_line.account_id                            AS groupby,
                    'sum'                                                   AS key,
                    MAX(account_move_line.date)                             AS max_date,
                    %s                                                      AS column_group_key,
                    COALESCE(SUM(account_move_line.amount_currency), 0.0)   AS amount_currency,
                    SUM(ROUND(account_move_line.debit * currency_table.rate, currency_table.precision))   AS debit,
                    SUM(ROUND(account_move_line.credit * currency_table.rate, currency_table.precision))  AS credit,
                    SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) AS balance,
                    COALESCE(SUM(account_move_line.second_currency_amount_currency), 0.0) AS second_currency_amount_currency,
                    SUM(ROUND(account_move_line.second_currency_debit * currency_table.rate, currency_table.precision))   AS second_currency_debit,
                    SUM(ROUND(account_move_line.second_currency_credit * currency_table.rate, currency_table.precision))  AS second_currency_credit,
                    SUM(ROUND(account_move_line.second_currency_balance * currency_table.rate, currency_table.precision)) AS second_currency_balance
                FROM {tables}
                LEFT JOIN {ct_query} ON currency_table.company_id = account_move_line.company_id
                WHERE {where_clause}
                GROUP BY account_move_line.account_id
            """)

            # ============================================
            # 2) Get sums for the unaffected earnings.
            # ============================================
            if not options_group.get('general_ledger_strict_range'):
                unaff_earnings_domain = [('account_id.include_initial_balance', '=', False)]

                # The period domain is expressed as:
                # [
                #   ('date' <= fiscalyear['date_from'] - 1),
                #   ('account_id.include_initial_balance', '=', False),
                # ]

                new_options = self._get_options_unaffected_earnings(options_group)
                tables, where_clause, where_params = report._query_get(new_options, 'strict_range', domain=unaff_earnings_domain)
                params.append(column_group_key)
                params += where_params
                queries.append(f"""
                        SELECT
                            account_move_line.company_id                            AS groupby,
                            'unaffected_earnings'                                   AS key,
                            NULL                                                    AS max_date,
                            %s                                                      AS column_group_key,
                            COALESCE(SUM(account_move_line.amount_currency), 0.0)   AS amount_currency,
                            SUM(ROUND(account_move_line.debit * currency_table.rate, currency_table.precision))   AS debit,
                            SUM(ROUND(account_move_line.credit * currency_table.rate, currency_table.precision))  AS credit,
                            SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) AS balance,
                            COALESCE(SUM(account_move_line.second_currency_amount_currency), 0.0)   AS second_currency_amount_currency,
                            SUM(ROUND(account_move_line.second_currency_debit * currency_table.rate, currency_table.precision))   AS second_currency_debit,
                            SUM(ROUND(account_move_line.second_currency_credit * currency_table.rate, currency_table.precision))  AS second_currency_credit,
                            SUM(ROUND(account_move_line.second_currency_balance * currency_table.rate, currency_table.precision)) AS second_currency_balance
                        FROM {tables}
                        LEFT JOIN {ct_query} ON currency_table.company_id = account_move_line.company_id
                        WHERE {where_clause}
                        GROUP BY account_move_line.company_id
                    """)

        return ' UNION ALL '.join(queries), params

    

    def _get_query_amls(self, report, options, expanded_account_ids, offset=0, limit=None):
        """ Construct a query retrieving the account.move.lines when expanding a report line with or without the load
        more.
        :param options:               The report options.
        :param expanded_account_ids:  The account.account ids corresponding to consider. If None, match every account.
        :param offset:                The offset of the query (used by the load more).
        :param limit:                 The limit of the query (used by the load more).
        :return:                      (query, params)
        """
        additional_domain = [('account_id', 'in', expanded_account_ids)] if expanded_account_ids is not None else None
        queries = []
        all_params = []
        lang = self.env.user.lang or get_lang(self.env).code
        journal_name = f"COALESCE(journal.name->>'{lang}', journal.name->>'en_US')" if \
            self.pool['account.journal'].name.translate else 'journal.name'
        account_name = f"COALESCE(account.name->>'{lang}', account.name->>'en_US')" if \
            self.pool['account.account'].name.translate else 'account.name'
        for column_group_key, group_options in report._split_options_per_column_group(options).items():
            # Get sums for the account move lines.
            # period: [('date' <= options['date_to']), ('date', '>=', options['date_from'])]
            tables, where_clause, where_params = report._query_get(group_options, domain=additional_domain, date_scope='strict_range')
            ct_query = self.env['res.currency']._get_query_currency_table(group_options)
            query = f'''
                    (SELECT
                        account_move_line.id,
                        account_move_line.date,
                        account_move_line.date_maturity,
                        account_move_line.name,
                        account_move_line.ref,
                        account_move_line.company_id,
                        account_move_line.account_id,
                        account_move_line.payment_id,
                        account_move_line.partner_id,
                        account_move_line.currency_id,
                        account_move_line.amount_currency,
                        ROUND(account_move_line.debit * currency_table.rate, currency_table.precision)   AS debit,
                        ROUND(account_move_line.credit * currency_table.rate, currency_table.precision)  AS credit,
                        ROUND(account_move_line.balance * currency_table.rate, currency_table.precision) AS balance,
                        account_move_line.second_currency_amount_currency,
                        ROUND(account_move_line.second_currency_debit * currency_table.rate, currency_table.precision)   AS second_currency_debit,
                        ROUND(account_move_line.second_currency_credit * currency_table.rate, currency_table.precision)  AS second_currency_credit,
                        ROUND(account_move_line.second_currency_balance * currency_table.rate, currency_table.precision) AS second_currency_balance,
                        move.name                               AS move_name,
                        company.currency_id                     AS company_currency_id,
                        partner.name                            AS partner_name,
                        move.move_type                          AS move_type,
                        account.code                            AS account_code,
                        {account_name}                          AS account_name,
                        journal.code                            AS journal_code,
                        {journal_name}                          AS journal_name,
                        full_rec.name                           AS full_rec_name,
                        %s                                      AS column_group_key
                    FROM {tables}
                    JOIN account_move move                      ON move.id = account_move_line.move_id
                    LEFT JOIN {ct_query}                        ON currency_table.company_id = account_move_line.company_id
                    LEFT JOIN res_company company               ON company.id = account_move_line.company_id
                    LEFT JOIN res_partner partner               ON partner.id = account_move_line.partner_id
                    LEFT JOIN account_account account           ON account.id = account_move_line.account_id
                    LEFT JOIN account_journal journal           ON journal.id = account_move_line.journal_id
                    LEFT JOIN account_full_reconcile full_rec   ON full_rec.id = account_move_line.full_reconcile_id
                    WHERE {where_clause}
                    ORDER BY account_move_line.date, account_move_line.id)
                '''

            queries.append(query)
            all_params.append(column_group_key)
            all_params += where_params

        full_query = " UNION ALL ".join(queries)

        if offset:
            full_query += ' OFFSET %s '
            all_params.append(offset)
        if limit:
            full_query += ' LIMIT %s '
            all_params.append(limit)

        return (full_query, all_params)

    def _get_initial_balance_values(self, report, account_ids, options):
        """
        Get sums for the initial balance.
        """
        queries = []
        params = []
        for column_group_key, options_group in report._split_options_per_column_group(options).items():
            new_options = self._get_options_initial_balance(options_group)
            ct_query = self.env['res.currency']._get_query_currency_table(new_options)
            tables, where_clause, where_params = report._query_get(new_options, 'normal', domain=[
                ('account_id', 'in', account_ids),
                ('account_id.include_initial_balance', '=', True),
            ])
            params.append(column_group_key)
            params += where_params
            queries.append(f"""
                    SELECT
                        account_move_line.account_id                                                          AS groupby,
                        'initial_balance'                                                                     AS key,
                        NULL                                                                                  AS max_date,
                        %s                                                                                    AS column_group_key,
                        COALESCE(SUM(account_move_line.amount_currency), 0.0)                                 AS amount_currency,
                        SUM(ROUND(account_move_line.debit * currency_table.rate, currency_table.precision))   AS debit,
                        SUM(ROUND(account_move_line.credit * currency_table.rate, currency_table.precision))  AS credit,
                        SUM(ROUND(account_move_line.balance * currency_table.rate, currency_table.precision)) AS balance,
                        COALESCE(SUM(account_move_line.second_currency_amount_currency), 0.0)                                 AS second_currency_amount_currency,
                        SUM(ROUND(account_move_line.second_currency_debit * currency_table.rate, currency_table.precision))   AS second_currency_debit,
                        SUM(ROUND(account_move_line.second_currency_credit * currency_table.rate, currency_table.precision))  AS second_currency_credit,
                        SUM(ROUND(account_move_line.second_currency_balance * currency_table.rate, currency_table.precision)) AS second_currency_balance
                    FROM {tables}
                    LEFT JOIN {ct_query} ON currency_table.company_id = account_move_line.company_id
                    WHERE {where_clause}
                    GROUP BY account_move_line.account_id
                """)
                

        self._cr.execute(" UNION ALL ".join(queries), params)

        init_balance_by_col_group = {
            account_id: {column_group_key: {} for column_group_key in options['column_groups']}
            for account_id in account_ids
        }
        for result in self._cr.dictfetchall():
            init_balance_by_col_group[result['groupby']][result['column_group_key']] = result

        accounts = self.env['account.account'].browse(account_ids)
        return {
            account.id: (account, init_balance_by_col_group[account.id])
            for account in accounts
        }

