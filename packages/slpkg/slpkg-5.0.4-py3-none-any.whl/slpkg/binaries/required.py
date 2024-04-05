#!/usr/bin/python3
# -*- coding: utf-8 -*-

from typing import Generator

from slpkg.utilities import Utilities
from slpkg.repositories import Repositories


class Required:
    """ Creates a tuple of dependencies with
    the right order to install. """
    __slots__ = (
        'data', 'name', 'flags', 'repos', 'utils',
        'special_repos', 'repo', 'repository_packages',
        'option_for_resolve_off'
    )

    def __init__(self, data: dict, name: str, flags: list):
        self.data: dict = data
        self.name: str = name
        self.repos = Repositories()
        self.utils = Utilities()

        self.special_repos: list = [
            self.repos.salixos_repo_name,
            self.repos.salixos_patches_repo_name,
            self.repos.salixos_extra_repo_name,
            self.repos.slackel_repo_name,
            self.repos.slint_repo_name
        ]

        self.repo: str = data[name]['repo']
        self.repository_packages: tuple = tuple(self.data.keys())

        self.option_for_resolve_off: bool = self.utils.is_option(
            ('-O', '--resolve-off'), flags)

    def resolve(self) -> tuple:
        """ Resolve the dependencies. """
        dependencies: tuple = ()
        if not self.option_for_resolve_off:
            requires: list[str] = list(
                self.remove_deps(self.data[self.name]['requires'])
            )

            # Resolve dependencies for some special repos.
            if self.repo in self.special_repos:
                for require in requires:
                    if require not in self.repository_packages:
                        requires.remove(require)

            else:
                for require in requires:
                    sub_requires: list[str] = list(
                        self.remove_deps(self.data[require]['requires'])
                    )
                    for sub in sub_requires:
                        requires.append(sub)

            requires.reverse()
            dependencies: tuple = tuple(dict.fromkeys(requires))

        return dependencies

    def remove_deps(self, requires: list) -> Generator:
        """ Remove requires that not in the repository or blacklisted. """
        for require in requires:
            if require in self.repository_packages:
                yield require
