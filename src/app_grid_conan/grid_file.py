import json
import jsonschema

json_schema = {
    "type": "object",
    "tabs": [
        {
        "name": {"type": "string"},
            "apps": [
                {
                    "name": {"type": "string"},
                    "package_id": {"type": "string"},
                    "executable": {"type": "string"},
                    "icon": {"type": "string"}
                }
            ]
        }
    ]
}

class GridFile():

    def __init__(self, grid_file_path=None):
        with open(grid_file_path) as f:
           app_config = json.load(f)
        jsonschema.validate(app_config, json_schema)

