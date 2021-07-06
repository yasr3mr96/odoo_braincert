# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Report(models.AbstractModel):
    _name = 'report.odoo_braincert.get_available_attendees_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docargs = {
            'data': data,
        }
        return docargs


class Usage(models.AbstractModel):
    _name = 'report.odoo_braincert.get_class_usage_report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docargs = {
            'lines': data.get('lines'),
        }
        return docargs