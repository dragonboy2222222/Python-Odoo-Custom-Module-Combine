# # custom-addons/sale_custom2/models/sale_order_fixed_discount.py
#
# from odoo import models, fields, api
#
#
# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#     # New fields for discounted calculations
#     untaxed_amount = fields.Monetary(string="Untaxed Amount (with discount)", compute='_compute_discounted_totals',
#                                      store=True)
#     tax_amount = fields.Monetary(string="Tax Amount (with discount)", compute='_compute_discounted_totals', store=True)
#     total_amount = fields.Monetary(string="Total Amount (with discount)", compute='_compute_discounted_totals',
#                                    store=True)
#
#     @api.depends('order_line.price_unit', 'order_line.product_uom_qty', 'order_line.tax_id',
#                  'order_line.fixed_discount')
#     def _compute_discounted_totals(self):
#         for order in self:
#             untaxed_amount = 0.0
#             tax_amount = 0.0
#             total_amount = 0.0
#
#             for line in order.order_line:
#                 # Calculate discounted subtotal for each line
#                 line_subtotal = (line.price_unit * line.product_uom_qty) - line.fixed_discount
#                 untaxed_amount += line_subtotal
#
#                 # Calculate taxes based on the original price for tax calculation
#                 taxes = line.tax_id.compute_all(
#                     line.price_unit,
#                     order.currency_id,
#                     line.product_uom_qty,
#                     product=line.product_id,
#                     partner=order.partner_id
#                 )
#                 line_tax = taxes['total_included'] - taxes['total_excluded']
#
#                 tax_amount += line_tax
#                 total_amount += line_subtotal + line_tax
#
#             order.update({
#                 'untaxed_amount': untaxed_amount,
#                 'tax_amount': tax_amount,
#                 'total_amount': total_amount,
#             })
#
#
# class AccountMove(models.Model):
#     _inherit = 'account.move'
#
#     # New fields for discounted calculations
#     untaxed_amount = fields.Monetary(string="Untaxed Amount (with discount)", compute='_compute_discounted_totals',
#                                      store=True)
#     tax_amount = fields.Monetary(string="Tax Amount (with discount)", compute='_compute_discounted_totals', store=True)
#     total_amount = fields.Monetary(string="Total Amount (with discount)", compute='_compute_discounted_totals',
#                                    store=True)
#
#     @api.depends('invoice_line_ids.price_unit', 'invoice_line_ids.quantity', 'invoice_line_ids.tax_ids',
#                  'invoice_line_ids.fixed_discount')
#     def _compute_discounted_totals(self):
#         for move in self:
#             untaxed_amount = 0.0
#             tax_amount = 0.0
#             total_amount = 0.0
#
#             for line in move.invoice_line_ids:
#                 # Calculate line subtotal with fixed discount
#                 line_subtotal = (line.price_unit * line.quantity) - line.fixed_discount
#                 untaxed_amount += line_subtotal
#
#                 # Calculate taxes based on the original price for tax calculation
#                 taxes = line.tax_ids.compute_all(
#                     line.price_unit,
#                     move.currency_id,
#                     line.quantity,
#                     product=line.product_id,
#                     partner=move.partner_id
#                 )
#                 line_tax = taxes['total_included'] - taxes['total_excluded']
#
#                 tax_amount += line_tax
#                 total_amount += line_subtotal + line_tax
#
#             move.update({
#                 'untaxed_amount': untaxed_amount,
#                 'tax_amount': tax_amount,
#                 'total_amount': total_amount,
#             })

# from odoo import models, fields, api
#
# class SaleOrder(models.Model):
#     _inherit = 'sale.order'
#
#     fixed_discount = fields.Float(string="Total Fixed Discount ($)", help="Total fixed discount for the order.", store=True)
#
#     @api.depends('order_line.price_subtotal', 'order_line.fixed_discount')
#     def _compute_amount(self):
#         """Compute amount_untaxed, fixed_discount total, and amount_total for the order."""
#         for order in self:
#             # Calculate the untaxed amount and the total fixed discount
#             amount_untaxed = sum(line.price_subtotal for line in order.order_line)
#             fixed_discount = sum(line.fixed_discount for line in order.order_line)
#             # Calculate the total amount as untaxed minus fixed_discount
#             amount_total = amount_untaxed - fixed_discount
#
#             # Update order fields with computed values
#             order.update({
#                 'amount_untaxed': amount_untaxed,
#                 'fixed_discount': fixed_discount,
#                 'amount_total': amount_total,
#                 'amount_tax': 0.0  # Override amount_tax to zero
#             })
#
#     amount_tax = fields.Float(string="Tax", compute='_compute_amount', store=True)
#
#
#
#     class AccountMove(models.Model):
#         _inherit = 'account.move'
#
#         amount_tax = fields.Monetary(compute='_compute_custom_amount_tax', store=True)
#
#         @api.depends('line_ids.tax_ids', 'line_ids.price_unit', 'line_ids.quantity')
#         def _compute_custom_amount_tax(self):
#             for record in self:
#                 # Clear and re-compute custom tax logic for each line
#                 tax_amount = 0.0
#                 for line in record.invoice_line_ids:
#                     # Custom logic to calculate tax for each line
#                     tax_amount += sum(tax.amount for tax in line.tax_ids)
#                 record.amount_tax = tax_amount