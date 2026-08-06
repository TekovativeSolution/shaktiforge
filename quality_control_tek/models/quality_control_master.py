from odoo import api, fields, models, _

class QualityControlMaster(models.Model):
    _name = "quality.control.master"
    _description = "Quality Control Master"
    _inherit = ['mail.thread']
    _order = "name, id"

    name = fields.Char(
        'Reference', copy=False, default=lambda self: _('New'),
        required=True)
    title = fields.Char('Title')
    product_ids = fields.Many2many(
        'product.product', string='Products',
        check_company=True,
        domain="[('type', 'in', ('product', 'consu'))]",
        help="Quality Point will apply to every selected Products.")
    product_category_ids = fields.Many2many(
        'product.category', string='Product Categories',
        help="Quality Point will apply to every Products in the selected Product Categories.")

    picking_type_ids = fields.Many2many(
        'stock.picking.type', string='Operation Types', required=True, check_company=True)

    company_id = fields.Many2one(
        'res.company', string='Company', required=True, index=True,
        default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', 'Responsible')
    team_id = fields.Many2one('quality.alert.team', 'Team')
    quality_lines = fields.One2many('quality.control.line', 'quality_control_id', string='Control Points')
    measure_on = fields.Selection([
        ('operation', 'Operation'),
        ('product', 'Product'),
        ('move_line', 'Quantity')], string="Control per", default='product')
    measure_frequency_type = fields.Selection([
        ('all', 'All'),
        ('random', 'Randomly'),
        ('periodical', 'Periodically')], string="Control Frequency",
        default='all')
    testing_percentage_within_lot = fields.Float(default=100,string="Partial Test")
    measure_frequency_value = fields.Float('Percentage')
    measure_frequency_unit_value = fields.Integer('Frequency Unit Value')
    measure_frequency_unit = fields.Selection([
        ('day', 'Days'),
        ('week', 'Weeks'),
        ('month', 'Months')], default="day")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ], string="State",default='draft')
    qc_count = fields.Integer(string='Quality Point', compute='_count_quality_point')
    failure_location_ids = fields.Many2many('stock.location', string="Failure Locations",
                                            domain="[('usage', '=', 'internal')]",
                                            help="If a quality check fails, a location is chosen from this list for each failed quantity.")
    picking_type_id = fields.Many2one('stock.picking.type', string='QC Fail Operation')


    def _count_quality_point(self):
        """It will use to count quality point."""
        quality_point = self.env['quality.point'].search([('quality_master_id','=',self.id)])
        self.qc_count = len(quality_point)

    def action_see_quality_points(self):
        """Use to open quality point."""
        action = self.env["ir.actions.actions"]._for_xml_id("quality_control_tek.action_quality_control_master")
        quality_point = self.env['quality.point'].search([('quality_master_id', '=', self.id)])
        action['domain'] = [('id', 'in', quality_point.ids)]
        action['context'] = {
            'default_company_id': self.company_id.id,
            'default_quality_master_id': self.id
        }
        return action


    def create_quality_point(self):
        """Create quality points according to quality lines."""
        for line in self.quality_lines:
            vals = {
                    'title' : line.name,
                    'test_type_id':line.test_type_id.id,
                    'norm':line.norm,
                    'norm_unit':line.norm_unit,
                    'tolerance_min':line.tolerance_min,
                    'tolerance_max':line.tolerance_max,
                    'reason':line.note,
                    'note':line.instruction,
                    'failure_message':line.failure_message,
                    'product_ids':[(6,0,self.product_ids.ids)],
                    'picking_type_ids':[(6,0,self.picking_type_ids.ids)],
                    'product_category_ids':[(6,0,self.product_category_ids.ids)],
                    'user_id':self.user_id.id,
                    'team_id':self.team_id.id,
                    'measure_on':self.measure_on,
                    'measure_frequency_type':self.measure_frequency_type,
                    'testing_percentage_within_lot':self.testing_percentage_within_lot,
                    'measure_frequency_value':self.measure_frequency_value,
                    'measure_frequency_unit_value':self.measure_frequency_unit_value,
                    'measure_frequency_unit':self.measure_frequency_unit,
                    'quality_master_id':self.id,
                    'failure_location_ids': [(6, 0, self.failure_location_ids.ids)],
                    'picking_type_id' :self.picking_type_id.id
                }
            self.env['quality.point'].create(vals)
        self.state = 'done'

    def cancel_qc_master(self):
        self.state = 'cancel'

    def reset_to_draft(self):
        self.state = 'draft'




    @api.model_create_multi
    def create(self, vals_list):
        """Use to create sequence."""
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('quality.control.master') or _('New')
        return super().create(vals_list)

# class QualityCheckWizard(models.TransientModel):
#     _inherit = 'quality.check.wizard'
#
#
#     correct_measure = fields.Char(string="Measure")