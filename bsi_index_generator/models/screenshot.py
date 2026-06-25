# -*- coding: utf-8 -*-
from odoo import fields, models

class BsiModuleScreenshot(models.Model):
    _name = 'bsi.module.screenshot'
    _description = 'Module Screenshot'
    _rec_name = 'ss_heading'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    ss_heading = fields.Char(string='Step Title', required=True)
    ss_description = fields.Text(string='Description',
                                 help='Caption shown below the screenshot')
    ss_image = fields.Binary(string='Screenshot Image', attachment=True)
    generator_id = fields.Many2one('bsi.index.generator', string='Generator', ondelete='cascade')
