from datetime import datetime

from AptUrl.Helpers import _

from odoo import tools
from odoo import fields, models, api
from odoo.exceptions import ValidationError


class Visitor(models.Model):
    _name = 'visitor.data'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Visitor data'
    _rec_name = 'v_name'
    _order = "visitor_seq desc"

    # Track Visibility for any changes
    I_AM = fields.Selection([('visitor', 'Visitor'), ('guest', 'Guest'), ('labour', 'Labour')], required=True)
    v_name = fields.Char(string="Name", required=True, track_visibility="always")
    v_company = fields.Char(string="Company", required=True, track_visibility="always")
    v_phn = fields.Integer(string="Phone Number", required=True, track_visibility="always")
    v_email = fields.Char(string="E-mail", track_visibility="always")
    v_purpose = fields.Text(string="Purpose")
    v_gender = fields.Selection([('male', 'Male'), ('female', 'Female')], default='male', string="Gender", required=True)
    v_image = fields.Binary(string='Take Photo')
    v_address = fields.Char(string="Address")
    visitor_seq = fields.Char(string='sequence', required=True, copy=False,
                              randomly=True, index=True,
                              default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)
    image_1920 = fields.Image(related='employee_id.image_1920', string="Photo")
    work_phone = fields.Char(related='employee_id.work_phone', string="Phone")
    work_email = fields.Char(related='employee_id.work_email', string="Email")
    dept = fields.Many2one(related='employee_id.department_id', string="Department")
    job_title = fields.Char(related='employee_id.job_title', string=" Job Position")
    check_in_date = fields.Datetime(string='Check-In', default=datetime.today())
    check_out_date = fields.Datetime(string='Check-Out')
    appoint_count = fields.Integer(string='Appointment', computed='get_appoint_count')

    # @api.depends('v_name')
    # def get_appoint_count(self):
    #     for rec in self:
    #         count = self.env['visitor.data'].search_count([('v_name' '=', self.id)])
    #         rec.appoint_count = count

    # ##################Phone number Validations################################
    @api.depends('v_phn')
    def check_phn(self):
        for rec in self:
            if rec.v_phn > 11:
                raise ValidationError(_("Incorrect"))
        return True

    # Phone number Validations end

    # @api.model
    # def create(self, vals):
    #     if vals:
    #         vals['visitor_seq'] = self.env['ir.sequence'].next_by_code('visitor.data.sequence') or _('New')
    #         result = super(Visitor, self).create(vals)
    #         return result

    ################################################################################
    # # Sequence method
    @api.model
    def create(self, vals):
        if vals.get('visitor_seq', _('New')) == _('New'):
            vals['visitor_seq'] = self.env['ir.sequence'].next_by_code('visitor.data.sequence') or _('New')
        result = super(Visitor, self).create(vals)
        return result

    ###################################################################################################

    # appointment count section
    def visitor_appointment(self):
        return {
            'name': _('Appointment'),
            'domain': [('v_name', '=', self.id)],
            'view_type': 'form',
            'res_model': 'visitor.data',
            'view_id': False,
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
        }

    def action_mail(self):
        template_id = self.env.ref('visitor_management.email_template').id
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)

    # @api.model
    # def get_appoint_count(self):
    #     count = self.env['visitor.data'].search_count([('v_phn', '+', 'v_phn')])
    #     self.appoint_count = count
