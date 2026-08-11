{
    "name": "Sale Sequence",
    "summary": "Generate Sale Order numbers using configurable sequences and delivery operation types",
    "author": "Karan Sumara",
    "description": """
    This module allows users to configure multiple Sale Order sequences.
Each sequence can be linked with a delivery operation type.
When a sequence is selected on a Sale Order, the configured operation
type is automatically applied to the Deliver From field. 
    """,
    "version": "17.0.0.0",
    "depends": ["sale_management", "sale", "operation_type_select_in_sale_order"],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_sequence.xml",
    ],
    'installable': True,
    "application": True,
    "license": "LGPL-3",
}
