#!/usr/bin/python3
# -*- coding: utf-8 -*-

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.error_messages import Errors


class Check(Configs):
    """ Some checks before proceed. """

    def __init__(self, repository: str):
        super(Configs, self).__init__()
        self.repository = repository

        self.errors = Errors()
        self.utils = Utilities()

    def package_exists_in_the_database(self, packages: list, data: dict) -> None:
        not_packages: list = []

        for pkg in packages:
            if not data.get(pkg) and pkg != '*':
                not_packages.append(pkg)

        if not_packages:
            self.errors.raise_error_message(f"Packages '{', '.join(not_packages)}' does not exists",
                                            exit_status=1)

    def is_package_installed(self, packages: list) -> None:
        """ Checking for installed packages. """
        not_found: list = []

        for pkg in packages:
            if not self.utils.is_package_installed(pkg):
                not_found.append(pkg)

        if not_found:
            self.errors.raise_error_message(f"Not found '{', '.join(not_found)}' installed packages",
                                            exit_status=1)
