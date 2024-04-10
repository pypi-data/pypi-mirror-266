# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2024 Jayesh Badwaik <j.badwaik@fz-juelich.de>
# --------------------------------------------------------------------------------------------------

import enum


class benchmark_type(enum.Enum):
    single = "single"
    strong = "strong"
    weak = "weak"

    def __str__(self):
        return self.value
