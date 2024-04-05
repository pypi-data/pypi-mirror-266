#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
    import tomli
except ModuleNotFoundError:
    import tomllib as tomli

from pathlib import Path

from slpkg.configs import Configs
from slpkg.toml_errors import TomlErrors


class Blacklist(Configs):
    """ Reads and returns the blacklist. """

    def __init__(self):
        super(Configs, self).__init__()

        self.toml_errors = TomlErrors()
        self.blacklist_file_toml = Path(self.etc_path, 'blacklist.toml')

    def packages(self) -> tuple:
        """ Reads the blacklist file. """
        packages: tuple = tuple()
        if self.blacklist_file_toml.is_file():
            try:
                with open(self.blacklist_file_toml, 'rb') as black:
                    packages: tuple = tuple(tomli.load(black)['BLACKLIST']['PACKAGES'])
            except (tomli.TOMLDecodeError, KeyError) as error:
                self.toml_errors.raise_toml_error_message(error, self.blacklist_file_toml)

        return packages
