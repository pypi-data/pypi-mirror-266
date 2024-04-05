#!/usr/bin/python3
# -*- coding: utf-8 -*-

from slpkg.utilities import Utilities


class Requires:
    """ Creates a tuple of dependencies with
    the right order to install. """
    __slots__ = (
        'data', 'name', 'flags', 'utils', 'option_for_resolve_off'
    )

    def __init__(self, data: dict, name: str, flags: list):
        self.data: dict = data
        self.name: str = name
        self.utils = Utilities()

        self.option_for_resolve_off: bool = self.utils.is_option(
            ('-O', '--resolve-off'), flags)

    def resolve(self) -> tuple:
        """ Resolve the dependencies. """
        dependencies: tuple = ()
        if not self.option_for_resolve_off:
            requires: list[str] = self.data[self.name]['requires']
            for require in requires:
                sub_requires: list[str] = self.data[require]['requires']
                for sub in sub_requires:
                    requires.append(sub)

            requires.reverse()
            dependencies: tuple = tuple(dict.fromkeys(requires))

        return dependencies
