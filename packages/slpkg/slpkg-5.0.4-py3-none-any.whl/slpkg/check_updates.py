#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from pathlib import Path
from multiprocessing import Process, Queue
from urllib3.exceptions import HTTPError, NewConnectionError
from urllib3 import PoolManager, ProxyManager, make_headers

from slpkg.configs import Configs
from slpkg.repo_info import RepoInfo
from slpkg.utilities import Utilities
from slpkg.progress_bar import ProgressBar
from slpkg.repositories import Repositories


class CheckUpdates(Configs):
    """ Check for changes in the ChangeLog file. """

    def __init__(self, flags: list, repository: str):
        super(Configs, self).__init__()
        self.flags: list = flags
        self.repository: str = repository

        self.utils = Utilities()
        self.progress = ProgressBar()
        self.repos = Repositories()
        self.repo_info = RepoInfo(flags, repository)

        self.compare: dict = {}
        self.error_connected: list = []

        self.http = PoolManager(timeout=self.urllib_timeout)
        self.proxy_default_headers = make_headers(
            proxy_basic_auth=f'{self.proxy_username}:{self.proxy_password}')

        self.option_for_repository: bool = self.utils.is_option(
            ('-o', '--repository='), flags)

        self.option_for_check: bool = self.utils.is_option(
            ('-c', '--check'), flags)

        self.option_for_progress_bar: bool = self.utils.is_option(
            ('-B', '--progress-bar'), flags)

    def check_the_repositories(self, queue=None) -> None:
        if self.option_for_repository:
            self.repositories(self.repository)
        else:
            self.check_updates_for_repositories()

        if queue is not None:
            queue.put(self.compare)
            queue.put(self.error_connected)

    def check_updates_for_repositories(self) -> None:
        for repo, enable in self.repos.repositories.items():
            if enable['enable']:
                self.repositories(repo)

    def repositories(self, repo: str) -> None:
        local_chg_txt: Path = Path(self.repos.repositories[repo]['path'],
                                   self.repos.repositories[repo]['changelog_txt'])
        repo_chg_txt: str = (f"{self.repos.repositories[repo]['mirror'][0]}"
                             f"{self.repos.repositories[repo]['changelog_txt']}")
        repo_data_file: Path = Path(self.repos.repositories[repo]['path'], self.repos.data_json)

        if not repo_data_file.is_file():
            self.compare[repo]: dict = True
        else:
            self.compare[repo] = self.compare_the_changelogs(local_chg_txt, repo_chg_txt)

    def compare_the_changelogs(self, local_chg_txt: Path, repo_chg_txt: str) -> bool:
        local_size: int = 0
        repo_size: int = 0

        if self.proxy_address.startswith('http'):
            self.set_http_proxy_server()

        if self.proxy_address.startswith('socks'):
            self.set_socks_proxy_server()

        # Get local changelog file size.
        if local_chg_txt.is_file():
            local_size: int = int(os.stat(local_chg_txt).st_size)

        try:  # Get repository changelog file size.
            repo = self.http.request(
                'GET', repo_chg_txt,
                retries=self.urllib_retries,
                redirect=self.urllib_redirect)
            repo_size: int = int(repo.headers.get('content-length', 0))
        except KeyboardInterrupt:
            raise SystemExit(1)
        except (HTTPError, NewConnectionError):
            self.error_connected.append(repo_chg_txt)

        if repo_size == 0:
            return False

        return local_size != repo_size

    def error_connected_repositories(self) -> None:
        if self.error_connected:
            print(f'\n{self.endc}Failed connected to the mirrors:\n')
            for repo in self.error_connected:
                print(f'{self.red}>{self.endc} {repo}')

    def set_http_proxy_server(self) -> None:
        self.http = ProxyManager(f'{self.proxy_address}', headers=self.proxy_default_headers)

    def set_socks_proxy_server(self) -> None:
        try:  # Try to import PySocks if it's installed.
            from urllib3.contrib.socks import SOCKSProxyManager
        except (ModuleNotFoundError, ImportError) as error:
            print(error)
        # https://urllib3.readthedocs.io/en/stable/advanced-usage.html#socks-proxies
        self.http = SOCKSProxyManager(f'{self.proxy_address}', headers=self.proxy_default_headers)

    def view_messages(self) -> None:
        repo_for_update: list = []
        for repo, comp in self.compare.items():
            if comp:
                repo_for_update.append(repo)

        if repo_for_update:
            last_updates: dict = self.repo_info.read_last_updated()
            print(f"\n{self.bgreen}There are new updates available for the "
                  f"repositories:{self.endc}\n")

            for repo in repo_for_update:
                repo_length: int = max(len(name) for name in repo_for_update)
                print(f'> {self.bgreen}{repo:<{repo_length}}{self.endc} Last Updated: '
                      f"'{last_updates.get(repo, None)}'")
            if not self.option_for_check:
                print()
        else:
            print(f'\n{self.endc}{self.yellow}No updated packages since the last check.{self.endc}')

        if self.option_for_check:
            print()

    def updates(self) -> dict:
        message: str = 'Checking for news, please wait'
        if self.progress_bar or self.option_for_progress_bar:
            queue = Queue()

            # Starting multiprocessing
            process_1 = Process(target=self.check_the_repositories, args=(queue,))
            process_2 = Process(target=self.progress.progress_bar, args=(message,))

            process_1.start()
            process_2.start()

            # Wait until process 1 finish
            process_1.join()

            # Terminate process 2 if process 1 finished
            if not process_1.is_alive():
                process_2.terminate()

            self.compare: dict = queue.get()
            self.error_connected: list = queue.get()

            print('\x1b[?25h')
        else:
            print(f'\r{message}... ', end='')
            self.check_the_repositories()
            print()

        self.error_connected_repositories()
        self.view_messages()
        return self.compare
