#!/usr/bin/python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import os
import re
import time
import json
import shutil
from pathlib import Path
from typing import Generator

from slpkg.configs import Configs
from slpkg.blacklist import Blacklist
from slpkg.error_messages import Errors


class Utilities(Configs):

    def __init__(self):
        super(Configs, self).__init__()
        self.black = Blacklist()
        self.errors = Errors()

    def is_package_installed(self, name: str) -> str:
        """ Returns the installed package binary. """
        installed_package: Generator = self.log_packages.glob(f'{name}*')

        for installed in installed_package:
            inst_name: str = self.split_package(installed.name)['name']
            if inst_name == name and inst_name not in self.ignore_packages([inst_name]):
                return installed.name
        return ''

    def all_installed(self) -> dict:
        """ Return all installed packages from /val/log/packages folder. """
        installed_packages: dict = {}

        for file in self.log_packages.glob('*'):
            name: str = self.split_package(file.name)['name']

            if not name.startswith('.'):
                installed_packages[name] = file.name

        blacklist_packages: list = self.ignore_packages(list(installed_packages.keys()))
        if blacklist_packages:
            for black in blacklist_packages:
                del installed_packages[black]

        return installed_packages

    @staticmethod
    def remove_file_if_exists(path: Path, file: str) -> None:
        """ Remove the old files. """
        archive: Path = Path(path, file)
        if archive.is_file():
            archive.unlink()

    @staticmethod
    def remove_folder_if_exists(folder: Path) -> None:
        """ Remove the old folders. """
        if folder.exists():
            shutil.rmtree(folder)

    @staticmethod
    def create_directory(directory: Path) -> None:
        """ Creates folder like mkdir -p. """
        if not directory.is_dir():
            directory.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def split_package(package: str) -> dict:
        """ Splits the binary package name in name, version, arch, build and tag. """
        name: str = '-'.join(package.split('-')[:-3])
        version: str = ''.join(package[len(name):].split('-')[:-2])
        arch: str = ''.join(package[len(name + version) + 2:].split('-')[:-1])
        build_tag: str = package.split('-')[-1]
        build: str = ''.join(re.findall(r'\d+', build_tag[:2]))
        pkg_tag: str = build_tag[len(build):]

        return {
            'name': name,
            'version': version,
            'arch': arch,
            'build': build,
            'tag': pkg_tag
        }

    @staticmethod
    def finished_time(elapsed_time: float) -> None:
        """ Printing the elapsed time. """
        print(f'\nFinished:', time.strftime(f'%H:%M:%S', time.gmtime(elapsed_time)))

    @staticmethod
    def is_option(options: tuple, flags: list) -> bool:
        """ Returns True if option applied. """
        for option in options:
            if option in flags:
                return True

    def read_packages_from_file(self, file: Path) -> Generator:
        """ Reads name packages from file and split these to list. """
        try:
            with open(file, 'r', encoding='utf-8') as pkgs:
                packages: list = pkgs.read().splitlines()

            for package in packages:
                if package and not package.startswith('#'):
                    if '#' in package:
                        package = package.split('#')[0].strip()
                    yield package
        except FileNotFoundError:
            self.errors.raise_error_message(f"No such file or directory: '{file}'", exit_status=20)

    def read_text_file(self, file: Path) -> list:
        """ Reads the text file and returns it into a list. """
        try:
            with open(file, 'r', encoding='utf-8', errors='replace') as text_file:
                return text_file.readlines()
        except FileNotFoundError:
            self.errors.raise_error_message(f"No such file or directory: '{file}'", exit_status=20)

    def count_file_size(self, name: str) -> int:
        """
        Read the contents files from the package file list and count
        the total installation file size in bytes.
        Args:
            name: The name of the package.

        Returns:
            The total package installation file size.
        """
        count_files: int = 0
        installed: Path = Path(self.log_packages, self.is_package_installed(name))
        if installed:
            file_installed: list = installed.read_text().splitlines()
            for line in file_installed:
                file: Path = Path('/', line)
                if file.is_file():
                    count_files += file.stat().st_size
        return count_files

    @staticmethod
    def convert_file_sizes(byte_size: float) -> str:
        """
        Convert bytes to kb, mb and gb.
        Args:
            byte_size: The file size in bytes.
        Returns:
            The size converted.
        """
        kb_size: float = byte_size / 1024
        mb_size: float = kb_size / 1024
        gb_size: float = mb_size / 1024

        if gb_size >= 1:
            return f"{gb_size:.0f} GB"
        elif mb_size >= 1:
            return f"{mb_size:.0f} MB"
        elif kb_size >= 1:
            return f"{kb_size:.0f} KB"
        else:
            return f"{byte_size} B"

    @staticmethod
    def apply_package_pattern(data: dict, packages: list) -> list:
        """ If the '*' applied returns all the package names. """
        for pkg in packages:
            if pkg == '*':
                packages.remove('*')
                packages.extend(list(data.keys()))
        return packages

    @staticmethod
    def change_owner_privileges(folder: Path) -> None:
        """ Changes the owner privileges. """
        os.chown(folder, 0, 0)
        for file in os.listdir(folder):
            os.chown(Path(folder, file), 0, 0)

    def case_insensitive_pattern_matching(self, packages: list, data: dict, flags: list) -> list:
        """ Case-insensitive pattern matching packages. """
        if self.is_option(('-m', '--no-case'), flags):
            repo_packages: tuple = tuple(data.keys())
            for package in packages:
                for pkg in repo_packages:
                    if package.lower() == pkg.lower():
                        packages.append(pkg)
                        packages.remove(package)
                        break
        return packages

    def read_json_file(self, file: Path) -> dict:
        """
        Read JSON data from the file.
        Args:
            file: Path file for reading.
        Returns:
            Dictionary with data.
        """
        json_data: dict = {}
        try:
            json_data: dict = json.loads(file.read_text(encoding='utf-8'))
        except FileNotFoundError:
            self.errors.raise_error_message(f'{file} not found.', exit_status=1)
        except json.decoder.JSONDecodeError:
            pass
        return json_data

    def ignore_packages(self, packages: list) -> list:
        """
        Matching packages using regular expression.
        Args:
            packages: Tha packages to apply the pattern.
        Returns:
            The matching packages.
        """
        matching_packages: list = []
        blacklist: tuple = self.black.packages()
        if blacklist:
            pattern: str = '|'.join(blacklist)
            matching_packages: list = [pkg for pkg in packages if re.search(pattern, pkg)]
        return matching_packages
