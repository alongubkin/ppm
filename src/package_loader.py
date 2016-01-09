import os
import json

from package_serializer import PackageSerializer

PACKAGE_FILE_NAME = "ppm-package.json"
CURRENT_IMAGE_FILE_NAME = ".ppm-image"

class PackageLoader(object):
    def load(self, path):
        serializer = PackageSerializer()

        # Load package info file
        package_file_path = os.path.join(path, PACKAGE_FILE_NAME)
        with open(package_file_path, "r") as package_file:
            package = serializer.deserialize(package_file.read())

        # Load current image file
        current_image_file_name = os.path.join(path, CURRENT_IMAGE_FILE_NAME)
        try:
            with open(current_image_file_name, "r") as current_image_file:
                package.current_image = current_image_file.read()
        except IOError:
            # The current image will be the base image
            pass

        return package

    def save(self, path, package):
        serializer = PackageSerializer()

        # Save package info file
        package_file_path = os.path.join(path, PACKAGE_FILE_NAME)
        with open(package_file_path, "w") as package_file:
            package_file.write(serializer.serialize(package))

        # Save current image file
        if package.base_image != package.current_image:
            current_image_file_name = os.path.join(path, CURRENT_IMAGE_FILE_NAME)
            with open(current_image_file_name, "w") as current_image_file:
                current_image_file.write(package.current_image)            
