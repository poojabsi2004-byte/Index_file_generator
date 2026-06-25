# -*- coding: utf-8 -*-
from odoo import fields, models


class BsiModuleFeature(models.Model):
    _name = 'bsi.module.feature'
    _description = 'Module Feature'
    _rec_name = 'feature_heading'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    feature_title = fields.Char(string='Category Label',
                                help='Short uppercase category label shown above the heading, e.g. "Smart Filter"')
    feature_heading = fields.Char(string='Heading', required=True)
    feature_description = fields.Text(string='Description')
    generator_id = fields.Many2one('bsi.index.generator', string='Generator', ondelete='cascade')
