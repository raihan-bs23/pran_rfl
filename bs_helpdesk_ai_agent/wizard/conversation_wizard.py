# -*- coding: utf-8 -*-
from odoo import api, fields, models, Command


class ConversationWizard(models.TransientModel):
    _name = 'conversation.wizard'
    _description = 'Conversation Wizard'


    conversation = fields.Html(string='Conversation')