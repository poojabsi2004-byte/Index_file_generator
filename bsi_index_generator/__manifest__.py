# -*- coding: utf-8 -*-
{
    'name': "Index File Generator",
    'author': 'Botspot Infoware Pvt. Ltd.',
    'category': 'Tools',
    'summary': """ Create index file for odoo app store.""",
    'website': 'https://www.botspotinfoware.com',
    'company': 'Botspot Infoware Pvt. Ltd.',
    'maintainer': 'Botspot Infoware Pvt. Ltd.',
    'description': """Create index file for odoo app store.""",
    'version': '19.0.1.0',
    'depends': ['base_setup', 'web'],
    'data': [
                'security/ir.model.access.csv',
                'views/index_generator.xml',
                'views/res_config_settings.xml',
            ],
    'assets': {
        'web.assets_backend': [
           'bsi_index_generator/static/description/index.html',
        ]
    },
    # 'images': ['static/description/Banner.gif'],
    # 'license': 'OPL-1',
    # 'price': 9.00,
    # 'currency': 'USD',
    'installable': True,
    'application': True,
    'auto_install': False,
}
