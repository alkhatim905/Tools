# -*- coding: utf-8 -*-
{
    'name': "Sale_info",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','web','sale','purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
     'assets': {
        'web.assets_backend': {
            '/sale_info/static/src/scss/popup.scss',
            '/sale_info/static/src/js/info_widget.js',
            
        },
        # 'web.assets_frontend': {
        #     '/vista_backend_theme/static/src/scss/login.scss',
        #     '/vista_backend_theme/static/src/scss/login.scss',
        # },
        'web.assets_qweb': {
            '/sale_info/static/src/xml/info_partner.xml'
        },
    },
}
