class Package(object):
    def __init__(self, name, version, description, entry_point, base_image):
        self._name = name
        self._version = version
        self._description = description
        self._entry_point = entry_point
        self._base_image = base_image
        self._current_image = self._base_image

    @property
    def name(self):
        return self._name

    @property
    def version(self):
        return self._version

    @property
    def description(self):
        return self._description

    @property
    def entry_point(self):
        return self._entry_point

    @property
    def base_image(self):
        return self._base_image

    @property
    def current_image(self):
        return self._current_image

    @current_image.setter
    def current_image(self, value):
        self._current_image = value
