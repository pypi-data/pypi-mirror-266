# pylint: disable=C0114,C0116

import pytest


@pytest.mark.parametrize("option", ["-cb", "--cbar"])
def test_debug_logs(cli_runner, csv_file, option):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-d", option)
    assert "cbar=True" in ret.stderr
