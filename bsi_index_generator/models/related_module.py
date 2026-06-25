# -*- coding: utf-8 -*-
from odoo import fields, models

class BsiRelatedModule(models.Model):
    _name = 'bsi.related.module'
    _description = 'Related Module'
    _rec_name = 'name'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    name = fields.Char(string='Module Name', required=True)
    short_description = fields.Text(string='Short Description',
                                    help='One-line description shown on the module card')
    price = fields.Char(string='Price', help='Display price, e.g. "$9.00"')
    store_url = fields.Char(string='Store URL', help='Link to the Odoo App Store listing')
    image = fields.Binary(string='Module Image', attachment=True,
                          help='Banner/screenshot shown on the related-module card')
    generator_id = fields.Many2one('bsi.index.generator', string='Generator', ondelete='cascade')
