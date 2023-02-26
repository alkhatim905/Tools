# -*- coding: utf-8 -*-
{
    'name': "Invoice Follow Up",
    'summary': """Invoice Follow Up""",
    'description': """
        This Module adds invoice follow up field to invoice.
    """,
    'author': "Digital Wave Solution Team",
    'website': "",
    'category': 'Accounting',
    'version': '12.0',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_invoice_inherit_view.xml',
    ],
    'sequence': 1,
}
