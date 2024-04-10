# --------------------------------------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0
# Copyright (C) 2024 Jayesh Badwaik <j.badwaik@fz-juelich.de>
# --------------------------------------------------------------------------------------------------

import csv
import json
import typing


def log(args):
    input_file = args.input_file
    csv_array = read_csv_file(input_file)
    log_dict = generate(csv_array, args.version, args.output_version)
    with open(args.output_file, "w") as json_file:
        json.dump(log_dict, json_file, indent=2)


def read_csv_file(filename: str) -> list:
    with open(filename, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        line_count = 0
        csv_array = []
        for row in csv_reader:
            csv_array.append(row)

        return csv_array


def generate(csv, version, output_version) -> dict:
    header = csv[0]
    data = csv[1:]

    if "system_name" not in header:
        raise ValueError("system_name field not found in data_dict")

    if "system_version" not in header:
        raise ValueError("system_version field not found in data_dict")

    if "bench_target" not in header:
        raise ValueError("bench_target field not found in data_dict")

    if "bench_variant" not in header:
        raise ValueError("bench_variant field not found in data_dict")

    data_dict_array = []
    for j in range(len(data)):
        data_dict = {}
        for i, h in enumerate(header):
            data_dict[h] = data[j][i]
        data_dict_array.append(data_dict)

    system_name = data_dict_array[0]["system_name"]
    system_version = data_dict_array[0]["system_version"]
    bench_target = data_dict_array[0]["bench_target"]
    bench_variant = data_dict_array[0]["bench_variant"]

    for data_dict in data_dict_array:
        if data_dict["system_name"] != system_name:
            raise ValueError(f"system_name mismatch: {data_dict['system_name']} != {system_name}")
        if data_dict["system_version"] != system_version:
            raise ValueError(
                f"system_version mismatch: {data_dict['system_version']} != {system_version}"
            )
        if data_dict["bench_target"] != bench_target:
            raise ValueError(
                f"bench_target mismatch: {data_dict['bench_target']} != {bench_target}"
            )
        if data_dict["bench_variant"] != bench_variant:
            raise ValueError(
                f"bench_variant mismatch: {data_dict['bench_variant']} != {bench_variant}"
            )

    log_dict: typing.Dict[typing.Any, typing.Any] = {}
    log_dict["meta"] = {}
    log_dict["meta"]["system_name"] = system_name
    log_dict["meta"]["system_version"] = system_version
    log_dict["meta"]["bench_target"] = bench_target
    log_dict["meta"]["bench_variant"] = bench_variant

    log_dict["data"] = [{}] * len(data_dict_array)

    for i, data_dict in enumerate(data_dict_array):
        log_dict["data"].append
        log_dict["data"][i]["jobid"] = data_dict["jobid"]
        log_dict["data"][i]["nodes"] = data_dict["nodes"]
        log_dict["data"][i]["taskspernode"] = data_dict["taskspernode"]
        log_dict["data"][i]["runtime"] = data_dict["runtime"]
        log_dict["data"][i]["success"] = data_dict["success"]

    return log_dict
