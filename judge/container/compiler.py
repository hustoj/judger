import json
import logging
from pathlib import Path

from docker.errors import DockerException

from .executor import DockerExecutor

LOGGER = logging.getLogger(__name__)
MAX_COMPILE_TIME = 3


class CompileException(Exception):
    pass


class Alarm(Exception):
    pass


def alarm_handler(signum, frame):
    raise Alarm


class Compiler:
    @staticmethod
    def compile(env):
        """
        :param judge.worker.enviro.Environment env:
        :return:
        """
        try:
            compiler = DockerExecutor()
            compiler.set_image(env.task.language_type.compile_image)
            compiler.set_command("compiler")
            compiler.execute(env.path)
            LOGGER.info(
                'Compiler: Task %d finished, result: %s',
                env.task.task_id,
                compiler.get_status(),
            )
            LOGGER.debug('Compiler stdout: %s', compiler.get_stdout())
            try:
                success = json.loads(compiler.get_stdout()).get('success') is True
            except (ValueError, AttributeError) as exc:
                raise RuntimeError('Invalid compiler response') from exc
            if not compiler.is_ok() or not success:
                details = []
                for name in ['compile.err', 'compile.out']:
                    path = Path(env.path) / name
                    if path.is_file():
                        with path.open(errors='replace') as output:
                            details.append(output.read(65536))
                message = '\n'.join(details).strip()
                raise CompileException(message or compiler.get_stderr().decode(errors='replace'))
        except DockerException as err:
            LOGGER.error('Docker Exception: %s', err)
            raise RuntimeError(f'Docker execute failed {err}') from err
