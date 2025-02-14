# A global config parser supporting YAML, CLI arguments.
__all__ = [
    "Configuration",
    "TCCErrorCallback",
]

import glob
import os
import warnings

from omegaconf import OmegaConf, DictConfig, ListConfig
from tenacity import retry, stop_after_attempt
from typing import Any, List, Optional, Union, Callable



_DEFAULT_CONFIG_FILE_NAME = "config.yaml"
_PROJECT_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)))
_DEFAULT_CONFIG_FILE = os.path.join(_PROJECT_ROOT, _DEFAULT_CONFIG_FILE_NAME)
# Enable reading configurations from CLI arguments
# See: https://omegaconf.readthedocs.io/en/latest/usage.html#from-command-line-arguments
_DISABLE_CLI_CONFIG = os.environ.get(
    "CONFIG_DISABLE_CLI", "false").lower() in ("true", "1")

class ConfigError(Exception):
    ...



def _read_yaml_config(yaml_path):
    if not os.path.exists(yaml_path):
        raise ConfigError(f"Can not find config YAML file: {yaml_path}")
    try:
        config = OmegaConf.load(yaml_path)
    except Exception:
        raise ConfigError(
            f"Error occurs while loading config YAML file: {yaml_path}")
    return config


def _read_cli_config() -> DictConfig:
    try:
        config = OmegaConf.from_cli()
    except Exception:
        raise ConfigError("Error occurs while parsing CLI parameters")
    return config


class Configuration:
    PROJ_ROOT_DIR = _PROJECT_ROOT

    _config: DictConfig = None

    def __init__(self) -> None:
        if self._config is None:
            raise ConfigError(
                "Configuration is not properly initialized, call 'Configuration.init_config()' first.")

    def get(self, key: str, default: Any = None, type=None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Specify the key of the required value. Support retrieve recursively
            default: Default return value if retrieving value fails
            type: Type for returned value
        Returns:
            Configuration value indexed by the provided key
        Usage:
            Get value by key and returns None if value is not found:\n
            > config.get("key", None)

            Get value recursively:\n
            > config.get("key1.key2.key3")

            Get value from a list:\n
            > config.get("key1.0")

            Get a int value explicitly:\n
            > config.get("key", type=int)
        """
        if not key:
            return default

        key_list = key.split(".")
        matched_key_list = []
        conf = self._config
        for it, k in enumerate(key_list):
            if isinstance(conf, DictConfig):
                conf = conf.get(k, default)
            elif isinstance(conf, ListConfig):
                try:
                    idx = int(k)
                except Exception:
                    # to access a list, a str number should provided
                    return default
                conf = conf.get(idx, default)
            else:
                if it != len(key_list) + 1:
                    # a non-DictConfig or non-ListConfig node should be a leaf config node
                    return default
            matched_key_list.append(k)

        # all matched key should be equal with given key
        if ".".join(matched_key_list) != key:
            return default

        if type is not None and conf is not None:
            # Not handle type conversion exception
            return type(conf)
        else:
            return conf

    
    def __getitem__(self, key: str) -> Any:
        """Get configuration value by key
        Args:
            key: Specify the key of the required value. Support retrieve recursively
        Returns:
            Configuration value indexed by the provided key
        Raises:
            KeyError if no value matches the provided key
            Other Exceptions if errors occur while retrievaling values
        Usage:
            Get value by key
            > config["key"]
            Get value by key recursively
            > config["key1.key2.key3"]
        """
        try:
            conf = self.get(key, None)
        except Exception as e:
            raise e
        if conf is None:
            raise KeyError(f"{key}")
        return conf

    def get_data_dir(self, auto_create=True):
        """
        Get the data directory for this party: '${core.path.data_dir}'
        """
        default_data_dir = os.path.join(self.PROJ_ROOT_DIR, "data")
        data_dir = self.get("path.data", default_data_dir)  # type:str
        if not data_dir.startswith("/"):
            data_dir = os.path.join(self.PROJ_ROOT_DIR, data_dir)

        if auto_create and not os.path.exists(data_dir):
            os.makedirs(data_dir)
        return data_dir

    @classmethod
    def init_config(cls, yaml_file: Optional[str] = _DEFAULT_CONFIG_FILE) -> None:
        """Initialize configurations for the Agent.

        Args:
            yaml_file: Specify the configuration YAML files to be read (optional).
                       Otherwise, 'configs/config.yaml' will be read

        Raises:
            JscmConfigError if parse configuration failed
        """
        # The lowest priority
        cls._config = _read_yaml_config(yaml_file)

        cli_config = None
        if not _DISABLE_CLI_CONFIG:
            cli_config = _read_cli_config()

        custom_configs = []
        if cli_config and cli_config.get("config_file", None):
            custom_yaml_files = cli_config.get("config_file")  # type: str
            custom_yaml_files = custom_yaml_files.split(",")
            for cf in custom_yaml_files:
                if cf:
                    custom_configs.append(_read_yaml_config(cf))

        # Higher priority than default configurations
        if custom_configs:
            cls._config = OmegaConf.merge(cls._config, *custom_configs)

        # Handle include files
        included_configs = []
        included_files = cls._config.get("include", [])  # type: List[str]
        for fl_or_dir in included_files:
            fls = []
            if fl_or_dir.endswith("/"):
                fls += glob.glob(fl_or_dir + "*.yaml") + \
                    glob.glob(fl_or_dir + "*.yml")
            else:
                fls.append(fl_or_dir)
            for f in fls:
                included_configs.append(_read_yaml_config(f))

        if included_configs:
            cls._config = OmegaConf.merge(cls._config, *included_configs)

        # The highest priority
        if cli_config:
            cls._config = OmegaConf.merge(cls._config, cli_config)

        # TODO(P1): Support load yaml dynamically.

        print("* Configs: ", cls._config)

    @classmethod
    def get_config(cls):
        """Get the global configuration for the Agent

        Raises:
            JscmConfigError if Configuration is not property initialized

        Usage:
            from utils.config import Configuration \n
            config = Configuration.get_config()

        """
        return cls()
