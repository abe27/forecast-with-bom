# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ForecastMonth(models.Model):
    _name = "import_forecast.forecast_month"
    _description = "รายละเอียด Forecast Month"
    _inherit = ['mail.thread','mail.activity.mixin']

    seq = fields.Integer(string="seq", tracking=True, readonly=True)
    name = fields.Char(size=50, string="OnMonth", tracking=True)
    forecast_id = fields.Many2one('import_forecast.forecast', string='Forecast No', required=True, tracking=True, ondelete='cascade', readonly=True)
    qty = fields.Float(string="Qty", tracking=True, readonly=True)
    remain_date = fields.Datetime(string="Remain Date", tracking=True, default=fields.datetime.now())

    @api.model
    def write(self, vals):
        return super().write(vals)

class ForecastRawMonth(models.Model):
    _name = "import_forecast.forecast_raw_month"
    _description = "รายละเอียด Forecast Raw Month"
    _inherit = ['mail.thread','mail.activity.mixin']

    seq = fields.Integer(string="seq", tracking=True, readonly=True)
    name = fields.Char(size=50, string="OnMonth", tracking=True)
    part_id = fields.Many2one('product.product', string="Part No", tracking=True, readonly=True)
    part_name = fields.Char(size=255, string="Part Name",compute="_value_part_name", store=False, tracking=True, readonly=True)
    qty = fields.Float(string="Qty", tracking=True, readonly=True)
    month_1 = fields.Float(string="N+1", tracking=True, default="0")
    month_2 = fields.Float(string="N+2", tracking=True, default="0")
    month_3 = fields.Float(string="N+3", tracking=True, default="0")
    status = fields.Boolean(string="Status", tracking=True, default=False)

    @api.depends('part_id')
    def _value_part_name(self):
        for r in self:
            r.part_name = r.part_id.name

class ForecastBom(models.Model):
    _name = "import_forecast.forecast_bom"
    _description = "รายละเอียด Forecast Bom"
    _inherit = ['mail.thread','mail.activity.mixin']

    seq = fields.Integer(string="seq", tracking=True, readonly=True)
    name = fields.Char(size=255, string="BOM Name", compute="_value_product_name",tracking=True)
    forecast_id = fields.Many2one('import_forecast.forecast', string='Forecast No', required=True, tracking=True, ondelete='cascade', readonly=True)
    forecast_detail_id = fields.Many2one('import_forecast.forecast_detail', string='Forecast Detail ID', required=True, tracking=True, ondelete='cascade', readonly=True)
    bom_id = fields.Many2one('mrp.bom', string="BOM ID", required=True, tracking=True, ondelete='cascade', readonly=True)
    bom_line_id = fields.Many2one('mrp.bom.line', string="BOM Line ID", required=True, tracking=True, ondelete='cascade', readonly=True)
    bom_qty = fields.Float(string="Bom Qty", tracking=True, readonly=True)
    require_qty = fields.Float(string="Qty", tracking=True, readonly=True)
    require_month_1_qty = fields.Float(string="Qty Month 1", tracking=True, readonly=True, default=0)
    require_month_2_qty = fields.Float(string="Qty Month 2", tracking=True, readonly=True, default=0)
    require_month_3_qty = fields.Float(string="Qty Month 3", tracking=True, readonly=True, default=0)

    @api.depends('bom_line_id')
    def _value_product_name(self):
        for r in self:
            r.name = r.bom_id.product_tmpl_id.name

