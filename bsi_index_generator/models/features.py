from odoo import fields, models, api

class ModuleFeatures(models.Model):
    _name = "index.generator.feature"
    _description = "Module Description"
    _rec_name = "feature_heading"
    
    feature_title = fields.Char(string="Feature Title")
    feature_heading = fields.Char(string="Feature Heading")
    feature_des = fields.Char(string="Feature Desciption")
    generator_id = fields.Many2one('index.file.generator', string="Generator")