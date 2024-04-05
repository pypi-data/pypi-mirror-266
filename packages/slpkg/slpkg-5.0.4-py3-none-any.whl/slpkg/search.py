#!/usr/bin/python3
# -*- coding: utf-8 -*-

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.repositories import Repositories


class SearchPackage(Configs):
    """ Search packages from the repositories. """

    def __init__(self, flags: list, packages: list, data: dict, repository: str):
        super(Configs, self).__init__()
        self.packages: list = packages
        self.data: dict = data
        self.repository: str = repository

        self.utils = Utilities()
        self.repos = Repositories()

        self.matching: int = 0
        self.data_dict: dict = {}
        self.repo_data: dict = {}

        self.option_for_no_case: bool = self.utils.is_option(
            ('-m', '--no-case'), flags)

    def search(self) -> None:
        if self.repository == '*':
            self.search_to_all_repositories()
        else:
            self.repo_data: dict = self.data
            self.search_for_the_packages(self.repository)

        print(f'The list below shows the repository packages:\n')
        self.summary_of_searching()

    def search_to_all_repositories(self) -> None:
        all_data: dict = self.data
        for name, repo in all_data.items():
            self.repo_data: dict = repo
            self.search_for_the_packages(name)

    def search_for_the_packages(self, repo: str) -> None:
        for package in self.packages:
            for name, data_pkg in self.repo_data.items():

                if package in name or package == '*' or self.is_not_case_sensitive(package, name):
                    self.matching += 1

                    self.data_dict[self.matching] = {
                        'repository': repo,
                        'name': name,
                        'version': data_pkg['version']
                    }

    def summary_of_searching(self) -> None:
        try:
            name_length: int = max(len(name['name']) for name in self.data_dict.values())
        except ValueError:
            name_length: int = 1
        if self.matching:
            for item in self.data_dict.values():
                print(f"{item['repository']}: {self.cyan}{item['name']:<{name_length}}{self.endc} "
                      f"{self.yellow}{item['version']}{self.endc}")

            print(f'\n{self.grey}Total found {self.matching} packages.{self.endc}')
        else:
            print('\nDoes not match any package.\n')

    def is_not_case_sensitive(self, package: str, name: str) -> bool:
        if self.option_for_no_case:
            return package.lower() in name.lower()
