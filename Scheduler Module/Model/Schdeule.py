# Odoo custom module: employee_scheduler
# This single python file contains multiple module files separated by headers.
# The module adds shift scheduling, shift templates, employee assignments, simple
# attendance auto-checkin/out helpers, and a small wizard. All files are Python
# only. Put each section into the module structure when installing in Odoo.

# -----------------------------
# File: __manifest__.py
# -----------------------------
{
    "name": "Employee Scheduler (Python-only example)",
    "version": "1.0.0",
    "summary": "Simple shift scheduling and attendance helpers",
    "description": "An example Odoo module written using Python-only files.\nProvides shift templates, shift instances, assignment wizard, and small attendance utilities.",
    "author": "ChatGPT example",
    "category": "Human Resources",
    "depends": ["base", "hr"],
    "data": [],  # No XML provided in this Python-only example
    "installable": True,
    "application": False,
}

# -----------------------------
# File: models/__init__.py
# -----------------------------
from . import hr_employee
from . import hr_shift
from . import hr_shift_assignment
from . import wizard_shift_assign

# -----------------------------
# File: models/hr_employee.py
# -----------------------------
from odoo import api, fields, models, exceptions
from datetime import datetime, timedelta

class Employee(models.Model):
    _inherit = 'hr.employee'

    # Add fields to link shifts
    shift_ids = fields.One2many(
        comodel_name='hr.shift.assignment',
        inverse_name='employee_id',
        string='Assigned Shifts',
    )

    primary_shift_id = fields.Many2one(
        comodel_name='hr.shift.template',
        string='Primary Shift Template',
        help='Default shift template for the employee',
    )

    def next_scheduled_shift(self, from_dt=None):
        """Return the next shift assignment for this employee after from_dt."""
        if from_dt is None:
            from_dt = fields.Datetime.now()
        Assignment = self.env['hr.shift.assignment']
        for emp in self:
            assignment = Assignment.search([
                ('employee_id', '=', emp.id),
                ('end_datetime', '>=', from_dt),
            ], order='start_datetime asc', limit=1)
            yield emp, assignment

    def action_view_shifts(self):
        # Simple helper for UI actions (no XML provided here)
        return True

# -----------------------------
# File: models/hr_shift.py
# -----------------------------
from odoo import api, fields, models
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

class ShiftTemplate(models.Model):
    _name = 'hr.shift.template'
    _description = 'Shift Template'

    name = fields.Char(required=True)
    code = fields.Char(help='Short code for the shift')
    start_time = fields.Float(required=True, default=9.0,
                               help='Start time as float hours (e.g. 9.5 = 9:30)')
    duration = fields.Float(required=True, default=8.0, help='Duration in hours')
    is_night = fields.Boolean(string='Night Shift')
    note = fields.Text()

    def compute_end_time(self):
        # returns start_time + duration normalized to 24h
        return (self.start_time + self.duration) % 24

    def _format_time(self, float_time):
        hours = int(float_time)
        minutes = int(round((float_time - hours) * 60))
        return '%02d:%02d' % (hours, minutes)

    def name_get(self):
        result = []
        for rec in self:
            display = rec.name or ''
            display += ' (%s - %s)' % (
                rec._format_time(rec.start_time),
                rec._format_time(rec.compute_end_time())
            )
            result.append((rec.id, display))
        return result

class ShiftAssignment(models.Model):
    _name = 'hr.shift.assignment'
    _description = 'Shift Assignment (instance)'
    _order = 'start_datetime desc'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, ondelete='cascade')
    template_id = fields.Many2one('hr.shift.template', string='Shift Template', required=True)
    start_datetime = fields.Datetime(required=True)
    end_datetime = fields.Datetime(required=True)
    state = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('done','Done'),('cancel','Cancelled')], default='draft')
    notes = fields.Text()

    @api.model
    def create(self, vals):
        # Basic validation: ensure end > start
        if 'start_datetime' in vals and 'end_datetime' in vals:
            if vals['end_datetime'] <= vals['start_datetime']:
                raise ValueError('End datetime must be after start datetime')
        return super(ShiftAssignment, self).create(vals)

    def write(self, vals):
        # Prevent overlapping assignments for same employee
        res = super(ShiftAssignment, self).write(vals)
        for rec in self:
            rec._no_overlaps_check()
        return res

    def _no_overlaps_check(self):
        for rec in self:
            overlapping = self.env['hr.shift.assignment'].search([
                ('employee_id', '=', rec.employee_id.id),
                ('id', '!=', rec.id),
                ('start_datetime', '<', rec.end_datetime),
                ('end_datetime', '>', rec.start_datetime),
                ('state', '!=', 'cancel')
            ], limit=1)
            if overlapping:
                raise models.ValidationError('Shift overlaps with another assignment (%s).' % overlapping.display_name)

    def action_confirm(self):
        self.state = 'confirmed'
        return True

    def action_done(self):
        self.state = 'done'
        return True

    def action_cancel(self):
        self.state = 'cancel'
        return True

# -----------------------------
# File: models/hr_shift_assignment.py
# -----------------------------
# (Additional helpers for shift assignments)
from odoo import api, fields, models
from datetime import timedelta

class ShiftAssignmentExtensions(models.Model):
    _inherit = 'hr.shift.assignment'

    def overlaps_with(self, other):
        self.ensure_one()
        return not (self.end_datetime <= other.start_datetime or self.start_datetime >= other.end_datetime)

    def duration_hours(self):
        self.ensure_one()
        start = fields.Datetime.from_string(self.start_datetime)
        end = fields.Datetime.from_string(self.end_datetime)
        delta = end - start
        return delta.total_seconds() / 3600.0

    @api.model
    def auto_generate_from_template(self, template_id, start_date, count=1):
        """Generate `count` shift assignments starting at start_date using template times."""
        template = self.env['hr.shift.template'].browse(template_id)
        if not template:
            raise ValueError('Template not found')
        assignments = []
        start_dt = fields.Datetime.from_string(start_date)
        for i in range(count):
            st = start_dt + timedelta(days=7 * i)
            # compute start/end using template hours
            st_dt = st.replace(hour=int(template.start_time), minute=int((template.start_time%1)*60), second=0)
            duration_td = timedelta(hours=template.duration)
            end_dt = st_dt + duration_td
            vals = {
                'employee_id': False,
                'template_id': template.id,
                'start_datetime': fields.Datetime.to_string(st_dt),
                'end_datetime': fields.Datetime.to_string(end_dt),
                'state': 'draft',
            }
            assignments.append(self.create(vals))
        return assignments

# -----------------------------
# File: wizard/wizard_shift_assign.py
# -----------------------------
from odoo import api, fields, models
from datetime import timedelta

class WizardAssignShift(models.TransientModel):
    _name = 'wizard.assign.shift'
    _description = 'Wizard: Assign shift to employees in bulk'

    template_id = fields.Many2one('hr.shift.template', string='Shift Template', required=True)
    employee_ids = fields.Many2many('hr.employee', string='Employees', required=True)
    start_datetime = fields.Datetime(required=True)
    end_datetime = fields.Datetime(required=True)
    copy_to_future_weeks = fields.Integer(default=0, string='Copy to future weeks')

    def action_assign(self):
        Assignment = self.env['hr.shift.assignment']
        created = []
        for emp in self.employee_ids:
            vals = {
                'employee_id': emp.id,
                'template_id': self.template_id.id,
                'start_datetime': self.start_datetime,
                'end_datetime': self.end_datetime,
                'state': 'confirmed'
            }
            assignment = Assignment.create(vals)
            created.append(assignment.id)
            # Optionally copy to following weeks
            for w in range(1, self.copy_to_future_weeks + 1):
                start = fields.Datetime.from_string(self.start_datetime) + timedelta(weeks=w)
                end = fields.Datetime.from_string(self.end_datetime) + timedelta(weeks=w)
                vals2 = vals.copy()
                vals2.update({'start_datetime': fields.Datetime.to_string(start), 'end_datetime': fields.Datetime.to_string(end)})
                Assignment.create(vals2)
        return {
            'type': 'ir.actions.act_window_close'
        }

# -----------------------------
# File: tools/attendance_utils.py
# -----------------------------
# Small helpers to integrate with hr.attendance if present
from odoo import api, models, fields

class AttendanceUtils(models.AbstractModel):
    _name = 'employee.scheduler.attendance.utils'
    _description = 'Attendance Utilities (helpers)'

    def action_auto_checkin_for_shift(self, assignment_id):
        """Create/check an attendance record at shift start. Lightweight: won't modify existing check-ins."""
        assignment = self.env['hr.shift.assignment'].browse(assignment_id)
        if not assignment:
            return False
        # Only proceed if hr_attendance module exists
        Attendance = self.env.get('hr.attendance')
        if not Attendance:
            return False
        emp = assignment.employee_id
        # check whether there's already an attendance for the given start
        domain = [
            ('employee_id', '=', emp.id),
            ('check_in', '>=', assignment.start_datetime),
            ('check_in', '<=', assignment.end_datetime),
        ]
        exists = Attendance.search(domain, limit=1)
        if exists:
            return exists
        # create a simulated check in exactly at start_datetime
        vals = {
            'employee_id': emp.id,
            'check_in': assignment.start_datetime,
        }
        return Attendance.create(vals)

    def action_auto_checkout_for_shift(self, assignment_id):
        assignment = self.env['hr.shift.assignment'].browse(assignment_id)
        if not assignment:
            return False
        Attendance = self.env.get('hr.attendance')
        if not Attendance:
            return False
        emp = assignment.employee_id
        att = Attendance.search([('employee_id', '=', emp.id), ('check_in', '>=', assignment.start_datetime)], order='check_in desc', limit=1)
        if not att:
            return False
        if att.check_out:
            return att
        att.check_out = assignment.end_datetime
        return att

# -----------------------------
# File: cron/cron_scheduler.py
# -----------------------------
from odoo import api, models, fields
from datetime import datetime, timedelta

class CronScheduler(models.TransientModel):
    _name = 'employee.scheduler.cron'
    _description = 'Cron scheduler helpers'

    @api.model
    def scheduled_check_create_attendance_for_starting_shifts(self):
        """Cron to auto create attendance records for shifts starting in the next 10 minutes.
        Designed to be called from automated action / scheduled job.
        """
        now = fields.Datetime.now()
        later = (fields.Datetime.from_string(now) + timedelta(minutes=10))
        later_str = fields.Datetime.to_string(later)
        Assignment = self.env['hr.shift.assignment']
        assignments = Assignment.search([
            ('start_datetime', '>=', now),
            ('start_datetime', '<=', later_str),
            ('state', 'confirmed')
        ])
        util = self.env['employee.scheduler.attendance.utils']
        created = 0
        for a in assignments:
            res = util.action_auto_checkin_for_shift(a.id)
            if res:
                created += 1
        return created

# -----------------------------
# File: __init__.py (module root)
# -----------------------------
# When splitting into files, ensure package imports are correct. If placed in a
# single python file for experimentation, import statements above already set.

# End of module content
