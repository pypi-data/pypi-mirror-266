#!/usr/bin/python3
# -*- coding: utf-8 -*-

class Version:
    """ Print the version. """

    def __init__(self):
        self.version_info: tuple = (5, 0, 4)
        self.version: str = '{0}.{1}.{2}'.format(*self.version_info)
        self.license: str = 'GNU General Public License v3 (GPLv3)'
        self.author: str = 'Dimitris Zlatanidis (dslackw)'
        self.homepage: str = 'https://dslackw.gitlab.io/slpkg'
        self.email: str = 'dslackw@gmail.com'

    def view(self) -> None:
        """ Prints the version. """
        print(f'Version: {self.version}\n'
              f'Author: {self.author}\n'
              f'License: {self.license}\n'
              f'Homepage: {self.homepage}\n'
              f'Email: {self.email}')
