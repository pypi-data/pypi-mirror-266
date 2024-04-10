# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2024 Jayesh Badwaik <j.badwaik@fz-juelich.de>
# --------------------------------------------------------------------------------------------------
import semver as SemVer
import enum


class major_version_type(enum.Enum):
    v0 = "0"
    v1 = "1"

    def __str__(self):
        return self.value


__version__ = "1.0.0"
semver = SemVer.VersionInfo.parse(__version__)
