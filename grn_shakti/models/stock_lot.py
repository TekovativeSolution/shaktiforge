from odoo import api,fields,models

class StockLot(models.Model):
    _inherit = 'stock.lot'

    heat_no = fields.Char('Heat No')