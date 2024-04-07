# pylint: disable=C0114,C0116

import pytest


def test_default_value(cli_runner, csv_file):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-d")
    assert "cmap_max=False" in ret.stderr


@pytest.mark.parametrize("option", ["-cmax", "--cmap-max"])
def test_set_value(cli_runner, csv_file, option):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-d", option, 100)
    assert "cmap_max='100'" in ret.stderr
