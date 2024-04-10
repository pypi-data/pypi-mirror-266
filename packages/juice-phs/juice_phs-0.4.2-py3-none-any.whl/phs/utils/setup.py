import os
import configparser


def get_version_from_setup_cfg():
    """
    Extract the version from the setup.cfg file.

    Returns
    -------
    str or None
        The version string if found in the 'metadata' section of the setup.cfg file,
        otherwise returns None.
    """
    config = configparser.ConfigParser()

    config.read(f'{os.path.dirname(os.path.abspath(__file__))}/../../../setup.cfg')
    # Check if the 'metadata' section exists and contains 'version'
    if 'metadata' in config and 'version' in config['metadata']:
        return config['metadata']['version']
    else:
        return None  # Return None if version is not found