#!/bin/env python3
# -*- coding: UTF-8 -*-

import logging.config
import yaml
import os
import pathlib

path = os.path.abspath(str(pathlib.Path(os.path.abspath(__file__)).parent.parent))

from importers.common.common_util import create_dir

default_log_dir = f'{path}/logs'
default_log_file = 'importer.log'
default_log_path = f'{default_log_dir}/{default_log_file}'

with open(path + '/log_conf.yaml', 'rt') as f:
    config = yaml.safe_load(f.read())
    config_log_path = config['handlers']['file']['filename']
    if default_log_file.__eq__(config_log_path):
        config['handlers']['file']['filename'] = f'{default_log_path}'
        create_dir(default_log_dir)
    else:
        config_log_dir, config_log_file = os.path.split(pathlib.Path(config_log_path))
        create_dir(config_log_dir)
    logging.config.dictConfig(config)

logger = logging.getLogger(__name__)

my_logger = logging.getLogger('my_logger')
my_logger.setLevel(logging.INFO)
