# -*- coding: utf-8 -*-
{
    'name': "IDC Verbex Integration",
    'summary': """CRM Campaign""",
    'description': """RM Campaign""",
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
        'views/product_template_views.xml',
        'views/helpdesk_ticket.xml',
    ],
}
