#!/usr/bin/python3
# -*- coding: utf-8 -*-

import hashlib
from pathlib import Path
from typing import Union
from urllib.parse import unquote

from slpkg.configs import Configs
from slpkg.views.views import View
from slpkg.error_messages import Errors
from slpkg.views.asciibox import AsciiBox


class Md5sum(Configs):
    """ Checksum the sources. """

    def __init__(self, flags: list):
        self.ascii = AsciiBox()
        self.errors = Errors()
        self.view = View(flags)

    def md5sum(self, path: Union[str, Path], source: str, checksum: str) -> None:
        """ Checksum the source. """
        if self.checksum_md5:
            source_file = unquote(source)
            filename = source_file.split('/')[-1]
            source_path = Path(path, filename)

            md5: bytes = self.read_binary_file(source_path)
            file_check: str = hashlib.md5(md5).hexdigest()
            checksum: str = "".join(checksum)

            if file_check != checksum:
                self.ascii.draw_checksum_error_box(filename, checksum, file_check)
                self.view.question()

    def read_binary_file(self, filename: Union[str, Path]) -> bytes:
        try:
            with open(filename, 'rb') as file:
                return file.read()
        except FileNotFoundError:
            self.errors.raise_error_message(f"No such file or directory: '{filename}'", exit_status=20)
