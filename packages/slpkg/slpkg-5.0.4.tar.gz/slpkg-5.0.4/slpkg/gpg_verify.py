#!/usr/bin/python3
# -*- coding: utf-8 -*-

import subprocess

from slpkg.configs import Configs
from slpkg.views.asciibox import AsciiBox
from slpkg.views.views import View


class GPGVerify(Configs):

    def __init__(self):
        super(Configs, self).__init__()
        self.ascii = AsciiBox()
        self.view = View()

    def verify(self, asc_files: list) -> None:
        if self.gpg_verification:
            verify_message: str = '\rVerify files with GPG... '
            gpg_command: str = 'gpg --verify'
            print(verify_message, end='')

            exit_code: int = 0
            for i, file in enumerate(asc_files):
                process = subprocess.Popen(f'{gpg_command} {file}', shell=True, stdout=subprocess.PIPE,
                                           stderr=subprocess.STDOUT, text=True)

                process.wait()

                if process.returncode != 0:
                    exit_code: int = process.returncode
                    if i == 0:
                        print(f'{self.bred}{self.ascii.failed}{self.endc}')
                    print(f"{'':>2}Error {process.returncode}: {file.name}")

            if exit_code == 0:
                print(f'{self.bgreen}{self.ascii.done}{self.endc}')
            elif exit_code != 0 and self.dialog:
                self.view.question()
