from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_type = fields.Selection(
        [('standard', 'Standard Delivery'),
         ('express', 'Express (Next-Day) Delivery'),
         ('same_day', 'Same-Day Delivery')],
        string="Delivery Type",
        default='standard',
        tracking = True
    )

    def _prepare_invoice(self):
        # Call the super method to get the invoice values
        invoice_vals = super(SaleOrder, self)._prepare_invoice()

        # Include the delivery_type in the invoice values
        invoice_vals['delivery_type'] = self.delivery_type
        return invoice_vals
