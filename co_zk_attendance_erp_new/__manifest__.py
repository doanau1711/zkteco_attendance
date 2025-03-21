# -*- coding: utf-8 -*-
{
    'name': "Zk Attendance",

    'summary': """
        Attendance by ZKTeco K21 Pro
        """,

    'description': """
        Attendance by ZKTeco K21 Pro
    """,

    'author': "Ngô Quang Trường",
    'maintainer': "CloudMedia Co.,Ltd",
    'website': "https://cloudmedia.vn",
    'license': 'GPL-3',
    'category': 'Human Resources',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_attendance'],
    
    'assets': {
    'web.assets_backend': [
        'co_zk_attendance_erp_new/static/src/js/co_hr_attendance.js',
    ],
},


    # always loaded
    'data': [
        'security/ir.model.access.csv',
        "wizard/co_attendance_wizard_view.xml",
        'views/hr_employee_views.xml',
        'views/hr_attendance_views.xml',
        'views/hr_biometric_device_views.xml',
        'views/hr_employee_biometric_views.xml',
        'views/zk_attendance_views.xml',
        'views/res_config_settings_views.xml',
        'views/menu_item.xml',
        # "views/assets.xml"
    ],
    'autoinstall': True,
    'application': True
}
