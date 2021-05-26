import os
from flask_env import MetaFlaskEnv


class EnvConfiguration(metaclass=MetaFlaskEnv):
    """
    This configuration class will loadd all the environment variables that start with the ENV_PREFIX into the
    app configuration automatically
    """
    ENV_PREFIX = 'APP_'
    ENV_LOAD_ALL = True



class FileConfiguration:
    """
    Gets all the configuration parameters from the python module
    """
    def __init__(self, config_module):
        """
        Constructor
        :param config_module: Python module to load the configuration parameters from
        """
        blacklist = ["os", "basedir"]
        double_underscore = "__"
        for attribute in dir(config_module):
            if attribute not in blacklist and not attribute.startswith(double_underscore):
                setattr(self, attribute, getattr(config_module, attribute))
