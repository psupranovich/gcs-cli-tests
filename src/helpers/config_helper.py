import json
from pathlib import Path


def get_config():
    """
    Read the config.json file and return its contents as a dictionary.
    """
    src_dir = Path(__file__).parent.parent
    config_path = src_dir / "config.json"

    try:
        with open(config_path, 'r') as config_file:
            config_data = json.load(config_file)
        return config_data
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at {config_path}")
    except json.JSONDecodeError:
        raise ValueError(f"Invalid JSON in config file at {config_path}")


def get_config_value(key, default=None):
    """
    Get a specific value from the config.
    """
    config = get_config()
    return config.get(key, default)
