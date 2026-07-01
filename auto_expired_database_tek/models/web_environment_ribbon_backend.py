from odoo import api, models
from datetime import datetime,timedelta

class WebEnvironmentRibbonBackend(models.AbstractModel):
    _name = "web.environment.ribbon.backend"
    _description = "Web Environment Ribbon Backend"

    @api.model
    def _prepare_ribbon_format_vals(self):
        data = eval(self.env["ir.config_parameter"].sudo().get_param("database.expired.data"))
        return {"db_date": data.get('date')}
        #return {"db_name": self.env.cr.dbname}

    @api.model
    def _prepare_ribbon_name(self):
        name_tmpl = self.env["ir.config_parameter"].sudo().get_param("ribbon.name")
        vals = self._prepare_ribbon_format_vals()
        return name_tmpl and name_tmpl.format(**vals) or name_tmpl

    @api.model
    def get_environment_ribbon(self):
        """
        This method returns the ribbon data from ir config parameters
        :return: dictionary
        """
        ir_config_model = self.env["ir.config_parameter"]
        expired_data = eval(ir_config_model.sudo().get_param('database.expired.data'))
        if expired_data and expired_data.get('date'):
            current_date = datetime.today().date()
            expired_date = datetime.strptime(expired_data.get('date'), "%d-%m-%Y").date() - timedelta(
                expired_data.get('days'))
            if current_date >= expired_date:
                name = self._prepare_ribbon_name()

                return {
                    "name": name,
                    "color": ir_config_model.sudo().get_param("ribbon.color"),
                    "background_color": ir_config_model.sudo().get_param(
                        "ribbon.background.color"
                    ),
                    "plan_expired": 'True',
                }
            else:
                return {
                    "plan_expired": 'False',
                }
        else:
            return {
                "plan_expired": 'False',
            }
