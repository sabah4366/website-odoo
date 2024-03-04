from odoo import api, fields, models, _


class Apartment_Booking(models.Model):

    _name = "apartment.booking"
    _description = "Booking"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name =  fields.Char(
        string="Reference",
        readonly=True,
        copy=False,
        default=lambda self: _("New"),
        help="Sequence/code for the property",
    )
    tenent_id = fields.Many2one("res.partner" ,string="Tenent" )
    property_id = fields.Many2one("property.property", string="Property")
    apartment_id = fields.Many2one("property.apartment", string="Apartment",domain="[('state','=','available'),('property_id','=',property_id)]")
    street = fields.Char(string="Street", required=True, help="The street name",translate=True)
    street2 = fields.Char(string="Street2", help="The street2 name",translate=True)
    zip = fields.Char(string="Zip", change_default=True, help="Zip code for the place")
    city = fields.Char(string="City", help="The name of the city")
    country_id = fields.Many2one(
        "res.country",
        string="Country",
        ondelete="restrict",
        required=True,
        help="The name of the country",
    )
    state_id = fields.Many2one(
        "res.country.state",
        string="State",
        ondelete="restrict",
        tracking=True,
        domain="[('country_id', '=?', country_id)]",
        help="The name of the state",
    )
    address_home_id = fields.Many2one(
        'res.partner', 'Address', help='Enter here the private address of the employee, not the one linked to your company.',
       )
    is_address_home_a_company = fields.Boolean(
        'The employee address has a company linked',

    )
    private_email = fields.Char( string=" Email", )
    country_id = fields.Many2one(
        'res.country', 'Nationality (Country)',  tracking=True)

    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('cohabitant', 'Legal Cohabitant'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status',  default='single', tracking=True)
    spouse_complete_name = fields.Char(string="Spouse Complete Name",  tracking=True)
    spouse_birthdate = fields.Date(string="Spouse Birthdate",  tracking=True)
    children = fields.Integer(string='Number of Dependent Children',  tracking=True)
    place_of_birth = fields.Char('Place of Birth', tracking=True)
    country_of_birth = fields.Many2one('res.country', string="Country of Birth",  tracking=True)
    birthday = fields.Date('Date of Birth',  tracking=True)
    ssnid = fields.Char('SSN No', help='Social Security Number', tracking=True)
    sinid = fields.Char('SIN No', help='Social Insurance Number',  tracking=True)
    identification_id = fields.Char(string='Identification No', tracking=True)
    passport_id = fields.Char('Passport No', groups="hr.group_hr_user", tracking=True)
    bank_account_id = fields.Many2one(
        'res.partner.bank', 'Bank Account Number',

        groups="hr.group_hr_user",
        tracking=True,
        help='Employee bank account to pay salaries')
    permit_no = fields.Char('Work Permit No', tracking=True)
    visa_no = fields.Char('Visa No', tracking=True)
    visa_expire = fields.Date('Visa Expire Date',  tracking=True)

    additional_note = fields.Text(string='Additional Note',  tracking=True)
    emergency_contact = fields.Char("Contact Name",  tracking=True)
    emergency_phone = fields.Char("Contact Phone",  tracking=True)
    km_home_work = fields.Integer(string="Home-Work Distance", tracking=True)
    work_place = fields.Char("Work Place",  tracking=True)

    phone = fields.Char(related='address_home_id.phone', related_sudo=False, readonly=False, string="Private Phone", )
    # employee in company
    # child_ids = fields.One2many('hr.employee', 'parent_id', string='Direct subordinates')

    # misc
    pin = fields.Char(string="PIN", copy=False,
        help="PIN used to Check In/Out in the Kiosk Mode of the Attendance application (if enabled in Configuration) and to change the cashier in the Point of Sale application.")



    id_card = fields.Binary(string="ID Card Copy")
    driving_license = fields.Binary(string="Driving License",)

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("booked", "Booked"),
            # ("rented", "Rented"),
            # ("sold", "Sold"),
        ],
        required=True,
        string="Status",
        default="draft",
        help="* The 'Draft' status is used when the property is in draft.\n"
             "* The 'Available' status is used when the property is "
             "available or confirmed\n"
             "* The 'Rented' status is used when the property is rented.\n"
             "* The 'sold' status is used when the property is sold.\n",
    )

    document_ids = fields.One2many("document.line","request_id", string="Upload Documents")
    contract_count = fields.Integer(compute='_compute_apartment_count')

    @api.model
    def create(self, vals):
        """Generating sequence number at the time of creation of record"""
        if vals.get("name", "New") == "New":
            vals["name"] = (
                    self.env["ir.sequence"].next_by_code("apartment.booking") or "New"
            )
        res = super(Apartment_Booking, self).create(vals)
        return res

    def _compute_apartment_count(self):
        self.contract_count = self.env['property.rental'].search_count([('related_booking_id', '=', self.id)])

    def action_create_contract(self):
            context = {
                'default_related_booking_id': self.id,
                'default_renter_id': self.tenent_id.id,
                'default_property_id': self.property_id.id,
                'default_apartment_id': self.apartment_id.id,
            }
            return {
                'type': 'ir.actions.act_window',
                'name': 'Rental Contract',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'property.rental',
                'context': context,
            }


    def action_view_contract(self):
        return {
            "name": "Contract",
            "view_mode": "tree,form",
            "res_model": "property.rental",
            "type": "ir.actions.act_window",
        }


class RentalDocument(models.Model):
    """A class for the model property.area.measure to represent
    the area of each sections"""
    _name = 'document.line'
    _description = ' Rental Documents'

    document_name = fields.Char(string='Document Name',)

    request_id = fields.Many2one('apartment.booking', string='Rental Request' )
    document =  fields.Binary(string="Upload Documents",  tracking=True)
