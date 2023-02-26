# -*- coding: utf-8 -*-
{
    'name': "Invoice Layout Modification",
    'summary': "Invoice Layout Modification",
    'author': "Digital Wave Solution Team",
    'description': """
    This Module adds changes to odoo 13 invoice layout""",
    'category': 'Accounting',
    'version': '0.1',
    'depends': ['account_accountant', 'base'],
    'data': [
        #"reports/inherit_invoice_report_view.xml",
        "views/inherit_res_partner_view.xml",
        "views/inherit_account_move_view.xml",
        "views/inherit_res_company_view.xml",
    ],
    'installable': True,
    'auto_install': False,
}
