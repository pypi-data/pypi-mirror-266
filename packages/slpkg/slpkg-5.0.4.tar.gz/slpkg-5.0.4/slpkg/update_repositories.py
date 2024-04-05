#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pathlib import Path

from slpkg.configs import Configs
from slpkg.views.views import View
from slpkg.utilities import Utilities
from slpkg.downloader import Downloader
from slpkg.install_data import InstallData
from slpkg.repositories import Repositories
from slpkg.multi_process import MultiProcess
from slpkg.check_updates import CheckUpdates
from slpkg.sbos.sbo_generate import SBoGenerate


class UpdateRepositories(Configs):
    """ Updates the local repositories and install the data
        into the database.
    """

    def __init__(self, flags: list, repository: str):
        super(Configs, self).__init__()
        self.flags: list = flags
        self.repository: str = repository

        self.view = View(flags)
        self.multi_process = MultiProcess(flags)
        self.repos = Repositories()
        self.utils = Utilities()
        self.data = InstallData()
        self.generate = SBoGenerate()
        self.check_updates = CheckUpdates(flags, repository)
        self.download = Downloader(flags)

        self.repos_for_update: dict = {}
        self.lftp_extra_options: str = ' '

        self.option_for_repository: bool = self.utils.is_option(
            ('-o', '--repository='), flags)

    def repositories(self) -> None:
        self.repos_for_update: dict = self.check_updates.updates()
        self.update_the_repositories()

    def update_the_repositories(self) -> None:
        if not any(list(self.repos_for_update.values())):
            self.view.question(message='Do you want to force update?')
            # Force update the repositories.
            for repo in self.repos_for_update:
                self.repos_for_update[repo] = True

        repositories: dict = {
            self.repos.sbo_repo_name: self.sbo_repository,
            self.repos.ponce_repo_name: self.ponce_repository,
            self.repos.slack_repo_name: self.slack_repository,
            self.repos.slack_extra_repo_name: self.slack_extra_repository,
            self.repos.slack_patches_repo_name: self.slack_patches_repository,
            self.repos.alien_repo_name: self.alien_repository,
            self.repos.multilib_repo_name: self.multilib_repository,
            self.repos.restricted_repo_name: self.restricted_repository,
            self.repos.gnome_repo_name: self.gnome_repository,
            self.repos.msb_repo_name: self.msb_repository,
            self.repos.csb_repo_name: self.csb_repository,
            self.repos.conraid_repo_name: self.conraid_repository,
            self.repos.slackdce_repo_name: self.slackdce_repository,
            self.repos.slackonly_repo_name: self.slackonly_repository,
            self.repos.salixos_repo_name: self.salixos_repository,
            self.repos.salixos_extra_repo_name: self.salixos_extra_repository,
            self.repos.salixos_patches_repo_name: self.salixos_patches_repository,
            self.repos.slackel_repo_name: self.slackel_repository,
            self.repos.slint_repo_name: self.slint_repository,
            self.repos.pprkut_repo_name: self.pprkut_repository
        }

        if self.option_for_repository:
            self.view_downloading_message(self.repository)
            self.set_lftp_extra_options(self.repository)
            repositories[self.repository]()
        else:
            for repo, update in self.repos_for_update.items():
                if update:
                    self.view_downloading_message(repo)
                    self.set_lftp_extra_options(repo)
                    repositories[repo]()

    def view_downloading_message(self, repo: str) -> None:
        print(f"Syncing with the repository '{self.green}{repo}{self.endc}', please wait...\n")

    def set_lftp_extra_options(self, repository: str) -> None:
        if self.lftp_mirror_extra_options.get(repository):
            self.lftp_extra_options: str = f' {self.lftp_mirror_extra_options[repository]} '

    def slack_repository(self) -> None:
        urls: dict = {}
        self.utils.create_directory(self.repos.slack_repo_path)

        self.utils.remove_file_if_exists(self.repos.slack_repo_path, self.repos.slack_repo_packages)
        self.utils.remove_file_if_exists(self.repos.slack_repo_path, self.repos.slack_repo_changelog)
        self.utils.remove_file_if_exists(self.repos.slack_repo_path, self.repos.slack_repo_checksums)

        if self.repos.slack_repo_local[0].startswith('file'):
            lftp_command: str = (
                f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}{self.repos.slack_repo_mirror[0]} '
                f'{self.repos.slack_repo_path}'
            )
            self.multi_process.process(lftp_command)
        else:
            changelog: str = f'{self.repos.slack_repo_mirror[0]}{self.repos.slack_repo_changelog}'
            packages: str = f'{self.repos.slack_repo_mirror[0]}{self.repos.slack_repo_packages}'
            checksums: str = f'{self.repos.slack_repo_mirror[0]}{self.repos.slack_repo_checksums}'

            urls[self.repos.slack_repo_name] = ((changelog, packages, checksums), self.repos.slack_repo_path)

            self.download.download(urls)

        self.data.install_slack_data()

    def slack_extra_repository(self) -> None:
        urls: dict = {}
        self.utils.create_directory(self.repos.slack_extra_repo_path)

        self.utils.remove_file_if_exists(self.repos.slack_extra_repo_path, self.repos.slack_extra_repo_changelog)
        self.utils.remove_file_if_exists(self.repos.slack_extra_repo_path, self.repos.slack_extra_repo_packages)
        self.utils.remove_file_if_exists(self.repos.slack_extra_repo_path, self.repos.slack_extra_repo_checksums)

        changelog: str = f'{self.repos.slack_extra_repo_mirror[0]}{self.repos.slack_extra_repo_changelog}'

        if self.repos.slack_extra_repo_local[0].startswith('file'):
            urls[self.repos.slack_extra_repo_name] = ((changelog,), self.repos.slack_extra_repo_path)
            lftp_command: str = (
                f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}'
                f'{"".join(self.repos.slack_extra_repo_mirror)} {self.repos.slack_extra_repo_path}'
            )
            self.multi_process.process(lftp_command)
        else:
            packages: str = f'{"".join(self.repos.slack_extra_repo_mirror)}{self.repos.slack_extra_repo_packages}'
            checksums: str = f'{"".join(self.repos.slack_extra_repo_mirror)}{self.repos.slack_extra_repo_checksums}'
            urls[self.repos.slack_extra_repo_name] = ((changelog, packages, checksums),
                                                      self.repos.slack_extra_repo_path)

        self.download.download(urls)

        self.data.install_slack_extra_data()

    def slack_patches_repository(self) -> None:
        urls: dict = {}
        self.utils.create_directory(self.repos.slack_patches_repo_path)

        self.utils.remove_file_if_exists(self.repos.slack_patches_repo_path,
                                         self.repos.slack_patches_repo_changelog)
        self.utils.remove_file_if_exists(self.repos.slack_patches_repo_path,
                                         self.repos.slack_patches_repo_packages)
        self.utils.remove_file_if_exists(self.repos.slack_patches_repo_path,
                                         self.repos.slack_patches_repo_checksums)

        changelog: str = f'{self.repos.slack_patches_repo_mirror[0]}{self.repos.slack_patches_repo_changelog}'

        if self.repos.slack_patches_repo_local[0].startswith('file'):
            urls[self.repos.slack_patches_repo_name] = ((changelog,), self.repos.slack_patches_repo_path)
            lftp_command: str = (
                f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}'
                f'{"".join(self.repos.slack_patches_repo_mirror)} {self.repos.slack_patches_repo_path}'
            )
            self.multi_process.process(lftp_command)
        else:
            packages: str = (f'{"".join(self.repos.slack_patches_repo_mirror)}'
                             f'{self.repos.slack_patches_repo_packages}')
            checksums: str = (f'{"".join(self.repos.slack_patches_repo_mirror)}'
                              f'{self.repos.slack_patches_repo_checksums}')

            urls[self.repos.slack_patches_repo_name] = ((changelog, packages, checksums),
                                                        self.repos.slack_patches_repo_path)

        self.download.download(urls)

        self.data.install_slack_patches_data()

    def alien_repository(self) -> None:
        urls: dict = {}
        self.utils.create_directory(self.repos.alien_repo_path)

        self.utils.remove_file_if_exists(self.repos.alien_repo_path, self.repos.alien_repo_changelog)
        self.utils.remove_file_if_exists(self.repos.alien_repo_path, self.repos.alien_repo_packages)
        self.utils.remove_file_if_exists(self.repos.alien_repo_path, self.repos.alien_repo_checksums)

        changelog: str = f'{self.repos.alien_repo_mirror[0]}{self.repos.alien_repo_changelog}'

        if self.repos.alien_repo_local[0].startswith('file'):
            urls[self.repos.alien_repo_name] = ((changelog,), self.repos.alien_repo_path)
            lftp_command: str = (
                f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}{"".join(self.repos.alien_repo_mirror)} '
                f'{self.repos.alien_repo_path}'
            )
            self.multi_process.process(lftp_command)
        else:
            packages: str = f'{"".join(self.repos.alien_repo_mirror)}{self.repos.alien_repo_packages}'
            checksums: str = f'{"".join(self.repos.alien_repo_mirror)}{self.repos.alien_repo_checksums}'

            urls[self.repos.alien_repo_name] = ((changelog, packages, checksums),
                                                self.repos.alien_repo_path)

        self.download.download(urls)

        self.data.install_alien_data()

    def multilib_repository(self) -> None:
        urls: dict = {}
        self.utils.create_directory(self.repos.multilib_repo_path)

        self.utils.remove_file_if_exists(self.repos.multilib_repo_path, self.repos.multilib_repo_changelog)
        self.utils.remove_file_if_exists(self.repos.multilib_repo_path, self.repos.multilib_repo_packages)
        self.utils.remove_file_if_exists(self.repos.multilib_repo_path, self.repos.multilib_repo_checksums)

        changelog: str = f'{self.repos.multilib_repo_mirror[0]}{self.repos.multilib_repo_changelog}'

        if self.repos.multilib_repo_local[0].startswith('file'):
            urls[self.repos.multilib_repo_name] = ((changelog,), self.repos.multilib_repo_path)
            lftp_command: str = (
                f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}{"".join(self.repos.multilib_repo_mirror)} '
                f'{self.repos.multilib_repo_path}'
            )
            self.multi_process.process(lftp_command)
        else:
            packages: str = f'{"".join(self.repos.multilib_repo_mirror)}{self.repos.multilib_repo_packages}'
            checksums: str = f'{"".join(self.repos.multilib_repo_mirror)}{self.repos.multilib_repo_checksums}'

            urls[self.repos.multilib_repo_name] = ((changelog, packages, checksums),
                                                   self.repos.multilib_repo_path)

        self.download.download(urls)

        self.data.install_multilib_data()

    def restricted_repository(self) -> None:
        urls: dict = {}
        self.utils.create_directory(self.repos.restricted_repo_path)

        self.utils.remove_file_if_exists(self.repos.restricted_repo_path, self.repos.restricted_repo_changelog)
        self.utils.remove_file_if_exists(self.repos.restricted_repo_path, self.repos.restricted_repo_packages)
        self.utils.remove_file_if_exists(self.repos.restricted_repo_path, self.repos.restricted_repo_checksums)

        changelog: str = f'{self.repos.restricted_repo_mirror[0]}{self.repos.restricted_repo_changelog}'

        if self.repos.restricted_repo_local[0].startswith('file'):
            urls[self.repos.restricted_repo_name] = ((changelog,), self.repos.restricted_repo_path)
            lftp_command: str = (
                f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}'
                f'{"".join(self.repos.restricted_repo_mirror)} {self.repos.restricted_repo_path}'
            )
            self.multi_process.process(lftp_command)
        else:
            packages: str = f'{"".join(self.repos.restricted_repo_mirror)}{self.repos.restricted_repo_packages}'
            checksums: str = f'{"".join(self.repos.restricted_repo_mirror)}{self.repos.restricted_repo_checksums}'

            urls[self.repos.restricted_repo_name] = ((changelog, packages, checksums),
                                                     self.repos.restricted_repo_path)

        self.download.download(urls)

        self.data.install_restricted_data()

    def gnome_repository(self) -> None:
        urls: dict = {}
        self.utils.create_directory(self.repos.gnome_repo_path)

        self.utils.remove_file_if_exists(self.repos.gnome_repo_path, self.repos.gnome_repo_changelog)
        self.utils.remove_file_if_exists(self.repos.gnome_repo_path, self.repos.gnome_repo_packages)
        self.utils.remove_file_if_exists(self.repos.gnome_repo_path, self.repos.gnome_repo_checksums)

        if self.repos.gnome_repo_local[0].startswith('file'):
            lftp_command: str = (
                f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}{self.repos.gnome_repo_mirror[0]} '
                f'{self.repos.gnome_repo_path}'
            )
            self.multi_process.process(lftp_command)
        else:
            changelog: str = f'{self.repos.gnome_repo_mirror[0]}{self.repos.gnome_repo_changelog}'
            packages: str = f'{self.repos.gnome_repo_mirror[0]}{self.repos.gnome_repo_packages}'
            checksums: str = f'{self.repos.gnome_repo_mirror[0]}{self.repos.gnome_repo_checksums}'

            urls[self.repos.gnome_repo_name] = ((changelog, packages, checksums), self.repos.gnome_repo_path)

            self.download.download(urls)

        self.data.install_gnome_data()

    def msb_repository(self) -> None:
        urls: dict = {}
        self.utils.create_directory(self.repos.msb_repo_path)

        self.utils.remove_file_if_exists(self.repos.msb_repo_path, self.repos.msb_repo_changelog)
        self.utils.remove_file_if_exists(self.repos.msb_repo_path, self.repos.msb_repo_packages)
        self.utils.remove_file_if_exists(self.repos.msb_repo_path, self.repos.msb_repo_checksums)

        changelog: str = f'{self.repos.msb_repo_mirror[0]}{self.repos.msb_repo_changelog}'

        if self.repos.msb_repo_local[0].startswith('file'):
            urls[self.repos.msb_repo_name] = ((changelog,), self.repos.msb_repo_path)
            lftp_command: str = (
                f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}{"".join(self.repos.msb_repo_mirror)} '
                f'{self.repos.msb_repo_path}'
            )
            self.multi_process.process(lftp_command)
        else:
            packages: str = f'{"".join(self.repos.msb_repo_mirror)}{self.repos.msb_repo_packages}'
            checksums: str = f'{"".join(self.repos.msb_repo_mirror)}{self.repos.msb_repo_checksums}'

            urls[self.repos.msb_repo_name] = ((changelog, packages, checksums), self.repos.msb_repo_path)

        self.download.download(urls)

        self.data.install_msb_data()

    def csb_repository(self) -> None:
        urls: dict = {}
        self.utils.create_directory(self.repos.csb_repo_path)

        self.utils.remove_file_if_exists(self.repos.csb_repo_path, self.repos.csb_repo_packages)
        self.utils.remove_file_if_exists(self.repos.csb_repo_path, self.repos.csb_repo_changelog)
        self.utils.remove_file_if_exists(self.repos.csb_repo_path, self.repos.csb_repo_checksums)

        if self.repos.csb_repo_local[0].startswith('file'):
            lftp_command: str = (
                f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}{"".join(self.repos.csb_repo_mirror)} '
                f'{self.repos.csb_repo_path}'
            )
            self.multi_process.process(lftp_command)
        else:
            changelog: str = f'{"".join(self.repos.csb_repo_mirror)}{self.repos.csb_repo_changelog}'
            packages: str = f'{"".join(self.repos.csb_repo_mirror)}{self.repos.csb_repo_packages}'
            checksums: str = f'{"".join(self.repos.csb_repo_mirror)}{self.repos.csb_repo_checksums}'

            urls[self.repos.csb_repo_name] = ((changelog, packages, checksums), self.repos.csb_repo_path)

            self.download.download(urls)

        self.data.install_csb_data()

    def conraid_repository(self) -> None:
        urls: dict = {}
        self.utils.create_directory(self.repos.conraid_repo_path)

        self.utils.remove_file_if_exists(self.repos.conraid_repo_path, self.repos.conraid_repo_changelog)
        self.utils.remove_file_if_exists(self.repos.conraid_repo_path, self.repos.conraid_repo_packages)
        self.utils.remove_file_if_exists(self.repos.conraid_repo_path, self.repos.conraid_repo_checksums)

        if self.repos.conraid_repo_local[0].startswith('file'):
            lftp_command: str = (
                f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}{self.repos.conraid_repo_mirror[0]} '
                f'{self.repos.conraid_repo_path}'
            )
            self.multi_process.process(lftp_command)
        else:
            changelog: str = f'{self.repos.conraid_repo_mirror[0]}{self.repos.conraid_repo_changelog}'
            packages: str = f'{self.repos.conraid_repo_mirror[0]}{self.repos.conraid_repo_packages}'
            checksums: str = f'{self.repos.conraid_repo_mirror[0]}{self.repos.conraid_repo_checksums}'

            urls[self.repos.conraid_repo_name] = ((changelog, packages, checksums), self.repos.conraid_repo_path)

            self.download.download(urls)

        self.data.install_conraid_data()

    def slackdce_repository(self) -> None:
        urls: dict = {}
        self.utils.create_directory(self.repos.slackdce_repo_path)

        self.utils.remove_file_if_exists(self.repos.slackdce_repo_path, self.repos.slackdce_repo_changelog)
        self.utils.remove_file_if_exists(self.repos.slackdce_repo_path, self.repos.slackdce_repo_packages)
        self.utils.remove_file_if_exists(self.repos.slackdce_repo_path, self.repos.slackdce_repo_checksums)

        if self.repos.slackdce_repo_local[0].startswith('file'):
            lftp_command: str = (
                f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}{self.repos.slackdce_repo_mirror[0]} '
                f'{self.repos.slackdce_repo_path}'
            )
            self.multi_process.process(lftp_command)
        else:
            changelog: str = f'{self.repos.slackdce_repo_mirror[0]}{self.repos.slackdce_repo_changelog}'
            packages: str = f'{self.repos.slackdce_repo_mirror[0]}{self.repos.slackdce_repo_packages}'
            checksums: str = f'{self.repos.slackdce_repo_mirror[0]}{self.repos.slackdce_repo_checksums}'

            urls[self.repos.slackdce_repo_name] = ((changelog, packages, checksums), self.repos.slackdce_repo_path)

            self.download.download(urls)

        self.data.install_slackdce_data()

    def slackonly_repository(self) -> None:
        urls: dict = {}
        self.utils.create_directory(self.repos.slackonly_repo_path)

        self.utils.remove_file_if_exists(self.repos.slackonly_repo_path, self.repos.slackonly_repo_changelog)
        self.utils.remove_file_if_exists(self.repos.slackonly_repo_path, self.repos.slackonly_repo_packages)
        self.utils.remove_file_if_exists(self.repos.slackonly_repo_path, self.repos.slackonly_repo_checksums)

        if self.repos.slackonly_repo_local[0].startswith('file'):
            lftp_command: str = (
                f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}{self.repos.slackonly_repo_mirror[0]} '
                f'{self.repos.slackonly_repo_path}'
            )
            self.multi_process.process(lftp_command)
        else:
            changelog: str = f'{self.repos.slackonly_repo_mirror[0]}{self.repos.slackonly_repo_changelog}'
            packages: str = f'{self.repos.slackonly_repo_mirror[0]}{self.repos.slackonly_repo_packages}'
            checksums: str = f'{self.repos.slackonly_repo_mirror[0]}{self.repos.slackonly_repo_checksums}'

            urls[self.repos.slackonly_repo_name] = ((changelog, packages, checksums),
                                                    self.repos.slackonly_repo_path)

            self.download.download(urls)

        self.data.install_slackonly_data()

    def salixos_repository(self) -> None:
        urls: dict = {}
        self.utils.create_directory(self.repos.salixos_repo_path)

        self.utils.remove_file_if_exists(self.repos.salixos_repo_path, self.repos.salixos_repo_changelog)
        self.utils.remove_file_if_exists(self.repos.salixos_repo_path, self.repos.salixos_repo_packages)
        self.utils.remove_file_if_exists(self.repos.salixos_repo_path, self.repos.salixos_repo_checksums)

        if self.repos.salixos_repo_local[0].startswith('file'):
            lftp_command: str = (
                f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}{self.repos.salixos_repo_mirror[0]} '
                f'{self.repos.salixos_repo_path}'
            )
            self.multi_process.process(lftp_command)
        else:
            changelog: str = f'{self.repos.salixos_repo_mirror[0]}{self.repos.salixos_repo_changelog}'
            packages: str = f'{self.repos.salixos_repo_mirror[0]}{self.repos.salixos_repo_packages}'
            checksums: str = f'{self.repos.salixos_repo_mirror[0]}{self.repos.salixos_repo_checksums}'

            urls[self.repos.salixos_repo_name] = ((changelog, packages, checksums), self.repos.salixos_repo_path)

            self.download.download(urls)

        self.data.install_salixos_data()

    def salixos_extra_repository(self) -> None:
        urls: dict = {}
        self.utils.create_directory(self.repos.salixos_extra_repo_path)

        self.utils.remove_file_if_exists(self.repos.salixos_extra_repo_path,
                                         self.repos.salixos_extra_repo_changelog)
        self.utils.remove_file_if_exists(self.repos.salixos_extra_repo_path,
                                         self.repos.salixos_extra_repo_packages)
        self.utils.remove_file_if_exists(self.repos.salixos_extra_repo_path,
                                         self.repos.salixos_extra_repo_checksums)

        changelog: str = f'{self.repos.salixos_extra_repo_mirror[0]}{self.repos.salixos_extra_repo_changelog}'

        if self.repos.salixos_extra_repo_local[0].startswith('file'):
            urls[self.repos.salixos_extra_repo_name] = ((changelog,), self.repos.salixos_extra_repo_path)
            lftp_command: str = (
                f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}'
                f'{"".join(self.repos.salixos_extra_repo_mirror)} {self.repos.salixos_extra_repo_path}'
            )
            self.multi_process.process(lftp_command)
        else:
            packages: str = f'{"".join(self.repos.salixos_extra_repo_mirror)}' \
                            f'{self.repos.salixos_extra_repo_packages}'
            checksums: str = (f'{"".join(self.repos.salixos_extra_repo_mirror)}'
                              f'{self.repos.salixos_extra_repo_checksums}')

            urls[self.repos.salixos_extra_repo_name] = ((changelog, packages, checksums),
                                                        self.repos.salixos_extra_repo_path)

        self.download.download(urls)

        self.data.install_salixos_extra_data()

    def salixos_patches_repository(self) -> None:
        urls: dict = {}
        self.utils.create_directory(self.repos.slack_patches_repo_path)

        self.utils.remove_file_if_exists(self.repos.salixos_patches_repo_path,
                                         self.repos.salixos_patches_repo_changelog)
        self.utils.remove_file_if_exists(self.repos.salixos_patches_repo_path,
                                         self.repos.salixos_patches_repo_packages)
        self.utils.remove_file_if_exists(self.repos.salixos_patches_repo_path,
                                         self.repos.salixos_patches_repo_checksums)

        changelog: str = f'{self.repos.salixos_patches_repo_mirror[0]}{self.repos.salixos_patches_repo_changelog}'

        if self.repos.salixos_patches_repo_local[0].startswith('file'):
            urls[self.repos.salixos_patches_repo_name] = ((changelog,), self.repos.salixos_patches_repo_path)
            lftp_command: str = (
                f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}'
                f'{"".join(self.repos.salixos_patches_repo_mirror)} {self.repos.salixos_patches_repo_path}'
            )
            self.multi_process.process(lftp_command)
        else:
            packages: str = (f'{"".join(self.repos.salixos_patches_repo_mirror)}'
                             f'{self.repos.salixos_patches_repo_packages}')
            checksums: str = (f'{"".join(self.repos.salixos_patches_repo_mirror)}'
                              f'{self.repos.salixos_patches_repo_checksums}')

            urls[self.repos.salixos_patches_repo_name] = ((changelog, packages, checksums),
                                                          self.repos.salixos_patches_repo_path)

        self.download.download(urls)

        self.data.install_salixos_patches_data()

    def slackel_repository(self) -> None:
        urls: dict = {}
        self.utils.create_directory(self.repos.slackel_repo_path)

        self.utils.remove_file_if_exists(self.repos.slackel_repo_path, self.repos.slackel_repo_changelog)
        self.utils.remove_file_if_exists(self.repos.slackel_repo_path, self.repos.slackel_repo_packages)
        self.utils.remove_file_if_exists(self.repos.slackel_repo_path, self.repos.slackel_repo_checksums)

        if self.repos.slackel_repo_local[0].startswith('file'):
            lftp_command: str = (
                f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}{self.repos.slackel_repo_mirror[0]} '
                f'{self.repos.slackel_repo_path}'
            )
            self.multi_process.process(lftp_command)
        else:
            changelog: str = f'{self.repos.slackel_repo_mirror[0]}{self.repos.slackel_repo_changelog}'
            packages: str = f'{self.repos.slackel_repo_mirror[0]}{self.repos.slackel_repo_packages}'
            checksums: str = f'{self.repos.slackel_repo_mirror[0]}{self.repos.slackel_repo_checksums}'

            urls[self.repos.slackel_repo_name] = ((changelog, packages, checksums), self.repos.slackel_repo_path)

            self.download.download(urls)

        self.data.install_slackel_data()

    def slint_repository(self) -> None:
        urls: dict = {}
        self.utils.create_directory(self.repos.slint_repo_path)

        self.utils.remove_file_if_exists(self.repos.slint_repo_path, self.repos.slint_repo_changelog)
        self.utils.remove_file_if_exists(self.repos.slint_repo_path, self.repos.slint_repo_packages)
        self.utils.remove_file_if_exists(self.repos.slint_repo_path, self.repos.slint_repo_checksums)

        if self.repos.slint_repo_local[0].startswith('file'):
            lftp_command: str = (
                f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}{self.repos.slint_repo_mirror[0]} '
                f'{self.repos.slint_repo_path}'
            )
            self.multi_process.process(lftp_command)
        else:
            changelog: str = f'{self.repos.slint_repo_mirror[0]}{self.repos.slint_repo_changelog}'
            packages: str = f'{self.repos.slint_repo_mirror[0]}{self.repos.slint_repo_packages}'
            checksums: str = f'{self.repos.slint_repo_mirror[0]}{self.repos.slint_repo_checksums}'

            urls[self.repos.slint_repo_name] = ((changelog, packages, checksums), self.repos.slint_repo_path)

            self.download.download(urls)

        self.data.install_slint_data()

    def pprkut_repository(self) -> None:
        urls: dict = {}
        self.utils.create_directory(self.repos.pprkut_repo_path)

        self.utils.remove_file_if_exists(self.repos.pprkut_repo_path, self.repos.pprkut_repo_changelog)
        self.utils.remove_file_if_exists(self.repos.pprkut_repo_path, self.repos.pprkut_repo_packages)
        self.utils.remove_file_if_exists(self.repos.pprkut_repo_path, self.repos.pprkut_repo_checksums)

        if self.repos.pprkut_repo_local[0].startswith('file'):
            lftp_command: str = (
                f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}{self.repos.pprkut_repo_mirror[0]} '
                f'{self.repos.pprkut_repo_path}'
            )
            self.multi_process.process(lftp_command)
        else:
            changelog: str = f'{self.repos.pprkut_repo_mirror[0]}{self.repos.pprkut_repo_changelog}'
            packages: str = f'{self.repos.pprkut_repo_mirror[0]}{self.repos.pprkut_repo_packages}'
            checksums: str = f'{self.repos.pprkut_repo_mirror[0]}{self.repos.pprkut_repo_checksums}'

            urls[self.repos.pprkut_repo_name] = ((changelog, packages, checksums), self.repos.pprkut_repo_path)

            self.download.download(urls)

        self.data.install_pprkut_data()

    def ponce_repository(self) -> None:
        """ Update the slackbuild repositories. """
        self.utils.create_directory(self.repos.ponce_repo_path)
        self.utils.remove_file_if_exists(self.repos.ponce_repo_path, self.repos.ponce_repo_slackbuilds)
        self.utils.remove_file_if_exists(self.repos.ponce_repo_path, self.repos.ponce_repo_changelog)

        lftp_command: str = (f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}'
                             f'{self.repos.ponce_repo_mirror[0]} {self.repos.ponce_repo_path}')

        self.multi_process.process(lftp_command)

        # It checks if there is the SLACKBUILDS.TXT file, otherwise going to create it.
        if not Path(self.repos.ponce_repo_path, self.repos.ponce_repo_slackbuilds).is_file():
            self.generate.slackbuild_file(self.repos.ponce_repo_path, self.repos.ponce_repo_slackbuilds)

        self.data.install_ponce_data()

    def sbo_repository(self) -> None:
        self.utils.create_directory(self.repos.sbo_repo_path)
        self.utils.remove_file_if_exists(self.repos.sbo_repo_path, self.repos.sbo_repo_slackbuilds)
        self.utils.remove_file_if_exists(self.repos.sbo_repo_path, self.repos.sbo_repo_changelog)

        lftp_command: str = (f'lftp {self.lftp_mirror_options}{self.lftp_extra_options}'
                             f'{self.repos.sbo_repo_mirror[0]} {self.repos.sbo_repo_path}')

        self.multi_process.process(lftp_command)

        # It checks if there is the SLACKBUILDS.TXT file, otherwise going to create it.
        if not Path(self.repos.sbo_repo_path, self.repos.sbo_repo_slackbuilds).is_file():
            self.generate.slackbuild_file(self.repos.sbo_repo_path, self.repos.sbo_repo_slackbuilds)

        self.data.install_sbo_data()
