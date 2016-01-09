import json

from package import Package

class PackageSerializer(object):
    def serialize(self, package):
        return json.dumps({
            "name": package.name,
            "version": package.version,
            "description": package.description,
            "entry_point": package.entry_point,
            "base_image": package.base_image
        }, indent=4, sort_keys=True)

    def deserialize(self, data):
        parsed_data = json.loads(data)
        return Package(name=parsed_data.get("name"),
                       version=parsed_data.get("version"),
                       description=parsed_data.get("description", None),
                       entry_point=parsed_data.get("entry_point", None),
                       base_image=parsed_data.get("base_image"))
