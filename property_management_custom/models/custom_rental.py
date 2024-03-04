from odoo import api, fields, models, _

from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta




class ApartmentRental(models.Model):
    """A class for the model property rental to represent
    the rental order of a property"""
    _inherit = 'property.rental'

    terms_conditions_ids = fields.One2many('property.terms','prop_rental',string='Terms and Conditions')

    @api.model
    def default_get(self, fields):
        defaults = super(ApartmentRental, self).default_get(fields)

        terms = self.env['property.terms'].search([])
        term_ids = [(4, term.id) for term in terms]

        defaults['terms_conditions_ids'] = term_ids

        return defaults

    apartment_id = fields.Many2one('property.apartment', string="Apartment",
                                   domain="[('state','=','available'),('property_id','=',property_id)]")
    rent_price = fields.Monetary(string='Annual Price',

                                 help='The Rental price per month of the '
                                      'property')
    owner_id = fields.Many2one('property.owner', string='Land Lord',
                               related='property_id.landlord_id', store=True,
                               help='The owner / land lord of the property')

    note = fields.Html(
        string="Terms and conditions",

         readonly=False)
    renter_id = fields.Many2one('res.partner', string='Tenant', required=True,
                                help='The customer who is renting the property')

    related_booking_id = fields.Many2one("apartment.booking", string = "Booking ID")

    invoice_policy = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),

        ],
        string="Invoice Policy",

    )
    start_date = fields.Date(string='Contract Period', required=True,
                             help='The starting date of the rent')
    end_date = fields.Date(string='To', required=True,
                           help='The Ending date of the rent')
    contract_value = fields.Char(string="Contract Value")
    security_amount =fields.Monetary(string='Security Deposit Amount'

                                )
    payment_type = fields.Selection(
        [
            ("bank", "Bank"),
            ("cash", "Cash"),

        ],
        string="Mode of Payment",

    )


    @api.onchange('property_id','apartment_id')
    def change_property_type(self):
        if self.apartment_id:
            if self.apartment_id.rent_month:
                self.rent_price =  self.apartment_id.rent_month
            if self.apartment_id.owner_id:
                self.owner_id = self.apartment_id.owner_id
        else:
            if self.property_id.rent_month:
                self.rent_price =  self.property_id.rent_month
            if self.property_id.landlord_id:
                self.owner_id = self.property_id.landlord_id

    # rent_price = fields.Monetary(string='Annual Rent',
    #                              related='property_id.rent_month',
    #                              help='The Rental price per month of the '
    #                                   'property')

    # def action_create_contract(self):
    #     """Creates an invoice for contract. Checks if the customer
    #     is blacklisted."""
    #     if self.renter_id.blacklisted:
    #         raise ValidationError(
    #             _('The Customer %r is Blacklisted.', self.renter_id.name))
    #     self.env['account.move'].create({
    #         'move_type': 'out_invoice',
    #         'property_rental_id': self.id,
    #         'partner_id': self.renter_id.id,
    #         'invoice_line_ids': [fields.Command.create({
    #             'name': self.property_id.name,
    #             'price_unit': self.rent_price,
    #             'currency_id': self.env.user.company_id.currency_id.id,
    #         })]
    #     })
    #     self.invoice_date = fields.Date.today()
    #     self.apartment_id.state = 'rented'
    #     self.state = 'in_contract'
    from datetime import datetime, timedelta

    from datetime import datetime, timedelta

    def action_create_contract(self):
        """Creates invoices for each month of the contract period. Checks if the customer
        is blacklisted."""
        if self.renter_id.blacklisted:
            raise ValidationError(
                _('The Customer %r is Blacklisted.', self.renter_id.name))

        start_date = self.start_date
        end_date = self.end_date
        if self.invoice_policy == "monthly":
            while start_date <= end_date:
                # Calculate the end date of the current month
                next_month = start_date.replace(day=28) + timedelta(days=4)
                end_of_month = next_month - timedelta(days=next_month.day)
                end_of_month = min(end_of_month, end_date)
                # Create invoice for the current month
                invoice = self.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'property_rental_id': self.id,
                    'partner_id':self.renter_id.id,
                    'invoice_line_ids': [fields.Command.create({
                        'name': self.property_id.name,
                        'price_unit': self.rent_price,
                        'currency_id': self.env.user.company_id.currency_id.id,
                    })],
                    'invoice_date': start_date,
                    'invoice_date_due':start_date,
                    # 'invoice_payment_term_id': self.env.ref('your_module_name.your_payment_term_id').id,
                    # Specify your payment term ID here
                    'invoice_origin': 'Contract Invoice',  # Or any other origin you prefer
                })
                invoice.action_post()

                # Set due date to the start of next month
                # due_date = start_date.replace(day=1) + timedelta(days=32)  # Ensure to move to the next month accurately
                # due_date = due_date.replace(day=1)
                # invoice.invoice_date_due = due_date

                # Move to the next month
                start_date = end_of_month + timedelta(days=1)
        elif self.invoice_policy == "quarterly":

            # Calculate the number of quarters in the contract period
            contract_duration_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month + 1
            print(contract_duration_months,'contract_duration_months')
            num_quarters = contract_duration_months // 4
            print(num_quarters,'num_quarters')

            for i in range(num_quarters):
                # Calculate start and end dates for the current quarter
                quarter_start_date = start_date + relativedelta(months=4 * i)
                quarter_end_date = quarter_start_date + relativedelta(months=4) - timedelta(days=1)
                quarter_end_date = min(quarter_end_date, end_date)

                # Create invoice for the current quarter
                invoice = self.env['account.move'].create({
                    'move_type': 'out_invoice',
                    'property_rental_id': self.id,
                    'partner_id': self.renter_id.id,
                    'invoice_line_ids': [fields.Command.create({
                        'name': self.property_id.name,
                        'price_unit': self.rent_price,
                        'currency_id': self.env.user.company_id.currency_id.id,
                    })],
                    'invoice_date': quarter_start_date,
                    'invoice_date_due': quarter_end_date,
                    'invoice_origin': 'Contract Invoice',
                })
                invoice.action_post()

        self.related_booking_id.state = 'booked'
        self.apartment_id.state = 'rented'
        self.state = 'in_contract'

    def action_view_pdc(self):
        return {
            "name": "PDC",
            "view_mode": "tree,form",
            "res_model": "pdc.wizard",
            "type": "ir.actions.act_window",
        }
    def print_rental_contract(self):
        return self.env.ref('property_management_custom.report_contract_rental').report_action(self, data={})