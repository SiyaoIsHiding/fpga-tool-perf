#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright 2018-2022 F4PGA Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

import time
import os


class Timed:
    def __init__(self, t, name, unprinted_runtime=False):
        self.t = t
        self.name = name
        self.start = None
        self.unprinted_runtime = unprinted_runtime

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, type, value, traceback):
        end = time.time()
        self.t.add_runtime(
            self.name,
            end - self.start,
            unprinted_runtime=self.unprinted_runtime
        )


def get_vivado_max_freq(report_file):
    processing = False

    group = ""
    delay = ""
    requirement = ""
    freq = 0
    freqs = dict()
    path_type = None

    with open(report_file, 'r') as fp:
        for l in fp:

            if l.startswith("Slack"):
                if '(MET)' in l:
                    violation = 0.0
                else:
                    violation = float(
                        l.split(':')[1].split()[0].strip().strip('ns')
                    )
                processing = True

            if processing is True:
                fields = l.split()
                if len(fields) > 1 and fields[1].startswith('----'):
                    processing = False
                    # check if this is a timing we want
                    if group not in requirement.split():
                        continue
                    if group not in freqs:
                        freqs[group] = dict()
                        freqs[group]['actual'] = freq
                        freqs[group]['requested'] = requested_freq
                        freqs[group]['met'] = freq >= requested_freq
                        freqs[group]['{}_violation'.format(path_type.lower())
                                     ] = violation
                        path_type = None
                    if path_type is not None:
                        freqs[group]['{}_violation'.format(path_type.lower())
                                     ] = violation

                data = l.split(':')
                if len(data) > 1:
                    if data[0].strip() == 'Data Path Delay':
                        delay = data[1].split()[0].strip('ns')
                        freq = 1e9 / float(delay)
                    if data[0].strip() == 'Path Group':
                        group = data[1].strip()
                    if data[0].strip() == 'Requirement':
                        requirement = data[1].strip()
                        r = float(requirement.split()[0].strip('ns'))
                        if r != 0.0:
                            requested_freq = 1e9 / r
                    if data[0].strip() == 'Path Type':
                        ptype = data[1].strip()
                        if path_type != ptype.split()[0]:
                            path_type = ptype.split()[0]
    for cd in freqs:
        freqs[cd]['actual'] = float("{:.3f}".format(freqs[cd]['actual'] / 1e6))
        freqs[cd]['requested'] = float(
            "{:.3f}".format(freqs[cd]['requested'] / 1e6)
        )
    return freqs


def get_yosys_resources(yosys_log):
    with open(yosys_log, "r") as f:
        data = f.readlines()

    resources = dict()
    print_stats = False
    proc_cells = False
    for line in data:
        print_stats = "Printing statistics" in line or print_stats

        if not print_stats:
            continue

        if proc_cells and line.strip():
            cell, count = line.split()
            resources[cell] = count

        proc_cells = ("Number of cells" in line or proc_cells) and line.strip()

    return resources


def have_exec(mybin):
    return which(mybin) != None


# https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python
def which(program, get_dir=False):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                if get_dir:
                    return path
                else:
                    return exe_file

    return None


def safe_get_dict_value(dict, key, default):
    if key in dict:
        return dict[key]
    else:
        return default


def get_file_dict(file_name, file_type):
    return dict(name=os.path.realpath(file_name), file_type=file_type)


def removeprefix(string, prefix):
    if string.startswith(prefix):
        return string[len(prefix):]
    else:
        return string[:]


def removesuffix(string, suffix):
    if suffix and string.endswith(suffix):
        return string[:-len(suffix)]
    else:
        return string[:]
