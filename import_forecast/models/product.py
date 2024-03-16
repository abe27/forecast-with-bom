from odoo import models, fields

# class ProductProduct(models.Model):
#     _inherit = 'product.product'

#     customer_ids = fields.Many2many(
#         comodel_name='res.partner',
#         string='Customers',
#         help='Select customers related to this product.',
#     )

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    customer_ids = fields.Many2many(
        comodel_name='res.partner',
        string='Customers',
        help='Select customers related to this product.',
    )