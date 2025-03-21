from odoo import fields, models


class Biometric(models.Model):
    _name = 'hr.biometric.device'
    _description = 'Biometric Device'

    _sql_constraints = [
        ('name_uniq', 'unique (serial)', 'The serial unique per biometric device!')
    ]
    name = fields.Char('Biometric Name', required=True)
    serial = fields.Char('Biometric Serial', required=True)
    active = fields.Boolean(default=True)

    def find_by_serial(self, sn: str):
        if sn:
            return self.sudo().search([('serial', '=', sn), ('active', '=', True)])
        return None
