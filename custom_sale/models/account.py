from odoo import models, fields , api

class AccountMove(models.Model):
    _inherit = 'account.move'

    delivery_type = fields.Selection(
        [('standard', 'Standard Delivery'),
         ('express', 'Express (Next-Day) Delivery'),
         ('same_day', 'Same-Day Delivery')],
        string="Delivery Type",
        default='standard'

    )

    customer_id = fields.Many2one('res.partner', compute='_compute_customer_id', string="Customer Name")

    @api.depends('invoice_line_ids.sale_line_ids.order_id')
    def _compute_customer_id(self):
        for record in self:
            # Get the sale order linked to this invoice
            sale_order = self.env['sale.order'].search([('invoice_ids', 'in', record.ids)], limit=1)
            if sale_order:
                record.customer_id = sale_order.partner_id
            else:
                record.customer_id = False