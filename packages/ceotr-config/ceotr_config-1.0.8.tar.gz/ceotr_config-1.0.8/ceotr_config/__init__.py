from .config_handler import ConfigHandler


class BaseConfigAgent:
    def __init__(self, default_template):
        self._debug = True
        self._config_yml = None
        self.default_template = default_template

    @property
    def debug(self):
        if hasattr(self, 'general_info'):
            return self.general_info['ENVIRONMENT'] != 'prod'
        return self._debug

    def load(self, setting_path=None, setting_template=None):
        self._config_yml = ConfigHandler(setting_path, setting_template, self.default_template).build_or_load()
        self._load(self._config_yml)

    def _load(self, config_yml):
        for item, value in config_yml.items():
            setattr(self, item, value)

    def dict(self):
        return self._config_yml


class DjangoConfigAgent(BaseConfigAgent):
    def __init__(self):
        super().__init__('default_django_setting.yml-tpl')


class ConfigAgent(BaseConfigAgent):
    def __init__(self):
        super().__init__('default_setting.yml-tpl')


config_agent = ConfigAgent()
