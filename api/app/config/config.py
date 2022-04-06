from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from django.conf import settings
import time

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

class Config(FileSystemEventHandler, metaclass=Singleton):
  def __init__(self):
    print('init config')
    self.config_file = join(settings.CONFIG_DIR, f"{settings.USE_CONFIG}.yml")
    self.config = {}
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
      
      self.load()


  def as_dict(self):
    return self.config
  
  @property
  def current(self):
    return DotConfig(self.config)

  def load(self):
    if not isfile(self.config_file):
        raise ConfigFileNotFoundException(self.config_file)

    logger.info(f"Reloading config from {self.config_file}")
    with open(self.config_file, 'r') as cf:
        self.config = yaml.load(cf, Loader=SafeLoader)