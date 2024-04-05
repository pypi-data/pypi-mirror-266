# SPDX-FileCopyrightText: 2023 German Aerospace Center <amiris@dlr.de>
#
# SPDX-License-Identifier: Apache-2.0

import logging as log
import shutil

from amirispy.source.logs import log_and_raise_critical

_ERR_NO_JAVA = "No Java installation found. See {} for further instructions."
_URL_INSTALLATION_INSTRUCTIONS = "https://gitlab.com/dlr-ve/esy/amiris/amiris-py#further-requirements"


def check_java_installation(raise_exception: bool = False) -> None:
    """If Java installation is not found, logs `Warning` (default) or raises Exception if `raise_exception`"""
    if not shutil.which("java"):
        if raise_exception:
            log_and_raise_critical(_ERR_NO_JAVA.format(_URL_INSTALLATION_INSTRUCTIONS))
        else:
            log.warning(_ERR_NO_JAVA.format(_URL_INSTALLATION_INSTRUCTIONS))
