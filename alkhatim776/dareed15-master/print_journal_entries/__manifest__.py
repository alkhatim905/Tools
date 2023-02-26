# -*- coding: utf-8 -*-
{
    'name': "Print Journal Entry Reports",
    'summary': "journal entry reports",
    'description': """ 
            This module prints Journal Entries as PDF report.
     """,
    'author': "Digital Wave Solution Team",
    'category': 'accounting',
    'version': '0.1',
    'depends': ['base', 'account'],
    'data': [
        'views/report_journal_entry.xml',
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
