# -*- coding: utf-8 -*-
from odoo import api, fields, models



class SaleOrder(models.Model):
    _name = "sale.order"
    _inherit = ["bs.mixin", "sale.order"]

    conversation = fields.Html(string='Conversation')
    call_id = fields.Char(string="Call ID")
    call_info_fetched = fields.Boolean(string="Call info fetched")
    is_ai_created = fields.Boolean(string="Is AI Created")


    def fetch_call_info(self):
        if self.call_id:
            self.fetch_call_information(self.call_id)


    def view_conversation(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Agent and Customer Conversation',
            'res_model': 'conversation.wizard',
            'target': 'new',
            'view_mode': 'form',
            'context': {
                'create': False,
                'default_conversation': self.conversation,
            }
        }