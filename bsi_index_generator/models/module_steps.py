from odoo import fields, models, api

class ModuleFeatures(models.Model):
    _name = 'module.steps'
    _description = "Module Steps"
    _rec_name = "module_step_heading"
    
    module_step_icon = fields.Binary(string="steps")
    module_step_heading = fields.Char(string="Module step wise Heading")
    module_step_des = fields.Char(string="Module step wise Desciption")
    generator_id = fields.Many2one('index.file.generator', string="Generator")