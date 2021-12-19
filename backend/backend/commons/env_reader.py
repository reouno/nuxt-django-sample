"""env value reader only for local environment"""
import os
from configparser import SafeConfigParser


def env_ini(ini_file: str = None) -> SafeConfigParser:
    """read environment variables ini file"""
    ini_file = './backend/settings/local-env.ini' if ini_file is None else ini_file
    config = SafeConfigParser()

    if os.path.exists(ini_file):
        config.read(ini_file)
    else:
        # Default values must be set for github CI to run django test successfully
        # because local-env.ini is excluded from git repo.
        config.set('DEFAULT', 'email_host_password', '')

    return config
