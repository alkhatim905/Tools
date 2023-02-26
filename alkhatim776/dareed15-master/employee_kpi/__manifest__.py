# -*- coding: utf-8 -*-
{
    'name': "Employee KPI",
    'summary': "Employee KPI",
    'description': """ 
        This module adds employee KPI configuration in employee payslip.
     """,
    'author': "Digital Wave Solution Team",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': ['hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_kpi_views.xml',
        'views/hr_payslip_inherit_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
