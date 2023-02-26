# -*- coding: utf-8 -*-
{
    'name': "HR Modification",
    'summary': "HR Modification",
    'description': """ 
            This module add some Customization related to hr module.
     """,
    'author': "Digital Wave Solution Team",
    'category': 'hr',
    'version': '0.1',
    'depends': ['base', 'hr', 'hr_payroll', 'hr_attendance', 'hr_holidays', 'hr_experience'],
    'data': [
        'security/ir.model.access.csv',
        #'data/hr_payroll_data.xml',
        'views/hr_contract_inherit_view.xml',
        'views/hr_employee_inherit_view.xml',
        'views/hr_employee_overtime.xml',
        'views/bi_conf_settings_view.xml',
        'views/payslip_inherit.xml',
        'views/accumulate_leaves.xml',
        'views/hr_leave_allocation.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
