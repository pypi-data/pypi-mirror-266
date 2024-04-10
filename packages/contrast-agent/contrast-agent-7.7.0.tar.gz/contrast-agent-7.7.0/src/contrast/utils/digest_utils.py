# Copyright © 2024 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
import zlib


class Digest:
    def __init__(self):
        self.crc32 = 0

    def finish(self):
        return str(self.crc32)

    def update(self, value):
        if not value:  # None or empty string
            return

        self.crc32 = zlib.crc32(str(value).encode(), self.crc32)
