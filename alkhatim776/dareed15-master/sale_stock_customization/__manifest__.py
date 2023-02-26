# -*- coding: utf-8 -*-
{
    'name': "Sale Stock Customization",
    'summary': "Sale Stock Customization",
    'description': """ 
            This module edit on sale to edit expected date in orders and it's shipments and pass effective date in pickings moves/entries.
     """,
    'author': "Digital Wave Solution Team",
    'category': 'Sale',
    'version': '0.1',
    'depends': ['base','sale_stock', 'sale', 'stock','stock_account'],
    'data': [
        'views/stock_picking_inherit_view.xml'
    ],
    'installable': True,
    'auto_install': False,
    'sequence': 1
}
