{
    'name': "Project Status Report",
    'summary': "Project Status Report",
    'description': """ 
            This module generates xlsx reports to Projects States.
     """,
    'author': "Digital Wave Solution Team",
    'category': 'Project',
    'version': '0.1',
    'depends': ['project_labor_planning', 'dareed_project_management', 'report_xlsx', 'project'],
    'data': ['views/wizard_view.xml'],
    'installable': True,
    'auto_install': False,
    'sequence': 1,
}
