# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2024 Jayesh Badwaik <j.badwaik@fz-juelich.de>
# --------------------------------------------------------------------------------------------------

import argparse
import jureap.benchmark


def make_wide(formatter, w=140, h=100):
    """Return a wider HelpFormatter, if possible."""
    try:
        # https://stackoverflow.com/a/5464440
        # beware: "Only the name of this class is considered a public API."
        kwargs = {"width": w, "max_help_position": h}
        formatter(None, **kwargs)
        return lambda prog: formatter(prog, **kwargs)
    except TypeError:
        warnings.warn("argparse help formatter failed, falling back.")
        return formatter


def log_parser(sp):
    sp.add_argument(
        "--version",
        type=jureap.metadata.major_version_type,
        default=jureap.metadata.semver.major,
        choices=list(jureap.metadata.major_version_type),
        help="Version of Input File",
    )
    sp.add_argument(
        "--output-version",
        type=jureap.metadata.major_version_type,
        default=jureap.metadata.semver.major,
        choices=list(jureap.metadata.major_version_type),
        help="Version of Log File",
    )
    sp.add_argument("input_file", type=str, help="Input File")
    sp.add_argument("output_file", type=str, help="Output File")


def report_parser(sp):
    pass


def top_level():
    parser = argparse.ArgumentParser(
        description="jureap",
        formatter_class=make_wide(argparse.ArgumentDefaultsHelpFormatter),
    )
    subparsers = parser.add_subparsers(dest="subcommand", required=True)
    lp = subparsers.add_parser(
        "log",
        help="Log Generator",
        formatter_class=make_wide(argparse.ArgumentDefaultsHelpFormatter),
    )
    rp = subparsers.add_parser("report", help="Report Generator")

    log_parser(lp)
    report_parser(rp)

    return parser
