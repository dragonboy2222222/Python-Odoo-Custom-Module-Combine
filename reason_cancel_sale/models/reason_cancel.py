from odoo import api, fields, models, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_cancel(self):

        # Open the wizard to capture the cancel reason
        return {
            'name': _('Cancel Reason'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order.cancel.reason',
            'view_mode': 'form',
            'view_id': False,
            'target': 'new',
            'context': {'active_ids': self.ids},
        }


class SaleOrderCancelReason(models.TransientModel):
    _name = 'sale.order.cancel.reason'
    _description = 'Cancel Reason Wizard'

    cancel_reason = fields.Html('Cancel Reason', sanitize=True, required=True)

    def action_apply_cancel_reason(self):
        # Apply the cancel reason to the Sale Order.
        self.ensure_one()
        sale_orders = self.env['sale.order'].browse(self._context.get('active_ids'))
        for order in sale_orders:
            # Log the cancel reason in the chatter
            order.message_post(body=_("Cancel Reason: %s") % self.cancel_reason)
            # Cancel the order
            order.write({'state': 'cancel'})
        return True



