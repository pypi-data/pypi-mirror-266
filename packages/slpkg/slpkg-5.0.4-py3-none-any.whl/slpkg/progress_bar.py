#!/usr/bin/python3
# -*- coding: utf-8 -*-

import time

from slpkg.configs import Configs
from slpkg.views.asciibox import AsciiBox


class ProgressBar(Configs):

    def __init__(self):
        super(Configs, self).__init__()
        self.ascii = AsciiBox()

        self.color: str = self.endc
        self.spinners: dict = {}
        self.spinners_color: dict = {}
        self.spinner: str = ''
        self.bar_message: str = ''

    def progress_bar(self, message: str, filename=None) -> None:
        """ Creating progress bar. """
        self.set_spinner()
        self.assign_spinner_colors()
        self.set_color()
        self.set_the_spinner_message(filename, message)
        print('\x1b[?25l', end='')  # Hide cursor before starting

        current_state = 0  # Index of the current state
        try:
            while True:
                print(f"\r{self.bar_message}{self.color}{self.spinner[current_state]}{self.endc}", end="")
                time.sleep(0.1)
                current_state = (current_state + 1) % len(self.spinner)
        except KeyboardInterrupt:
            print('\x1b[?25h', end='')
            raise SystemExit(1)

    def assign_spinner_colors(self) -> None:
        self.spinners_color: dict = {
            'green': self.green,
            'violet': self.violet,
            'yellow': self.yellow,
            'blue': self.blue,
            'cyan': self.cyan,
            'grey': self.grey,
            'red': self.red,
            'white': self.endc
        }

    def set_the_spinner_message(self, filename: str, message: str) -> None:
        self.bar_message: str = f'{message}... '
        if filename:
            self.bar_message: str = (f"{'':>2}{self.yellow}{self.ascii.bullet}{self.endc} {filename}: "
                                     f"{message}... ")

    def set_spinner(self) -> None:
        self.spinners: dict = {
            'spinner': ('-', '\\', '|', '/'),
            'pie': ('◷', '◶', '◵', '◴'),
            'moon': ('◑', '◒', '◐', '◓'),
            'line': ('⎺', '⎻', '⎼', '⎽', '⎼', '⎻'),
            'pixel': ('⣾', '⣷', '⣯', '⣟', '⡿', '⢿', '⣻', '⣽'),
            'ball': ('_', '.', '|', 'o'),
            'clock': ('🕛', '🕑', '🕒', '🕔', '🕧', '🕗', '🕘', '🕚')
        }
        try:
            self.spinner: tuple = self.spinners[self.progress_spinner]
        except KeyError:
            self.spinner: tuple = self.spinners['spinner']

    def set_color(self) -> None:
        try:
            self.color: str = self.spinners_color[self.spinner_color]
        except KeyError:
            self.color: str = self.endc
