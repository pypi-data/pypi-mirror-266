#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time
import json

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.dialog_box import DialogBox
from slpkg.views.views import View
from slpkg.multi_process import MultiProcess


class RemovePackages(Configs):
    """ Removes installed packages with dependencies if they installed with
        slpkg install command.
    """

    def __init__(self, packages: list, flags: list):
        super(Configs, self).__init__()
        self.packages: list = packages

        self.dialogbox = DialogBox()
        self.utils = Utilities()
        self.multi_proc = MultiProcess(flags)
        self.view = View(flags)

        self.deps_log: dict = {}
        self.packages_for_remove: list = []
        self.dependencies: list = []
        self.found_dependent_packages: dict = {}

        self.option_for_yes: bool = self.utils.is_option(
            ('-y', '--yes'), flags)

    def remove(self, upgrade=False) -> None:
        self.deps_log: dict = self.utils.read_json_file(self.deps_log_file)

        if upgrade:
            self.packages: list = self.choose_packages_for_remove(self.packages, upgrade)

        if self.packages:
            self.add_packages_for_remove()
            self.remove_doubles_dependencies()
            self.dependencies: list = self.choose_packages_for_remove(self.dependencies)
            self.add_installed_dependencies_to_remove()

            self.view.remove_packages(self.packages, self.dependencies)
            self.found_dependent()

            answer: str = 'y'
            if upgrade:
                answer: str = self.remove_question()
            else:
                self.view.question()

            if answer in ['y', 'Y']:
                start: float = time.time()
                self.remove_packages()
                elapsed_time: float = time.time() - start
                self.utils.finished_time(elapsed_time)

    def add_packages_for_remove(self) -> None:
        for package in self.packages:
            installed: str = self.utils.is_package_installed(package)
            if installed:
                self.packages_for_remove.append(installed)

            if self.deps_log.get(package):
                dependencies: list = self.deps_log[package]
                for dep in dependencies:
                    if self.utils.is_package_installed(dep) and dep not in self.packages:
                        self.dependencies.append(dep)

    def found_dependent(self) -> None:
        for package in self.packages_for_remove:
            name: str = self.utils.split_package(package)['name']
            version: str = self.utils.split_package(package)['version']
            for pkg, deps in self.deps_log.items():
                if name in deps and pkg not in self.packages + self.dependencies:
                    self.found_dependent_packages[pkg] = version

        if self.found_dependent_packages:
            dependent_packages: list = list(set(self.found_dependent_packages))
            print(f'\n{self.bred}Warning: {self.endc}found extra ({len(dependent_packages)}) dependent packages:')
            for pkg, ver in self.found_dependent_packages.items():
                print(f"{'':>2}{pkg} {self.grey}{ver}{self.endc}")

    def remove_doubles_dependencies(self) -> None:
        self.dependencies: list = list(set(self.dependencies))

    def add_installed_dependencies_to_remove(self) -> None:
        for dep in self.dependencies:
            installed: str = self.utils.is_package_installed(dep)
            if installed:
                self.packages_for_remove.append(installed)

    def remove_packages(self) -> None:
        # Remove old slpkg.log file.
        if self.slpkg_log_file.is_file():
            self.slpkg_log_file.unlink()

        print(f'Started of removing total ({self.cyan}{len(self.packages_for_remove)}{self.endc}) packages:\n')
        for package in self.packages_for_remove:
            command: str = f'{self.removepkg} {package}'
            progress_message: str = f'{self.bold}{self.red}Removing{self.endc}'

            self.multi_proc.process_and_log(command, package, progress_message)
            name: str = self.utils.split_package(package)['name']
            if name in self.deps_log.keys():
                self.deps_log.pop(name)

        self.deps_log_file.write_text(json.dumps(self.deps_log, indent=4))

    def choose_packages_for_remove(self, packages: list, upgrade=False) -> list:
        if packages and self.dialog:
            height: int = 10
            width: int = 70
            list_height: int = 0
            choices: list = []
            title: str = " Choose dependencies you want to remove "
            if upgrade:
                title: str = ' Choose packages you want to remove '

            for package in packages:
                installed_package: str = self.utils.is_package_installed(package)
                installed_version: str = self.utils.split_package(installed_package)['version']
                choices.extend([(package, installed_version, True, f'Package: {installed_package}')])

            text: str = f'There are {len(choices)} dependencies:'
            if upgrade:
                text: str = f'There are {len(choices)} packages:'
            code, packages = self.dialogbox.checklist(text, title, height, width, list_height, choices)
            os.system('clear')
            return packages
        return []

    def remove_question(self) -> str:
        if not self.option_for_yes and self.ask_question:
            answer: str = input('\nDo you want to remove these packages? [y/N] ')
            return answer
