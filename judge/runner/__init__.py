from .docker import DockerExecutor


def get_executor():
    return DockerExecutor()
