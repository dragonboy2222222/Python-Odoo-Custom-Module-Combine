from odoo import models, fields

class ResUsers(models.Model):
    _inherit = 'res.users'

    department_id = fields.Many2many('hr.department', string="Department")
    area_id= fields.Many2many('res.area', string="Areas")
