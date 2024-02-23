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
        forecast_id = None
        for r in self:
            # print(f"delete from forecast: {r.forecast_id}")
            forecast_id = r.forecast_id.id

        ### Delete forecast Detail
        super().unlink()

        ### Update forecast Status to draff
        forecast = self.env["import_forecast.forecast"].search([("id", "=", forecast_id)])
        forecast.write({"is_status": "0"})    
        return True
    
    def write(self, obj):
        res = super().write(obj)
        ### Get Last Update
        qty = 0
        month_1 = 0
        month_2 = 0
        month_3 = 0
        seq = 0
        forecastDetail = self.env["import_forecast.forecast_detail"].search([("forecast_id", "=", self.forecast_id.id)])
        for i in forecastDetail:
            qty += i.qty
            month_1 += i.month_1
            month_2 += i.month_2
            month_3 += i.month_3
            seq += 1

        print(f"SEQ: {seq}  Qty: {qty} N1: {month_1} N2: {month_2} N3: {month_3}") 
        #### Month N Update Forecast Month
        forecastMonth = self.env["import_forecast.forecast_month"].search([("forecast_id","=", self.forecast_id.id)])
        seq = 0
        for r in forecastMonth:
            print(f"SEQ: {seq} ID: {r.id} Month: {r.name} Qty: {qty} N1: {month_1} N2: {month_2} N3: {month_3}")
            if seq == 0:
                if qty > 0:
                    r.write({"qty": qty})

            elif seq == 1:
                r.write({"qty": month_1})

            elif seq == 2:
                r.write({"qty": month_2})

            elif seq == 3:
                r.write({"qty": month_3})

            seq += 1

        return res