# -*- coding: utf-8 -*-
{
    'name': "Dareed HR fields",
    'summary': "Dareed hr fields",
    'description': """ 
            This module adds some new fields to hr.employee.
     """,
    'author': "Digital Wave Solution Team",
    'category': 'HR',
    'version': '0.1',
    'depends': ['base', 'hr', 'hr_payroll'],
    'data': [
        'views/inherited_hr_employee_view.xml',
        'views/inherited_hr_contract_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
