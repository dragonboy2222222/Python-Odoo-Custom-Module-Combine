from odoo import models, _
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_confirm(self):
        """Validate stock availability, auto-validate delivery orders, and create invoices."""
        for order in self:
            # Validate stock availability
            for line in order.order_line:
                if line.product_id.type in ('product', 'consu') and line.product_uom_qty > line.product_id.virtual_available:
                    raise UserError(
                        _("Product '%s' does not have enough stock. Reduce the quantity or restock before confirming the order.")
                        % line.product_id.display_name
                    )

            # Confirm the sales order
            super(SaleOrder, order).action_confirm()

            # Auto-validate delivery orders
            for picking in order.picking_ids.filtered(lambda p: p.state not in ('done', 'cancel')):
                if all(move.product_uom_qty <= move.product_id.virtual_available for move in picking.move_ids):
                    picking.action_assign()
                    picking.action_confirm()  # Confirm the picking
                    picking.button_validate()  # Validate the picking (mark as done)

            # Auto-create invoice
            if order.invoice_status == 'to invoice':
                invoice = order._create_invoices()

                invoice.action_post()   #to make the confirm in invoice by calling action_post
                order.invoice_ids |= invoice  #Adds the created invoice to the invoice_ids field of the sales order

        return True
