import base64
import csv
from datetime import datetime
import io
from odoo import models, fields, api


class Forecast(models.Model):
    _name = "import_forecast.forecast"
    _description = "อัพโหลดข้อมูล Forecast"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    name = fields.Char(size=50, string="Customer Name", tracking=True, readonly=True)
    partner_id = fields.Many2one(
        "res.partner", string="Customer", required=True, tracking=True
    )
    on_month = fields.Date(
        string="Forecast On Month",
        required=True,
        tracking=True,
        default=lambda self: fields.datetime.now(),
    )
    revise_level = fields.Selection(
        [("0", "Revise 0"), ("1", "Revise 1"), ("2", "Revise 2"), ("3", "Revise 3")],
        string="Revise Level",
        tracking=True,
        required=True,
    )
    file_forecast_name = fields.Char(size=50, string="File Name", tracking=True)
    file_forecast = fields.Binary(string="Import Forecast", tracking=True)
    img_partner = fields.Image(
        compute="_value_partner_image", store=True, readonly=True
    )
    line_ids = fields.One2many(
        "import_forecast.forecast_detail",
        "forecast_id",
        string="Forecast Detail",
        required=True,
        tracking=True,
    )
    item = fields.Integer(string="Item", tracking=True, readonly=True, default="0")
    qty = fields.Float(string="Qty", tracking=True, readonly=True, default="0")
    is_status = fields.Selection(
        [("0", "Draff"), ("1", "In Process"), ("2", "Wait Approve"), ("3", "Purchased"), ("4", "Done")],
        string="Status",
        tracking=True,
        default="0",
    )
    _on_month = fields.Char(
        size=8, compute="_value_on_month", string="On Month", store=False, tracking=True
    )
    partner_street = fields.Char(size=255, string="street", store=True, readonly=True)
    partner_zip = fields.Char(size=255, string="zip", store=True, readonly=True)
    partner_city = fields.Char(size=255, string="city", store=True, readonly=True)
    partner_country_id = fields.Char(
        size=255, string="country_id", store=True, readonly=True
    )
    partner_phone = fields.Char(size=255, string="phone", store=True, readonly=True)
    partner_mobile = fields.Char(size=255, string="mobile", store=True, readonly=True)
    partner_email = fields.Char(size=255, string="email", store=True, readonly=True)
    partner_website = fields.Char(size=255, string="website", store=True, readonly=True)
    partner_tag = fields.Char(size=255, string="tag", store=True, readonly=True)

    @api.depends("on_month")
    def _value_on_month(self):
        for r in self:
            r._on_month = r.on_month.strftime("%m/%Y")

    @api.depends("partner_id")
    def _value_partner_image(self):
        for r in self:
            r.img_partner = r.partner_id.image_1920
            r.partner_street = r.partner_id.street
            r.partner_zip = r.partner_id.zip
            r.partner_city = r.partner_id.city
            r.partner_country_id = r.partner_id.country_id.name
            r.partner_phone = r.partner_id.phone
            r.partner_mobile = r.partner_id.mobile
            r.partner_email = r.partner_id.email
            r.partner_website = r.partner_id.website
            tags = []
            docs = []
            for tag in r.partner_id.category_id:
                # print(f"Label: {tag.name}")
                tags.append(tag.name)
                prodTemp = self.env["product.template"].search(
                    [("product_tag_ids", "=", tag.name)]
                )
                for p in prodTemp:
                    if (p.id in docs) is False:
                        docs.append(p.id)

            r.partner_tag = ",".join(tags)
            # print(f"Context: {docs}")
            # ctx = {'tags_id' : docs}
            # self.partner_id(context=ctx)
            # context = dict(self.env.context)
            # print(context)

    ### Override Create Methods #####
    @api.model_create_multi
    def create(self, obj_list):
        for obj in obj_list:
            onForecast = datetime.strptime(obj["on_month"], "%Y-%m-%d")
            onMonth = int(onForecast.strftime("%m"))
            onYear = int(onForecast.strftime("%Y"))
            ### Generate Forecast No. ###
            dte = datetime.now()
            runData = self.env["import_forecast.forecast"].search(
                [("create_date", ">=", fields.date.today())]
            )
            obj["name"] = f"FC{dte.strftime('%m%Y')}{(len(runData) + 1):03d}"

            ### Create Record
            req = super().create(obj)

            ### GET PRODUCT TAG ###
            # print(req.partner_id.category_id)
            docs = []
            for i in req.partner_id.category_id:
                prodTemp = self.env["product.template"].search(
                    [("product_tag_ids", "=", i.name)]
                )
                for p in prodTemp:
                    if (p.id in docs) is False:
                        docs.append(p.id)
            qty = 0
            seq = 1
            # print(docs)
            prod = self.env["product.product"].search(
                [("product_tmpl_id", "in", docs), ("detailed_type", "=", "product")]
            )
            for id in prod:
                ### create forecast detail
                prodDetail = self.env["import_forecast.forecast_detail"].create(
                    {
                        "seq": seq,
                        "forecast_id": req.id,
                        "part_id": id.id,
                        "qty": 0,
                        "month_1": 0,
                        "month_2": 0,
                        "month_3": 0,
                    }
                )

                ### create forecast month

                ### create forecast bom
                checkBom = self.env["mrp.bom"].search([("product_id", "=", id.id)])
                if checkBom:
                    ### get bom line ID
                    lineID = 0
                    bomLine = self.env["mrp.bom.line"].search(
                        [("bom_id", "=", checkBom.id)]
                    )
                    if bomLine:
                        for b in bomLine:
                            lineID += 1
                            print(f"{lineID}. BOM Line ID: {b.id} Qty: {b.product_qty}")
                            bomLineLevel2 = self.env["mrp.bom"].search(
                                [("product_id", "=", b.product_id.id)]
                            )
                            if bomLineLevel2:
                                for bL in bomLineLevel2:
                                    lineID += 1
                                    print(f"{lineID}. BOM Line Level2 ID: {bL.id} Qty: {bL.product_qty}")
                            else:
                                forecastBom = self.env["import_forecast.forecast_bom"].search(
                                    [
                                        ("forecast_id", "=", req.id),
                                        ("forecast_detail_id", "=", prodDetail.id),
                                        ("bom_id", "=", checkBom.id),
                                        ("bom_line_id", "=", b.id),
                                    ]
                                )
                                print(f"Forecast BOM: {len(forecastBom)}")
                                if len(forecastBom) == 0:
                                    self.env["import_forecast.forecast_bom"].create(
                                        {
                                            "forecast_id": req.id,
                                            "forecast_detail_id": prodDetail.id,
                                            "bom_id": checkBom.id,
                                            "bom_line_id": b.id,
                                            "remain_qty": b.product_qty
                                        }
                                    )
                seq += 1

            #### ITEMS,QTY and set Status #####
            isStatus = "0"
            if seq > 0:
                isStatus = "1"

            if req.file_forecast:
                isStatus = "2"

            req.write(
                {
                    "item": (seq - 1),
                    "qty": qty,
                    "is_status": isStatus,
                }
            )
            return req

        return False

    ### Override Update Methods #####
    def write(self, obj):
        res = super().write(obj)
        prodDetail = self.env["import_forecast.forecast_detail"].search(
            [("forecast_id", "=", self.id)], order="id ASC"
        )
        seq = 1
        for r in prodDetail:
            r.write(
                {
                    "seq": seq,
                }
            )
            seq += 1
        return res

    @api.onchange("file_forecast")
    def upload_forecast_detail(self):
        if self.file_forecast:
            id = int(str(self.id).replace("NewId_", ""))
            csv_data = base64.b64decode(self.file_forecast)
            data_file = io.StringIO(csv_data.decode("utf-8"))
            data_file.seek(0)
            file_reader = []
            csv_reader = csv.reader(data_file, delimiter=",")
            file_reader.extend(csv_reader)
            seq = 0
            # print(f"ID: {self.id}")
            for r in file_reader:
                if seq > 0:
                    partCode = str(r[0]).strip()
                    # partName = str(r[1]).strip()
                    # partPrice = float(str(r[2]))
                    partN = float(str(r[3]))
                    partN1 = float(str(r[4]))
                    partN2 = float(str(r[5]))
                    partN3 = float(str(r[6]))

                    prodID = self.env["product.product"].search(
                        [("default_code", "=", partCode)], limit=1
                    )
                    if len(prodID) > 0:
                        prodDetail = self.env["import_forecast.forecast_detail"].search(
                            [("forecast_id", "=", id), ("part_id", "=", prodID.id)],
                            limit=1,
                        )
                        if len(prodDetail) >= 0:
                            prodDetail.write(
                                {
                                    "qty": partN,
                                    "month_1": partN1,
                                    "month_2": partN2,
                                    "month_3": partN3,
                                    "is_match": "1",
                                }
                            )
                        # print(f"Found : {prodDetail}")

                seq += 1

            ### Update forecast Status ###
            forecast = self.env["import_forecast.forecast"].search([("id", "=", id)])
            # forecast.write({"is_status": "2"})
