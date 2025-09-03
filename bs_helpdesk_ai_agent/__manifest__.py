# -*- coding: utf-8 -*-
{
    'name': "BS Helpdesk AI Agent",
    'summary': """CRM""",
    'description': """CRM""",
    "author": "Brain Station 23 LTD",
    "website": "http://www.brainstation-23.com",
    "license": "LGPL-3",
    'category': 'CRM',
    'version': '18.0',
    "application": True,
    "installable": True,
    "auto_install": False,
    'depends': ['mail', 'contacts', 'sale_management', 'fastapi', 'helpdesk'],

    'data': [
        'security/ir.model.access.csv',
        'views/res_config_setting_views.xml',
        'data/helpdesk.xml',
        'views/product_template_views.xml',
        'views/helpdesk_ticket.xml',
        'views/sale_order_views.xml',
        'wizard/conversation_wizard_views.xml',
    ],
}
