# # In your custom module, you can override the `action_apply_discount` method in the wizard
# from odoo import models, fields, api
#
#
# class SaleOrderDiscount(models.Model):
#     _inherit = 'sale.order.discount'
#
#     @api.model
#     def action_apply_discount(self):
#         # You can add logic here to apply the fixed discount in addition to the percentage discount
#         super().action_apply_discount()
#
#         for order_line in self.sale_order_id.order_line:
#             # Apply fixed discount in addition to existing logic
#             order_line.fixed_discount = 10.0  # Example: Set a fixed discount for each line
#
#             # Recompute totals after applying fixed discount
#             order_line._compute_amount()
#
#         self.sale_order_id._compute_amount()  # Ensure the order is re-calculated


