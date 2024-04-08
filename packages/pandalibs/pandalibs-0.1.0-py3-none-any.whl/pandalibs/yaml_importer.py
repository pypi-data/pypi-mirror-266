import os
import sys
import yaml


# Custom exception for configuration errors
class ConfigurationError(Exception):
    pass


# Constants
DEFAULT_CONFIG_FILE = "user_config.yaml"


# Get path of running application
def get_application_path():
    """Returns the directory containing the running script or executable."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(sys.argv[0]))


# Get configuration data as a dictionary
def get_configuration_data(
    file_name=DEFAULT_CONFIG_FILE, subfolder=None):
    """Load and convert configuration file into appropriate data.
    Accepts optional filename and subfolder. Defaults to user_config.yaml.
    """
    try:
        exe_dir = get_application_path()
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
