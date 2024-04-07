# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-od", "--output-dir"])
def test_debug_logs(cli_runner, csv_file, tmpdir, option):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-d", option, tmpdir, "-wk", "42")

    assert f"{tmpdir}/001_2024_week_42_RdYlGn_r_heatmap_" in ret.stderr
