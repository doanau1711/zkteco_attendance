from odoo import fields, models, api, exceptions
from odoo.osv import expression


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    device_id = fields.Char(
        string='Biometric Device ID',
        help="Give the biometric device id",
        groups="hr.group_hr_user"
    )

    #
    # @api.model
    # def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
    #     args = args or []
    #     if name:
    #         return self._search(expression.AND([[
    #             '|',
    #             ('name', operator, name),
    #             ('code', operator, name)
    #         ], args]), limit=limit,
    #                             access_rights_uid=name_get_uid)
    #     return super(HrEmployee, self)._name_search(name, args=args, operator=operator, limit=limit,
    #                                                    name_get_uid=name_get_uid)