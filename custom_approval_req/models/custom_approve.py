from odoo import models, fields, api

class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    department_id = fields.Many2one(
        'hr.department',
        string="Department",
        compute='_compute_department_area',
        store=True
    )
    area_id = fields.Many2one(
        'res.area',
        string="Area",
        compute='_compute_department_area',
        store=True
    )

    @api.depends('create_uid')
    def _compute_department_area(self):
        for record in self:
            
            user = record.create_uid
            if user:
                
                record.department_id = user.department_id[:1] if user.department_id else False
                record.area_id = user.area_id[:1] if user.area_id else False
            else:
                
                record.department_id = False
                record.area_id = False
