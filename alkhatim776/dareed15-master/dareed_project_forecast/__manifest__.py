# -*- coding: utf-8 -*-
{
    'name': "Dareed Project Forecast",
    'summary': """Forecast your resources on project tasks""",
    'description': """
    Schedule your teams across projects and estimate deadlines more accurately.
    """,
    'sequence': 1,
    "author": "Digital Wave Solution Team",
    'category': 'Dareed Project Forecasting',
    'version': '1.0',
    'depends': ['project_forecast', 'dareed_project_management'],
    'data': [
        'security/ir.model.access.csv',
        'views/project_forecast_views.xml',
    ],
    'application': True
}
