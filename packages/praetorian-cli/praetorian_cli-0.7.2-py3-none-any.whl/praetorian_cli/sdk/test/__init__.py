import configparser
import os
from pathlib import Path

from praetorian_cli.sdk.keychain import Keychain
from praetorian_cli.sdk.chaos import Chaos


class BaseTest:

    def setup_chaos(self):
        location = os.path.join(Path.home(), '.praetorian', 'keychain.ini')
        config = configparser.ConfigParser()
        config.read(location)
        return Chaos(Keychain(location=location)), config['United States']['username']
