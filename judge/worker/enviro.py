import json
import logging
import os
import shlex
import shutil
from tempfile import mkdtemp

from judge.utils import is_debug, write_file

LOGGER = logging.getLogger(__name__)

RUNTIME_SYSCALLS = [
    'close',
    'futex',
    'lseek',
    'newfstatat',
    'openat',
    'rt_sigaction',
    'rt_sigprocmask',
]
JAVA_RUNTIME_SYSCALLS = [
    'clock_getres', 'clock_nanosleep', 'clone', 'clone3', 'connect', 'faccessat2',
    'fchdir', 'fcntl', 'flock', 'ftruncate', 'getcwd', 'getdents64',
    'geteuid', 'getpid', 'getrusage', 'gettid', 'getuid', 'ioctl', 'kill',
    'madvise', 'mkdir', 'munmap', 'prctl', 'pread64', 'sched_getaffinity',
    'sched_yield', 'socket', 'stat', 'statfs', 'sysinfo', 'unlink',
]


class CaseConfig:
    def __init__(self, task):
        self.task = task

    def to_json(self):
        command = self.task.language_type.running_command
        command = shlex.split(command) if isinstance(command, str) else list(command)
        args = self.task.language_type.running_args
        args = shlex.split(args) if isinstance(args, str) else list(args)
        if self.task.language == 3:
            command = command[:1] + [
                '-XX:-MaxFDLimit', '-Xmx32m', '-Xss256k',
                '-XX:ReservedCodeCacheSize=16m', '-XX:CompressedClassSpaceSize=16m',
                '-XX:MaxMetaspaceSize=32m', '-XX:CICompilerCount=2',
                '-XX:ActiveProcessorCount=2',
            ] + command[1:]
        syscalls = RUNTIME_SYSCALLS + (JAVA_RUNTIME_SYSCALLS if self.task.language == 3 else [])
        if self.task.language == 2:
            syscalls = syscalls + ['getrlimit', 'ioctl']
        return {
            'cpu': self.task.time_limit,
            'wallClock': max(2, self.task.time_limit * 2),
            'memory': self.task.memory_limit,
            'output': self.task.output_limit,
            'command': command[0],
            'args': command[1:] + args,
            'RunUID': 1536,
            'RunGID': 1536,
            'NoNewPrivs': True,
            'MaxProcs': 64 if self.task.language == 3 else 16,
            'AdditionCalls': syscalls,
            'verbose': is_debug(),
        }


class Environment:
    data_path: str
    current_dir = None
    path: str

    def __init__(self, task):
        """
        :type task: judge.task.Task
        """
        self.task = task

        self.backup()
        self.make_work_dir()
        self.prepare_compile()
        self.write_case_info()

    def make_work_dir(self):
        self.path = mkdtemp(prefix='judge_')
        if os.geteuid() == 0:
            os.chown(self.path, 1536, 1536)
        os.chdir(self.path)
        LOGGER.info('Task %s dir is %s', self.task.task_id, self.path)

    def place_input(self, data):
        # type: (str) -> None
        write_file('user.in', data)

    def write_case_info(self):
        cc = CaseConfig(self.task)
        with open('case.json', "w") as f:
            content = json.dumps(cc.to_json())
            f.write(content)

    def prepare_compile(self):
        write_file(self.task.language_type.source_name, self.task.code)
        config = self.task.language_type.to_compile_info()
        config.update(RunUID=1536, RunGID=1536, NoNewPrivs=True, memory=512)
        if self.task.language == 3:
            config['args'] = (
                '-J-XX:-UseCompressedClassPointers '
                '-J-Xmx128m -J-XX:ReservedCodeCacheSize=16m '
                '-J-XX:MaxMetaspaceSize=64m Main.java'
            )
            config['memory'] = 1024
        content = json.dumps(config)
        write_file('compile.json', content)

    def clear_user_data(self):
        LOGGER.info("Clear working dir for next case")
        files = ['user.in', 'user.out', 'user.err']
        for file in files:
            if os.path.exists(file):
                os.unlink(file)

    def clean(self):
        if self.path and not is_debug():
            LOGGER.info("Clean working dir %s", self.path)
            if os.path.exists(self.path):
                shutil.rmtree(self.path)
            else:
                LOGGER.error("working path[%s] is not exist!", self.path)
        self.restore()

    def restore(self):
        os.chdir(self.current_dir)

    def backup(self):
        self.current_dir = os.getcwd()
