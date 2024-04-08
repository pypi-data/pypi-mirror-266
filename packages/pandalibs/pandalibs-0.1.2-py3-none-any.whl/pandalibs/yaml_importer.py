import os
import sys
import yaml


# Custom exception for configuration errors
class ConfigurationError(Exception):
    pass


# Constants
DEFAULT_CONFIG_FILE = "config.yaml"


# Get path of running application
def get_application_path(go_up_one_level=False):
    """
    Returns the application path or its parent directory based on the argument.

    Args:
        go_up_one_level (bool, optional): If True, returns the parent directory. Defaults to False.

    Returns:
        str: The path to the application directory or its parent.
    """
    if getattr(sys, "frozen", False):
        # Frozen executable, path manipulation
        path = os.path.dirname(sys.executable)
        return path if not go_up_one_level else os.path.dirname(path)
    else:
        # Regular script, path manipulation
        path = os.path.dirname(os.path.abspath(sys.argv[0]))
        return path if not go_up_one_level else os.path.dirname(path)


# Get configuration data as a dictionary
def get_configuration_data(up_a_level=False, file_name=DEFAULT_CONFIG_FILE, subfolder="config"):
    """Load and convert configuration file into appropriate data.
    Accepts optional filename and subfolder, as well as option to go up a level.
    Defaults to config.yaml within config subfolder.
    """
    try:
        exe_dir = get_application_path(up_a_level)
        if subfolder:
            config_path = os.path.join(exe_dir, subfolder, file_name)
        else:
            config_path = os.path.join(exe_dir, file_name)

        if not os.path.exists(config_path):
            raise ConfigurationError(f"Configuration file '{file_name}' not found at '{config_path}'")

        with open(config_path, "r") as f:
            userinfo = yaml.safe_load(f)

        # Generate CONFIG_KEYS dynamically from keys present in the configuration file
        CONFIG_KEYS = list(userinfo.keys())

        # Create a dictionary to store configuration data
        config_dict = {}
        for key in CONFIG_KEYS:
            config_dict[key] = userinfo.get(key)

        return config_dict

    except ConfigurationError as e:
        raise e

    except Exception as e:
        raise ConfigurationError(f"An error occurred: {e}")
