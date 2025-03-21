from odoo import fields, models, api


class BiometricSetting(models.Model):
    _inherit = "hr.biometric.device"

    ip = fields.Char('Biometric IP')
    port = fields.Char('Biometric Port', default='4370')




