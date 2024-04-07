# Copyright (C) 2023,2024 Kian-Meng Ang
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""A console program that generates yearly calendar heatmap.

  website: https://github.com/kianmeng/heatmap_cli
  changelog: https://github.com/kianmeng/heatmap_cli/blob/master/CHANGELOG.md
  issues: https://github.com/kianmeng/heatmap_cli/issues
"""

import argparse
import datetime
import logging
import multiprocessing
import os
import platform
import random
import shutil
import subprocess
import sys
from itertools import zip_longest
from pathlib import Path
from typing import Dict, Optional, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from heatmap_cli import __version__

# generating matplotlib graphs without a x-server
# see http://stackoverflow.com/a/4935945
mpl.use("Agg")

# Suppress logging from matplotlib in debug mode
logging.getLogger("matplotlib").propagate = False
logger = multiprocessing.get_logger()

# Sort in insensitive case
CMAPS = sorted(plt.colormaps, key=str.casefold)
DEFAULT_CMAP = "RdYlGn_r"


def _parse_args(
    args: Optional[Sequence[str]] = None,
) -> argparse.Namespace:
    """Parse the CLI arguments.

    Args:
        args (List | None): Argument passed through the command line

    Returns:
        argparse.Namespace
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        description=__doc__,
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(
            prog,
            max_help_position=6,
        ),
    )

    parser.add_argument(
        "--demo",
        default=0,
        const=len(CMAPS),
        nargs="?",
        type=int,
        dest="demo",
        help=(
            "generate number of heatmaps by colormaps"
            f" (default: '{len(CMAPS)}')"
        ),
        metavar="NUMBER_OF_COLORMAP",
    )

    parser.add_argument(
        "-yr",
        "--year",
        dest="year",
        type=int,
        default=datetime.datetime.today().year,
        help="filter by year from the CSV file (default: '%(default)s')",
        metavar="YEAR",
    )

    parser.add_argument(
        "-wk",
        "--week",
        dest="week",
        type=int,
        default=datetime.datetime.today().strftime("%W"),
        help=(
            "filter until week of the year from the CSV file "
            "(default: '%(default)s')"
        ),
        metavar="WEEK",
    )

    parser.add_argument(
        "-od",
        "--output-dir",
        dest="output_dir",
        default="output",
        help="set default output folder (default: '%(default)s')",
    )

    parser.add_argument(
        "-o",
        "--open",
        default=False,
        action="store_true",
        dest="open",
        help=(
            "open the generated heatmap using default program "
            "(default: '%(default)s')"
        ),
    )

    parser.add_argument(
        "-p",
        "--purge",
        default=False,
        action="store_true",
        dest="purge",
        help=(
            "remove all leftover artifacts set by "
            "--output-dir folder (default: '%(default)s')"
        ),
    )

    parser.add_argument(
        "-v",
        "--verbose",
        default=0,
        action="count",
        dest="verbose",
        help="show verbosity of debugging log, use -vv, -vvv for more details",
    )

    parser.add_argument(
        "-e",
        "--env",
        default=False,
        action="store_true",
        dest="env",
        help=(
            "print environment information for bug reporting "
            "(default: '%(default)s')"
        ),
    )

    config, _remainder_args = parser.parse_known_args(args)

    if not config.env:
        parser.add_argument(
            "input_filename",
            help="csv filename",
            type=str,
            metavar="CSV_FILENAME",
            nargs="?" if config.demo else None,  # type: ignore
        )

    if config.demo:
        parser.set_defaults(input_filename=f"{config.output_dir}/sample.csv")
        parser.set_defaults(year=2024)
        parser.set_defaults(week=52)

    cmap_help = "set default colormap"
    cmap_default = f" (default: {DEFAULT_CMAP})"
    if config.verbose:
        cmap_choices = ""
        cmap_bygroups = zip_longest(*(iter(CMAPS),) * 6)
        for cmap_bygroup in cmap_bygroups:
            cmap_choices += ", ".join(filter(None, cmap_bygroup)) + "\n"

        cmap_help = cmap_help + cmap_default + "\n" + cmap_choices
    else:
        cmap_help = cmap_help + ", use -v to show all colormaps" + cmap_default

    parser.add_argument(
        "-t",
        "--title",
        dest="title",
        default=False,
        help="set title for the heatmap (default: '%(default)s')",
    )

    parser.add_argument(
        "-f",
        "--format",
        dest="format",
        default="png",
        help="set the default image format(default: '%(default)s')",
        metavar="IMAGE_FORMAT",
    )

    parser.add_argument(
        "-cm",
        "--cmap",
        choices=plt.colormaps,
        dest="cmap",
        action="append",
        help=cmap_help,
        metavar="COLORMAP",
    )

    parser.add_argument(
        "-cmin",
        "--cmap-min",
        dest="cmap_min",
        default=False,
        help=(
            "set the minimum value of the colormap range "
            "(default: '%(default)s')"
        ),
        metavar="COLORMAP_MIN_VALUE",
    )

    parser.add_argument(
        "-cmax",
        "--cmap-max",
        dest="cmap_max",
        default=False,
        help=(
            "set the maximum value of the colormap range "
            "(default: '%(default)s')"
        ),
        metavar="COLORMAP_MAX_VALUE",
    )

    parser.add_argument(
        "-cb",
        "--cbar",
        default=False,
        action="store_true",
        dest="cbar",
        help="show colorbar (default: '%(default)s')",
    )

    parser.add_argument(
        "-a",
        "--annotate",
        default=False,
        action="store_true",
        dest="annotate",
        help="add count to each heatmap region (default: '%(default)s')",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        default=False,
        action="store_true",
        dest="quiet",
        help="suppress all logging",
    )

    parser.add_argument(
        "-Y",
        "--yes",
        default=False,
        action="store_true",
        dest="yes",
        help="yes to prompt",
    )

    parser.add_argument(
        "-d",
        "--debug",
        default=False,
        action="store_true",
        dest="debug",
        help="show debugging log and stacktrace",
    )

    parser.add_argument(
        "-V", "--version", action="version", version=f"%(prog)s {__version__}"
    )

    parser.add_argument(
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="show this help message and exit",
    )

    parsed_args = parser.parse_args(args)

    if parsed_args.demo:
        # we want to enable all features in demo
        parsed_args.annotate = True
        parsed_args.cbar = True
        parsed_args.cmap = random.sample(CMAPS, parsed_args.demo)
    else:
        parsed_args.cmap = parsed_args.cmap or [DEFAULT_CMAP]

    return parsed_args


def _generate_sample_csv(config: argparse.Namespace) -> None:
    """Generate a sample CSV data file.

    Args:
        config (argparse.Namespace): Config from command line arguments

    Returns:
        None
    """
    if config.demo:
        df_dates = pd.DataFrame(
            {
                "date": pd.date_range(
                    start=f"{config.year}-01-01",
                    end=f"{config.year}-12-31",
                ),
            }
        )
        df_dates["count"] = random.sample(range(12000), len(df_dates))

        csv_filename = Path(config.output_dir, "sample.csv")
        csv_filename.parent.mkdir(parents=True, exist_ok=True)
        df_dates.to_csv(csv_filename, sep=",", index=False, header=False)
        logger.debug("generate sample csv file: %s", csv_filename)


def _massage_data(config: argparse.Namespace) -> pd.core.frame.DataFrame:
    """Filter the data from CSV file.

    Args:
        config (argparse.Namespace): Config from command line arguments

    Returns:
        dataframe (pd.core.frameDataFrame): Filtered Dataframe
    """
    dataframe = pd.read_csv(
        config.input_filename, header=None, names=["date", "count"]
    )
    dataframe["date"] = pd.to_datetime(dataframe["date"])
    dataframe["weekday"] = dataframe["date"].dt.weekday + 1
    dataframe["week"] = dataframe["date"].dt.strftime("%W")
    dataframe["count"] = dataframe["count"].apply(_truncate_rounded_count)

    if config.week == 52:
        steps = dataframe[dataframe["date"].dt.year == config.year]
    else:
        steps = dataframe[
            (dataframe["date"].dt.year == config.year)
            & (dataframe["week"] <= str(config.week).zfill(2))
        ]

    if steps.empty:
        raise ValueError("no data extracted from csv file")

    logger.debug(
        "last date: %s of current week: %s",
        max(steps["date"]).date(),
        config.week,
    )

    pre_missing_steps = pd.DataFrame(
        {
            "date": pd.date_range(
                start=f"{config.year}-01-01",
                end=min(steps["date"]).date() - datetime.timedelta(days=1),
            )
        }
    )
    pre_missing_steps["weekday"] = pre_missing_steps["date"].dt.weekday + 1
    pre_missing_steps["week"] = pre_missing_steps["date"].dt.strftime("%W")
    pre_missing_steps["count"] = 0

    post_missing_steps = pd.DataFrame(
        {
            "date": pd.date_range(
                start=max(steps["date"]).date() + datetime.timedelta(days=1),
                end=f"{config.year}-12-31",
            )
        }
    )
    post_missing_steps["weekday"] = post_missing_steps["date"].dt.weekday + 1
    post_missing_steps["week"] = post_missing_steps["date"].dt.strftime("%W")
    post_missing_steps["count"] = 0

    if not pre_missing_steps.empty:
        steps = pd.concat([pre_missing_steps, steps], ignore_index=True)

    if not post_missing_steps.empty:
        steps = pd.concat([steps, post_missing_steps], ignore_index=True)

    steps.reset_index(drop=True, inplace=True)

    year_dataframe = steps.pivot_table(
        values="count", index=["weekday"], columns=["week"], fill_value=0
    )
    return year_dataframe


def _truncate_rounded_count(count):
    return int(round(count, -2) / 100)


def _generate_heatmap(
    seq: int,
    cmap: str,
    config: argparse.Namespace,
    dataframe: pd.core.frame.DataFrame,
) -> None:
    """Generate a heatmap.

    Args:
        config (argparse.Namespace): Config from command line arguments
        dataframe (pd.core.frameDataFrame): Dataframe with data loaded from CSV
        file

    Returns:
        None
    """
    _fig, axis = plt.subplots(figsize=(8, 5))
    axis.tick_params(axis="both", which="major", labelsize=9)
    axis.tick_params(axis="both", which="minor", labelsize=9)

    cbar_options = {
        "orientation": "horizontal",
        "label": f"generated by: heatmap_cli, colormap: {cmap}",
        "pad": 0.10,
        "aspect": 60,
        "extend": "max",
    }
    options = {
        "ax": axis,
        "fmt": "",
        "square": True,
        "cmap": cmap,
        "cbar": config.cbar,
        "cbar_kws": cbar_options,
    }

    if config.cmap_min:
        options.update({"vmin": config.cmap_min})

    if config.cmap_max:
        options.update({"vmax": config.cmap_max})

    if config.annotate:
        cbar_options.update(
            {
                "label": f"{cbar_options['label']}, count: by hundred",
            }
        )
        options.update(
            {
                "annot": True,
                "annot_kws": {"fontsize": 8},
                "linewidth": 0,
            }
        )

    # convert value larger than 100 to >1
    res = sns.heatmap(dataframe, **options)
    for text in res.texts:
        if int(text.get_text()) >= 100:
            text.set_text(">" + text.get_text()[0])

    img_filename = Path(
        os.getcwd(), config.output_dir, _generate_filename(config, seq, cmap)
    )
    img_filename.parent.mkdir(parents=True, exist_ok=True)

    axis.set_title(_generate_title(config), fontsize=11, loc="left")
    axis.set_title("kianmeng.org", fontsize=11, loc="right")
    plt.tight_layout()
    plt.savefig(
        img_filename,
        bbox_inches="tight",
        transparent=False,
        dpi=76,
        format=config.format,
    )
    logger.info("generate heatmap: %s", img_filename)

    if config.open:
        _open_heatmap(img_filename)


def _open_heatmap(filename):
    """Open generated heatmap using default program."""
    if sys.platform == "linux":
        subprocess.call(["xdg-open", filename])
    elif sys.platform == "darwin":
        subprocess.call(["open", filename])
    elif sys.platform == "windows":
        os.startfile(filename)

    logger.info("open heatmap: %s using default program.", filename.resolve())


def _generate_filename(config: argparse.Namespace, seq: int, cmap: str) -> str:
    """Generate a PNG filename.

    Args:
        config (argparse.Namespace): Config from command line arguments

    Returns:
        str: A generated file name for the PNG image
    """
    annotated = ""
    if config.annotate:
        annotated = "_annotated"

    filename = (
        f"{annotated}_heatmap_of_total_daily_walked_steps_count"
        f".{config.format}"
    )
    if config.week == 52:
        return f"{seq:03}_{config.year}_{cmap}" + filename

    return f"{seq:03}_{config.year}_week_{config.week}_{cmap}" + filename


def _generate_title(config: argparse.Namespace) -> str:
    """Run the main flow.

    Args:
        config (argparse.Namespace): Config from command line arguments

    Returns:
        str: A generated title for the heatmap title
    """
    if not config.title:
        title = f"Year {config.year}: Total Daily Walking Steps"
        if config.week != 52:
            title = f"{title} Through Week {config.week}"
    else:
        title = config.title

    logger.debug(title)
    return title


def _refresh_output_dir(config: argparse.Namespace) -> None:
    """Delete, and recreate the output folder.

    Args:
        config (argparse.Namespace): Config from command line arguments

    Returns:
        None
    """
    output_dir = _get_output_dir(config)
    if config.purge and output_dir.exists():
        if config.yes:
            _recrete_output_folder(output_dir)
        else:
            prompt = (
                "Are you sure to purge output folder: "
                f"{output_dir.absolute()}? [y/N] "
            )
            answer = input(prompt)
            if answer.lower() == "y":
                _recrete_output_folder(output_dir)


def _recrete_output_folder(output_dir) -> None:
    """Recreate the output folder.

    Args:
        outputdir (str): Output directory path

    Returns:
        None
    """
    logger.info("purge output folder: %s", output_dir.absolute())
    shutil.rmtree(output_dir)
    logger.info("create output folder: %s", output_dir.absolute())
    output_dir.mkdir(parents=True, exist_ok=True)


def _get_output_dir(config: argparse.Namespace) -> Path:
    """Get the current working directory.

    Args:
        config (argparse.Namespace): Config from command line arguments

    Returns:
        str
    """
    output_dir = Path(config.output_dir)
    if output_dir.is_absolute():
        return output_dir

    return Path(os.getcwd(), config.output_dir)


def _run(config: argparse.Namespace) -> None:
    """Run the main flow.

    Args:
        config (argparse.Namespace): Config from command line arguments

    Returns:
        None
    """
    logger.debug(config)
    logger.debug("number of cpu: %d", multiprocessing.cpu_count())

    if not config.env:
        _refresh_output_dir(config)
        _generate_sample_csv(config)

        dataframe = _massage_data(config)
        args = [
            (*seq_cmap, config, dataframe)
            for seq_cmap in enumerate(config.cmap, 1)
        ]

        # fork, instead of spawn process (child) inherit parent logger config
        # see https://stackoverflow.com/q/14643568
        with multiprocessing.get_context("fork").Pool() as pool:
            pool.starmap(_generate_heatmap, args)
    else:
        print_env()


def print_env() -> None:
    """Print environment details for bug reporting.

    Returns:
        None
    """
    sys_version = sys.version.replace("\n", "")
    print(
        f"heatmap: {__version__}",
        f"python: {sys_version}",
        f"platform: {platform.platform()}",
        sep="\n",
    )


def _setup_logging(config: argparse.Namespace) -> None:
    """Set up logging by level.

    Args:
        debug (boolean): Whether to toggle debugging logs

    Returns:
        None
    """
    if config.quiet:
        logging.disable(logging.NOTSET)
    else:
        conf: Dict = {
            True: {
                "level": logging.DEBUG,
                "format": (
                    "[%(asctime)s] %(levelname)s: %(processName)s: %(message)s"
                ),
            },
            False: {
                "level": logging.INFO,
                "format": "%(message)s",
            },
        }

        logger.setLevel(conf[config.debug]["level"])
        formatter = logging.Formatter(conf[config.debug]["format"])
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        if not config.debug:
            logger.addFilter(
                lambda record: not record.getMessage().startswith(
                    ("child", "process")
                )
            )


def main(args: Optional[Sequence[str]] = None) -> None:
    """Run the main program flow.

    Args:
        args (List | None): Argument passed through the command line

    Returns:
        None
    """
    try:
        parsed_args = _parse_args(args)
        _setup_logging(parsed_args)
        _run(parsed_args)
    except Exception as error:
        logger.error(
            "error: %s", getattr(error, "message", str(error)), exc_info=True
        )
        raise SystemExit(1) from None
