from odoo import fields, models

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    minimum_work_time = fields.Float(
        string='Minimum Work Time',
        default=1.0,
        config_parameter='attendance_minimum_work_time'
    )

    start_hour_of_day = fields.Float(
        string='Start Hour of the Day',
        default=0.0,
        config_parameter='start_hour_of_day'
    )
