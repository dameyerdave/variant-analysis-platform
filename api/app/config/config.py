from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from django.conf import settings
import time
from importlib import reload as reload_module

import yaml
from yaml.loader import SafeLoader
from os.path import join, isfile

from config.helpers import Singleton

import logging
logger = logging.getLogger(__name__)

class ConfigFileNotFoundException(Exception):
  def __init__(self, config_file):
    super().__init__({'detail': f"Config file {config_file} not found."})

class DotConfig():
  def __init__(self, cfg):
    self._cfg = cfg
  def __getattr__(self, k):
    v = self._cfg[k]
    if isinstance(v, dict):
      return DotConfig(v)
    return v

def reload_on_config_change(target):
  config = Config()
  config.register_reload_module(target)
  
  return target


class Config(FileSystemEventHandler, metaclass=Singleton):
  def __init__(self):
    print('init config')
    self.config_file = join(settings.CONFIG_DIR, f"{settings.USE_CONFIG}.yml")
    self.config = {}
    self.reload_modules = set()
    self.load()
    self.last_trigger_time = time.time()
    self.observer = Observer()
    self.__start_observer()
    

  def __start_observer(self):
    self.observer.schedule(self, self.config_file, recursive=False)
    self.observer.start()

  
  def on_modified(self, event):
    # We need to debounce the on_modified event because of an error in the library
    current_time = time.time()
    if event.src_path.find('~') == -1 and (current_time - self.last_trigger_time) > 1:
      self.last_trigger_time = current_time
      
      self.load(reload = True)

  def register_reload_module(self, module):
      print('register module', module.__name__)
      self.reload_modules.add(module)

  def as_dict(self):
    return self.config

  def get_filter(self, _type: str, _filter: str):
    """ returns the filter object of a specific type """
    if not _type in self.config:
        return None
    if not 'filters' in self.config[_type]:
        return None
    if not _filter in self.config[_type]['filters']:
        return None
    return self.config[_type]['filters'][_filter]
  
  def get_ordering(self, _type: str):
    """ returns the ordering of a specific type """
    if not _type in self.config:
        return None
    if not 'ordering' in self.config[_type]:
        return None
    return self.config[_type]['ordering']

  def get_flag_fields(self, _type: str):
    """ returns the flag fields of a specific type """
    if not _type in self.config:
        return ()
    if not 'flags' in self.config[_type]:
        return ()
    return tuple(map(lambda f: f"flag__{f}", self.config[_type]['flags'].keys()))

  def get_import_config(self, config: str):
    if not 'import' in self.config:
        return None
    if not config in self.config['import']:
        return None
    return self.config['import'][config]

  def get_import_module_config(self, config, module: str):
    if not 'import' in self.config:
        return None
    if not config in self.config['import']:
        return None
    if not module in self.config['import'][config]:
        return None
    return self.config['import'][config][module]

  @property
  def current(self):
    return DotConfig(self.config)

  def load(self, reload=False):
    if not isfile(self.config_file):
        raise ConfigFileNotFoundException(self.config_file)

    logger.info(f"{'Reloading' if reload else 'Loading'} config from {self.config_file}")
    with open(self.config_file, 'r') as cf:
        self.config = yaml.load(cf, Loader=SafeLoader)
    
    # if reload:
    #   from config import reload_on_config_change
    #   for module in reload_on_config_change:
    #       logger.info(f"Reloading module {module}")
    #       reload_module(__import__(module))