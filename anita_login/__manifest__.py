# -*- coding: utf-8 -*-
{
    'name': "anita_login",

    'summary': """
        Login Pages For Odoo
    """,

    'description': """
        Login Pages For Odoo
    """,

    'author': "crax",
    'website': "https://www.openerpnext.com",

    'category': 'Theme/Backend',
    'version': '17.0.0.2',
    'license': 'OPL-1',
    'images': [
        'static/description/banner.png',
        'static/description/anita_screenshot.png'
    ],

    'depends': ['base', 'web'],

    'data': [
        "views/login_style1.xml",
        "views/login_style2.xml",
        "views/login_style3.xml",
        "views/login_style4.xml"
    ],

    'assets': {
        'web.assets_backend': [],
    }
}
