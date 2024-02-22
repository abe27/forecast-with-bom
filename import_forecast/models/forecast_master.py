# -*- coding: utf-8 -*-
import base64
import csv
from datetime import datetime
import io
from odoo import models, fields, api

class ForecastMonth(models.Model):
    _name = "import_forecast.forecast_month"
    _description = "รายละเอียด Forecast Month"
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Char(size=50, string="OnMonth", tracking=True)
    forecast_id = fields.Many2one('import_forecast.forecast', string='Forecast No', required=True, tracking=True, ondelete='cascade', readonly=True)
    part_id = fields.Many2one('product.product', string="Part No", tracking=True, readonly=True)
    qty = fields.Float(string="Qty", tracking=True, readonly=True)
    remain_date = fields.Datetime(string="Remain Date", tracking=True)

class ForecastBom(models.Model):
    _name = "import_forecast.forecast_bom"
    _description = "รายละเอียด Forecast Bom"
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Char(size=255, string="BOM Name", tracking=True)
    forecast_id = fields.Many2one('import_forecast.forecast', string='Forecast No', required=True, tracking=True, ondelete='cascade', readonly=True)
    forecast_detail_id = fields.Many2one('import_forecast.forecast_detail', string='Forecast Detail ID', required=True, tracking=True, ondelete='cascade', readonly=True)
    bom_id = fields.Many2one('mrp.bom', string="BOM ID", required=True, tracking=True, ondelete='cascade', readonly=True)
    bom_line_id = fields.Many2one('mrp.bom.line', string="BOM Line ID", required=True, tracking=True, ondelete='cascade', readonly=True)
    remain_qty = fields.Float(string="Qty", tracking=True, readonly=True)

