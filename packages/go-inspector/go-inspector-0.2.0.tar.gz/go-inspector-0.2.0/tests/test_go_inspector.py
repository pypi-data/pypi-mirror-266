# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/g-inspector for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

import pytest
from commoncode.testcase import FileDrivenTesting
from scancode.cli_test_utils import check_json
from scancode.cli_test_utils import check_json_scan
from scancode.cli_test_utils import run_scan_click
from scancode_config import REGEN_TEST_FIXTURES

from go_inspector.plugin import collect_and_parse_symbols

test_env = FileDrivenTesting()
test_env.test_data_dir = os.path.join(os.path.dirname(__file__), "data")


def test_collect_and_parse_symbols_with_plain_windows_exe():
    go_binary = test_env.get_test_loc("plain_windows.exe")
    with pytest.raises(Exception) as e:
        collect_and_parse_symbols(go_binary)


def test_collect_and_parse_symbols_with_plain_elf():
    go_binary = test_env.get_test_loc("plain_arm_gentoo_elf")
    with pytest.raises(Exception) as e:
        collect_and_parse_symbols(go_binary)


@pytest.mark.parametrize(
    "exe_path",
    [
        "basic/app_lin_exe",
        "basic/app_mac_exe",
        "basic/app_win_exe",
        "basic/app_lin_exe_stripped",
    ],
)
def test_collect_and_parse_symbols_with_mini_go_app_linux(exe_path):
    go_binary = test_env.get_test_loc(exe_path)
    expected = f"{go_binary}-goresym.json"
    results = collect_and_parse_symbols(go_binary)
    check_json(expected, results, regen=REGEN_TEST_FIXTURES)


def test_collect_and_parse_symbols_with_large_go_app_linux():
    from pathlib import Path

    go_binary = Path(test_env.test_data_dir).parent.parent / "src/go_inspector/bin/GoReSym_lin"
    expected = test_env.get_test_loc(f"GoReSym_lin-goresym.json", must_exist=False)
    results = collect_and_parse_symbols(go_binary)
    check_json(expected, results, regen=REGEN_TEST_FIXTURES)


def test_scancode_plugin_with_go_symbol_option():
    test_file = test_env.get_test_loc("basic/app_lin_exe", copy=True)
    result_file = test_env.get_temp_file("json")
    args = ["--go-symbol", test_file, "--json", result_file]
    run_scan_click(args)
    expected = test_env.get_test_loc("basic/app_lin_exe-scancode.expected.json", must_exist=False)
    check_json_scan(expected, result_file, regen=REGEN_TEST_FIXTURES)
