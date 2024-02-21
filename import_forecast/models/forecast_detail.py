import base64
import csv
from datetime import datetime
import io
from odoo import models, fields, api

class ForecastDetail(models.Model):
    _name = "import_forecast.forecast_detail"
    _description = "รายละเอียด Forecast Detail"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    seq = fields.Integer(string="Seq", default="1")
    name = fields.Char(size=50, string="Forecast No.",compute="_value_forecast_name", tracking=True, readonly=True)
    forecast_id = fields.Many2one('import_forecast.forecast', string='Forecast No', required=True, tracking=True, ondelete='cascade', readonly=True)
    part_id = fields.Many2one('product.product', string="Part No", tracking=True, readonly=True)
    part_name = fields.Char(size=255, string="Part Name",compute="_value_part_name", tracking=True, readonly=True)
    qty = fields.Float(string="N", required=True, tracking=True)
    month_1 = fields.Float(string="N+1", tracking=True, default="0")
    month_2 = fields.Float(string="N+2", tracking=True, default="0")
    month_3 = fields.Float(string="N+3", tracking=True, default="0")
    is_match = fields.Selection([("0", "Not Match"), ("1", "Matched")],string="Status", tracking=True, default="0")

    @api.depends('forecast_id')
    def _value_forecast_name(self):
        for r in self:
            r.name = r.forecast_id.name

    @api.depends('part_id')
    def _value_part_name(self):
        for r in self:
            r.part_name = r.part_id.name
            
    @api.model
    def unlink(self):
        # for r in self:
        #     print(f"delete from forecast: {r.id}")
            
        return super().unlink()