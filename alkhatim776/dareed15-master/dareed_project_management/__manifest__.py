{
    'license': 'LGPL-3',
    "name": "Dareed Project Management",
    "version": "1",
    'sequence': 1,
    "author": "Digital Wave Solution Team",
    "category": "Dareed Project Management",
    "summary": "Adding requirements in (https://drive.google.com/file/d/1ARi5j7D7F-EfBNhQ-86Er0JvJn9PRNA1/view)",
    "depends": ["project", "dareed_services"],
    # "percent_field"
    "data": [
        "security/ir.model.access.csv",
        "security/groups.xml",
        "views/project_task_tree.xml",
        "views/project_task_form.xml",
        "views/project_project_form.xml",
        "views/hr_employee_form.xml",
        "views/account_analytic_line_tree.xml",
    ],
    "installable": True
}
