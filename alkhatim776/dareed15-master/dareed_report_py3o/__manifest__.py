{
    'name': 'Reports Py3o(.doc)',
    'version': '15.0.1.0.0',
    'category': 'Sales',
    'license': 'AGPL-3',
    'summary': 'py3o reports(.doc)',
    'description': """
Reports Py3o
=================

This module adds a py3o sale report (.doc format).
    """,
    'author': 'Digital Wave Solution Team',
    'depends': [
        'report_py3o',
        'sale',
        'dareed_services',
    ],
    'data': [
        'sale_report.xml',
        'cleaning_report.xml',
        'steam_report.xml',
        'marble_report.xml',
        'cleaning_steam_marble_report.xml',
        # 'cleaning_steam_marble_report.xml',
        'cleaning_steam_report.xml',
        'cleaning_marble_report.xml',
        'cleaning_sterilization_report.xml',
    ],
    'installable': True,
}
