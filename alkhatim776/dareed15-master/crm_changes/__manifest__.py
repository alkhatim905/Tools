{
    'license': 'LGPL-3',
    "name": "Dareed CRM Changes",
    "version": "1",
    'sequence': 1,
    "author": "Digital Wave Solution Team",
    "category": "Dareed CRM",
    "summary": "Adding requirements in (https://drive.google.com/file/d/1uKtX40ST63f3nCC_y48Bdcbkejy3mYNN/view)",
    "depends": ["crm", "dareed_services", "sale_crm"],
    "data": [
        "security/ir.model.access.csv",
        "views/crm_stage_form.xml",
        "views/crm_lead_form.xml",
        "views/service_type_views.xml",
    ],
    "installable": True
}
