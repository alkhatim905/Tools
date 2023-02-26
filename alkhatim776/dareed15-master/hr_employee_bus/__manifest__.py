# -*- coding: utf-8 -*-
{
    'name': "Employee Bus",
    'summary': "Employee Bus",
    'description': """ 
        This module adds the employee buses, and handles the buses delay.
     """,
    'author': "Digital Wave Solution Team",
    'category': 'Human Resources',
    'version': '0.1',
    'depends': ['hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_bus_views.xml',
        'views/hr_attendance_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}