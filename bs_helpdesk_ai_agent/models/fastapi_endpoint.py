# -*- coding: utf-8 -*-
from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException, Query
from pydantic import BaseModel
from odoo import api, fields, models, Command
from odoo.api import Environment
from datetime import datetime
from fastapi.responses import HTMLResponse, JSONResponse
import ast, json
import logging
from odoo.addons.fastapi.dependencies import odoo_env
_logger = logging.getLogger(__name__)
PRIORITY = {
    "low": "0",
    "medium": "1",
    "high": "2",
    "urgent": "3",
}

class FastapiEndpoint(models.Model):
    _inherit = "fastapi.endpoint"

    app: str = fields.Selection(
        selection_add=[("pran_rfl", "Pran RFL Endpoint")], ondelete={"pran_rfl": "cascade"}
    )

    def _get_fastapi_routers(self):
        if self.app == "pran_rfl":
            return [pran_rfl_router]
        return super(FastapiEndpoint, self)._get_fastapi_routers()


# create a router
pran_rfl_router = APIRouter()

class ProductInput(BaseModel):
    sku_code: str
    quantity: float
    price: float

class SaleOrderInput(BaseModel):
    partner_phone: str
    call_id: str
    product_list: list[str, ProductInput]

class HelpDeskTicket(BaseModel):
    title: str
    tags: str
    partner_phone: str
    partner_name: str
    priority: str
    description: str
    call_id: str


def get_or_create_partner(env, mobile):
    """
    :param env:
    :param mobile:
    :return:
        Partner Object
    """
    partner = env["res.partner"].search(
        [
            "|",
            ("mobile", "=", mobile),
            ("phone", "=", mobile)
        ],
        limit=1
    )
    if not partner:
        partner = env["res.partner"].create({
            "mobile": mobile,
            "phone": mobile,
            "name": mobile,
            "is_company": False,
        })
        _logger.info(f"********** New Partner Created **********: {partner.name}")
    return partner


@pran_rfl_router.post("/create_sale_order")
async def create_sale_order(param: SaleOrderInput, env: Annotated[Environment, Depends(odoo_env)]):
    _logger.info(f"**********Incoming product_list**********: {param.product_list}")
    try:
        products_dict = ast.literal_eval(param.product_list[0])
        partner_id = get_or_create_partner(env, param.partner_phone)
        order_line = []
        errors = ""
        for key, val in products_dict.items():
            product_id = env["product.template"].sudo().search([("barcode", "=", val.get("sku_code"))], limit=1)
            if product_id:
                order_line.append(
                    (0, 0, {
                        'name': 'Order from Help Desk',
                        'product_id': product_id.id,
                        'price_unit': val.get('price', 1.0),
                        'product_uom_qty': val.get('quantity', 0.0),
                        'tax_id': [(6, 0, [])],
                    })
                )
            else:
                errors += f"No Products Found for SKU CODE: [{val.get('sku_code')}] !\n"
        if not errors:
            sale_order = env['sale.order'].create({
                'partner_id': partner_id.id,
                'date_order': datetime.now(),
                'order_line': order_line,
                "user_id": env.uid,
                "is_ai_created": True,
                "call_id": param.call_id
            })

            if sale_order:
                _logger.info(f"********** Sale Order Created **********: {sale_order.name}")
                print('Sale Order Created', sale_order.name)
                return [{
                    'sale_order_id': sale_order.name,
                    'response_message': f"Sale Order: {sale_order.name} Created Successfully"
                }]
    except Exception as e:
        _logger.info(f"**********Invalid Payload **********: {param.product_list}")
        raise HTTPException(status_code=400, detail=f"Invalid product_list format: {e}")


@pran_rfl_router.post("/create_support_ticket")
async def create_support_ticket(param: HelpDeskTicket, env: Annotated[Environment, Depends(odoo_env)]):
    _logger.info(f"********** Incoming Ticket Details **********: {param.title}")
    try:
        tags = env["helpdesk.tag"].sudo().search([("name", "in", [param.tags])])
        ticket = env["helpdesk.ticket"].create({
            "name": param.title,
            "tag_ids": [Command.set(tags.ids)] if tags else False,
            "partner_phone": param.partner_phone,
            "priority": PRIORITY.get(param.priority.lower()),
            "description": param.description,
            "partner_name": param.partner_name,
            "user_id": env.uid,
            "call_id": param.call_id,
            "is_ai_created": True,
        })
        if ticket:
            _logger.info(f"********** Helpdesk Ticket Created **********: {ticket.name}")
            print('Helpdesk Ticket Created', ticket.name)
            return [{
                'ticket_id': ticket.id,
                'response_message': f"Helpdesk Ticket: {ticket.reference} Created Successfully"
            }]
    except Exception as e:
        _logger.info(f"**********Invalid Payload **********: {param}")
        raise HTTPException(status_code=400, detail=f"Invalid product_list format: {e}")




@pran_rfl_router.get("/get_all_products_information")
async def get_all_products_information(
        env: Annotated[Environment, Depends(odoo_env)],
        format: str = Query("html", enum=["html", "json"])
):
    products = env['product.template'].search_read(
        [],
        ['display_name', 'list_price', 'bengali_pronunciation', 'barcode']
    )

    # --- JSON Response ---
    if format == "json":
        return JSONResponse(
            content=json.loads(json.dumps(products, indent=4, ensure_ascii=False))
        )

    # --- HTML Response (Table) ---
    html = """
        <html>
        <head>
            <title>IDC Product Catalog</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; font-size: 18px; }
                table { width: 100%; border-collapse: collapse; margin-top: 20px; }
                th, td { border: 1px solid #333; padding: 10px; text-align: left; }
                th { background-color: #f2f2f2; font-size: 18px; }
                td { font-size: 17px; }
                h1 { font-size: 24px; margin-bottom: 10px; }
            </style>
        </head>
        <body>
            <h1>Available Products</h1>
            <table>
                <tr>
                    <th>Product Name</th>
                    <th>মূল্য</th>
                    <th>উচ্চারণ</th>
                    <th>SKU CODE</th>
                </tr>
        """

    for product in products:
        html += f"""
                <tr>
                    <td>{product.get('display_name', '')}</td>
                    <td>{product.get('list_price', 0.0)} টাকা</td>
                    <td>{product.get('bengali_pronunciation', '')}</td>
                    <td>{product.get('barcode', '')}</td>
                </tr>
            """

    html += """
            </table>
        </body>
        </html>
        """

    return HTMLResponse(content=html)
