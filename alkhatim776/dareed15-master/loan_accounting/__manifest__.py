# -*- coding: utf-8 -*-
{
    'name': 'Loan Accounting',
    'version': '0.1',
    'summary': 'Loan Accounting',
    'description': """
        Create accounting entries for loan requests.
        """,
    'category': 'Human Resources',
    'author': "Digital Wave Solution Team",
    'depends': [
        'base', 'hr_payroll', 'hr', 'account', 'loan_management',
    ],
    'data': [
        'wizard/loan_payment_wizard.xml',
        'views/hr_loan_config.xml',
        'views/hr_loan_acc.xml',
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
