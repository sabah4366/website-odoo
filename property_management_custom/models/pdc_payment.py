from odoo import api, fields, models,_
from odoo.exceptions import UserError
from datetime import timedelta,datetime,date

class PdcProperty(models.Model):
    _inherit = "pdc.wizard"


    def action_done(self):
        move = self.env['account.move']

        self.check_payment_amount()  # amount must be positive
        pdc_account = self.check_pdc_account()
        # bank_account = self.journal_id.payment_debit_account_id.id or self.journal_id.payment_credit_account_id.id
        bank_account = self.env.company.account_journal_payment_debit_account_id.id or self.env.company.account_journal_payment_credit_account_id.id

        # Create Journal Item
        move_line_vals_debit = {}
        move_line_vals_credit = {}
        if self.payment_type == 'receive_money':
            move_line_vals_debit = self.get_debit_move_line(bank_account)
            move_line_vals_credit = self.get_credit_move_line(pdc_account)
        else:
            move_line_vals_debit = self.get_debit_move_line(pdc_account)
            move_line_vals_credit = self.get_credit_move_line(bank_account)

        if self.memo:
            move_line_vals_debit.update({'name': 'PDC Payment :' + self.memo, 'partner_id': self.partner_id.id})
            move_line_vals_credit.update({'name': 'PDC Payment :' + self.memo, 'partner_id': self.partner_id.id})
        else:
            move_line_vals_debit.update({'name': 'PDC Payment', 'partner_id': self.partner_id.id})
            move_line_vals_credit.update({'name': 'PDC Payment', 'partner_id': self.partner_id.id})

        # create move and post it
        move_vals = self.get_move_vals(
            move_line_vals_debit, move_line_vals_credit)

        # invoice = self.env['account.move'].sudo().search([('name','=',self.memo)])
        # if invoice:
        total_amount_residuals = sum(self.invoice_ids.mapped('amount_residual'))
        if self.invoice_ids and total_amount_residuals != 0:

            move_id = move.create(move_vals)
            move_id.action_post()

            payment_amount = self.payment_amount
            for invoice in self.invoice_ids:

                if self.payment_type == 'receive_money':
                    # reconcilation Entry for Invoice
                    debit_move_id = self.env['account.move.line'].sudo().search([('move_id', '=', invoice.id),
                                                                                 ('debit', '>', 0.0)], limit=1)

                    credit_move_id = self.env['account.move.line'].sudo().search([('move_id', '=', move_id.id),
                                                                                  ('credit', '>', 0.0)], limit=1)

                    if debit_move_id and credit_move_id and payment_amount > 0:
                        full_reconcile_id = self.env['account.full.reconcile'].sudo().create({})

                        if payment_amount > invoice.amount_residual:
                            amount = invoice.amount_residual

                        else:
                            amount = payment_amount

                        payment_amount -= invoice.amount_residual
                        partial_reconcile_id_1 = self.env['account.partial.reconcile'].sudo().create(
                            {'debit_move_id': debit_move_id.id,
                             'credit_move_id': credit_move_id.id,
                             'amount': amount,
                             'debit_amount_currency': amount,
                             'credit_amount_currency': amount
                             })

                        # partial_reconcile_id_2 = self.env['account.partial.reconcile'].sudo().create(
                        #     {'debit_move_id': self.deposited_debit.id,
                        #      'credit_move_id': self.deposited_credit.id,
                        #      'amount': amount,
                        #      'debit_amount_currency': amount
                        #      })

                        if invoice.amount_residual == 0:
                            involved_lines = []

                            debit_invoice_line_id = self.env['account.move.line'].search(
                                [('move_id', '=', invoice.id), ('debit', '>', 0)], limit=1)
                            partial_reconcile_ids = self.env['account.partial.reconcile'].sudo().search(
                                [('debit_move_id', '=', debit_invoice_line_id.id)])

                            for partial_reconcile_id in partial_reconcile_ids:
                                involved_lines.append(partial_reconcile_id.credit_move_id.id)
                                involved_lines.append(partial_reconcile_id.debit_move_id.id)
                            self.env['account.full.reconcile'].create({
                                'partial_reconcile_ids': [(6, 0, partial_reconcile_ids.ids)],
                                'reconciled_line_ids': [(6, 0, involved_lines)],
                            })

                        involved_lines = [self.deposited_debit.id, self.deposited_credit.id]

                        self.env['account.full.reconcile'].create({
                            'partial_reconcile_ids': [(6, 0, [partial_reconcile_id_1.id])],
                            'reconciled_line_ids': [(6, 0, involved_lines)],
                        })

                else:
                    # reconcilation Entry for Invoice
                    credit_move_id = self.env['account.move.line'].sudo().search([('move_id', '=', invoice.id),
                                                                                  ('credit', '>', 0.0)], limit=1)

                    debit_move_id = self.env['account.move.line'].sudo().search([('move_id', '=', move_id.id),
                                                                                 ('debit', '>', 0.0)], limit=1)

                    if debit_move_id and credit_move_id and payment_amount > 0:

                        if payment_amount > invoice.amount_residual:
                            amount = invoice.amount_residual

                        else:
                            amount = payment_amount

                        payment_amount -= invoice.amount_residual

                        partial_reconcile_id_1 = self.env['account.partial.reconcile'].sudo().create(
                            {'debit_move_id': debit_move_id.id,
                             'credit_move_id': credit_move_id.id,
                             'amount': amount,
                             'credit_amount_currency': amount
                             })
                        # partial_reconcile_id_2 = self.env['account.partial.reconcile'].sudo().create(
                        #     {'debit_move_id': self.deposited_debit.id,
                        #      'credit_move_id': self.deposited_credit.id,
                        #      'amount': amount,
                        #      'debit_amount_currency': amount
                        #      })
                        if invoice.amount_residual == 0:
                            involved_lines = []

                            credit_invoice_line_id = self.env['account.move.line'].search(
                                [('move_id', '=', invoice.id), ('credit', '>', 0)], limit=1)
                            partial_reconcile_ids = self.env['account.partial.reconcile'].sudo().search(
                                [('credit_move_id', '=', credit_invoice_line_id.id)])

                            for partial_reconcile_id in partial_reconcile_ids:
                                involved_lines.append(partial_reconcile_id.credit_move_id.id)
                                involved_lines.append(partial_reconcile_id.debit_move_id.id)
                            self.env['account.full.reconcile'].create({
                                'partial_reconcile_ids': [(6, 0, partial_reconcile_ids.ids)],
                                'reconciled_line_ids': [(6, 0, involved_lines)],
                            })

                        involved_lines = [self.deposited_debit.id, self.deposited_credit.id]

                        self.env['account.full.reconcile'].create({
                            'partial_reconcile_ids': [(6, 0, [partial_reconcile_id_1.id])],
                            'reconciled_line_ids': [(6, 0, involved_lines)],
                        })

        else:
            bank_account = self.journal_id.payment_debit_account_id.id or self.journal_id.payment_credit_account_id.id

            partner_account = self.get_partner_account()

            debit_move_line = {
                'pdc_id': self.id,
                'partner_id': self.partner_id.id,
                'account_id': bank_account if self.payment_type == 'receive_money' else partner_account,
                'debit': self.payment_amount,
                'ref': self.memo,
                'date': self.due_date,
                'date_maturity': self.due_date,
            }

            credit_move_line = {
                'pdc_id': self.id,
                'partner_id': self.partner_id.id,
                'account_id': partner_account if self.payment_type == 'receive_money' else bank_account,
                'credit': self.payment_amount,
                'ref': self.memo,
                'date': self.due_date,
                'date_maturity': self.due_date,
            }

            move_vals = {
                'pdc_id': self.id,
                'date': self.due_date,
                'journal_id': self.journal_id.id,
                'ref': self.memo,
                'line_ids': [(0, 0, debit_move_line),
                             (0, 0, credit_move_line)]
            }

            move = self.env['account.move'].create(move_vals)
            move.action_post()

        self.write({
            'state': 'done',
            'done_date': date.today(),
        })
        email_to = self.partner_id.email
        email_values = {
            'email_to': email_to,
        }
        self.env.ref(
            'property_management_custom.send_email_done').sudo().send_mail(self.id, force_send=True,
                                                                              email_values=email_values)

    def action_register(self):
        res =  super(PdcProperty, self).action_register()
        email_to = self.partner_id.email
        email_values = {
            'email_to': email_to,
        }
        self.env.ref(
            'property_management_custom.send_email_to_register').sudo().send_mail(self.id, force_send=True, email_values=email_values)
        return res


    def action_deposited(self):
        res =  super(PdcProperty, self).action_deposited()
        email_to = self.partner_id.email
        email_values = {
            'email_to': email_to,
        }
        self.env.ref(
            'property_management_custom.send_email_deposit').sudo().send_mail(self.id, force_send=True, email_values=email_values)
        return res

    # def send_email_team(self):
    #     if self.company_type_rer == 'rer':
    #         if not self.team_id.team_members:
    #             raise UserError(_("Team Missing: Must have to select the team here"))
    #         else:
    #             if self.team_id.email_template:
    #                 email_addresses = [user.email for user in self.team_id.team_members]
    #                 email_to = ','.join(email_addresses)
    #                 email_values = {
    #                     'email_to': email_to,
    #                 }
    #                 self.team_id.email_template.sudo().send_mail(self.id, force_send=True, email_values=email_values)