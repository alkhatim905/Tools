{
    'name': 'Project Labor Planning',
    'version': '15.0.1.0.0',
    'category': 'Project',
    'license': 'AGPL-3',
    'summary': 'Plan Labor Allocation on Projects',
    'description': """
This module allows you to allocate your labor in projects.
    """,
    'author': 'Digital Wave Solution Team',
    'depends': [
        'project','dareed_project_management',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/project_labor_planning_views.xml',
        'views/project_labor_planning_templates.xml',
        'views/project_views.xml',
        'views/plp_config_settings_views.xml',
        'views/not_attended_staff_views.xml',
        'views/project_allocation_views.xml',
        'views/project_allocation_report.xml',
    ],
    "assets": {
        "web.assets_backend": [
            "/project_labor_planning/static/src/js/project_labor_planning_widget.js",
        ],
    },
    'qweb': ['static/src/xml/plp_backend.xml'],

    'installable': True,
}
