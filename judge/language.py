import logging

import toml

LOGGER = logging.getLogger(__name__)

LANG_C = 0
LANG_CPP = 1
LANG_PAS = 2
LANG_JAVA = 3


class LanguageType(object):
    language_id = 0
    name = ''
    source_name = ''
    compile_command = ''
    running_command = ''
    execute_name = ''
    compile_args = []
    running_args = []
    compile_image = ''
    running_image = ''
    enabled = False
    memory = 512

    def __init__(self):
        pass

    def __str__(self):
        return self.name

    def to_compile_info(self):
        return {
            "command": self.compile_command,
            "args": ' '.join(self.compile_args),
            "memory": self.memory,
        }

    def get_running_command(self):
        args = [self.running_command]
        args.extend(self.running_args)

        return args

    def get_compile_command(self):
        args = [self.compile_command]
        args.extend(self.compile_args)

        return args

    def is_language(self, lang_type: int) -> bool:
        return self.language_id == lang_type

    @property
    def is_enabled(self):
        return self.enabled


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
            language_type.name = lang['name']
            language_type.source_name = lang['source_name']
            language_type.compile_command = lang['compile_command']
            language_type.execute_name = lang['execute_name']
            language_type.compile_args = lang['compile_args']
            language_type.compile_image = lang['compile_image']
            language_type.running_command = lang['running_command']
            language_type.running_args = lang['running_args']
            language_type.running_image = lang['running_image']
            language_type.enabled = lang['enabled']
            if 'memory' in lang:
                language_type.memory = lang['memory']

            self._languages[str(lang['language_id'])] = language_type

    def get_language(self, language_id) -> LanguageType:
        language_id = str(language_id)
        if language_id in self._languages:
            return self._languages[language_id]
        LOGGER.info('language id not exist: {id}'.format(id=language_id))
        raise LanguageNotExist()
