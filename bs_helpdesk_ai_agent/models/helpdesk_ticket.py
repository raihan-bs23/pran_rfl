# -*- coding: utf-8 -*-
from odoo import api, fields, models



class HelpdeskTicket(models.Model):
    _name = "helpdesk.ticket"
    _inherit = ["bs.mixin","helpdesk.ticket"]
    _order = "reference desc"

    reference = fields.Char(string="Reference", default="New")
    call_id = fields.Char(string="Call ID")
    conversation = fields.Html(string='Conversation')
    call_info_fetched = fields.Boolean(string="Call info fetched")
    is_ai_created = fields.Boolean(string="Is AI Created")



    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('reference') or vals['reference'] == 'New':
                vals['reference'] = self.env['ir.sequence'].next_by_code('helpdesk.ticket.ai') or 'New'
        return super().create(vals_list)


    def fetch_call_info(self):
        if self.call_id:
            self.fetch_call_information()


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

