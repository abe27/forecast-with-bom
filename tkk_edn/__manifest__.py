# -*- coding: utf-8 -*-
{
    'name': "EDN",
    'summary': "โมดูลสำหรับงาน Upload ข้อมูล TKK EDN.",
    'description': """โมดูลนี้จัดทำมาเพื่ออำนวยความสะดวกในการทำงานกับระบบ Electronic Data Interchange""",
    'author': "Taweechai Yuenyang",
    "email": "taweechai.yuenyang@outlook.com",
    'website': 'https://taweechai-yuenyang.github.io',
    'sequence': 5,
    # license คือ หมวดหมู่หน่วยงานของโมดูล
    'license': 'Other OSI approved licence',
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web', 'mail','stock','abe_backend_theme'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
        'demo/partner_tag.xml',
        'demo/partner.xml',
        'demo/part_group.xml',
        'demo/part_tag.xml',
        'demo/uom.xml',
    ],
    "application": True,
    'installable': True,  # installable คือ ระบุว่าโมดูลสามารถติดตั้งได้หรือไม่
    'auto_install': False,  # auto_install คือ ระบุว่าโมดูลจะติดตั้งโดยอัตโนมัติหรือไม่
}

