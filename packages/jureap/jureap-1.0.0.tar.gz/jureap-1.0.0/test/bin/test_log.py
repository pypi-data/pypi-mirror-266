# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2024 Jayesh Badwaik <j.badwaik@fz-juelich.de>
# --------------------------------------------------------------------------------------------------

import jureap.log
import os
import argparse
import csv
import json
import jureap.metadata


def test_00_generate_log():
    input_filename = "test/share/log/00.input.csv"
    data_csv_file = jureap.log.read_csv_file(input_filename)
    log_dict = jureap.log.generate(
        data_csv_file, jureap.metadata.semver.major, jureap.metadata.semver.major
    )

    input_log_dict = json.load(open("test/share/log/00.output.json"))
    assert log_dict == input_log_dict


def test_01_generate_log():
    input_filename = "test/share/log/01.input.csv"
    data_csv_file = jureap.log.read_csv_file(input_filename)
    log_dict = jureap.log.generate(
        data_csv_file, jureap.metadata.semver.major, jureap.metadata.semver.major
    )

    input_log_dict = json.load(open("test/share/log/01.output.json"))
    assert log_dict == input_log_dict


def test_command_line_interace():
    os.makedirs("output/test/share/log", exist_ok=True)
    args = argparse.Namespace(
        input_file="test/share/log/00.input.csv",
        output_file="output/test/share/log/00.output.json",
        version="major",
        output_version="major",
    )

    jureap.log.log(args)

    output_log_dict = json.load(open("output/test/share/log/00.output.json"))
    input_log_dict = json.load(open("test/share/log/00.output.json"))

    assert output_log_dict == input_log_dict


def test_generate_01():
    csv_header = ["sytem_name", "system_version", "bench_target", "bench_variant", "value"]
    data = ["jurecadc", "2024.01", "dc-cpu", "single", "12738372", "1", "4", "4993.08", "true"]

    csv_data = [csv_header, data]

    try:
        jureap.log.generate(csv_data, jureap.metadata.semver.major, jureap.metadata.semver.major)
    except ValueError as e:
        assert str(e) == "system_name field not found in data_dict"

    csv_data = [["system_name", "sytem_version", "bench_target", "bench_variant", "value"]]

    try:
        jureap.log.generate(csv_data, jureap.metadata.semver.major, jureap.metadata.semver.major)
    except ValueError as e:
        assert str(e) == "system_version field not found in data_dict"

    csv_data = [["system_name", "system_version", "bench_tget", "bench_variant", "value"]]

    try:
        jureap.log.generate(csv_data, jureap.metadata.semver.major, jureap.metadata.semver.major)
    except ValueError as e:
        assert str(e) == "bench_target field not found in data_dict"

    csv_data = [["system_name", "system_version", "bench_target", "bench_riant", "value"]]

    try:
        jureap.log.generate(csv_data, jureap.metadata.semver.major, jureap.metadata.semver.major)
    except ValueError as e:
        assert str(e) == "bench_variant field not found in data_dict"


def test_system_name_mismatch():
    csv_header = ["system_name", "system_version", "bench_target", "bench_variant", "value"]
    data1 = ["jurecadc", "2024.01", "dc-cpu", "single", "12738372", "1", "4", "4993.08", "true"]
    data2 = ["juwels", "2024.01", "dc-cpu", "single", "12738372", "1", "4", "4993.08", "true"]

    csv_data = [csv_header, data1, data2]

    try:
        jureap.log.generate(csv_data, jureap.metadata.semver.major, jureap.metadata.semver.major)
    except ValueError as e:
        assert str(e) == "system_name mismatch: juwels != jurecadc"

    csv_header = ["system_name", "system_version", "bench_target", "bench_variant", "value"]
    data1 = ["jurecadc", "2024.01", "dc-cpu", "single", "12738372", "1", "4", "4993.08", "true"]
    data2 = ["jurecadc", "2024.02", "dc-cpu", "single", "12738372", "1", "4", "4993.08", "true"]

    csv_data = [csv_header, data1, data2]

    try:
        jureap.log.generate(csv_data, jureap.metadata.semver.major, jureap.metadata.semver.major)
    except ValueError as e:
        assert str(e) == "system_version mismatch: 2024.02 != 2024.01"

    csv_header = ["system_name", "system_version", "bench_target", "bench_variant", "value"]
    data1 = ["jurecadc", "2024.01", "dc-cpu", "single", "12738372", "1", "4", "4993.08", "true"]
    data2 = ["jurecadc", "2024.01", "d-gpu", "single", "12738372", "1", "4", "4993.08", "true"]

    csv_data = [csv_header, data1, data2]

    try:
        jureap.log.generate(csv_data, jureap.metadata.semver.major, jureap.metadata.semver.major)
    except ValueError as e:
        assert str(e) == "bench_target mismatch: d-gpu != dc-cpu"

    csv_header = ["system_name", "system_version", "bench_target", "bench_variant", "value"]
    data1 = ["jurecadc", "2024.01", "dc-cpu", "single", "12738372", "1", "4", "4993.08", "true"]
    data2 = ["jurecadc", "2024.01", "dc-cpu", "multi", "12738372", "1", "4", "4993.08", "true"]

    csv_data = [csv_header, data1, data2]

    try:
        jureap.log.generate(csv_data, jureap.metadata.semver.major, jureap.metadata.semver.major)
    except ValueError as e:
        assert str(e) == "bench_variant mismatch: multi != single"
