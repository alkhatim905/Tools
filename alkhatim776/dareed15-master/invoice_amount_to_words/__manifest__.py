# -*- coding: utf-8 -*-
{
    'name': "Invoice amount to words - Support Multi Languages",

    'summary': """
        Covert invoice/bill amount to words with support of many languages
        """,

    'description': """
        This module meet the needs of many companies to covert invoice/bill amount to words according to their languages.
        and also show this in the invoice/bill printout.
    """,

    'author': "iTech technical consulting & programming",
    'website': "http://www.itech.com.eg",
    'category': 'Accounting',
    'version': '14.0.1.4.4',
    'company': 'iTech Co.',
    'maintainer': 'iTech',

    'depends': ['base', 'account'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}