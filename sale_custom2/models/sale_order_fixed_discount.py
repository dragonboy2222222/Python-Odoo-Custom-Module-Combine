# custom-addons/sale_custom2/models/sale_order_fixed_discount.py
#
# from odoo import models, fields, api
#
#
# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     fixed_discount = fields.Float(string="Fixed Discount ($)", help="Fixed discount in amount, not percentage.",
#                                   store=True)
#
#     @api.depends('fixed_discount', 'product_uom_qty', 'price_unit')
#     def _compute_amount(self):
#         for line in self:
#             # Calculate subtotal with fixed discount on sale order line
#             subtotal = (line.price_unit * line.product_uom_qty) - line.fixed_discount
#             line.price_subtotal = subtotal
#
#
#
#     def _prepare_invoice_line(self, **optional_values):
#         # Prepare values to create the invoice line
#         invoice_line_vals = super(SaleOrderLine, self)._prepare_invoice_line(**optional_values)
#
#         # Adjust price_unit on the invoice line to reflect fixed_discount
#         if self.product_uom_qty:
#             discounted_price_unit = self.price_subtotal / self.product_uom_qty
#
#
#
#         else:
#             discounted_price_unit = self.price_unit
#
#         # Pass the discount and adjusted price_unit to the invoice line
#         invoice_line_vals.update({
#             'fixed_discount': self.fixed_discount,
#             'price_unit': discounted_price_unit,
#         })
#
#         return invoice_line_vals

# In your custom module, extend SaleOrderLine


from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    fixed_discount = fields.Float(string='Fixed Discount', default=0.0)

    @api.depends('price_unit', 'product_uom_qty', 'tax_id', 'fixed_discount')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line, including fixed discounts.
        """
        for line in self:
            price = line.price_unit * line.product_uom_qty
            subtotal = price - line.fixed_discount
            taxes = line.tax_id.compute_all(
                subtotal,
                currency=line.order_id.currency_id,
                quantity=1.0,
                product=line.product_id,
                partner=line.order_id.partner_id,
            )
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    fixed_discount = fields.Float(string='Fixed Discount (Total)', default=0.0)

    @api.depends('order_line.price_total', 'fixed_discount')
    def _amount_all(self):
        """
        Compute the total amounts of the SO, including fixed discounts.
        """
        for order in self:
            amount_untaxed = sum(line.price_subtotal for line in order.order_line)
            amount_tax = sum(line.price_tax for line in order.order_line)
            total_fixed_discount = order.fixed_discount
            order.update({
                'amount_untaxed': amount_untaxed - total_fixed_discount,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax - total_fixed_discount,
            })





class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def _compute_taxes(self, base_lines, tax_lines=None, handle_price_include=True, include_caba_tags=False):
        # Call the super method to preserve default functionality
        res = super(AccountTax, self)._compute_taxes(
            base_lines, tax_lines=tax_lines, handle_price_include=handle_price_include,
            include_caba_tags=include_caba_tags
        )

        # Adjust base amounts for each line based on fixed_discount
        for base_line in base_lines:
            fixed_discount = base_line.get('fixed_discount', 0.0)
            if fixed_discount:
                # Subtract fixed_discount from the untaxed amount
                base_line['price_subtotal'] -= fixed_discount
                # Ensure no negative values
                base_line['price_subtotal'] = max(base_line['price_subtotal'], 0.0)

        # Recompute the totals to reflect changes
        for currency, totals in res['totals'].items():
            totals['amount_untaxed'] = sum(
                base_line.get('price_subtotal', 0.0) for base_line in base_lines
            )

        return res

    @api.model
    def _prepare_tax_totals(self, base_lines, currency, tax_lines=None, is_company_currency_requested=False):
        # Call the super method to get the default tax totals
        res = super(AccountTax, self)._prepare_tax_totals(
            base_lines, currency, tax_lines=tax_lines, is_company_currency_requested=is_company_currency_requested
        )

        # Adjust the untaxed total to reflect fixed discounts
        for base_line in base_lines:
            fixed_discount = base_line.get('fixed_discount', 0.0)
            if fixed_discount:
                base_line['price_subtotal'] -= fixed_discount
                base_line['price_subtotal'] = max(base_line['price_subtotal'], 0.0)

        # Recalculate totals with the adjusted values
        res['amount_untaxed'] = sum(
            base_line.get('price_subtotal', 0.0) for base_line in base_lines
        )
        res['amount_total'] = res['amount_untaxed'] + res.get('amount_tax', 0.0)

        return res