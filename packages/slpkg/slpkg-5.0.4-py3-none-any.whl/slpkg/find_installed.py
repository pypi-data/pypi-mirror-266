#!/usr/bin/python3
# -*- coding: utf-8 -*-

from slpkg.configs import Configs
from slpkg.utilities import Utilities


class FindInstalled(Configs):
    """ Find installed packages. """

    def __init__(self, flags: list, packages: list):
        super(Configs, self).__init__()
        self.packages: list = packages

        self.utils = Utilities()
        self.matching: list = []

        self.option_for_no_case: bool = self.utils.is_option(
            ('-m', '--no-case'), flags)

    def find(self) -> None:
        self.view_title()
        for package in self.packages:
            for name in self.utils.all_installed().values():

                if package in name or package == '*' or self.is_not_case_sensitive(package, name):
                    self.matching.append(name)
        self.matched()

    @staticmethod
    def view_title() -> None:
        print(f'The list below shows the installed packages:\n')

    def matched(self) -> None:
        if self.matching:
            self.view_matched_packages()
        else:
            print('\nDoes not match any package.\n')

    def view_matched_packages(self) -> None:
        for package in self.matching:
            print(f'{self.cyan}{package}{self.endc}')
        self.view_summary()

    def view_summary(self) -> None:
        print(f'\n{self.grey}Total found {len(self.matching)} packages.{self.endc}')

    def is_not_case_sensitive(self, package: str, name: str) -> bool:
        if self.option_for_no_case:
            return package.lower() in name.lower()
