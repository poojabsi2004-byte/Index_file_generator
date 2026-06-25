# -*- coding: utf-8 -*-
from odoo import fields, models

class BsiIndexLanguage(models.Model):
    _name = 'bsi.index.language'
    _description = 'Index Language'
    _rec_name = 'name'
    _order = 'sequence, id'

    sequence = fields.Integer(default=10)
    name = fields.Char(string='Language', required=True)
    icon = fields.Binary(string='Flag Icon', attachment=True)
    icon_filename = fields.Char(string='Icon Filename')
    icon_asset_name = fields.Char(
        string='Built-in Icon Asset',
        help='Filename inside static/description/assets/icons/ (e.g. eng.png). '
             'Used when no custom icon is uploaded.',
    )
