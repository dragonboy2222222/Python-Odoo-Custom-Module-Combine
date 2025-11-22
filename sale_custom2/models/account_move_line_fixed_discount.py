from odoo import models, fields, api, _


class AccountMove(models.Model):
    _inherit = 'account.move'

    fixed_discount = fields.Float(string='Fixed Discount', default=0.0)

    def _recompute_dynamic_lines(self, recompute_tax_base_amount=False):
        """
        Recompute journal items dynamically, accounting for fixed discounts.
        """
        super(AccountMove, self)._recompute_dynamic_lines(recompute_tax_base_amount=recompute_tax_base_amount)
        for move in self:
            if move.fixed_discount:
                # Ensure the journal has a default account for balancing
                default_account = move.journal_id.default_account_id
                if not default_account:
                    raise UserError(
                        _("The journal '%s' does not have a default account. Please configure one to balance the move.")
                        % move.journal_id.name
                    )

                # Add the fixed discount line
                discount_line = move.line_ids.filtered(lambda line: line.name == 'Fixed Discount')
                if not discount_line:
                    move.line_ids.create({
                        'move_id': move.id,
                        'name': 'Fixed Discount',
                        'account_id': default_account.id,
                        'debit': 0.0,
                        'credit': move.fixed_discount,
                        'partner_id': move.partner_id.id,
                    })
                else:
                    discount_line.update({
                        'credit': move.fixed_discount,
                        'debit': 0.0,
                    })

                # Rebalance total
                total_credits = sum(move.line_ids.mapped('credit'))
                total_debits = sum(move.line_ids.mapped('debit'))
                difference = total_credits - total_debits

                if not move.line_ids.filtered(lambda l: l.account_id == default_account and l.debit > 0):
                    move.line_ids.create({
                        'move_id': move.id,
                        'name': 'Balancing Entry',
                        'account_id': default_account.id,
                        'debit': difference if difference > 0 else 0.0,
                        'credit': abs(difference) if difference < 0 else 0.0,
                        'partner_id': move.partner_id.id,
                    })

    @api.depends('invoice_line_ids.price_total', 'fixed_discount')
    def _compute_amount(self):
        """
        Compute the total amounts of the invoice, including fixed discounts.
        """
        for move in self:
            amount_untaxed = sum(line.price_subtotal for line in move.invoice_line_ids)
            amount_tax = sum(line.price_total - line.price_subtotal for line in move.invoice_line_ids)
            total_fixed_discount = move.fixed_discount
            move.update({
                'amount_untaxed': amount_untaxed - total_fixed_discount,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax - total_fixed_discount,
            })
