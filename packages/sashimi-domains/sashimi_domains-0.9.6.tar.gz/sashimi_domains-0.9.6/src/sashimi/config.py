from copy import deepcopy
from functools import wraps
from pathlib import Path
import re

from .ioio import ioio


STORAGE_DIR_KEY = "storage_dir"
STORAGE_DIR_DEFAULT = "auto_sashimi"
ANALYSIS_DIR_KEY = "analysis_dir"
RESOURCES_DIR_KEY = "resources_dir"
ANALYSIS_DIR_DEFAULT = "reports"
RESOURCES_DIR_DEFAULT = "resources"


def get_config_path(config_path, analysis_dir=None, storage_dir=None):
    if config_path is not None:
        config_path = Path(config_path)
    elif analysis_dir is not None:
        config_path = Path(analysis_dir)
    elif storage_dir is not None:
        config_path = Path(storage_dir, ANALYSIS_DIR_DEFAULT)
    else:
        config_path = Path(STORAGE_DIR_DEFAULT, ANALYSIS_DIR_DEFAULT)
    if config_path.is_dir():
        config_path /= "config.json"
    return config_path


def load_config(config_path):
    if config_path.is_file():
        config = load_config_file(config_path)
    else:
        config = get_base_config()
    return config


def load_config_file(config_path):
    config = ioio.load(config_path)
    config = Updates.apply_updates(config)
    return config


def get_base_config():
    return {
        Updates.version_key: Updates.get_current_version(),
        "data": [],
        "properties": {},
    }


def update(func):
    """
    Decorator for updates in Updates
    """

    @classmethod
    @wraps(func)
    def wrapper(cls, config):
        config = deepcopy(config)
        update_version = cls.get_update_version(func.__name__)
        if cls.get_config_version(config) != update_version - 1:
            raise ValueError("Innapropriate update for config")
        func(cls, config)
        cls.set_config_version(config, update_version)
        return config

    return wrapper


class Updates:
    version_key = "__version__"

    @classmethod
    def get_config_version(cls, config):
        return config.get(cls.version_key, 0)

    @classmethod
    def set_config_version(cls, config, version):
        config[cls.version_key] = version

    @classmethod
    def get_update_version(cls, name):
        rex_version = re.compile(r"^update_(\d+)$")
        if name in dir(cls) and (match := rex_version.match(name)):
            return int(match.group(1))

    @classmethod
    def get_updates(cls, config_version):
        updates = (
            (up_ver, getattr(cls, name))
            for name in dir(cls)
            if (up_ver := cls.get_update_version(name)) is not None
            and up_ver > config_version
        )
        return sorted(updates)

    @classmethod
    def apply_updates(cls, config):
        for _, update in cls.get_updates(cls.get_config_version(config)):
            config = update(config)
        return config

    @classmethod
    def get_current_version(cls):
        return cls.get_updates(-1)[-1][0]

    @update
    def update_0(cls, config):
        """We assign version 0 to the non versioned configs. Nothing to be done."""
        raise RuntimeError("This should never be reached")

    @update
    def update_1(cls, config):
        config["column_labels"] = config.pop("labels")
        config["column_labels"]["id"] = config["properties"].pop("gdocvname")
        config["column_labels"]["url"] = config["column_labels"].pop(
            "uri", config["column_labels"].pop("url", None)
        )
        config["column_labels"]["venue"] = config["column_labels"].pop("source")

    @update
    def update_2(cls, config):
        text_source = config["properties"].pop("text_source", None)
        config["properties"]["text_sources"] = [] if text_source is None else [text_source]
