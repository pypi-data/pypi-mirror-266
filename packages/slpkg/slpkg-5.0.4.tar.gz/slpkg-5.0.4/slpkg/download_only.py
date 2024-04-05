#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time
import shutil
from pathlib import Path

from slpkg.configs import Configs
from slpkg.views.views import View
from slpkg.utilities import Utilities
from slpkg.gpg_verify import GPGVerify
from slpkg.downloader import Downloader
from slpkg.views.asciibox import AsciiBox
from slpkg.repositories import Repositories


class DownloadOnly(Configs):
    """ Download only the sources and the slackbuilds or the packages
        for binary repositories.
    """

    def __init__(self, directory: Path, flags: list, data: dict, repository: str):
        super(Configs, self).__init__()
        self.directory: Path = directory
        self.flags: list = flags
        self.data: dict = data
        self.repository: str = repository

        self.view = View(flags, repository, data)
        self.download = Downloader(flags)
        self.repos = Repositories()
        self.utils = Utilities()
        self.ascii = AsciiBox()
        self.gpg = GPGVerify()

        self.urls: dict = {}
        self.asc_files: list = []
        self.download_path: Path = Path()

        self.sbo_repo: dict = {
            self.repos.sbo_repo_name: self.repos.sbo_repo_path,
            self.repos.ponce_repo_name: self.repos.ponce_repo_path
        }

        self.option_for_directory: bool = self.utils.is_option(
            ('-z', '--directory='), flags)

    def packages(self, packages: list) -> None:
        packages: list = self.utils.apply_package_pattern(self.data, packages)
        self.view.download_packages(packages, self.directory)
        self.view.question()
        self.set_download_path()
        start: float = time.time()

        print(f'\rPrepare sources for downloading... ', end='')
        for pkg in packages:
            if self.repository not in [self.repos.sbo_repo_name, self.repos.ponce_repo_name]:
                self.save_binary_sources(pkg)
            else:
                self.save_slackbuild_sources(pkg)
                self.copy_slackbuild_scripts(pkg)

        print(f'{self.bgreen}{self.ascii.done}{self.endc}')
        self.download_the_sources()

        elapsed_time: float = time.time() - start
        self.utils.finished_time(elapsed_time)

    def set_download_path(self) -> None:
        self.download_path: Path = self.download_only_path
        if self.option_for_directory:
            self.download_path: Path = self.directory

    def save_binary_sources(self, name: str) -> None:
        package: str = self.data[name]['package']
        mirror: str = self.data[name]['mirror']
        location: str = self.data[name]['location']
        url: str = f'{mirror}{location}/{package}'
        self.urls[name] = ((url,), self.tmp_slpkg)
        asc_url: list = [f'{mirror}{location}/{package}.asc']
        asc_file: Path = Path(self.tmp_slpkg, f'{package}.asc')

        if self.gpg_verification:
            self.urls[f'{name}.asc'] = (asc_url, self.tmp_slpkg)
            self.asc_files.append(asc_file)

    def save_slackbuild_sources(self, name: str) -> None:
        if self.os_arch == 'x86_64' and self.data[name]['download64']:
            sources: tuple = self.data[name]['download64']
        else:
            sources: tuple = self.data[name]['download']
        self.urls[name] = (sources, Path(self.build_path, name))

        if self.gpg_verification and self.repository == self.repos.sbo_repo_name:
            location: str = self.data[name]['location']
            asc_file: Path = Path(self.repos.repositories_path, self.repos.sbo_repo_name,
                                  location, f'{name}{self.repos.sbo_repo_tar_suffix}.asc')
            self.asc_files.append(asc_file)

    def copy_slackbuild_scripts(self, name: str) -> None:
        repo_path_package: Path = Path(self.sbo_repo[self.repository], self.data[name]['location'], name)
        if not Path(self.download_path, name).is_dir():
            shutil.copytree(repo_path_package, Path(self.download_path, name))

    def download_the_sources(self) -> None:
        if self.urls:
            print(f'\nStarted to download total ({self.cyan}{len(self.urls)}{self.endc}) sources:\n')
            self.download.download(self.urls)
            print()

        if self.gpg_verification and self.repository != self.repos.ponce_repo_name:
            self.gpg.verify(self.asc_files)
