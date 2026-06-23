from odoo import fields, models, api

class ModuleFeatures(models.Model):
    _name = "index.generator.screenshot"
    _description = "Module SchreenShots"
    _rec_name = "ss_title"
    
    ss_title = fields.Char(string="SS Title")
    ss_heading = fields.Char(string="SS Heading")
    ss_des = fields.Char(string="SS Desciption")
    ss_image = fields.Binary(string="SS image")
    generator_id = fields.Many2many('index.file.generator', string="Generator")