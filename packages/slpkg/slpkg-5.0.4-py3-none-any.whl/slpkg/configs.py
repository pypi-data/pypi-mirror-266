#!/usr/bin/python3
# -*- coding: utf-8 -*-

try:
    import tomli
except ModuleNotFoundError:
    import tomllib as tomli

import platform
from typing import Any
from pathlib import Path
from dataclasses import dataclass

from slpkg.toml_errors import TomlErrors


@dataclass
class Configs:
    """ Default configurations. """
    toml_errors = TomlErrors()

    prog_name: str = 'slpkg'
    os_arch: str = platform.machine()
    tmp_path: Path = Path('/tmp')
    tmp_slpkg: Path = Path(tmp_path, prog_name)
    build_path: Path = Path(tmp_path, prog_name, 'build')
    download_only_path: Path = Path(tmp_slpkg, '')
    etc_path: Path = Path('/etc', prog_name)
    lib_path: Path = Path('/var/lib', prog_name)
    log_path: Path = Path('/var/log/', prog_name)
    log_packages: Path = Path('/var', 'log', 'packages')

    deps_log_file: Path = Path(log_path, 'deps.log')
    slpkg_log_file: Path = Path(log_path, 'slpkg.log')
    upgrade_log_file: Path = Path(log_path, 'upgrade.log')

    file_list_suffix: str = '.pkgs'
    installpkg: str = 'upgradepkg --install-new'
    reinstall: str = 'upgradepkg --reinstall'
    removepkg: str = 'removepkg'
    colors: bool = True
    makeflags: str = '-j4'
    gpg_verification: bool = False
    checksum_md5: bool = True
    dialog: bool = True
    new_packages: bool = False
    removed_packages: bool = False
    downloader: str = 'wget'
    wget_options: str = '--c -q --progress=bar:force:noscroll --show-progress'
    curl_options: str = ''
    lftp_get_options: str = '-c get -e'
    lftp_mirror_options: str = '-c mirror --parallel=100 --only-newer --delete'
    lftp_mirror_extra_options = {}
    ascii_characters: bool = True
    ask_question: bool = True
    parallel_downloads: bool = False
    progress_bar: bool = False
    progress_spinner: str = 'pixel'
    spinner_color: str = 'green'
    border_color: str = 'bold_green'
    process_log: bool = True

    urllib_retries: Any = False
    urllib_redirect: Any = False
    urllib_timeout: float = 3.0

    proxy_address: str = ''
    proxy_username: str = ''
    proxy_password: str = ''

    try:
        # Load user configuration.
        config_path_file = Path(etc_path, f'{prog_name}.toml')
        if config_path_file.exists():
            with open(config_path_file, 'rb') as conf:
                configs = tomli.load(conf)

        if configs:
            config = configs['CONFIGS']

            os_arch: str = config['OS_ARCH']
            download_only_path: Path = Path(config['DOWNLOAD_ONLY_PATH'])
            ask_question: bool = config['ASK_QUESTION']
            installpkg: str = config['INSTALLPKG']
            reinstall: str = config['REINSTALL']
            removepkg: str = config['REMOVEPKG']
            colors: bool = config['COLORS']
            makeflags: str = config['MAKEFLAGS']
            gpg_verification: bool = config['GPG_VERIFICATION']
            checksum_md5: bool = config['CHECKSUM_MD5']
            dialog: str = config['DIALOG']
            new_packages: bool = config['NEW_PACKAGES']
            removed_packages: bool = config['REMOVED_PACKAGES']
            downloader: str = config['DOWNLOADER']
            wget_options: str = config['WGET_OPTIONS']
            curl_options: str = config['CURL_OPTIONS']
            lftp_get_options: str = config['LFTP_GET_OPTIONS']
            lftp_mirror_options: str = config['LFTP_MIRROR_OPTIONS']
            lftp_mirror_extra_options = config['LFTP_MIRROR_EXTRA_OPTIONS']
            ascii_characters: bool = config['ASCII_CHARACTERS']
            file_list_suffix: str = config['FILE_LIST_SUFFIX']
            parallel_downloads: bool = config['PARALLEL_DOWNLOADS']
            progress_bar: str = config['PROGRESS_BAR']
            progress_spinner: str = config['PROGRESS_SPINNER']
            spinner_color: str = config['SPINNER_COLOR']
            border_color: str = config['BORDER_COLOR']
            process_log: bool = config['PROCESS_LOG']

            urllib_retries: Any = config['URLLIB_RETRIES']
            urllib_redirect: Any = config['URLLIB_REDIRECT']
            urllib_timeout: float = config['URLLIB_TIMEOUT']

            proxy_address: str = config['PROXY_ADDRESS']
            proxy_username: str = config['PROXY_USERNAME']
            proxy_password: str = config['PROXY_PASSWORD']

    except (KeyError, tomli.TOMLDecodeError) as error:
        toml_errors.raise_toml_error_message(error, toml_file='/etc/slpkg/slpkg.toml')

    blink: str = ''
    bold: str = ''
    red: str = ''
    bred: str = ''
    green: str = ''
    bgreen: str = ''
    yellow: str = ''
    byellow: str = ''
    cyan: str = ''
    bcyan: str = ''
    blue: str = ''
    bblue: str = ''
    grey: str = ''
    violet: str = ''
    endc: str = ''

    if colors:
        blink: str = '\033[32;5m'
        bold: str = '\033[1m'
        red: str = '\x1b[91m'
        bred: str = f'{bold}{red}'
        green: str = '\x1b[32m'
        bgreen: str = f'{bold}{green}'
        yellow: str = '\x1b[93m'
        byellow: str = f'{bold}{yellow}'
        cyan: str = '\x1b[96m'
        bcyan: str = f'{bold}{cyan}'
        blue: str = f'\x1b[94m'
        bblue: str = f'{bold}{blue}'
        grey: str = '\x1b[38;5;247m'
        violet: str = '\x1b[35m'
        endc: str = '\x1b[0m'

    # Creating the paths if not exists
    paths = [
        lib_path,
        etc_path,
        build_path,
        tmp_slpkg,
        log_path,
        download_only_path,
    ]

    for path in paths:
        if not path.is_dir():
            path.mkdir(parents=True, exist_ok=True)
