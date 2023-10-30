import os
import json
from datetime import datetime
from pathlib import Path
from collections import OrderedDict

def read_json(fname):
    with fname.open('rt') as handle:
        return json.load(handle, object_hook=OrderedDict)

class ConfigParser:
    def __init__(self, config_filename, timestamp):
        self.cfg_fname = Path(config_filename)

        # load config file
        self.config = read_json(self.cfg_fname)

        # set save_dir where trained model and log will be saved.
        save_dir = Path(f'tmp/{timestamp}')
        self._save_dir = save_dir
        self._temp_dir = save_dir / 'dmvlm'

        self.save_dir.mkdir(parents=True, exist_ok=True)
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        print(save_dir)

    def __getitem__(self, name):
        return self.config[name]
    
    @property
    def save_dir(self):
        return self._save_dir
    
    @property
    def temp_dir(self):
        return self._temp_dir