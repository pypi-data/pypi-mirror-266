# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [0-based versioning](https://0ver.org/).

## [Unreleased]

## v0.12.0 (2024-04-07)

### Added

- Add `-f` or `--format` option to set the heatmap image format

### Changed

- Update help message in README
- Bump deps

## v0.11.6 (2024-03-31)

### Changed

- Update help message in README
- Bump deps

### Fixed

- Fix incorrect label when walking steps exceeding 20k

## v0.11.5 (2024-03-24)

### Added

- Test `--env` flag

### Fixed

- Fix newline in the `sys.version` output on Python 3.8

## v0.11.4 (2024-03-17)

### Added

- Add program name to colourbar label

### Changed

- Bump deps and `pre-commit` hooks

### Fixed

- Add default value for `--env` in help message
- Fix incorrect headers in changelog

## v0.11.3 (2024-03-10)

### Changed

- Update help message in README
- Bump `pre-commit` hooks

### Fixed

- Fix missing closing parenthesis in description

## v0.11.2 (2024-03-03)

### Changed

- Adjust the width (aspect) of the colour bar to 60
- Resize the padding between the colour bar and heatmap to 0.10
- Remove unused options to generation heatmap
- Fit annotated value by converting value larger than 100 to `>1`
- Set and left align the heatmap title by axis
- Extend the max value of the colorbar with arrow
- Align the heatmap title and domain name to left and right
- Revise the heatmap title correctly

### Fixed

- Set to current year and last week when generating demo heatmaps

## v0.11.1 (2024-02-25)

### Fixed

- Update help message in README

## v0.11.0 (2024-02-18)

### Added

- Add `-o` or `--open` flag to open the generated heatmap using default program

## v0.10.1 (2024-02-11)

### Changed

- Add missing types in doc
- Remove `creosote` pre-commit hook

## v0.10.0 (2024-02-04)

### Added

- Add `-e` or `--env` flag for printing environment details for bug reporting

## v0.9.3 (2024-01-28)

### Added

- Add instruction on upgrade

### Fixed

- Fix incorrect return type

## v0.9.2 (2024-01-21)

### Fixed

- Fix incorrect long title option name

### Changed

- Exclude `__repr__` from test coverage

## v0.9.1 (2024-01-14)

### Fixed

- Fix incorrect help message in readme
- Add missing markdown markup

## v0.9.0 (2024-01-07)

### Added

- Add `-cmin` or `--cmap-min` to set minimum value of the colormap range
- Add `-cmax` or `--cmap-max` to set maximum value of the colormap range

### Changed

- Bump copyright year

### Fixed

- Pre-fill dataframe that start from middle of the year
- Fix test errors due to current year assertion

## v0.8.8 (2023-12-31)

### Changed

- Add additional `pre-commit` hooks
- Bump Python versions for `pyenv` environment
- Replace `.prettierignore` config with `pre-commit` config

### Fixed

- Fix test default title error when running the test in week 52

## v0.8.7 (2023-12-24)

### Added

- Add `creosote` pre-commit hook

### Changed

- Support all or latest Python versions for pre-commit hooks
- Sort deps in Pipfile

## v0.8.6 (2023-12-17)

### Added

- Randomize test cases through `pytest-randomly`

## v0.8.5 (2023-12-10)

### Fixed

- Only log output folder creation message when needed

### Changed

- Refactor output folder re-creation

## v0.8.4 (2023-12-03)

### Fixed

- Only create `sample.csv` file after refreshing the output folder

### Changed

- Show purging output folder actions at logging.INFO level
- Update help message in README.md

## v0.8.3 (2023-11-26)

### Fixed

- Check if output directory path is absolute path
- Do not append absolute output directory path to current working directory
- Revise the pre-conditions before purging output directory
- Update outdated help message in README

### Changed

- Always create the output folder
- Allow scriptttest runner to accept keyword args
- Enable all `--purge` flag related tests

## v0.8.2 (2023-11-19)

### Added

- Add `-Y` or `--yes` flag to confirm any prompts

### Changed

- Add Developer's Certificate of Origin (DCO) to contributing doc

## v0.8.1 (2023-11-12)

### Changed

- Add additional tests on `--purge` flag
- Prompt before purging output folder

### Fixed

- Fix incorrect editable installation of itself in default environment
- Fix and update incorrect help message

## v0.8.0 (2023-11-05)

### Added

- Add `-p` or `--purge` flag to remove generated heatmaps specified by
  `--output-folder` option

### Changed

- Refactor script_runner cli fixture

## v0.7.1 (2023-10-29)

### Fixed

- Remove extra space on title when week is set to last week (52) of the year

### Changed

- Add additional tests for `--title` option
- Bump Python's version for `pyenv`
- Use short code for `pylint` disabling rules

## v0.7.0 (2023-10-22)

### Added

- Add `-t` or `--title` option to set title for heatmap

### Fixed

- Add missing classifier

## v0.6.0 (2023-10-15)

### Added

- Add `-cb` or `--cbar` flag to toggle colourbar

### Changed

- Show all features (annotation, and colorbar) when generating demo heatmaps

### Fixed

- Fix incorrect output when testing help message

## v0.5.2 (2023-10-13)

### Fixed

- Fix incorrect coverage omit pattern
- Fix duplicate path of `cov` environment in `tox`

## v0.5.1 (2023-10-08)

### Added

- Support Python 3.12.0

### Fixed

- Fix total number of heatmap not showing

## v0.5.0 (2023-10-01)

### Added

- Add `-a` or `--annotate` flag to add count to each heatmap region
- Add `-q` or `--quiet` flag to suppress logging
- Add `flake8-print` and `flake8-simplify` for `pre-commit` check
- Add `heatmap` as alias to `heatmap_cli`

### Changed

- Refactor annotated count calculation
- Set annotated font size to 8 to better readability

## v0.4.5 (2023-09-24)

### Fixed

- Add missing `flake8` related deps in dev environment

### Changed

- Allow to generate number of heatmaps by setting `--demo` option
- Filter log record from subprocess by default (`debug` flag is disabled)
- Shorten the logging message when generating PNG file to fit screen width
- Sort test coverage report by coverage percentage

## v0.4.4 (2023-09-17)

### Fixed

- Fix logging not working in child process by switching pooling method from
  spawn to fork
- Suppress `nargs` incompatible type warning

## v0.4.3 (2023-09-11)

### Fixed

- Fix incorrect log format

## v0.4.2 (2023-09-10)

### Changed

- Refactor setting default CSV filename for `--demo` flag

### Fixed

- Use correct `pyenv` wording in contributing doc
- Fix logging not using the config from command line flag

## v0.4.1 (2023-09-03)

### Added

- Optimize heatmaps generation using pooling
- Use generated sample CSV file upon `--demo` flag

### Changed

- Prepend sequence number to output PNG filename
- Refactor colormaps initialization
- Show all colormaps in help message upon `-v`, or `--verbose` flag
- Switch `pytest-console-script` to `scripttest` due to failure to capture
  worker logs

### Fixed

- Ignore default `output` folder

## v0.4.0 (2023-08-27)

### Added

- Add `-dm` or `--demo` flag to generate all heatmaps by colormap
- Add `-od` or `--output-dir` option to set a default output folder for
  generated heatmaps

### Changed

- Bump Python versions for `pyenv`
- Changelog url should comes before issue url

### Fixed

- Fix two underscores in PNG filename

## v0.3.2 (2023-08-20)

### Changed

- Generate multiple heatmaps at once by different colormaps through `-cm`
  option

## v0.3.1 (2023-08-13)

### Changed

- Add logging for `-wk` related usages
- Sort URLs in project config

### Fixed

- Fix incorrect changelog URL
- Fix title without proper spacing

## v0.3.0 (2023-08-06)

### Added

- Add additional default hook for `pre-commit`
- Add `-cm` or `--cmap` option to set a default colormap

### Changed

- Rename test files based on the right term
- Add missing tests for `-wk` option

### Fixed

- Fix incorrect coverage configs
- Fix incorrect changelog URL

## v0.2.2 (2023-07-30)

### Added

- Add changelog URL to help message
- Add missing documentation for functions

### Changed

- Set title and PNG filename to year only when week is set to 52
- Reset DataFrame index after the last filtering step
- Move some coverage configs to `tox.ini` file

### Fixed

- Fix incorrect header level in changelog
- Fix incorrect source module in coverage config file

## v0.2.1 (2023-07-28)

### Changed

- Move `coverage` config from `tox` to its own file
- Reset DataFrame index after filtering

### Fixed

- Show verbose log of last date of current week
- Fix incorrect header level in changelog

## v0.2.0 (2023-07-23)

### Added

- Add `yr` or `--year` argument to filter CSV data by year
- Add `wk` or `--week` argument to filter CSV data until week of the year
- Add additional pre-commit default checks
- Show generated PNG filename upon completion

### Changed

- Group all `sphinx` related deps under the `doc` category
- Standardize `tox` environment names

### Fixed

- Fix incorrect ignored coverage module
- Suppress logging from `matplotlib` in `debug` mode

## v0.1.3 (2023-07-16)

### Fixed

- Fix missing `pylint` dependency when running `pre-commit`
- Ignore word when running `codespell` pre-commit hook

## v0.1.2 (2023-07-11)

### Changed

- Link to license from contributing doc
- Use the same output folder for `sphinx` doc generation
- Revise `pyenv` installation with plugins in contributing doc
- Install `heatmap_cli` as editable installation in `pipenv` dev env

## v0.1.1 (2023-07-09)

### Fixed

- Fix missing dependencies on `pipx` installation
- Fix incorrect module name in `pre-commit` hooks

## v0.1.0 (2023-07-08)

### Added

- Initial public release
