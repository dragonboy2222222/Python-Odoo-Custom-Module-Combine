from odoo import models, fields

class ResArea(models.Model):
    _name = 'res.area'
    _description = 'Resource Area'

    name = fields.Char(string="Area Name", required=True)
  
    
