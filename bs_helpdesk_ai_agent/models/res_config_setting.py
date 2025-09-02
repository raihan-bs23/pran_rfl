# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    verbex_api_base_url = fields.Char(string='API Base URL', config_parameter='bs_helpdesk_ai_agent.verbex_api_base_url')
    verbex_api_key = fields.Char(string='API Key', config_parameter='bs_helpdesk_ai_agent.verbex_api_key')