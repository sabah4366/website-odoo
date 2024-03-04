from odoo import api, fields, models, _


class Property_Apartment(models.Model):
    """A class for the model property to represent the property"""

    _name = "property.apartment"
    _description = "apartment"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    image = fields.Binary(string='Image', required=True,
                          help='The properties image')
    property_id = fields.Many2one('property.property',string='Property')


    name = fields.Char(string="Name")
    property_id = fields.Many2one("property.property",string="Property")
    type_residence = fields.Char(
        string="Type of Residence", help="The type of the residence"
    )

    bedroom = fields.Integer(
        string="Bedrooms", help="Number of bedrooms in the property"
    )
    bathroom = fields.Integer(
        string="Bathrooms", help="Number of bathrooms in the property"
    )
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
    currency_id = fields.Many2one(
        "res.currency", string="Currency", related="company_id.currency_id"
    )
    rent_month = fields.Monetary(
        string="Annual Rent", help="Rent price per month", tracking=True
    )
    company_id = fields.Many2one(
        "res.company",
        string="Property Management Company",
        default=lambda self: self.env.company,
    )
    area_measurement_ids = fields.One2many(
        "property.area.measure", "apartment_id", string="Area Measurement"
    )
    total_sq_feet = fields.Float(
        string="Total Square Feet",
        compute="_compute_total_sq_feet",
        help="The total area square feet of the " "property",
    )
    owner_id = fields.Many2one('property.owner', string='Land Lord',

                               help='The owner / land lord of the property')
    plot_number = fields.Integer(string="Plot No")
    makani_number = fields.Integer(string="Makani No")
    property_number = fields.Integer(string="Property No")
    building_name = fields.Char(string="Building Name")
    property_area = fields.Float(string="Property Area (s.m)")
    type_property = fields.Char(string="Property Type")
    location = fields.Char(string="Location")
    permission_no = fields.Integer(string="Permises No (DEWA)")

    def _compute_total_sq_feet(self):
        """Calculates the total square feet of the property"""
        for rec in self:
            rec.total_sq_feet = sum(rec.mapped("area_measurement_ids").mapped("area"))

    def action_property_rental_view(self):
            """View rental order Of the Property"""
            return {
                "name": "Property Rental",
                "view_mode": "tree,form",
                "res_model": "property.rental",
                "type": "ir.actions.act_window",
                "domain": [("apartment_id", "=", self.id)],
            }

    def action_available(self):
        """Set the state to available"""
        self.state = "available"

class ApartmentAreaMeasure(models.Model):
    """A class for the model property.area.measure to represent
    the area of each sections"""
    _inherit = 'property.area.measure'
    _description = 'Apartment Area Measurement'

    apartment_id = fields.Many2one('property.apartment', string='Apartment',
                                  help='The corresponding Apartment')


