# -*- coding: utf-8 -*-
from odoo import api, fields, models



class SaleOrder(models.Model):
    _inherit = "sale.order"

    conversation = fields.Html(string='Conversation')
    call_info_fetched = fields.Boolean(string="Call info fetched")
    is_ai_created = fields.Boolean(string="Is AI Created")
    call_id = fields.Char(string="Call ID")