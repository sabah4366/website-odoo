from odoo import api, fields, models, _


class AProperty_Owner(models.Model):
    _name = "property.owner"
    _description = "Owner/Lessor"
    _rec_name = "owners_name"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    owners_name = fields.Char(string="Owner's Name")
    lessor_name = fields.Char(string="Lessor’s Name")
    emirates_id = fields.Char('Lessor’s Emirates ID')
    lessor_type =  fields.Selection(string='Lessor Type',
                                    selection=[('person', 'Individual'), ('company', 'Company')],default = "person")
    license_no = fields.Integer(string="License No")
    license_auth = fields.Char(string = "Licensing Authority")
    lessor_email = fields.Char(string = "Email")
    lessor_phone =fields.Char(string = "Phone")
    active = fields.Boolean(default=True)
    street = fields.Char()
    street2 = fields.Char()
    zip = fields.Char(change_default=True)
    city = fields.Char()
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict',
                               domain="[('country_id', '=?', country_id)]")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict')
    country_code = fields.Char(related='country_id.code', string="Country Code")


