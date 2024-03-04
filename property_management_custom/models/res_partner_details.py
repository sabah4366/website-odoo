from odoo import fields, models


class ProprtyPartner(models.Model):
    """A class that inherits the already existing model res partner"""
    _inherit = 'res.partner'

    emirates_id = fields.Char('Tenant’s Emirates ID')
    co_occupants = fields.Integer('Number of Co-Occupants')
    license_no = fields.Integer(string="License No")
    license_auth = fields.Char(string="Licensing Authority")