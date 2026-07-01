

{
    "name": "Auto Expired Database Tesk",
    "version": "17.0.0.0",
    "category": "Web",
    "author": "Mansi Vaghela ",

    "website": "http://www.teknovativesolution.com/",
    "license": "AGPL-3",
    "depends": ["web"],
    "data": [
        "data/ribbon_data.xml",
    ],
    "auto_install": False,
    "installable": True,
    "assets": {
        "web.assets_backend": [
            "auto_expired_database_tek/static/src/components/environment_ribbon/*",
        ],
    },
}
