import yaml
import pkgutil


def read_config(config_dir="config"):
    """
    Return the project configuration settings.

    Args:
        config_dir (str): Name of directory containing config

    Returns:
        (dict): combined general settings with params settings
    """
    params_config_path = pkgutil.get_data(__name__, f"{config_dir}/params.yaml")
    configurations = yaml.safe_load(params_config_path)

    return configurations
