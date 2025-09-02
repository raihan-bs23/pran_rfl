# -*- coding: utf-8 -*-
import logging
from odoo import api, fields, models, Command
from datetime import datetime
from markupsafe import escape
import requests
_logger = logging.getLogger(__name__)


class BsMixin(models.AbstractModel):
    _name = "bs.mixin"
    
    
    def fetch_call_information(self, call_id):
        if not call_id:
            objects = self.env["sale.order"].search([('is_ai_created', '=', True), ('call_info_fetched', '=', False)])
        else:
            objects = self

        verbex_api_base_url = self.env['ir.config_parameter'].get_param('bs_helpdesk_ai_agent.verbex_api_base_url', False)
        verbex_api_key = self.env['ir.config_parameter'].get_param('bs_helpdesk_ai_agent.verbex_api_key', False)

        for obj in objects:
            _logger.info(f"********** Fetching Call Info for : {obj.name} **********")
            url = f"{verbex_api_base_url}/v1/calls/{obj.call_id}"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {verbex_api_key}',
            }
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                result = response.json()
                if result:
                    transcript_list = result.get('messages')
                    formated_html_response = self.format_transcript_to_html(transcript_list)
                    obj.write({
                        'conversation': formated_html_response,
                    })

            except requests.exceptions.HTTPError as e:
                _logger.error("HTTPError: %s", e.response.reason)
            except Exception as e:
                _logger.error("Error while Calling: %s", str(e))
        _logger.info(f"********** Call Information Fetched **********")


    def format_transcript_to_html(self, transcript_list):
        html_lines = []
        time_color = "#888"

        for entry in transcript_list:
            role = entry.get("role", "").capitalize()
            content = entry.get("content", "")

            if ") " in content:
                time_part, text_part = content.split(") ", 1)
                time_part += ")"
            else:
                time_part = ""
                text_part = content
            time_html = f'<span style="color:{time_color}; font-size: 12px;">{escape(time_part)}</span>'
            if role == 'Agent':
                speaker_html = '<b style="color: navy;">Agent:</b>'
            elif role == 'User':
                speaker_html = '<b style="color: green;">User:</b>'
            else:
                speaker_html = f'<b>{escape(role)}:</b>'

            text_html = escape(text_part)
            html_line = f'<p>{speaker_html} {time_html}<br>{text_html}</p>'
            html_lines.append(html_line)

        return "".join(html_lines)