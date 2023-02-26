{
    'license': 'LGPL-3',
    "name": "Dareed Calculation Sheet",
    "version": "1",
    'sequence': 1,
    "author": "Digital Wave Solution Team",
    "category": "Dareed Services",
    "summary": "Adding requirements in (Inspection & calculation sheet_V2.xlsx)",
    "depends": ["sale_management", "project", "hr_timesheet"],
    #"percent_field"
    "data": [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/quotation_data.xml',
        'data/functions.xml',
        'views/menuitems.xml',
        'views/sale_config_changes.xml',
        'views/sale_order_changes.xml',
        'views/project_task.xml',
        'views/project_project.xml',
        'views/res_partner_form.xml',
        'views/product_template_changes.xml',
        'views/adding_configuration_menuitems.xml',
    ],
    "installable": True
}
