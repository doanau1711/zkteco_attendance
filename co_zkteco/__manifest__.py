# -*- coding: utf-8 -*-
{
    'name': "ZKTeco",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_attendance', 'co_zk_attendance_erp_new'],
    
     'assets': {
    'web.assets_backend': [
        'co_zkteco/static/src/js/hr_attendance_temporary_button.js',
        'co_zkteco/static/src/xml/hr_attendance_temporary_button.xml',
    ],
},

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        # 'views/assets.xml',
        'views/hr_attendance_temporary_views.xml',
        'views/co_hr_attendance_zk_views.xml',
    ],
    'qweb': [
        'static/src/xml/hr_attendance_temporary_button.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
