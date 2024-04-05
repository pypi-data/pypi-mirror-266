#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import json
from pathlib import Path

from slpkg.configs import Configs
from slpkg.utilities import Utilities
from slpkg.views.asciibox import AsciiBox
from slpkg.repositories import Repositories
from slpkg.multi_process import MultiProcess


class InstallData(Configs):

    def __init__(self):
        super(Configs, self).__init__()
        self.utils = Utilities()
        self.repos = Repositories()
        self.ascii = AsciiBox()
        self.multi_process = MultiProcess()

    def _import_GPG_KEY(self, mirror: str, gpg_key='GPG-KEY') -> None:
        if self.gpg_verification:
            gpg_command: str = 'gpg --quiet --fetch-key'
            GPG_KEY: str = f'{mirror}{gpg_key}'
            self.multi_process.process(f'{gpg_command} {GPG_KEY}')

    def write_last_update(self, changelog_file: Path, repo: str) -> None:
        """ Reads the first date of the changelog file."""
        last_date: str = ''
        last_update_json: dict = {}
        lines: list = self.utils.read_text_file(changelog_file)
        days = ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
        for line in lines:
            if line.startswith(days):
                last_date: str = line.replace('\n', '')
                break

        last_update_json[repo]: dict = last_date
        if self.repos.last_update_json.is_file():
            last_update_json: dict = self.utils.read_json_file(self.repos.last_update_json)
            last_update_json[repo] = last_date

        self.repos.last_update_json.write_text(json.dumps(last_update_json, indent=4))

    def view_done_message(self) -> None:
        print(f'{self.bgreen}{self.ascii.done}{self.endc}\n')

    def install_sbo_data(self) -> None:
        """
        Reads the SLACKBUILDS.TXT FILE and creates a json data file.
        Returns:
            None.
        """
        print(f"Updating the database for '{self.cyan}{self.repos.sbo_repo_name}{self.endc}'... ",
              end='', flush=True)

        self._import_GPG_KEY(mirror='https://www.slackbuilds.org/')

        data: dict = {}
        cache: list = []
        sbo_tags: list = [
            'SLACKBUILD NAME:',
            'SLACKBUILD LOCATION:',
            'SLACKBUILD FILES:',
            'SLACKBUILD VERSION:',
            'SLACKBUILD DOWNLOAD:',
            'SLACKBUILD DOWNLOAD_x86_64:',
            'SLACKBUILD MD5SUM:',
            'SLACKBUILD MD5SUM_x86_64:',
            'SLACKBUILD REQUIRES:',
            'SLACKBUILD SHORT DESCRIPTION:'
        ]

        slackbuilds_txt: list = Path(self.repos.sbo_repo_path,
                                     self.repos.sbo_repo_slackbuilds).read_text(encoding='utf-8').splitlines()

        for i, line in enumerate(slackbuilds_txt, 1):
            for tag in sbo_tags:
                if line.startswith(tag):
                    line = line.replace(tag, '').strip()
                    cache.append(line)

            if (i % 11) == 0:
                build: str = ''
                name: str = cache[0]
                version: str = cache[3]
                location: str = cache[1].split('/')[1]
                requires: list = cache[8].replace('%README%', '').split()

                data[name]: dict = {
                    'location': location,
                    'files': cache[2].split(),
                    'version': version,
                    'download':  cache[4].split(),
                    'download64': cache[5].split(),
                    'md5sum': cache[6].split(),
                    'md5sum64': cache[7].split(),
                    'requires': requires,
                    'description': cache[9]
                }

                arch: str = self.os_arch
                sbo_file: Path = Path(self.repos.sbo_repo_path, location, name, f'{name}.SlackBuild')
                if sbo_file.is_file():
                    slackbuild = sbo_file.read_text(encoding='utf-8').splitlines()
                    for sbo_line in slackbuild:
                        if sbo_line.startswith('BUILD=$'):
                            build: str = ''.join(re.findall(r'\d+', sbo_line))
                        if sbo_line.startswith('ARCH=noarch'):
                            arch: str = 'noarch'

                data[name].update({'arch': arch})
                data[name].update({'build': build})
                package: str = f'{name}-{version}-{arch}-{build}{self.repos.sbo_repo_tag}.tgz'
                data[name].update({'package': package})

                cache: list = []  # reset cache after 11 lines

        path_changelog: Path = Path(self.repos.sbo_repo_path, self.repos.sbo_repo_changelog)
        self.write_last_update(path_changelog, self.repos.sbo_repo_name)

        data_file: Path = Path(self.repos.sbo_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()

    def install_ponce_data(self) -> None:
        """
        Reads the SLACKBUILDS.TXT FILE and creates a json data file.
        Returns:
            None.
        """
        print(f"Updating the database for '{self.cyan}{self.repos.ponce_repo_name}{self.endc}'... ",
              end='', flush=True)
        data: dict = {}
        cache: list = []
        names: list = []
        sbo_tags: list = [
            'SLACKBUILD NAME:',
            'SLACKBUILD LOCATION:',
            'SLACKBUILD FILES:',
            'SLACKBUILD VERSION:',
            'SLACKBUILD DOWNLOAD:',
            'SLACKBUILD DOWNLOAD_x86_64:',
            'SLACKBUILD MD5SUM:',
            'SLACKBUILD MD5SUM_x86_64:',
            'SLACKBUILD REQUIRES:',
            'SLACKBUILD SHORT DESCRIPTION:'
        ]

        slackbuilds_txt: list = Path(self.repos.ponce_repo_path,
                                     self.repos.ponce_repo_slackbuilds).read_text(encoding='utf-8').splitlines()

        for line in slackbuilds_txt:
            if line.startswith(sbo_tags[0]):
                names.append(line.replace(sbo_tags[0], '').strip())

        for i, line in enumerate(slackbuilds_txt, 1):
            for tag in sbo_tags:
                if line.startswith(tag):
                    line = line.replace(tag, '').strip()
                    cache.append(line)

            if (i % 11) == 0:
                build: str = ''
                name: str = cache[0]
                version: str = cache[3]
                location: str = cache[1].split('/')[1]
                requires: list = [item for item in cache[8].split() if item in names]

                data[name]: dict = {
                    'location': location,
                    'files': cache[2].split(),
                    'version': version,
                    'download':  cache[4].split(),
                    'download64': cache[5].split(),
                    'md5sum': cache[6].split(),
                    'md5sum64': cache[7].split(),
                    'requires': requires,
                    'description': cache[9]
                }

                arch: str = self.os_arch
                sbo_file: Path = Path(self.repos.ponce_repo_path, location, name, f'{name}.SlackBuild')
                if sbo_file.is_file():
                    slackbuild = sbo_file.read_text(encoding='utf-8').splitlines()
                    for sbo_line in slackbuild:
                        if sbo_line.startswith('BUILD=$'):
                            build: str = ''.join(re.findall(r'\d+', sbo_line))
                        if sbo_line.startswith('ARCH=noarch'):
                            arch: str = 'noarch'

                data[name].update({'arch': arch})
                data[name].update({'build': build})
                package: str = f'{name}-{version}-{arch}-{build}{self.repos.sbo_repo_tag}.tgz'
                data[name].update({'package': package})

                cache: list = []  # reset cache after 11 lines

        path_changelog: Path = Path(self.repos.ponce_repo_path, self.repos.ponce_repo_changelog)
        self.write_last_update(path_changelog, self.repos.ponce_repo_name)

        data_file: Path = Path(self.repos.ponce_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()

    def install_slack_data(self) -> None:
        """ Install the data for slackware repository. """
        print(f"\nUpdating the database for '{self.cyan}{self.repos.slack_repo_name}{self.endc}'... ",
              end='', flush=True)

        mirror: str = self.repos.slack_repo_mirror[0]
        if self.repos.slack_repo_local[0].startswith('file'):
            mirror: str = self.repos.slack_repo_local[0]

        self._import_GPG_KEY(mirror=mirror)

        data: dict = {}
        checksums_dict: dict = {}
        build: str = ''
        arch: str = ''
        requires: list = []
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE MIRROR:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.slack_repo_path, self.repos.slack_repo_packages)
        path_checksums: Path = Path(self.repos.slack_repo_path, self.repos.slack_repo_checksums)
        packages_txt: list = self.utils.read_text_file(path_packages)
        checksums_md5: list = self.utils.read_text_file(path_checksums)

        for line in checksums_md5:
            line = line.strip()

            if line.endswith(('.txz', '.tgz')):
                file: str = line.split('./')[1].split('/')[-1].strip()
                checksum: str = line.split('./')[0].strip()
                checksums_dict[file] = checksum
        cache: list = []  # init cache

        for line in packages_txt:

            if line.startswith(pkg_tag[0]):
                package = line.replace(pkg_tag[0], '').strip()
                name: str = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build: str = self.utils.split_package(package)['build']
                arch: str = self.utils.split_package(package)['arch']
                cache.append(name)
                cache.append(version)
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')

            if line.startswith(pkg_tag[2]):
                package_location = line.replace(pkg_tag[2], '').strip()
                cache.append(package_location[2:])  # Do not install (.) dot

            if line.startswith(pkg_tag[3]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[4]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[5]):
                package_description = line.replace(pkg_tag[5], '').strip()
                cache.append(package_description)

            if len(cache) == 9:
                data[cache[0]]: dict = {
                    'repo': self.repos.slack_repo_name,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'description': cache[8],
                    'build': build,
                    'arch': arch,
                    'requires': requires,
                    'conflicts': '',
                    'suggests': ''
                }

                cache: list = []  # reset cache

        path_changelog: Path = Path(self.repos.slack_repo_path, self.repos.slack_repo_changelog)
        self.write_last_update(path_changelog, self.repos.slack_repo_name)

        data_file: Path = Path(self.repos.slack_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()

    def install_slack_extra_data(self) -> None:
        """ Install the data for slackware extra repository. """
        print(f"\nUpdating the database for '{self.cyan}{self.repos.slack_extra_repo_name}{self.endc}'... ",
              end='', flush=True)

        mirror: str = self.repos.slack_extra_repo_mirror[0]
        if self.repos.slack_extra_repo_local[0].startswith('file'):
            mirror: str = self.repos.slack_extra_repo_local[0]

        self._import_GPG_KEY(mirror=mirror)

        checksums_dict: dict = {}
        data: dict = {}
        build: str = ''
        arch: str = ''
        requires: list = []
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE MIRROR:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.slack_extra_repo_path, self.repos.slack_extra_repo_packages)
        path_checksums: Path = Path(self.repos.slack_extra_repo_path, self.repos.slack_extra_repo_checksums)
        packages_txt: list = self.utils.read_text_file(path_packages)
        checksums_md5: list = self.utils.read_text_file(path_checksums)

        for line in checksums_md5:
            line = line.strip()

            if line.endswith(('.txz', '.tgz')):
                file: str = line.split('./')[1].split('/')[-1].strip()
                checksum: str = line.split('./')[0].strip()
                checksums_dict[file] = checksum
        cache: list = []  # init cache

        for line in packages_txt:

            if line.startswith(pkg_tag[0]):
                package = line.replace(pkg_tag[0], '').strip()
                name: str = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build: str = self.utils.split_package(package)['build']
                arch: str = self.utils.split_package(package)['arch']
                cache.append(name)
                cache.append(version)
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')

            if line.startswith(pkg_tag[2]):
                package_location = line.replace(pkg_tag[2], '').strip()
                cache.append(package_location[2:])  # Do not install (.) dot

            if line.startswith(pkg_tag[3]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[4]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[5]):
                package_description = line.replace(pkg_tag[5], '').strip()
                cache.append(package_description)

            if len(cache) == 9:
                data[cache[0]]: dict = {
                    'repo': self.repos.slack_extra_repo_name,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'description': cache[8],
                    'build': build,
                    'arch': arch,
                    'requires': requires,
                    'conflicts': '',
                    'suggests': ''
                }

                cache: list = []  # reset cache

        path_changelog: Path = Path(self.repos.slack_extra_repo_path, self.repos.slack_extra_repo_changelog)
        self.write_last_update(path_changelog, self.repos.slack_extra_repo_name)

        data_file: Path = Path(self.repos.slack_extra_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()

    def install_slack_patches_data(self) -> None:
        """ Install the data for slackware patches repository. """
        print(f"\nUpdating the database for '{self.cyan}{self.repos.slack_patches_repo_name}{self.endc}'... ",
              end='', flush=True)

        mirror: str = self.repos.slack_patches_repo_mirror[0]
        if self.repos.slack_patches_repo_local[0].startswith('file'):
            mirror: str = self.repos.slack_patches_repo_local[0]

        self._import_GPG_KEY(mirror=mirror)

        checksums_dict: dict = {}
        data: dict = {}
        build: str = ''
        arch: str = ''
        requires: list = []
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE MIRROR:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.slack_patches_repo_path, self.repos.slack_patches_repo_packages)
        path_checksums: Path = Path(self.repos.slack_patches_repo_path, self.repos.slack_patches_repo_checksums)
        packages_txt: list = self.utils.read_text_file(path_packages)
        checksums_md5: list = self.utils.read_text_file(path_checksums)

        for line in checksums_md5:
            line = line.strip()

            if line.endswith(('.txz', '.tgz')):
                file: str = line.split('./')[1].split('/')[-1].strip()
                checksum: str = line.split('./')[0].strip()
                checksums_dict[file] = checksum
        cache: list = []  # init cache

        for line in packages_txt:

            if line.startswith(pkg_tag[0]):
                package = line.replace(pkg_tag[0], '').strip()
                name: str = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build: str = self.utils.split_package(package)['build']
                arch: str = self.utils.split_package(package)['arch']
                cache.append(name)
                cache.append(version)
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')

            if line.startswith(pkg_tag[2]):
                package_location = line.replace(pkg_tag[2], '').strip()
                cache.append(package_location[2:])  # Do not install (.) dot

            if line.startswith(pkg_tag[3]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[4]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[5]):
                package_description = line.replace(pkg_tag[5], '').strip()
                cache.append(package_description)

            if len(cache) == 9:
                data[cache[0]]: dict = {
                    'repo': self.repos.slack_patches_repo_name,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'description': cache[8],
                    'build': build,
                    'arch': arch,
                    'requires': requires,
                    'conflicts': '',
                    'suggests': ''
                }

                cache: list = []  # reset cache

        path_changelog: Path = Path(self.repos.slack_patches_repo_path, self.repos.slack_patches_repo_changelog)
        self.write_last_update(path_changelog, self.repos.slack_patches_repo_name)

        data_file: Path = Path(self.repos.slack_patches_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()

    def install_alien_data(self) -> None:
        """ Install the data for alien repository. """
        print(f"\nUpdating the database for '{self.cyan}{self.repos.alien_repo_name}{self.endc}'... ",
              end='', flush=True)

        mirror: str = ''.join(self.repos.alien_repo_mirror)
        if self.repos.alien_repo_local[0].startswith('file'):
            mirror: str = ''.join(self.repos.alien_repo_local)

        self._import_GPG_KEY(mirror=mirror)

        checksums_dict: dict = {}
        data: dict = {}
        build: str = ''
        arch: str = ''
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE REQUIRED:',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.alien_repo_path, self.repos.alien_repo_packages)
        path_checksums: Path = Path(self.repos.alien_repo_path, self.repos.alien_repo_checksums)
        packages_txt: list = self.utils.read_text_file(path_packages)
        checksums_md5: list = self.utils.read_text_file(path_checksums)

        for line in checksums_md5:
            line = line.strip()

            if line.endswith(('.txz', '.tgz')):
                file: str = line.split('./')[1].split('/')[-1].strip()
                checksum: str = line.split('./')[0].strip()
                checksums_dict[file] = checksum

        cache: list = []  # init cache

        for line in packages_txt:

            if line.startswith(pkg_tag[0]):
                package = line.replace(pkg_tag[0], '').strip()
                name: str = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build: str = self.utils.split_package(package)['build']
                arch: str = self.utils.split_package(package)['arch']
                cache.append(name)
                cache.append(version)
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')

            if line.startswith(pkg_tag[1]):
                package_location = line.replace(pkg_tag[1], '').strip()
                cache.append(package_location[2:])  # Do not install (.) dot

            if line.startswith(pkg_tag[2]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[3]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[4]):
                required = line.replace(pkg_tag[4], '').strip()
                package_required = required.replace(',', ' ').strip()
                cache.append(package_required)

            if line.startswith(pkg_tag[5]):
                package_description = line.replace(pkg_tag[5], '').strip()
                cache.append(package_description)

            if len(cache) == 10:
                data[cache[0]]: dict = {
                    'repo': self.repos.alien_repo_name,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'requires': cache[8].split(),
                    'description': cache[9],
                    'build': build,
                    'arch': arch,
                    'conflicts': '',
                    'suggests': ''
                }

                cache: list = []  # reset cache

        path_changelog: Path = Path(self.repos.alien_repo_path, self.repos.alien_repo_changelog)
        self.write_last_update(path_changelog, self.repos.alien_repo_name)

        data_file: Path = Path(self.repos.alien_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()

    def install_multilib_data(self) -> None:
        """ Install the data for multilib repository. """
        print(f"\nUpdating the database for '{self.cyan}{self.repos.multilib_repo_name}{self.endc}'... ",
              end='', flush=True)

        mirror: str = ''.join(self.repos.multilib_repo_mirror)
        if self.repos.multilib_repo_local[0].startswith('file'):
            mirror: str = ''.join(self.repos.multilib_repo_local)

        self._import_GPG_KEY(mirror=mirror)

        checksums_dict: dict = {}
        data: dict = {}
        build: str = ''
        arch: str = ''
        requires: list = []
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.multilib_repo_path, self.repos.multilib_repo_packages)
        path_checksums: Path = Path(self.repos.multilib_repo_path, self.repos.multilib_repo_checksums)
        packages_txt: list = self.utils.read_text_file(path_packages)
        checksums_md5: list = self.utils.read_text_file(path_checksums)

        for line in checksums_md5:
            line = line.strip()

            if line.endswith(('.txz', '.tgz')):
                file: str = line.split('./')[1].split('/')[-1].strip()
                checksum: str = line.split('./')[0].strip()
                checksums_dict[file] = checksum

        cache: list = []  # init cache

        for line in packages_txt:

            if line.startswith(pkg_tag[0]):
                package = line.replace(pkg_tag[0], '').strip()
                name: str = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build: str = self.utils.split_package(package)['build']
                arch: str = self.utils.split_package(package)['arch']
                cache.append(name)  # package name
                cache.append(version)  # package version
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')

            if line.startswith(pkg_tag[1]):
                package_location = line.replace(pkg_tag[1], '').strip()
                cache.append(package_location[2:])  # Do not install (./) dot

            if line.startswith(pkg_tag[2]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[3]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[4]):
                package_description = line.replace(pkg_tag[4], '').strip()
                cache.append(package_description)

            if len(cache) == 9:
                data[cache[0]]: dict = {
                    'repo': self.repos.multilib_repo_name,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'description': cache[8],
                    'requires': requires,
                    'build': build,
                    'arch': arch,
                    'conflicts': '',
                    'suggests': ''
                }

                cache: list = []  # reset cache

        path_changelog: Path = Path(self.repos.multilib_repo_path, self.repos.multilib_repo_changelog)
        self.write_last_update(path_changelog, self.repos.multilib_repo_name)

        data_file: Path = Path(self.repos.multilib_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()

    def install_restricted_data(self) -> None:
        """ Install the data for multilib repository. """
        print(f"\nUpdating the database for '{self.cyan}{self.repos.restricted_repo_name}{self.endc}'... ",
              end='', flush=True)

        mirror: str = ''.join(self.repos.restricted_repo_mirror)
        if self.repos.restricted_repo_local[0].startswith('file'):
            mirror: str = ''.join(self.repos.restricted_repo_local)

        self._import_GPG_KEY(mirror=mirror)

        checksums_dict: dict = {}
        data: dict = {}
        build: str = ''
        arch: str = ''
        requires: list = []
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.restricted_repo_path, self.repos.restricted_repo_packages)
        path_checksums: Path = Path(self.repos.restricted_repo_path, self.repos.restricted_repo_checksums)
        packages_txt: list = self.utils.read_text_file(path_packages)
        checksums_md5: list = self.utils.read_text_file(path_checksums)

        for line in checksums_md5:
            line = line.strip()

            if line.endswith(('.txz', '.tgz')):
                file: str = line.split('./')[1].split('/')[-1].strip()
                checksum: str = line.split('./')[0].strip()
                checksums_dict[file] = checksum

        cache: list = []  # init cache

        for line in packages_txt:

            if line.startswith(pkg_tag[0]):
                package = line.replace(pkg_tag[0], '').strip()
                name: str = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build: str = self.utils.split_package(package)['build']
                arch: str = self.utils.split_package(package)['arch']
                cache.append(name)
                cache.append(version)
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')

            if line.startswith(pkg_tag[1]):
                package_location = line.replace(pkg_tag[1], '').strip()
                cache.append(package_location[2:])  # Do not install (./) dot

            if line.startswith(pkg_tag[2]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[3]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[4]):
                package_description = line.replace(pkg_tag[4], '').strip()
                cache.append(package_description)

            if len(cache) == 9:
                data[cache[0]]: dict = {
                    'repo': self.repos.restricted_repo_name,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'description': cache[8],
                    'requires': requires,
                    'build': build,
                    'arch': arch,
                    'conflicts': '',
                    'suggests': ''
                }

                cache: list = []  # reset cache

        path_changelog: Path = Path(self.repos.restricted_repo_path, self.repos.restricted_repo_changelog)
        self.write_last_update(path_changelog, self.repos.restricted_repo_name)

        data_file: Path = Path(self.repos.restricted_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()

    def install_gnome_data(self) -> None:
        """ Install the data for gnome repository. """
        print(f"\nUpdating the database for '{self.cyan}{self.repos.gnome_repo_name}{self.endc}'... ",
              end='', flush=True)

        mirror: str = self.repos.gnome_repo_mirror[0]
        if self.repos.gnome_repo_local[0].startswith('file'):
            mirror: str = self.repos.gnome_repo_local[0]

        self._import_GPG_KEY(mirror=mirror)

        checksums_dict: dict = {}
        data: dict = {}
        build: str = ''
        arch: str = ''
        requires: list = []
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE MIRROR:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.gnome_repo_path, self.repos.gnome_repo_packages)
        path_checksums: Path = Path(self.repos.gnome_repo_path, self.repos.gnome_repo_checksums)
        packages_txt: list = self.utils.read_text_file(path_packages)
        checksums_md5: list = self.utils.read_text_file(path_checksums)

        for line in checksums_md5:
            line = line.strip()

            if line.endswith(('.txz', '.tgz')):
                file: str = line.split('./')[1].split('/')[-1].strip()
                checksum: str = line.split('./')[0].strip()
                checksums_dict[file] = checksum

        cache: list = []  # init cache

        for line in packages_txt:

            if line.startswith(pkg_tag[0]):
                package = line.replace(pkg_tag[0], '').strip()
                name: str = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build: str = self.utils.split_package(package)['build']
                arch: str = self.utils.split_package(package)['arch']
                cache.append(name)
                cache.append(version)
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')

            if line.startswith(pkg_tag[2]):
                package_location = line.replace(pkg_tag[2], '').strip()
                cache.append(package_location[1:])  # Do not install (.) dot

            if line.startswith(pkg_tag[3]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[4]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[5]):
                package_description = line.replace(pkg_tag[5], '').strip()
                cache.append(package_description)

            if len(cache) == 9:
                data[cache[0]]: dict = {
                    'repo': self.repos.gnome_repo_name,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'description': cache[8],
                    'requires': requires,
                    'build': build,
                    'arch': arch,
                    'conflicts': '',
                    'suggests': ''
                }

                cache: list = []  # reset cache

        path_changelog: Path = Path(self.repos.gnome_repo_path, self.repos.gnome_repo_changelog)
        self.write_last_update(path_changelog, self.repos.gnome_repo_name)

        data_file: Path = Path(self.repos.gnome_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()

    def install_msb_data(self) -> None:
        """ Install the data for msb repository. """
        print(f"\nUpdating the database for '{self.cyan}{self.repos.msb_repo_name}{self.endc}'... ",
              end='', flush=True)

        mirror: str = ''.join(self.repos.msb_repo_mirror)
        if self.repos.msb_repo_local[0].startswith('file'):
            mirror: str = ''.join(self.repos.msb_repo_local)

        self._import_GPG_KEY(mirror=mirror)

        checksums_dict: dict = {}
        data: dict = {}
        build: str = ''
        arch: str = ''
        requires: list = []
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.msb_repo_path, self.repos.msb_repo_packages)
        path_checksums: Path = Path(self.repos.msb_repo_path, self.repos.msb_repo_checksums)
        packages_txt: list = self.utils.read_text_file(path_packages)
        checksums_md5: list = self.utils.read_text_file(path_checksums)

        for line in checksums_md5:
            line = line.strip()

            if line.endswith(('.txz', '.tgz')):
                file: str = line.split('./')[1].split('/')[-1].strip()
                checksum: str = line.split('./')[0].strip()
                checksums_dict[file] = checksum

        cache: list = []  # init cache

        for line in packages_txt:

            if line.startswith(pkg_tag[0]):
                package = line.replace(pkg_tag[0], '').strip()
                name: str = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build: str = self.utils.split_package(package)['build']
                arch: str = self.utils.split_package(package)['arch']
                cache.append(name)
                cache.append(version)
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')

            if line.startswith(pkg_tag[1]):
                package_location = line.replace(pkg_tag[1], '').strip()
                cache.append(package_location[2:])  # Do not install (./) dot

            if line.startswith(pkg_tag[2]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[3]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[4]):
                package_description = line.replace(pkg_tag[4], '').strip()
                cache.append(package_description)

            if len(cache) == 9:
                data[cache[0]]: dict = {
                    'repo': self.repos.msb_repo_name,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'description': cache[8],
                    'requires': requires,
                    'build': build,
                    'arch': arch,
                    'conflicts': '',
                    'suggests': ''
                }

                cache: list = []  # reset cache

        path_changelog: Path = Path(self.repos.msb_repo_path, self.repos.msb_repo_changelog)
        self.write_last_update(path_changelog, self.repos.msb_repo_name)

        data_file: Path = Path(self.repos.msb_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()

    def install_csb_data(self) -> None:
        """ Install the data for csb repository. """
        print(f"\nUpdating the database for '{self.cyan}{self.repos.csb_repo_name}{self.endc}'... ",
              end='', flush=True)

        mirror: str = ''.join(self.repos.csb_repo_mirror)
        if self.repos.csb_repo_local[0].startswith('file'):
            mirror: str = ''.join(self.repos.csb_repo_local)

        self._import_GPG_KEY(mirror=mirror)

        checksums_dict: dict = {}
        data: dict = {}
        build: str = ''
        arch: str = ''
        requires: list = []
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.csb_repo_path, self.repos.csb_repo_packages)
        path_checksums: Path = Path(self.repos.csb_repo_path, self.repos.csb_repo_checksums)
        packages_txt: list = self.utils.read_text_file(path_packages)
        checksums_md5: list = self.utils.read_text_file(path_checksums)

        for line in checksums_md5:
            line = line.strip()

            if line.endswith(('.txz', '.tgz')):
                file: str = line.split('./')[1].split('/')[-1].strip()
                checksum: str = line.split('./')[0].strip()
                checksums_dict[file] = checksum

        cache: list = []  # init cache

        for line in packages_txt:

            if line.startswith(pkg_tag[0]):
                package = line.replace(pkg_tag[0], '').strip()
                name: str = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build: str = self.utils.split_package(package)['build']
                arch: str = self.utils.split_package(package)['arch']
                cache.append(name)
                cache.append(version)
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')

            if line.startswith(pkg_tag[1]):
                package_location = line.replace(pkg_tag[1], '').strip()
                cache.append(package_location[2:])  # Do not install (./) dot

            if line.startswith(pkg_tag[2]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[3]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[4]):
                package_description = line.replace(pkg_tag[4], '').strip()
                cache.append(package_description)

            if len(cache) == 9:
                data[cache[0]]: dict = {
                    'repo': self.repos.csb_repo_name,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'description': cache[8],
                    'requires': requires,
                    'build': build,
                    'arch': arch,
                    'conflicts': '',
                    'suggests': ''
                }

                cache: list = []  # reset cache

        path_changelog: Path = Path(self.repos.csb_repo_path, self.repos.csb_repo_changelog)
        self.write_last_update(path_changelog, self.repos.csb_repo_name)

        data_file: Path = Path(self.repos.csb_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()

    def install_conraid_data(self) -> None:
        """ Install the data for conraid repository. """
        print(f"\nUpdating the database for '{self.cyan}{self.repos.conraid_repo_name}{self.endc}'... ",
              end='', flush=True)

        mirror: str = self.repos.conraid_repo_mirror[0]
        if self.repos.conraid_repo_local[0].startswith('file'):
            mirror: str = self.repos.conraid_repo_local[0]

        self._import_GPG_KEY(mirror=mirror)

        checksums_dict: dict = {}
        data: dict = {}
        build: str = ''
        arch: str = ''
        requires: list = []
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE MIRROR:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.conraid_repo_path, self.repos.conraid_repo_packages)
        path_checksums: Path = Path(self.repos.conraid_repo_path, self.repos.conraid_repo_checksums)
        packages_txt: list = self.utils.read_text_file(path_packages)
        checksums_md5: list = self.utils.read_text_file(path_checksums)

        for line in checksums_md5:
            line = line.strip()

            if line.endswith(('.txz', '.tgz')):
                file: str = line.split('./')[1].split('/')[-1].strip()
                checksum: str = line.split('./')[0].strip()
                checksums_dict[file] = checksum

        cache: list = []

        for line in packages_txt:

            if line.startswith(pkg_tag[0]):
                package: str = line.replace(pkg_tag[0], '').strip()
                name: str = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build: str = self.utils.split_package(package)['build']
                arch: str = self.utils.split_package(package)['arch']
                cache.append(name)
                cache.append(version)
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')

            if line.startswith(pkg_tag[2]):
                package_location: str = line.replace(pkg_tag[2], '').strip()
                cache.append(package_location[2:])  # Do not install (./) dot

            if line.startswith(pkg_tag[3]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[4]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[5]):
                package_description: str = line.replace(pkg_tag[5], '').strip()
                cache.append(package_description)

            if len(cache) == 9:
                data[cache[0]]: dict = {
                    'repo': self.repos.conraid_repo_name,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'description': cache[8],
                    'requires': requires,
                    'build': build,
                    'arch': arch,
                    'conflicts': '',
                    'suggests': ''
                }

                cache: list = []  # reset cache

        path_changelog: Path = Path(self.repos.conraid_repo_path, self.repos.conraid_repo_changelog)
        self.write_last_update(path_changelog, self.repos.conraid_repo_name)

        data_file: Path = Path(self.repos.conraid_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()

    def install_slackdce_data(self) -> None:
        """ Install the data for slackdce repository. """
        print(f"\nUpdating the database for '{self.cyan}{self.repos.slackdce_repo_name}{self.endc}'... ",
              end='', flush=True)

        mirror: str = self.repos.slackdce_repo_mirror[0]
        if self.repos.slackdce_repo_local[0].startswith('file'):
            mirror: str = self.repos.slackdce_repo_local[0]

        self._import_GPG_KEY(mirror=mirror)

        checksums_dict: dict = {}
        data: dict = {}
        build: str = ''
        arch: str = ''
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE REQUIRED:',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.slackdce_repo_path, self.repos.slackdce_repo_packages)
        path_checksums: Path = Path(self.repos.slackdce_repo_path, self.repos.slackdce_repo_checksums)
        packages_txt: list = self.utils.read_text_file(path_packages)
        checksums_md5: list = self.utils.read_text_file(path_checksums)

        for line in checksums_md5:
            line = line.strip()

            if line.endswith(('.txz', '.tgz')):
                file: str = line.split('./')[1].split('/')[-1].strip()
                checksum: str = line.split('./')[0].strip()
                checksums_dict[file] = checksum

        cache: list = []  # init cache

        for line in packages_txt:

            if line.startswith(pkg_tag[0]):
                package = line.replace(pkg_tag[0], '').strip()
                name: str = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build: str = self.utils.split_package(package)['build']
                arch: str = self.utils.split_package(package)['arch']
                cache.append(name)
                cache.append(version)
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')

            if line.startswith(pkg_tag[1]):
                package_location = line.replace(pkg_tag[1], '').strip()
                cache.append(package_location[2:])  # Do not install (./) dot

            if line.startswith(pkg_tag[2]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[3]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[4]):
                required = line.replace(pkg_tag[4], '').strip()
                package_required = required.replace(',', ' ').strip()
                cache.append(package_required)

            if line.startswith(pkg_tag[5]):
                package_description = line.replace(pkg_tag[5], '').strip()
                cache.append(package_description)

            if len(cache) == 10:
                data[cache[0]]: dict = {
                    'repo': self.repos.slackdce_repo_name,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'requires': cache[8].split(),
                    'description': cache[9],
                    'build': build,
                    'arch': arch,
                    'conflicts': '',
                    'suggests': ''
                }

                cache: list = []  # reset cache

        path_changelog: Path = Path(self.repos.slackdce_repo_path, self.repos.slackdce_repo_changelog)
        self.write_last_update(path_changelog, self.repos.slackdce_repo_name)

        data_file: Path = Path(self.repos.slackdce_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()

    def install_slackonly_data(self) -> None:
        """ Install the data for slackonly repository. """
        print(f"\nUpdating the database for '{self.cyan}{self.repos.slackonly_repo_name}{self.endc}'... ",
              end='', flush=True)

        mirror: str = self.repos.slackonly_repo_mirror[0]
        if self.repos.slackonly_repo_local[0].startswith('file'):
            mirror: str = self.repos.slackonly_repo_local[0]

        self._import_GPG_KEY(mirror=mirror)

        checksums_dict: dict = {}
        data: dict = {}
        build: str = ''
        arch: str = ''
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE REQUIRED:',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.slackonly_repo_path, self.repos.slackonly_repo_packages)
        path_checksums: Path = Path(self.repos.slackonly_repo_path, self.repos.slackonly_repo_checksums)
        packages_txt: list = self.utils.read_text_file(path_packages)
        checksums_md5: list = self.utils.read_text_file(path_checksums)

        for line in checksums_md5:
            line = line.strip()

            if line.endswith(('.txz', '.tgz')):
                file: str = line.split('./')[1].split('/')[-1].strip()
                checksum: str = line.split('./')[0].strip()
                checksums_dict[file] = checksum

        cache: list = []  # init cache

        for line in packages_txt:

            if line.startswith(pkg_tag[0]):
                package = line.replace(pkg_tag[0], '').strip()
                name: str = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build: str = self.utils.split_package(package)['build']
                arch: str = self.utils.split_package(package)['arch']
                cache.append(name)
                cache.append(version)
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')

            if line.startswith(pkg_tag[1]):
                package_location = line.replace(pkg_tag[1], '').strip()
                cache.append(package_location[2:])  # Do not install (./) dot

            if line.startswith(pkg_tag[2]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[3]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[4]):
                required = line.replace(pkg_tag[4], '').strip()
                package_required = required.replace(',', ' ').strip()
                cache.append(package_required)

            if line.startswith(pkg_tag[5]):
                package_description = line.replace(pkg_tag[5], '').strip()
                cache.append(package_description)

            if len(cache) == 10:
                data[cache[0]]: dict = {
                    'repo': self.repos.slackonly_repo_name,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'requires': cache[8].split(),
                    'description': cache[9],
                    'build': build,
                    'arch': arch,
                    'conflicts': '',
                    'suggests': ''
                }

                cache: list = []  # reset cache

        path_changelog: Path = Path(self.repos.slackonly_repo_path, self.repos.slackonly_repo_changelog)
        self.write_last_update(path_changelog, self.repos.slackonly_repo_name)

        data_file: Path = Path(self.repos.slackonly_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()

    def install_salixos_data(self) -> None:
        """ Install the data for salixos repository. """
        print(f"\nUpdating the database for '{self.cyan}{self.repos.salixos_repo_name}{self.endc}'... ",
              end='', flush=True)

        mirror: str = self.repos.salixos_repo_mirror[0]
        if self.repos.salixos_repo_local[0].startswith('file'):
            mirror: str = self.repos.salixos_repo_local[0]

        self._import_GPG_KEY(mirror=mirror)

        checksums_dict: dict = {}
        data: dict = {}
        build: str = ''
        arch: str = ''
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE REQUIRED:',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.salixos_repo_path, self.repos.salixos_repo_packages)
        path_checksums: Path = Path(self.repos.salixos_repo_path, self.repos.salixos_repo_checksums)
        packages_txt: list = self.utils.read_text_file(path_packages)
        checksums_md5: list = self.utils.read_text_file(path_checksums)

        for line in checksums_md5:
            line = line.strip()

            if line.endswith(('.txz', '.tgz')):
                file: str = line.split('./')[1].split('/')[-1].strip()
                checksum: str = line.split('./')[0].strip()
                checksums_dict[file] = checksum

        cache: list = []  # init cache

        for line in packages_txt:

            if line.startswith(pkg_tag[0]):
                package = line.replace(pkg_tag[0], '').strip()
                name: str = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build: str = self.utils.split_package(package)['build']
                arch: str = self.utils.split_package(package)['arch']
                cache.append(name)
                cache.append(version)
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')

            if line.startswith(pkg_tag[1]):
                package_location = line.replace(pkg_tag[1], '').strip()
                cache.append(package_location[2:])  # Do not install (./) dot

            if line.startswith(pkg_tag[2]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[3]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[4]):
                deps: list = []
                required = line.replace(pkg_tag[4], '').strip()

                for req in required.split(','):
                    dep = req.split('|')
                    if len(dep) > 1:
                        deps.append(dep[1])
                    else:
                        deps.extend(dep)

                cache.append(' '.join(deps))

            if line.startswith(pkg_tag[5]):
                package_description = line.replace(pkg_tag[5], '').strip()
                cache.append(package_description)

            if len(cache) == 10:
                data[cache[0]]: dict = {
                    'repo': self.repos.salixos_repo_name,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'requires': cache[8].split(),
                    'description': cache[9],
                    'build': build,
                    'arch': arch,
                    'conflicts': '',
                    'suggests': ''
                }

                cache: list = []  # reset cache

        path_changelog: Path = Path(self.repos.salixos_repo_path, self.repos.salixos_repo_changelog)
        self.write_last_update(path_changelog, self.repos.salixos_repo_name)

        data_file: Path = Path(self.repos.salixos_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()

    def install_salixos_extra_data(self) -> None:
        """ Install the data for salixos_extra repository. """
        print(f"\nUpdating the database for '{self.cyan}{self.repos.salixos_extra_repo_name}{self.endc}'... ",
              end='', flush=True)

        mirror: str = self.repos.salixos_extra_repo_mirror[0]
        if self.repos.salixos_extra_repo_local[0].startswith('file'):
            mirror: str = self.repos.salixos_extra_repo_local[0]

        self._import_GPG_KEY(mirror=mirror)

        checksums_dict: dict = {}
        data: dict = {}
        build: str = ''
        arch: str = ''
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE REQUIRED:',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.salixos_extra_repo_path, self.repos.salixos_extra_repo_packages)
        path_checksums: Path = Path(self.repos.salixos_extra_repo_path, self.repos.salixos_extra_repo_checksums)
        packages_txt: list = self.utils.read_text_file(path_packages)
        checksums_md5: list = self.utils.read_text_file(path_checksums)

        for line in checksums_md5:
            line = line.strip()

            if line.endswith(('.txz', '.tgz')):
                file: str = line.split('./')[1].split('/')[-1].strip()
                checksum: str = line.split('./')[0].strip()
                checksums_dict[file] = checksum

        cache: list = []  # init cache

        for line in packages_txt:

            if line.startswith(pkg_tag[0]):
                package = line.replace(pkg_tag[0], '').strip()
                name: str = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build: str = self.utils.split_package(package)['build']
                arch: str = self.utils.split_package(package)['arch']
                cache.append(name)
                cache.append(version)
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')

            if line.startswith(pkg_tag[1]):
                package_location = line.replace(pkg_tag[1], '').strip()
                cache.append(package_location[2:])  # Do not install (./) dot

            if line.startswith(pkg_tag[2]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[3]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[4]):
                deps: list = []
                required = line.replace(pkg_tag[4], '').strip()

                for req in required.split(','):
                    dep = req.split('|')
                    if len(dep) > 1:
                        deps.append(dep[1])
                    else:
                        deps.extend(dep)

                cache.append(' '.join(deps))

            if line.startswith(pkg_tag[5]):
                package_description = line.replace(pkg_tag[5], '').strip()
                cache.append(package_description)

            if len(cache) == 10:
                data[cache[0]]: dict = {
                    'repo': self.repos.salixos_extra_repo_name,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'requires': cache[8].split(),
                    'description': cache[9],
                    'build': build,
                    'arch': arch,
                    'conflicts': '',
                    'suggests': ''
                }

                cache: list = []  # reset cache

        path_changelog: Path = Path(self.repos.salixos_extra_repo_path, self.repos.salixos_extra_repo_changelog)
        self.write_last_update(path_changelog, self.repos.salixos_extra_repo_name)

        data_file: Path = Path(self.repos.salixos_extra_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()

    def install_salixos_patches_data(self) -> None:
        """ Install the data for salixos_patches repository. """
        print(f"\nUpdating the database for '{self.cyan}{self.repos.salixos_patches_repo_name}{self.endc}'... ",
              end='', flush=True)

        mirror: str = self.repos.salixos_patches_repo_mirror[0]
        if self.repos.salixos_patches_repo_local[0].startswith('file'):
            mirror: str = self.repos.salixos_patches_repo_local[0]

        self._import_GPG_KEY(mirror=mirror)

        checksums_dict: dict = {}
        data: dict = {}
        build: str = ''
        arch: str = ''
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE REQUIRED:',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.salixos_patches_repo_path,
                                   self.repos.salixos_patches_repo_packages)
        path_checksums: Path = Path(self.repos.salixos_patches_repo_path,
                                    self.repos.salixos_patches_repo_checksums)
        packages_txt: list = self.utils.read_text_file(path_packages)
        checksums_md5: list = self.utils.read_text_file(path_checksums)

        for line in checksums_md5:
            line = line.strip()

            if line.endswith(('.txz', '.tgz')):
                file: str = line.split('./')[1].split('/')[-1].strip()
                checksum: str = line.split('./')[0].strip()
                checksums_dict[file] = checksum

        cache: list = []  # init cache

        for line in packages_txt:

            if line.startswith(pkg_tag[0]):
                package = line.replace(pkg_tag[0], '').strip()
                name: str = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build: str = self.utils.split_package(package)['build']
                arch: str = self.utils.split_package(package)['arch']
                cache.append(name)
                cache.append(version)
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')

            if line.startswith(pkg_tag[1]):
                package_location = line.replace(pkg_tag[1], '').strip()
                cache.append(package_location[2:])  # Do not install (./) dot

            if line.startswith(pkg_tag[2]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[3]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[4]):
                deps: list = []
                required = line.replace(pkg_tag[4], '').strip()

                for req in required.split(','):
                    dep = req.split('|')
                    if len(dep) > 1:
                        deps.append(dep[1])
                    else:
                        deps.extend(dep)

                cache.append(' '.join(deps))

            if line.startswith(pkg_tag[5]):
                package_description = line.replace(pkg_tag[5], '').strip()
                cache.append(package_description)

            if len(cache) == 10:
                data[cache[0]]: dict = {
                    'repo': self.repos.salixos_extra_repo_name,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'requires': cache[8].split(),
                    'description': cache[9],
                    'build': build,
                    'arch': arch,
                    'conflicts': '',
                    'suggests': ''
                }

                cache: list = []  # reset cache

        path_changelog: Path = Path(self.repos.salixos_patches_repo_path,
                                    self.repos.salixos_patches_repo_changelog)
        self.write_last_update(path_changelog, self.repos.salixos_patches_repo_name)

        data_file: Path = Path(self.repos.salixos_patches_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()

    def install_slackel_data(self) -> None:
        """ Install the data for slackel repository. """
        print(f"\nUpdating the database for '{self.cyan}{self.repos.slackel_repo_name}{self.endc}'... ",
              end='', flush=True)

        mirror: str = self.repos.slackel_repo_mirror[0]
        if self.repos.slackel_repo_local[0].startswith('file'):
            mirror: str = self.repos.slackel_repo_local[0]

        self._import_GPG_KEY(mirror=mirror)

        checksums_dict: dict = {}
        data: dict = {}
        build: str = ''
        arch: str = ''
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE REQUIRED:',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.slackel_repo_path, self.repos.slackel_repo_packages)
        path_checksums: Path = Path(self.repos.slackel_repo_path, self.repos.slackel_repo_checksums)
        packages_txt: list = self.utils.read_text_file(path_packages)
        checksums_md5: list = self.utils.read_text_file(path_checksums)

        for line in checksums_md5:
            line = line.strip()

            if line.endswith(('.txz', '.tgz')):
                file: str = line.split('./')[1].split('/')[-1].strip()
                checksum: str = line.split('./')[0].strip()
                checksums_dict[file] = checksum

        cache: list = []  # init cache

        for line in packages_txt:

            if line.startswith(pkg_tag[0]):
                package = line.replace(pkg_tag[0], '').strip()
                name: str = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build: str = self.utils.split_package(package)['build']
                arch: str = self.utils.split_package(package)['arch']
                cache.append(name)
                cache.append(version)
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')

            if line.startswith(pkg_tag[1]):
                package_location = line.replace(pkg_tag[1], '').strip()
                cache.append(package_location[2:])  # Do not install (./) dot

            if line.startswith(pkg_tag[2]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[3]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[4]):
                deps: list = []
                required = line.replace(pkg_tag[4], '').strip()

                for req in required.split(','):
                    dep = req.split('|')
                    if len(dep) > 1:
                        deps.append(dep[1])
                    else:
                        deps.extend(dep)

                cache.append(' '.join(deps))

            if line.startswith(pkg_tag[5]):
                package_description = line.replace(pkg_tag[5], '').strip()
                cache.append(package_description)

            if len(cache) == 10:
                data[cache[0]]: dict = {
                    'repo': self.repos.slackel_repo_name,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'requires': cache[8].split(),
                    'description': cache[9],
                    'build': build,
                    'arch': arch,
                    'conflicts': '',
                    'suggests': ''
                }

                cache: list = []  # reset cache

        path_changelog: Path = Path(self.repos.slackel_repo_path, self.repos.slackel_repo_changelog)
        self.write_last_update(path_changelog, self.repos.slackel_repo_name)

        data_file: Path = Path(self.repos.slackel_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()

    def install_slint_data(self) -> None:
        """ Install the data for slint repository. """
        print(f"\nUpdating the database for '{self.cyan}{self.repos.slint_repo_name}{self.endc}'... ",
              end='', flush=True)

        mirror: str = self.repos.slint_repo_mirror[0]
        if self.repos.slint_repo_local[0].startswith('file'):
            mirror: str = self.repos.slint_repo_local[0]

        self._import_GPG_KEY(mirror=mirror)

        checksums_dict: dict = {}
        data: dict = {}
        build: str = ''
        arch: str = ''
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE REQUIRED:',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.slint_repo_path, self.repos.slint_repo_packages)
        path_checksums: Path = Path(self.repos.slint_repo_path, self.repos.slint_repo_checksums)
        packages_txt: list = self.utils.read_text_file(path_packages)
        checksums_md5: list = self.utils.read_text_file(path_checksums)

        for line in checksums_md5:
            line = line.strip()

            if line.endswith(('.txz', '.tgz')):
                file: str = line.split('./')[1].split('/')[-1].strip()
                checksum: str = line.split('./')[0].strip()
                checksums_dict[file] = checksum

        cache: list = []  # init cache

        for line in packages_txt:

            if line.startswith(pkg_tag[0]):
                package = line.replace(pkg_tag[0], '').strip()
                name: str = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build: str = self.utils.split_package(package)['build']
                arch: str = self.utils.split_package(package)['arch']
                cache.append(name)  # package name
                cache.append(version)  # package version
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')

            if line.startswith(pkg_tag[1]):
                package_location = line.replace(pkg_tag[1], '').strip()
                cache.append(package_location[2:])  # Do not install (./) dot

            if line.startswith(pkg_tag[2]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[3]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[4]):
                deps: list = []
                required = line.replace(pkg_tag[4], '').strip()

                for req in required.split(','):
                    dep = req.split('|')
                    if len(dep) > 1:
                        deps.append(dep[1])
                    else:
                        deps.extend(dep)

                cache.append(' '.join(deps))

            if line.startswith(pkg_tag[5]):
                package_description = line.replace(pkg_tag[5], '').strip()
                cache.append(package_description)

            if len(cache) == 10:
                data[cache[0]]: dict = {
                    'repo': self.repos.slint_repo_name,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'requires': cache[8].split(),
                    'description': cache[9],
                    'build': build,
                    'arch': arch,
                    'conflicts': '',
                    'suggests': ''
                }

                cache: list = []  # reset cache

        path_changelog: Path = Path(self.repos.slint_repo_path, self.repos.slint_repo_changelog)
        self.write_last_update(path_changelog, self.repos.slint_repo_name)

        data_file: Path = Path(self.repos.slint_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()

    def install_pprkut_data(self) -> None:
        """ Install the data for pprkut repository. """
        print(f"\nUpdating the database for '{self.cyan}{self.repos.pprkut_repo_name}{self.endc}'... ",
              end='', flush=True)

        mirror: str = ''.join(self.repos.pprkut_repo_mirror)
        if self.repos.pprkut_repo_local[0].startswith('file'):
            mirror: str = ''.join(self.repos.pprkut_repo_local)

        self._import_GPG_KEY(mirror=mirror)

        checksums_dict: dict = {}
        data: dict = {}
        build: str = ''
        arch: str = ''
        requires: list = []
        pkg_tag = [
            'PACKAGE NAME:',
            'PACKAGE LOCATION:',
            'PACKAGE SIZE (compressed):',
            'PACKAGE SIZE (uncompressed):',
            'PACKAGE DESCRIPTION:'
        ]
        path_packages: Path = Path(self.repos.pprkut_repo_path, self.repos.pprkut_repo_packages)
        path_checksums: Path = Path(self.repos.pprkut_repo_path, self.repos.pprkut_repo_checksums)
        packages_txt: list = self.utils.read_text_file(path_packages)
        checksums_md5: list = self.utils.read_text_file(path_checksums)

        for line in checksums_md5:
            line = line.strip()

            if line.endswith(('.txz', '.tgz')):
                file: str = line.split('./')[1].split('/')[-1].strip()
                checksum: str = line.split('./')[0].strip()
                checksums_dict[file] = checksum

        cache: list = []  # init cache

        for line in packages_txt:

            if line.startswith(pkg_tag[0]):
                package = line.replace(pkg_tag[0], '').strip()
                name: str = self.utils.split_package(package)['name']
                version: str = self.utils.split_package(package)['version']
                build: str = self.utils.split_package(package)['build']
                arch: str = self.utils.split_package(package)['arch']
                cache.append(name)
                cache.append(version)
                cache.append(package)
                cache.append(mirror)
                try:
                    cache.append(checksums_dict[package])
                except KeyError:
                    cache.append('error checksum')

            if line.startswith(pkg_tag[1]):
                package_location = line.replace(pkg_tag[1], '').strip()
                cache.append(package_location[2:])  # Do not install (./) dot

            if line.startswith(pkg_tag[2]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[3]):
                cache.append(''.join(re.findall(r'\d+', line)))

            if line.startswith(pkg_tag[4]):
                package_description = line.replace(pkg_tag[4], '').strip()
                cache.append(package_description)

            if len(cache) == 9:
                data[cache[0]]: dict = {
                    'repo': self.repos.pprkut_repo_name,
                    'version': cache[1],
                    'package': cache[2],
                    'mirror': cache[3],
                    'checksum': cache[4],
                    'location': cache[5],
                    'size_comp': cache[6],
                    'size_uncomp': cache[7],
                    'description': cache[8],
                    'requires': requires,
                    'build': build,
                    'arch': arch,
                    'conflicts': '',
                    'suggests': ''
                }

                cache: list = []  # reset cache

        path_changelog: Path = Path(self.repos.pprkut_repo_path, self.repos.pprkut_repo_changelog)
        self.write_last_update(path_changelog, self.repos.pprkut_repo_name)

        data_file: Path = Path(self.repos.pprkut_repo_path, self.repos.data_json)
        data_file.write_text(json.dumps(data, indent=4))

        self.view_done_message()
