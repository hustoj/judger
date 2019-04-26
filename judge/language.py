import toml

from judge.utils.log import logger


class LanguageType(object):
    language_id = 0
    source_name = ''
    compile_command = ''
    running_command = ''
    execute_name = ''
    compile_args = []
    running_args = []
    memory = 512

    def __init__(self):
        pass

    def get_running_args(self):
        return self.running_args

    def to_compile_info(self):
        return {
            "command": self.compile_command,
            "args": ' '.join(self.compile_args),
            "memory": self.memory,
        }

    def get_compile_args(self):
        return self.compile_args

    def full_compile_command(self):
        args = self.compile_args[:]
        args.insert(0, self.compile_command)
        return args


class LanguageNotExist(Exception):
    pass


language_manager = None


def load_languages():
    global language_manager
    if language_manager is None:
        languages = toml.load('languages.toml')
        language_manager = LanguageCentre(languages)


def get_language(language_id) -> LanguageType:
    load_languages()

    return language_manager.get_language(language_id)


class LanguageCentre(object):
    _languages = {}

    def __init__(self, cfg):
        self.load(cfg)

    def load(self, languages):
        for lang in languages['language']:
            language_type = LanguageType()
            language_type.language_id = lang['language_id']
            language_type.source_name = lang['source_name']
            language_type.compile_command = lang['compile_command']
            language_type.execute_name = lang['execute_name']
            language_type.compile_args = lang['compile_args']
            language_type.running_command = lang['running_command']
            language_type.running_args = lang['running_args']
            if 'memory' in lang:
                language_type.memory = lang['memory']

            self._languages[lang['language_id']] = language_type

    def get_language(self, language_id) -> LanguageType:
        if language_id in self._languages:
            return self._languages[language_id]
        logger().info('Language id not exist: {id}'.format(id=language_id))
        raise LanguageNotExist()