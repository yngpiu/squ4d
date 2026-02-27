# SPDX-FileCopyrightText: 2018-2025 Joonas Rautiola <mail@joinemm.dev>
# SPDX-License-Identifier: MPL-2.0
# https://git.joinemm.dev/miso-bot

import os

from loguru import logger


class Keychain:
    def __init__(self):
        self.LASTFM_API_KEY: str = ""
        self.GCS_DEVELOPER_KEY: str = ""
        self.RAPIDAPI_KEY: str = ""
        self.DATALAMA_ACCESS_KEY: str = ""
        self.SHLINK_API_KEY: str = ""
        self.LASTFM_USERNAME: str = ""
        self.LASTFM_PASSWORD: str = ""
        self.EZ_API_KEY: str = ""

        for name in self.__dict__:
            value = os.environ.get(name)
            optional = []
            if not value and name not in optional:
                logger.warning(f'No value set for env variable "{name}"')

            setattr(self, name, value)
