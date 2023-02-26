# -*- coding: utf-8 -*-
{
    'name': "Dareed Invoice Customization",
    'summary': """Dareed Invoice Customization""",
    'description': """
        This Modules Add new fields to invoice.
    """,
    'author': "Digital Wave Solution Team",
    'website': " ",
    'category': 'Accounting',
    'version': '12.0',
    'depends': ['account', 'project'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_invoice_cron.xml',
        'views/account_invoice_inherit_view.xml',
    ],
    'sequence': 1,
}
