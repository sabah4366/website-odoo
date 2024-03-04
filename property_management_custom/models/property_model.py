from odoo import api, fields, models, _


class Property(models.Model):
    """A class for the model property to represent the property"""

    _inherit = "property.property"
    _description = "Property"

    apartment_count = fields.Integer(compute='_compute_apartment_count')
    apartment_ids = fields.One2many(
        "property.apartment",
        'property_id',
        string="Apartments",


    )

    def _compute_apartment_count(self):
        self.apartment_count = self.env['property.apartment'].search_count([('property_id', '=', self.id)])

    property_type = fields.Selection(
        [
            ("land", "Land"),
            ("residential", "Residential"),
            ("commercial", "Commercial"),
            ("industry", "Industry"),
        ],
        string="Type",
        required=True,
        help="The type of the property",
    )
    sale_rent = fields.Selection(
        [
            ("for_sale", "For Sale"),
            ("for_tenancy", "For Tenancy"),
            ("for_auction", "For Auction"),
        ],
        string="Sale | Rent",
        required=True,
        default="for_tenancy",
        readonly=True,
    )
    rent_month = fields.Monetary(
        string="Rent/Month", help="Annual Rent", tracking=True,
    )
    property_category = fields.Selection(
        [
            ("apartment", "Apartment"),
            ("villa", "Villa"),

        ],
        string="Property Category",
        default = "apartment",
        required=True)
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("available", "Available"),
            ("rented", "Rented"),
            ("sold", "Sold"),
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
    landlord_id = fields.Many2one("property.owner", string="LandLord")
    furnishing = fields.Selection(
        [
            ("no_furnished", "Not Furnished"),
            ("half_furnished", "Partially Furnished"),
            ("furnished", "Fully Furnished"),
        ],
        string="Furnishing",
        help="Whether the residence is fully furnished or partially/half "
             "furnished or not at all furnished",
    )
    bedroom = fields.Integer(
        string="Bedrooms", help="Number of bedrooms in the property"
    )
    bathroom = fields.Integer(
        string="Bathrooms", help="Number of bathrooms in the property"
    )

    plot_number = fields.Integer(string="Plot No")
    makani_number = fields.Integer(string="Makani No")
    property_number = fields.Integer(string="Property No")
    building_name = fields.Char(string="Building Name")
    property_area = fields.Float(string="Property Area (s.m)")
    type_property = fields.Char(string="Property Type")
    location = fields.Char(string="Location")
    permission_no = fields.Integer(string="Permises No (DEWA)")

    emirate_state =  fields.Selection(
        [
            ("abu_dhabi", "Abu Dhab"),
            ("dubai", "Dubai"),
            ("sharjah", " Sharjah"),
            ("ajman", " Ajman"),
            ("quwain", "Umm Al Quwain"),
            ("khaimah", " Ras Al Khaimah"),
            ("fujairah", " Fujairah"),

        ],
        string="State of Emirates",

    )

    def action_get_apartment(self):
        """View rental order Of the Property"""
        return {
            "name": "Apartment : " + self.name,
            "view_mode": "tree,form",
            "res_model": "property.apartment",
            "type": "ir.actions.act_window",
            "domain": [("property_id", "=", self.id)],

        }
class PropertyTermsConditions(models.Model):
    _name = "property.terms"
    _description = "Property Terms Conditions"

    terms_and_conditions_english = fields.Html(string='Terms & Conditions English')
    terms_and_conditions_arabic = fields.Html(string='Terms & Conditions Arabic')
    prop_rental = fields.Many2one('property.rental')

