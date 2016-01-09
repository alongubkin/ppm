import json

class Package(object):
    def __init__(self, name, version, description, entry_point):
        self._name = name
        self._version = version
        self._description = description
        self._entry_point = entry_point

    @property
    def entry_point(self):
        return self._entry_point
    
    def serialize(self):
        return json.dumps({
            "name": self._name,
            "version": self._version,
            "description": self._description,
            "entry_point": self._entry_point
        }, indent=4, sort_keys=True)

    @staticmethod
    def deserialize(data):
        parsed_data = json.loads(data)
        return Package(name=parsed_data.get("name"),
                       version=parsed_data.get("version"),
                       description=parsed_data.get("description", None),
                       entry_point=parsed_data.get("entry_point", None))
