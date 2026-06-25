# -*- coding: utf-8 -*-
{
    'name': 'BSI Dynamic Index Generator',
    'author': 'Botspot Infoware Pvt. Ltd.',
    'category': 'Tools',
    'summary': 'Dynamically generate Odoo App Store index.html files from backend data.',
    'website': 'https://www.botspotinfoware.com',
    'description': """
        Generate fully dynamic index.html pages for Odoo App Store listings.

        Control all content including:
        - Hero section
        - Statistics
        - Steps (with compatible version info)
        - Features
        - Screenshots
        - Demo video
        - Related modules
        - Multi-language support (dynamic)
        - Footer

        All content is managed from a single Odoo backend form.
        """,
    'version': '18.0.1.0.0',
    'maintainer': 'Botspot Infoware Pvt. Ltd.',
    'depends': ['base_setup', 'web'],
    'data': [
        'security/ir.model.access.csv',
        'data/default_languages.xml',
        'views/index_generator.xml',
    ],

    'license': 'LGPL-3',
    'assets': {
        'web.assets_backend': [
            'bsi_dynamic_index_generator/static/src/scss/index_generator_form.scss',
        ],
    },

    'installable': True,
    'application': True,
    'auto_install': False,
}
