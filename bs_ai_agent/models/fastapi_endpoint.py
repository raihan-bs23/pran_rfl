# -*- coding: utf-8 -*-
from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException
from pydantic import BaseModel
from odoo import api, fields, models, Command
from odoo.api import Environment
from datetime import datetime
from fastapi.responses import HTMLResponse
import ast
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
    product_list: list[str, ProductInput]

class HelpDeskTicket(BaseModel):
    title: str
    tags: str
    partner_phone: str
    partner_name: str
    priority: str
    description: str


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
    return partner


@pran_rfl_router.post("/create_sale_order")
async def create_sale_order(param: SaleOrderInput, env: Annotated[Environment, Depends(odoo_env)]):
    _logger.info(f"**********Incoming product_list**********: {param.product_list}")
    try:
        products_dict = ast.literal_eval(param.product_list[0])
        partner_id = get_or_create_partner(env, param.partner_phone)
    except Exception as e:
        _logger.info(f"**********Invalid Payload **********: {param.product_list}")
        raise HTTPException(status_code=400, detail=f"Invalid product_list format: {e}")
    order_line = []
    for key, val in products_dict.items():
        product_id = env["product.template"].sudo().search([("barcode", "=", val.get("sku_code"))])
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
    sale_order = env['sale.order'].create({
        'partner_id': partner_id.id,
        'date_order': datetime.now(),
        'order_line': order_line
    })

    if sale_order:
        _logger.info(f"********** Sale Order Created **********: {sale_order.name}")
        print('Sale Order Created', sale_order.name)
        return [{
            'sale_order_id': sale_order.name,
            'response_message': f"Sale Order: {sale_order.name} Created Successfully"
        }]


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
        })
        if ticket:
            _logger.info(f"********** Helpdesk Ticket Created **********: {ticket.name}")
            print('Helpdesk Ticket Created', ticket.name)
            return [{
                'ticket_id': ticket.name,
                'response_message': f"Helpdesk Ticket: {ticket.name} Created Successfully"
            }]
    except Exception as e:
        _logger.info(f"**********Invalid Payload **********: {param}")
        raise HTTPException(status_code=400, detail=f"Invalid product_list format: {e}")




@pran_rfl_router.get("/get_all_products_information")
async def get_all_products_information(env: Annotated[Environment, Depends(odoo_env)]):
    products = env['product.template'].search_read([], ['display_name', 'list_price', 'bengali_pronunciation', 'barcode'])

    html = "<html><head><title>IDC Product Catalog</title></head><body>"
    html += "<h1>Available Products</h1><ul>"

    for product in products:
        html += (
             f"<li>"
             f"<strong>Product Name: {product.get('display_name', '')}</strong><br/>"
             f"<strong> মূল্য :</strong> {product.get('list_price', 0.0)} টাকা<br/> "
             f"<strong> উচ্চারণ: </strong>{product.get('bengali_pronunciation', '')}<br/> "
             f"<strong> SKU CODE: </strong>{product.get('barcode')}</li><br/>"
        )

    html += "</ul></body></html>"
    return HTMLResponse(content=html)
