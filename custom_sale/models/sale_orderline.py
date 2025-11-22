# from odoo import api, fields, models
#
# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#
#     fixdis = fields.Float(string="Fixed Discount")
#
#     @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'fixdis')
#     def _compute_amount(self):
#         """
#         Compute the amounts of the sale line, considering the fixed discount.
#         """
#         for line in self:
#             # Apply fixed discount by subtracting it from the unit price
#             price = line.price_unit - line.fixdis
#             taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_id)
#             line.update({
#                 'price_tax': taxes['total_included'] - taxes['total_excluded'],
#                 'price_total': taxes['total_included'],
#                 'price_subtotal': taxes['total_excluded'],
#             })
