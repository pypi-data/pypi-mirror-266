# pylint: disable=C0114,C0116

import pytest


def test_default_value(cli_runner, csv_file):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-d")
    assert "cmap_min=False" in ret.stderr


@pytest.mark.parametrize("option", ["-cmin", "--cmap-min"])
def test_set_value(cli_runner, csv_file, option):
    csv = csv_file("sample.csv")
    ret = cli_runner(csv, "-d", option, 0)
    assert "cmap_min='0'" in ret.stderr
