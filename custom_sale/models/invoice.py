# from odoo import models, fields, api
#
# class AccountMoveLine(models.Model):
#     _inherit = 'account.move.line'
#
#     fixed_discount = fields.Float(string="Fixed Discount", default=0.0)
#
#     @api.depends('quantity', 'discount', 'price_unit', 'tax_ids', 'fixed_discount')
#     def _compute_price(self):
#         """
#         Overriding method to include fixed discount in the invoice line calculations.
#         """
#         for line in self:
#             price = line.price_unit - line.fixed_discount
#             taxes = line.tax_ids.compute_all(price, line.move_id.currency_id, line.quantity, product=line.product_id, partner=line.partner_id)
#             line.update({
#                 'price_subtotal': taxes['total_excluded'],
#                 'price_total': taxes['total_included'],
#                 'price_tax': taxes['total_included'] - taxes['total_excluded'],
#             })