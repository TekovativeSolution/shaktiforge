{
    "name": "GRN Shakti",
    "summary": "GRN Shakti",
    "author": "Karan Sumara",
    "description": """
Goods Receipt & QC Management
===========================================

Purchase Order - Line Wise Separate Receipt
adds GRN fields(Mill TC No., Heat No., Mill TS, No of Received, Lab Chemical Test TC No.,
Verified By fields) on the Receipt. Heat No auto-propagates from Receipt
to its Moves, Move Lines, and generated Lots.
Added prefix, next number and sequence size in material grade master,
Dynamically generates Lot/Serial numbers from a product's Material Grade based on prefix, sequence size and next number field. 
stock move line create based on Heat No. and number of lots. 
Includes a QC Status workflow (Pending -> Transfer to QC -> Done) with a dedicated user group only show Transfer-to-QC receipts and not show any other receipts , deliveries. 
Validate Receipt qc status field value change to qc done.

""",
    "version": "17.0.0.0",
    "depends": ["purchase", "purchase_stock", "stock"],
    "data": [
        "security/security_access_demo.xml",
        "views/stock_picking_view.xml",
        "views/stock_lot_view.xml",
        "views/stock_move_view.xml",
        "views/stock_move_line_view.xml",
        "views/product_category_view.xml",
    ],
    'installable': True,
    "application": True,
    "license": "LGPL-3",
}
