# -*- coding: utf-8 -*-
from odoo import fields, models

class BsiModuleStep(models.Model):
    _name = 'bsi.module.step'
    _description = 'Module Step'
    _rec_name = 'step_heading'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    step_heading = fields.Char(string='Heading', required=True)
    step_description = fields.Text(string='Description')
    generator_id = fields.Many2one('bsi.index.generator', string='Generator', ondelete='cascade')
