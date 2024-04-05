#!/usr/bin/python3
# -*- coding: utf-8 -*-

from typing import Generator
from packaging.version import parse, InvalidVersion
from pathlib import Path

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.repositories import Repositories


class Upgrade(Configs):
    """ Upgrade the installed packages. """

    def __init__(self, repository: str, data: dict):
        super(Configs, self).__init__()
        self.repository: str = repository
        self.data: dict = data

        self.utils = Utilities()
        self.repos = Repositories()
        self.id: int = 0
        self.sum_upgrade: int = 0
        self.sum_removed: int = 0
        self.sum_added: int = 0
        self.installed_names: list = []
        self.installed_packages: list = []

    def load_installed_packages(self, repository: str) -> None:
        if repository in [self.repos.slack_repo_name, self.repos.salixos_repo_name]:
            installed: dict = self.utils.all_installed()

            for name, package in installed.items():
                tag: str = self.utils.split_package(package)['tag']
                if not tag:
                    self.installed_packages.append(Path(package))
                    self.installed_names.append(name)
        else:
            repo_tag: str = self.repos.repositories[repository]['repo_tag']
            self.installed_packages: list = list(self.log_packages.glob(f'*{repo_tag}'))

    def packages(self) -> Generator:
        """ Returns the upgradable packages. """
        # Delete log file before starts.
        if self.upgrade_log_file.is_file():
            self.upgrade_log_file.unlink()

        self.load_installed_packages(self.repository)

        for inst in self.installed_packages:
            name: str = self.utils.split_package(inst.name)['name']
            if self.is_package_upgradeable(inst.name):
                yield name

            if self.repository == self.repos.slack_repo_name and self.removed_packages:
                if name not in self.data.keys():
                    yield name + '_Removed.'

        if self.repository == self.repos.slack_repo_name and self.new_packages:
            for name in self.data.keys():
                # if not self.utils.is_package_installed(name):
                if name not in self.installed_names:
                    yield name

    def is_package_upgradeable(self, installed: str) -> bool:
        """ Returns True for upgradeable packages. """
        inst_name: str = self.utils.split_package(installed)['name']
        if self.data.get(inst_name):
            repo_version: str = self.data[inst_name]['version']
            repo_build: str = self.data[inst_name]['build']
            inst_version: str = self.utils.split_package(installed)['version']
            inst_build: str = self.utils.split_package(installed)['build']
            try:
                if parse(repo_version) > parse(inst_version):
                    return True

                if parse(repo_version) == parse(inst_version) and int(repo_build) > int(inst_build):
                    return True
            except InvalidVersion as err:
                # Different options to compare packages.
                repo_package: str = self.data[inst_name]['package']
                if repo_version > inst_version:  # Try to compare the strings.
                    return True
                elif repo_version == inst_version and int(repo_build) > int(inst_build):
                    return True
                elif installed != repo_package[:-4]:  # Add the package if a new one on the repository.
                    return True
                elif installed == repo_package[:-4]:  # Not new packages in the repository.
                    return False
                self._write_log_file(installed, inst_name, err)

        return False

    def _write_log_file(self, installed: str, name: str, err: InvalidVersion) -> None:
        """ Writes a log file for invalid versions. """
        if self.log_path.is_dir():
            with self.upgrade_log_file.open('a') as log:
                log.write(f"Installed: {installed}, "
                          f"Repository: {self.data[name]['package']}, "
                          f"Error: {err}\n")

    def check_packages(self) -> None:
        repo_data: dict = {}
        found_packages: dict = {}

        if self.repository == '*':
            repo_data: dict = self.data
        else:
            repo_data[self.repository] = self.data

        for repo, data in repo_data.items():
            self.load_installed_packages(repo)

            for installed in self.installed_packages:
                name: str = self.utils.split_package(installed.name)['name']

                if data.get(name):
                    self.data: dict = data

                    if self.is_package_upgradeable(installed.name):
                        self.id += 1
                        self.sum_upgrade += 1
                        inst_version: str = self.utils.split_package(installed.name)['version']
                        inst_build: str = self.utils.split_package(installed.name)['build']
                        repo_version: str = data[name]['version']
                        repo_build: str = data[name]['build']

                        found_packages[self.id]: dict = {
                            'name': name,
                            'inst_version': inst_version,
                            'inst_build': inst_build,
                            'repo_version': repo_version,
                            'repo_build': repo_build,
                            'repo': repo,
                            'type': 'upgrade'
                        }

                if repo == self.repos.slack_repo_name and self.removed_packages:
                    tag: str = self.utils.split_package(installed.name)['tag']
                    if not tag and name not in data.keys():
                        self.id += 1
                        self.sum_removed += 1
                        inst_version: str = self.utils.split_package(installed.name)['version']
                        inst_build: str = self.utils.split_package(installed.name)['build']

                        found_packages[self.id]: dict = {
                            'name': name,
                            'inst_version': inst_version,
                            'inst_build': inst_build,
                            'repo_version': '',
                            'repo_build': '',
                            'repo': repo,
                            'type': 'remove'
                        }

            if repo == self.repos.slack_repo_name and self.new_packages:
                for name in data.keys():
                    # if not self.utils.is_package_installed(name):
                    if name not in self.installed_names:
                        self.id += 1
                        self.sum_added += 1
                        repo_version: str = data[name]['version']
                        repo_build: str = data[name]['build']

                        found_packages[self.id]: dict = {
                            'name': name,
                            'inst_version': '',
                            'inst_build': '',
                            'repo_version': repo_version,
                            'repo_build': repo_build,
                            'repo': self.repos.slack_repo_name,
                            'type': 'add'
                        }

        if found_packages:
            print()
            title: str = f"{'packages':<18} {'Repository':<15} {'Build':<6} {'Installed':<15} {'Build':<5} {'Repo':>15}"
            print(len(title) * '=')
            print(f'{self.bgreen}{title}{self.endc}')
            print(len(title) * '=')

            for data in found_packages.values():
                name: str = data['name']
                repo_version: str = data['repo_version']
                repo_build: str = data['repo_build']
                inst_version: str = data['inst_version']
                inst_build: str = data['inst_build']
                repo: str = data['repo']
                mode: str = data['type']

                if len(name) > 17:
                    name: str = f'{name[:14]}...'
                if len(inst_version) > 15:
                    inst_version: str = f"{inst_version[:11]}..."
                if len(repo_version) > 15:
                    repo_version: str = f"{repo_version[:11]}..."

                color: str = self.violet
                if mode == 'remove':
                    color: str = self.red
                if mode == 'add':
                    color: str = self.cyan

                print(f"{color}{name:<18}{self.endc} {repo_version:<15} {repo_build:<6} {inst_version:<15} "
                      f"{inst_build:<5} {repo:>15}")

            print(len(title) * '=')
            print(f'{self.grey}Packages to upgrade {self.sum_upgrade}, packages to remove '
                  f'{self.sum_removed} and packages added {self.sum_added}.{self.endc}\n')
        else:
            print('\nEverything is up-to-date!\n')
        raise SystemExit(0)
