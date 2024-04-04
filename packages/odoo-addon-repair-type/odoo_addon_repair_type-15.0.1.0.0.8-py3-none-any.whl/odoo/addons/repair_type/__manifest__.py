# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Repair Type",
    "version": "15.0.1.0.0",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/repair",
    "summary": "Repair type",
    "category": "Repair",
    "depends": ["repair"],
    "data": [
        "views/repair.xml",
        "views/repair_type.xml",
        "security/ir.model.access.csv",
    ],
    "installable": True,
    "development_status": "Beta",
    "license": "AGPL-3",
    "application": False,
}
