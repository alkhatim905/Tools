{
    'name': "Stock Card Report",
    'summary': "Stock Card Report",
    'description': """ 
            This module generates xlsx reports to .
     """,
    'author': "Digital Wave Solution Team",
    'category': 'Sales',
    'version': '0.1',
    'depends': ['stock', 'sale', 'purchase', 'report_xlsx'],
    'data': ['views/wizard_view.xml',
             'security/ir.model.access.csv',],
    'installable': True,
    'auto_install': False,
    'sequence': 1,
}
