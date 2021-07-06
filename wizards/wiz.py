# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime
import requests
from odoo.exceptions import ValidationError

class Available(models.TransientModel):
    _name = 'wizard.get_available_attendees'

    class_id = fields.Many2one(comodel_name="braincert.class", string="Class ID", required=True)

    def print_pdf(self):
        key="vyKd9ypfda8wnHmcmFV3"
        class_id=self.class_id.class_id
        url = """https://api.braincert.com/v2/availableAttendees?apikey={key}&class_id={class_id}""".\
            format(key=key,class_id=class_id)
        res = requests.request(url=url, method="POST", headers={'Content-Type': 'application/json'}).json()
        print(">>>>>>>>>>>>>>>>>",res,)
        data={}
        if res.get('status')=='ok':
            data = {'class_name': self.class_id.title, 'remaning_attendees': res.get('remaning_attendees')}
        else:
            raise ValidationError(res.get('error'))

        return self.env.ref('odoo_braincert.action_get_available_attendees_report').report_action(self, data=data,
                                                                                                 config=False)


class Usage(models.TransientModel):
    _name = 'wizard.get_class_usage'

    class_id = fields.Many2one(comodel_name="braincert.class", string="Class ID", required=True)
    user_id = fields.Many2one(comodel_name="braincert.users", string="User ID", required=False)

    def print_pdf(self):
        key="vyKd9ypfda8wnHmcmFV3"
        class_id=self.class_id.class_id
        user_id=self.user_id.id
        if user_id:
            url = """https://api.braincert.com/v2/getclassreport?apikey={key}&classId={class_id}&userId={user_id}""".\
                format(key=key,class_id=class_id,user_id=user_id)
        else:
            url = """https://api.braincert.com/v2/getclassreport?apikey={key}&classId={class_id}""". \
                format(key=key, class_id=class_id)

        print(">url",url)
        res = requests.request(url=url, method="POST", headers={'Content-Type': 'application/json'}).json()
        data={}
        print(">>>>>>>>>>....",type(res))
        if isinstance(res,dict):
            if res.get('error'):
                raise ValidationError(res.get('error'))
        if res:
            data = {'lines': res}

        return self.env.ref('odoo_braincert.action_get_class_usage_report').report_action(self, data=data,
                                                                                                 config=False)


