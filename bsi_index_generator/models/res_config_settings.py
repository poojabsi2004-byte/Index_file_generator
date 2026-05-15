from odoo import fields, models, api

class ModuleFeatures(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = "Custom Settings"
    
    index_file = fields.Binary(string="Index File")