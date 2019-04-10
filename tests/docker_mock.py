class DockerMocker(object):
    command = None
    image_name = None

    def execute(self, task):
        pass

    def is_ok(self):
        return True

    def get_status(self):
        return 0

    def set_command(self, command):
        self.command = command

    def set_image(self, name):
        self.image_name = name
