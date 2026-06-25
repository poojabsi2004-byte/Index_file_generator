# -*- coding: utf-8 -*-
from odoo import api, fields, models

class BsiIndexFile(models.Model):
    _name = 'bsi.index.file'
    _description = 'BSI Index File Template'
    _rec_name = 'name'

    name = fields.Char(string='Name', required=True)
    template = fields.Binary(string='Template File', attachment=True)
    template_filename = fields.Char(string='Template Filename')
    use_template = fields.Boolean(
        string='Use Template?',
        help='Only one template can be active at a time. '
             'Setting this True will automatically unset it on all other templates. '
             'The active template is auto-loaded in the Index Generator.',
    )

    # ── Mutual exclusivity: only one record can have use_template=True ─────────

    def write(self, vals):
        if vals.get('use_template'):
            # Capture old active templates BEFORE the super() write
            old_active = self.env['bsi.index.file'].search(
                [('id', 'not in', self.ids), ('use_template', '=', True)]
            )
            old_active_ids = old_active.ids

        result = super().write(vals)

        if vals.get('use_template'):
            # Turn off use_template on every other index-file record
            if old_active_ids:
                self.env['bsi.index.file'].browse(old_active_ids).write({'use_template': False})
            # Update generators: those with no template OR pointing to the old active template
            domain = ['|', ('index_file_id', '=', False), ('index_file_id', 'in', old_active_ids)]
            self.env['bsi.index.generator'].search(domain).write({'index_file_id': self.id})
        return result

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records.filtered('use_template'):
            # Turn off all other records
            self.env['bsi.index.file'].search(
                [('id', '!=', record.id), ('use_template', '=', True)]
            ).write({'use_template': False})
            # Auto-fill generators with no explicit template
            self.env['bsi.index.generator'].search(
                [('index_file_id', '=', False)]
            ).write({'index_file_id': record.id})
        return records
