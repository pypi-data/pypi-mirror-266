import logging
import os

import click_log
import yaml

logger = logging.getLogger(__name__)
click_log.basic_config(logger)


def home_config(config_filename):
    result = None
    home = os.path.expanduser("~")
    config_file = os.path.join(home, config_filename)
    if not os.path.exists(config_file):
        build_empty_config(config_file)
    with open(config_file) as stream:
        try:
            result = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return result


def build_empty_config(config_file):
    data = {
        "username": "STEAM_USERNAME",
        "password": "STEAM_PASSWORD",
        "workshop": "/home/steam/.steam/steamapps/workshop/content/107410",
        "arma_home": "/home/steam/.steam/steamcmd/arma3",
        "arma_configs": "/home/steam/arma_configs",
    }
    with open(config_file, "w", encoding="utf8") as outfile:
        yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)


def load_local_yaml(filename):

    product = None
    with open(filename, "r") as stream:
        try:
            product = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return product
