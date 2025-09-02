# -*- coding: utf-8 -*-
from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    bengali_pronunciation = fields.Char(string="Bengali Pronunciation")