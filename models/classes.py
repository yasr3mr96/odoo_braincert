# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import requests
from odoo.exceptions import ValidationError



class BraincertClass(models.Model):
    _name="braincert.class"
    _rec_name='title'

    title = fields.Char(string="Title", required=True)
    timezone = fields.Many2one(comodel_name="braincert.timezone", string="Timezone", required=True)
    start_time = fields.Float(string="Start Time", required=True)
    end_time = fields.Float(string="End Time", required=True)
    date = fields.Date(string="Date", required=True,default=datetime.now().date())
    state = fields.Selection(string="Status", selection=[('draft', 'Draft'), ('schedule', 'Schedule'), ('cancel', 'Cancel') ],default='draft')
    class_id = fields.Char(string="Class Id", readonly=True,copy=False)
    start_time_am_pm = fields.Selection(string="AM/PM", selection=[('am', 'AM'), ('pm', 'PM'), ], required=True,default="am")
    end_time_am_pm = fields.Selection(string="AM/PM", selection=[('am', 'AM'), ('pm', 'PM'), ], required=True,default="am")

    # get time format from float format
    def get_time_from_float(self, float_time):
        TIME_FORMAT = "%H:%M:%S"
        str_time = str(float_time)
        str_hour = str_time.split('.')[0]
        str_minute = ("%2d" % int(str(float("0." + str_time.split('.')[1]) * 60).split('.')[0])).replace(' ', '0')
        str_ret_time = str_hour + ":" + str_minute + ":00"
        str_ret_time = datetime.strptime(str_ret_time, TIME_FORMAT).time()
        return str_ret_time

    def make_schedule(self):
        key="vyKd9ypfda8wnHmcmFV3"
        start_time=str(self.get_time_from_float(self.start_time))+" "+self.start_time_am_pm
        end_time=str(self.get_time_from_float(self.end_time))+" "+self.end_time_am_pm
        url = """https://api.braincert.com/v2/schedule?apikey={key}&title={title}&timezone={timezone}&date={date}&start_time={start_time}&end_time={end_time}&""".\
            format(key=key,title=self.title,timezone=self.timezone.code,date=str(self.date),start_time=start_time,end_time=end_time)
        res = requests.request(url=url, method="POST", headers={'Content-Type': 'application/json'}).json()
        print(">>>>>>>>>>>>>>>>>",res,)
        if res.get('status')=='ok':
            self.state='schedule'
            self.class_id=res.get('class_id')
        else:
            raise ValidationError(res.get('error'))







    def cancel_class(self):
        key = "vyKd9ypfda8wnHmcmFV3"
        url = """https://api.braincert.com/v2/cancelclass?apikey={key}&class_id={class_id}&isCancel=1""". \
            format(key=key, class_id=self.class_id)
        res = requests.request(url=url, method="POST", headers={'Content-Type': 'application/json'}).json()
        print(">>>>>>>>>>>>>>>>>", res, )
        if res.get('status') == 'ok':
            self.state='cancel'
        else:
            raise ValidationError(res.get('error'))

    @api.multi
    def unlink(self):
        for cls in self:
            key = "vyKd9ypfda8wnHmcmFV3"
            url = """https://api.braincert.com/v2/removeclass?apikey={key}&cid={class_id}""". \
                format(key=key, class_id=cls.class_id)
            res = requests.request(url=url, method="POST", headers={'Content-Type': 'application/json'}).json()
            return super(BraincertClass, self).unlink()
            # print(">>>>>>>>>>>>>>>>>", res, )
            # if res.get('status') == 'ok':
            #     return super(BraincertClass, self).unlink()
            # else:
            #     raise ValidationError(res.get('error'))




class BraincertTimezone(models.Model):
    _name="braincert.timezone"

    name = fields.Char(string="Name", required=True)
    code = fields.Char(string="Code", required=True)




class BraincertCourses(models.Model):
    _name = "braincert.courses"
    name = fields.Char(string="Name", required=True)
    class_id = fields.Many2one(comodel_name="braincert.class", string="Class Name", required=True)
    teachers = fields.One2many(comodel_name="braincert.users", inverse_name="course_id", string="Teachers")
    students = fields.One2many(comodel_name="braincert.users", inverse_name="course_id2", string="Users")


class BraincertLessons(models.Model):
    _name = "braincert.lessons"
    name = fields.Char(string="Name", required=True)
    course_id = fields.Many2one(comodel_name="braincert.courses", string="Course Name", required=True)
    class_id = fields.Many2one(comodel_name="braincert.class", string="Class Name", related='course_id.class_id',store=True)

    def send_class_launch_url(self):
        key = "vyKd9ypfda8wnHmcmFV3"
        class_id=self.class_id.class_id
        course_name=self.course_id.name
        lesson_name=self.name
        for teacher in self.course_id.teachers:
            url = """https://api.braincert.com/v2/getclasslaunch?apikey={key}&class_id={class_id}&userId={userId}&userName={userName}&isTeacher={isTeacher}&courseName={course_name}&lessonName={lesson_name}&lessonTime=60&isRecord=0""". \
                format(key=key, class_id=class_id,userId=teacher.id,userName=teacher.name,isTeacher=1 if teacher.is_teacher else 0,course_name=course_name,lesson_name=lesson_name)
            res = requests.request(url=url, method="POST", headers={'Content-Type': 'application/json'}).json()
            if res.get('status') == 'ok':
                url = res.get('launchurl')
                teacher.write({'url':url})
                return teacher.action_send_user_data()
            else:
                raise ValidationError(res.get('error'))
        for student in self.course_id.students:
            url = """https://api.braincert.com/v2/getclasslaunch?apikey={key}&class_id={class_id}&userId={userId}&userName={userName}&isTeacher={isTeacher}&courseName={course_name}&lessonName={lesson_name}&lessonTime=60&isRecord=0""". \
                format(key=key, class_id=class_id, userId=student.id, userName=student.name,
                       isTeacher=1 if student.is_teacher else 0, course_name=course_name, lesson_name=lesson_name)
            res = requests.request(url=url, method="POST", headers={'Content-Type': 'application/json'}).json()
            if res.get('status') == 'ok':
                url = res.get('launchurl')
                student.write({'url': url})
                return student.action_send_user_data()
            else:
                raise ValidationError(res.get('error'))








class BraincertUsers(models.Model):
    _name = "braincert.users"
    partner_id = fields.Many2one('res.partner', delegate=True, ondelete='cascade', auto_join=True, required=True, string="Name")  # connect by id (namepassed to view)
    is_teacher = fields.Boolean(string="Is Teacher?")
    course_id = fields.Many2one(comodel_name="braincert.courses", string="Course Name", required=True)
    url = fields.Char()
    course_id2 = fields.Many2one(comodel_name="braincert.courses", string="Course Name", required=True)

    def action_send_user_data(self):
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        try:

            template_id = \
                ir_model_data.get_object_reference('odoo_braincert', 'email_template_lesson')[1]
        except ValueError:
            template_id = False

        try:
            """
            Load the e-mail composer to show the e-mail template in
            """
            compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = {
            # Model on which you load the e-mail dialog
            'default_model': 'braincert.users',
            'default_res_id': self.ids[0],
            # Checks if we have a template and sets it if Odoo found our e-mail template
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'force_email': True
        }

        # Will show the e-mail dialog to the user in the frontend
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }





