from odoo import models
from odoo.http import request
from datetime import  datetime

class IrHttp(models.AbstractModel):

    _inherit = "ir.http"


    ### use to expired session when of user.
    @classmethod
    def _authenticate(cls, endpoint):
        res = super(IrHttp, cls)._authenticate(endpoint=endpoint)
        if (
            request
            and request.session
            and request.session.uid
            and not request.env["res.users"].browse(request.session.uid)._is_public() and not request.session.uid == 2
        ):

            ir_config_model = request.env["ir.config_parameter"].sudo().get_param('database.expired.data')
            expired_data = eval(ir_config_model)
            if expired_data and expired_data.get('date'):
                current_date = datetime.today().date()
                expired_date = datetime.strptime(expired_data.get('date'), "%d-%m-%Y").date()
                if current_date >= expired_date:
                    request.session.logout(keep_db=True)
        return res
