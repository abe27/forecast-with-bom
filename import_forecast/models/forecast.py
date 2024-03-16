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
    prev_revise_level = fields.Integer(
        string="Previous Revise Level", tracking=True, readonly=True, default="0"
    )
    revise_level = fields.Selection(
        [("0", "Revise 0"), ("1", "Revise 1"), ("2", "Revise 2"), ("3", "Revise 3")],
        string="Revise Level",
        tracking=True,
        required=True,
    )
    file_forecast_name = fields.Char(size=50, string="File Name", tracking=True)
    file_forecast = fields.Binary(
        string="Import Forecast", tracking=True, help="File Name(csv,xls,xlsx)"
    )
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
    month_line_ids = fields.One2many(
        "import_forecast.forecast_month",
        "forecast_id",
        string="Summary Month",
        required=True,
        tracking=True,
    )
    bom_line_ids = fields.One2many(
        "import_forecast.forecast_bom",
        "forecast_id",
        string="Bom Line",
        required=True,
        tracking=True,
    )
    item = fields.Integer(string="Item", tracking=True, readonly=True, default="0")
    qty = fields.Float(string="Qty", tracking=True, readonly=True, default="0")
    is_status = fields.Selection(
        [
            ("0", "Draff"),
            ("1", "In Process"),
            ("2", "Wait Approve"),
            ("3", "Done"),
            ("4", "Reject"),
        ],
        string="Status",
        tracking=True,
        default="0",
    )
    remark = fields.Text(string="Remark", tracking=True)
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

    def move_to_month(self, seq, on_month, part_id, qty, month_1, month_2, month_3):
        result = self.env["import_forecast.forecast_raw_month"].search(
            [("name", "=", on_month), ("part_id", "=", part_id)]
        )
        if len(result) == 0:
            result = self.env["import_forecast.forecast_raw_month"].create(
                {
                    "seq": seq,
                    "name": on_month,
                    "part_id": part_id,
                    "qty": qty,
                    "month_1": month_1,
                    "month_2": month_2,
                    "month_3": month_3,
                }
            )

        else:
            result.write(
                {
                    "qty": result.qty + qty,
                    "month_1": result.month_1 + month_1,
                    "month_2": result.month_2 + month_2,
                    "month_3": result.month_3 + month_3,
                }
            )

    def get_bom_header(self, prod):
        bomQty = 0
        bomLevel = self.env["mrp.bom"].search([("product_id", "=", prod.id)])
        if bomLevel:
            bomLine = self.env["mrp.bom.line"].search([("bom_id", "=", bomLevel.id)])
            for b in bomLine:
                bomQty = b.product_qty
            return [True, bomQty]

        return [False, 0]

    def get_bom(self, prod, req, prodDetail):
        bomLevel = self.env["mrp.bom"].search([("product_id", "=", prod.id)])
        if bomLevel:
            bomLine = self.env["mrp.bom.line"].search([("bom_id", "=", bomLevel.id)])
            if bomLine:
                for b in bomLine:
                    # print(f"PROD ID:{b.product_id.id} => {b.product_id.name}")
                    bomQty = 0
                    bomHead = self.get_bom_header(b.product_id)
                    if bomHead[0]:
                        bomQty = bomHead[1]
                        self.get_bom(b.product_id, req, prodDetail)

                    # else:
                    forecastBom = self.env["import_forecast.forecast_bom"].search(
                        [
                            ("forecast_id", "=", req.id),
                            (
                                "forecast_detail_id",
                                "=",
                                prodDetail.id,
                            ),
                            ("bom_id", "=", bomLevel.id),
                            ("bom_line_id", "=", b.id),
                        ]
                    )
                    if len(forecastBom) == 0:
                        ### Get Last Seq
                        qty = b.product_qty
                        if bomQty > 0:
                            qty = bomQty * b.product_qty

                        seq = self.env["import_forecast.forecast_bom"].search(
                            [("forecast_id", "=", req.id)]
                        )
                        self.env["import_forecast.forecast_bom"].create(
                            {
                                "seq": len(seq) + 1,
                                "forecast_id": req.id,
                                "forecast_detail_id": prodDetail.id,
                                "bom_id": bomLevel.id,
                                "bom_line_id": b.id,
                                "bom_qty": qty,
                            }
                        )

        return False

    @api.onchange("revise_level")
    def onchange_revise_level(self):
        # print(f"Revise Change :{self.revise_level} Prev.: {self.prev_revise_level}")
        if self.revise_level is False:
            return
        
        if int(self.revise_level) < self.prev_revise_level:
            res = {
                "warning": {
                    "title": str("Warning"),
                    "message": str("กรุณาระบุ Revise Level ให้ถูกต้องด้วย"),
                }
            }
            return res

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
            ### Get Last Sequence Number
            bomSeq = self.env["import_forecast.forecast_bom"].search(
                [("forecast_id", "=", req.id)]
            )

            ### GET PRODUCT TAG ###
            # print(req.partner_id.category_id)
            docs = []
            prodTemp = self.env["product.template"].search(
                [("customer_ids", "=", req.partner_id.id)]
            )
            for p in prodTemp:
                if (p.id in docs) is False:
                    docs.append(p.id)

            qty = 0
            seq = 1
            # print(docs)
            prod = self.env["product.product"].search(
                [("product_tmpl_id", "in", docs), ("detailed_type", "=", "product")],
                order="name asc",
            )

            for p in prod:
                ### create forecast detail
                prodDetail = self.env["import_forecast.forecast_detail"].create(
                    {
                        "seq": seq,
                        "forecast_id": req.id,
                        "part_id": p.id,
                        "qty": 0,
                        "month_1": 0,
                        "month_2": 0,
                        "month_3": 0,
                    }
                )

                ### create forecast bom
                self.get_bom(p, req, prodDetail)
                seq += 1

            ### create forecast month
            for r in range(0, 4):
                if onMonth == 13:
                    onMonth = 1
                    onYear += 1

                remainQty = 0
                onForecastMonth = f"{onMonth:02d}/{onYear}"
                forecastMonth = self.env["import_forecast.forecast_month"].search(
                    [("name", "=", onForecastMonth), ("forecast_id", "=", req.id)]
                )
                if len(forecastMonth) == 0:
                    self.env["import_forecast.forecast_month"].create(
                        {
                            "seq": (r + 1),
                            "name": onForecastMonth,
                            "forecast_id": req.id,
                            "qty": remainQty,
                        }
                    )
                # print(f"ID: {r} Month: {onMonth} Year: {onYear}")
                onMonth += 1

            #### ITEMS,QTY and set Status #####
            isStatus = "0"
            if seq > 0:
                isStatus = "1"

            # if req.file_forecast:
            #     isStatus = "2"

            req.write(
                {
                    "item": (seq - 1),
                    "qty": qty,
                    "prev_revise_level": 0,
                    "is_status": isStatus,
                }
            )
            return req

        return False

    ### Override Update Methods #####
    def write(self, obj):
        obj["prev_revise_level"] = int(self.revise_level)
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
            for r in file_reader:
                if seq > 1:
                    partCode = str(r[1]).strip()
                    partNo = str(r[2]).strip()
                    partName = str(r[3]).strip()
                    partTag = str(r[4]).strip()
                    partModel = str(r[5]).strip()
                    rv0 = float(str(r[6]))
                    rv1 = float(str(r[7]))
                    rv2 = float(str(r[8]))
                    rv3 = float(str(r[9]))
                    n1 = float(str(r[10]))
                    n2 = float(str(r[11]))
                    n3 = float(str(r[12]))

                    prodID = self.env["product.product"].search(
                        [("default_code", "=", partNo)], limit=1
                    )
                    if len(prodID) > 0:
                        prodDetail = self.env["import_forecast.forecast_detail"].search(
                            [("forecast_id", "=", id), ("part_id", "=", prodID.id)],
                            limit=1,
                        )
                        for r in prodDetail:
                            r.write(
                                {
                                    "qty": rv0,
                                    "month_1": n1,
                                    "month_2": n2,
                                    "month_3": n3,
                                    "is_match": "1",
                                }
                            )
                        # print(f"Found : {prodDetail}")
                    else:
                        res = {
                            "warning": {
                                "title": str("Warning"),
                                "message": str(
                                    "ข้อมูลไม่ถูกต้องกรุณาตรวจสอบข้อมูลก่อนทำการอัพโหลดด้วย"
                                ),
                            }
                        }
                        return res

                seq += 1

            # ### Update forecast Status ###
            forecast = self.env["import_forecast.forecast"].search([("id", "=", id)])
            forecast.write({"is_status": "2"})

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "type": "success",
                    "title": "ข้อความแจ้งเตือน!",
                    "message": "Testtt",
                    "sticky": False,
                    "fadeout": "slow",
                    "next": {
                        "type": "ir.actions.act_window_close",
                    },
                },
            }

    def action_reload_forecast(self):
        forecast = self.env["import_forecast.forecast"].search([("id", "=", self.id)])
        for req in forecast:
            docs = []
            prodTemp = self.env["product.template"].search(
                [("customer_ids", "=", req.partner_id.id)]
            )
            for p in prodTemp:
                if (p.id in docs) is False:
                    docs.append(p.id)

            qty = 0
            seq = 1
            # print(docs)
            prod = self.env["product.product"].search(
                [("product_tmpl_id", "in", docs), ("detailed_type", "=", "product")],
                order="name asc",
            )

            for p in prod:
                prodDetail = self.env["import_forecast.forecast_detail"].search(
                    [("part_id", "=", p.id)]
                )
                if len(prodDetail) == 0:
                    ### create forecast detail
                    prodDetail = self.env["import_forecast.forecast_detail"].create(
                        {
                            "seq": seq,
                            "forecast_id": req.id,
                            "part_id": p.id,
                            "qty": 0,
                            "month_1": 0,
                            "month_2": 0,
                            "month_3": 0,
                        }
                    )

                # ### create forecast bom
                self.get_bom(p, req, prodDetail)
                seq += 1

            seq = 0
            prodDetail = self.env["import_forecast.forecast_detail"].search(
                [("forecast_id", "=", req.id)], order="id ASC"
            )
            for r in prodDetail:
                r.write(
                    {
                        "seq": seq,
                    }
                )
                seq += 1

    def action_download_template_forecast(self):
        return {
            "type": "ir.actions.act_url",
            "url": "/import_forecast/static/src/download/template_import_forecast.csv",
            "target": "self",
        }

    def action_approve_forecast(self):
        #### Get Forecast Status = 2
        r = self.env["import_forecast.forecast"].search(
            [("id", "=", self.id), ("is_status", "=", "2")]
        )
        if len(r) < 1:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": str("Warning"),
                    "type": "warning",
                    "message": f"ไม่สามารถดำเนินการได้\nเนื่องจาก {self.name} นี้ยังไม่อยู่ในขั้นตอนรออนุมัติ",
                    "sticky": False,
                    "fadeout": "slow",
                    "next": {
                        "type": "ir.actions.act_window_close",
                    },
                },
            }

        seq = (
            len(
                self.env["import_forecast.forecast_raw_month"].search(
                    [("name", "=", self._on_month)]
                )
            )
            + 1
        )
        ### Copy Data Forecast Detail to Forecast Raw
        forecastDetail = self.env["import_forecast.forecast_detail"].search(
            [("forecast_id", "=", r.id)], order="seq ASC"
        )
        for i in forecastDetail:
            self.move_to_month(
                seq, r._on_month, i.part_id.id, i.qty, i.month_1, i.month_2, i.month_3
            )
            seq += 1

        ### Copy Data Forecast Bom to Forecast Raw
        forecastBom = self.env["import_forecast.forecast_bom"].search(
            [("forecast_id", "=", r.id)], order="seq ASC"
        )
        for i in forecastBom:
            self.move_to_month(
                seq,
                r._on_month,
                i.bom_line_id.product_id.id,
                i.require_qty,
                i.require_month_1_qty,
                i.require_month_2_qty,
                i.require_month_3_qty,
            )
            seq += 1

        ### Update Status to Done
        r.write({"is_status": "3"})

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": str("Warning"),
                "type": "success",
                "message": f"อนุมัติรายการ {self.name} เรียบร้อยแล้ว",
                "sticky": False,
                "fadeout": "slow",
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }

    def action_reject_forecast(self):
        res = self.env["import_forecast.forecast"].search(
            [("id", "=", self.id), ("is_status", "!=", "3")]
        )
        if len(res) == 0:
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": str("Warning"),
                    "type": "danger",
                    "message": f"ไม่สามารถดำเนินการ Reject {self.name} ได้เนื่องจากรายการนี้ดำเนินการเสร็จสิ้นแล้ว",
                    "sticky": False,
                    "fadeout": "slow",
                    "next": {
                        "type": "ir.actions.act_window_close",
                    },
                },
            }

        res.write({"is_status": "4"})

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": str("Warning"),
                "type": "success",
                "message": f"ดำเนินการ Reject {self.name} เรียบร้อยแล้ว",
                "sticky": False,
                "fadeout": "slow",
                "next": {
                    "type": "ir.actions.act_window_close",
                },
            },
        }
