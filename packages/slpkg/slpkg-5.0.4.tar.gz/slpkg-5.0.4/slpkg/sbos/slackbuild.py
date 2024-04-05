#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import time
import json
import shutil

from pathlib import Path
from collections import OrderedDict

from slpkg.upgrade import Upgrade
from slpkg.checksum import Md5sum
from slpkg.configs import Configs
from slpkg.views.views import View
from slpkg.utilities import Utilities
from slpkg.dialog_box import DialogBox
from slpkg.gpg_verify import GPGVerify
from slpkg.downloader import Downloader
from slpkg.views.asciibox import AsciiBox
from slpkg.repositories import Repositories
from slpkg.multi_process import MultiProcess
from slpkg.sbos.dependencies import Requires


class Slackbuilds(Configs):
    """ Download build and install the SlackBuilds. """

    def __init__(self, repository: str, data: dict, slackbuilds: list, flags: list, mode: str):
        super(Configs, self).__init__()
        self.repository: str = repository
        self.data: dict = data
        self.slackbuilds: list = slackbuilds
        self.flags: list = flags
        self.mode: str = mode

        self.ascii = AsciiBox()
        self.repos = Repositories()
        self.utils = Utilities()
        self.dialogbox = DialogBox()
        self.multi_proc = MultiProcess(flags)
        self.view = View(flags, repository, data)
        self.check_md5 = Md5sum(flags)
        self.download = Downloader(flags)
        self.upgrade = Upgrade(repository, data)
        self.gpg = GPGVerify()

        self.sources: dict = {}
        self.install_order: list = []
        self.dependencies: list = []
        self.skipped_packages: list = []
        self.asc_files: list = []
        self.progress_message: str = f'{self.cyan}Installing{self.endc}'

        self.option_for_reinstall: bool = self.utils.is_option(
            ('-r', '--reinstall'), flags)

        self.option_for_skip_installed: bool = self.utils.is_option(
            ('-k', '--skip-installed'), flags)

        self.slackbuilds: list = self.utils.apply_package_pattern(data, slackbuilds)

        self.repo_tag: str = self.repos.repositories[repository]['repo_tag']
        self.tar_suffix: str = self.repos.repositories[repository]['tar_suffix']

    def execute(self) -> None:
        self.creating_dependencies_list()
        self.choose_package_dependencies()
        self.add_dependencies_to_install_order()
        self.clean_the_main_slackbuilds()
        self.add_main_packages_to_install_order()
        self.check_for_skipped()
        self.view_slackbuilds_before_build()

        start: float = time.time()
        self.view.skipping_packages(self.skipped_packages)
        self.prepare_slackbuilds_for_build()
        self.download_the_sources()
        self.set_progress_message()
        self.build_and_install_the_slackbuilds()
        elapsed_time: float = time.time() - start

        self.utils.finished_time(elapsed_time)

    def creating_dependencies_list(self) -> None:
        print('\rResolving dependencies... ', end='')
        for slackbuild in self.slackbuilds:
            dependencies: tuple = Requires(self.data, slackbuild, self.flags).resolve()

            for dependency in dependencies:
                self.dependencies.append(dependency)

        self.dependencies: list = list(OrderedDict.fromkeys(self.dependencies))
        print(f'{self.bgreen}{self.ascii.done}{self.endc}')

    def add_dependencies_to_install_order(self) -> None:
        self.install_order.extend(self.dependencies)

    def clean_the_main_slackbuilds(self) -> None:
        for dep in self.dependencies:
            if dep in self.slackbuilds:
                self.slackbuilds.remove(dep)

    def add_main_packages_to_install_order(self) -> None:
        self.install_order.extend(self.slackbuilds)

    def check_for_skipped(self):
        if self.option_for_skip_installed:
            for name in self.install_order:
                installed: str = self.utils.is_package_installed(name)
                if installed:
                    self.skipped_packages.append(name)

        # Remove packages from skipped packages.
        self.install_order: list = [pkg for pkg in self.install_order if pkg not in self.skipped_packages]

    def view_slackbuilds_before_build(self) -> None:
        if self.mode == 'build':
            self.view.build_packages(self.slackbuilds, self.dependencies)
        else:
            self.view.install_upgrade_packages(self.slackbuilds, self.dependencies, self.mode)

        self.view.question()

    def prepare_slackbuilds_for_build(self) -> None:
        if self.install_order:
            print(f'\rPrepare sources for downloading... ', end='')
            for sbo in self.install_order:
                build_path: Path = Path(self.build_path, sbo)

                self.utils.remove_folder_if_exists(build_path)
                location: str = self.data[sbo]['location']
                slackbuild: Path = Path(self.build_path, sbo, f'{sbo}.SlackBuild')

                # Copy slackbuilds to the build folder.
                path_repo_package: Path = Path(self.repos.repositories[self.repository]['path'], location, sbo)
                shutil.copytree(path_repo_package, build_path)

                os.chmod(slackbuild, 0o775)

                if self.os_arch == 'x86_64' and self.data[sbo]['download64']:
                    sources: tuple = self.data[sbo]['download64']
                else:
                    sources: tuple = self.data[sbo]['download']

                if self.gpg_verification and self.repository == self.repos.sbo_repo_name:
                    asc_file: Path = Path(self.repos.repositories_path, self.repos.sbo_repo_name,
                                          location, f'{sbo}{self.tar_suffix}.asc')
                    self.asc_files.append(asc_file)

                self.sources[sbo] = (sources, Path(self.build_path, sbo))

            print(f'{self.bgreen}{self.ascii.done}{self.endc}')

    def download_the_sources(self) -> None:
        if self.sources:
            print(f'Started to download total ({self.cyan}{len(self.sources)}{self.endc}) sources:\n')
            self.download.download(self.sources)
            print()

            self.checksum_downloaded_sources()

    def checksum_downloaded_sources(self) -> None:
        for sbo in self.install_order:
            path: Path = Path(self.build_path, sbo)

            if self.os_arch == 'x86_64' and self.data[sbo]['md5sum64']:
                checksums: list = self.data[sbo]['md5sum64']
                sources: list = self.data[sbo]['download64']
            else:
                checksums: list = self.data[sbo]['md5sum']
                sources: list = self.data[sbo]['download']

            for source, checksum in zip(sources, checksums):
                self.check_md5.md5sum(path, source, checksum)

    def build_and_install_the_slackbuilds(self) -> None:
        # Remove old slpkg.log file.
        if self.slpkg_log_file.is_file():
            self.slpkg_log_file.unlink()

        if self.gpg_verification and self.repository == self.repos.sbo_repo_name:
            self.gpg.verify(self.asc_files)

        if self.install_order:
            print(f'Started the processing of ({self.cyan}{len(self.install_order)}{self.endc}) packages:\n')

            for sbo in self.install_order:
                self.patch_slackbuild_tag(sbo)
                self.build_the_script(self.build_path, sbo)

                if self.mode in ('install', 'upgrade'):
                    self.install_package(sbo)

    def patch_slackbuild_tag(self, sbo: str) -> None:
        sbo_script: Path = Path(self.build_path, sbo, f'{sbo}.SlackBuild')
        if sbo_script.is_file() and self.repo_tag:
            lines: list = self.utils.read_text_file(sbo_script)

            with open(sbo_script, 'w') as script:
                for line in lines:
                    if line.startswith('TAG=$'):
                        line: str = f'TAG=${{TAG:-{self.repo_tag}}}\n'
                    script.write(line)

    def install_package(self, name: str) -> None:
        package: str = self.find_package_for_install(name)

        command: str = f'{self.installpkg} {self.tmp_path}/{package}'
        if self.option_for_reinstall:
            command: str = f'{self.reinstall} {self.tmp_path}/{package}'

        self.multi_proc.process_and_log(command, package, self.progress_message)
        self.write_deps_log(name)

    def write_deps_log(self, name: str) -> None:
        deps: dict = {}
        deps_logs: dict = {}
        installed_requires: list = []
        requires: tuple = Requires(self.data, name, self.flags).resolve()
        # Verify for installation.
        for req in requires:
            if self.utils.is_package_installed(req):
                installed_requires.append(req)

        deps[name] = installed_requires
        if self.deps_log_file.is_file():
            deps_logs: dict = self.utils.read_json_file(self.deps_log_file)
            deps_logs.update(deps)
        self.deps_log_file.write_text(json.dumps(deps_logs, indent=4))

    def find_package_for_install(self, name: str) -> str:
        version: str = self.data[name]['version']
        pattern: str = f'{name}-{version}*{self.repo_tag}*'
        packages: list = [file.name for file in self.tmp_path.glob(pattern)]
        try:
            return max(packages)
        except ValueError:
            self.toml_errors.raise_error_message(f"Package '{name}' not found for install", exit_status=20)

    def build_the_script(self, path: Path, name: str) -> None:
        self.set_makeflags()
        folder: Path = Path(path, name)
        filename: str = f'{name}.SlackBuild'
        command: str = f'{folder}/./{filename}'
        self.utils.change_owner_privileges(folder)
        progress_message: str = f'{self.red}Building{self.endc}'
        self.multi_proc.process_and_log(command, filename, progress_message)

    def set_progress_message(self) -> None:
        if self.mode == 'upgrade' or self.option_for_reinstall:
            self.progress_message: str = f'{self.violet}Upgrading{self.endc}'

    def set_makeflags(self) -> None:
        os.environ['MAKEFLAGS'] = f'-j {self.makeflags}'

    def choose_package_dependencies(self) -> None:
        if self.dependencies and self.dialog:
            height: int = 10
            width: int = 70
            list_height: int = 0
            choices: list = []
            title: str = ' Choose dependencies you want to install '

            for package in self.dependencies:
                status: bool = True
                repo_ver: str = self.data[package]['version']
                description: str = self.data[package]['description']
                help_text: str = f'Description: {description}'
                installed: str = self.utils.is_package_installed(package)
                upgradeable: bool = self.upgrade.is_package_upgradeable(installed)

                if installed:
                    status: bool = False

                if self.mode == 'upgrade' and upgradeable:
                    status: bool = True

                if self.option_for_reinstall:
                    status: bool = True

                choices.extend(
                    [(package, repo_ver, status, help_text)]
                )
            text: str = f'There are {len(choices)} dependencies:'

            code, self.dependencies = self.dialogbox.checklist(text, title, height, width, list_height, choices)

            os.system('clear')
