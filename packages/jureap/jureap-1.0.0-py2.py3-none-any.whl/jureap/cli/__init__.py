# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2024 Jayesh Badwaik <j.badwaik@fz-juelich.de>
# --------------------------------------------------------------------------------------------------

import sys
import jureap.cli.parser
import jureap.log


def main():
    raw_args = sys.argv[1:]
    parser = jureap.cli.parser.top_level()
    args = parser.parse_args(raw_args)

    if args.subcommand == "log":
        jureap.log.log(args)
