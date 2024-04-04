# git-stats-report

| PyPI    | [![PyPI Downloads](https://img.shields.io/pypi/dm/git-stats-report?style=for-the-badge&label=Installations&color=steelblue&logo=pypi)](https://pypistats.org/packages/git-stats-report) [![PyPI Version](https://img.shields.io/pypi/v/git-stats-report?style=for-the-badge&logo=pypi)](https://pypi.org/project/git-stats-report/) ![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/juanjfarina/git-stats-report/test.yml?style=for-the-badge&logo=githubactions&label=CICD) <br> ![Unreleased Commits](https://img.shields.io/github/commits-difference/juanjfarina/git-stats-report?base=develop&head=master&style=for-the-badge&logo=git&label=Unreleased%20Commits) ![Last Released date](https://img.shields.io/github/last-commit/juanjfarina/git-stats-report/master?style=for-the-badge&logo=git&label=Last%20Released%20on) 	|
|---------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	|
| Quality | [![Coveralls branch](https://img.shields.io/coverallsCoverage/github/JuanJFarina/git-stats-report?branch=master&style=for-the-badge&logo=coveralls)](https://coveralls.io/github/JuanJFarina/git-stats-report) [![Code Climate maintainability](https://img.shields.io/codeclimate/maintainability/JuanJFarina/git-stats-report?style=for-the-badge&logo=codeclimate)](https://codeclimate.com/github/JuanJFarina/git-stats-report) [![Code Climate technical debt](https://img.shields.io/codeclimate/tech-debt/JuanJFarina/git-stats-report?style=for-the-badge&logo=codeclimate)](https://codeclimate.com/github/JuanJFarina/git-stats-report) <br> ![OSSF-Scorecard Score](https://img.shields.io/ossf-scorecard/github.com/JuanJFarina/git-stats-report?style=for-the-badge&label=OpenSSF%20Score) [![Dependabot](https://img.shields.io/badge/Dependabot-Enabled-brightgreen?style=for-the-badge&logo=dependabot)](https://github.com/JuanJFarina/git-stats-report/blob/master/.github/dependabot.yml)                                                                                                           	|
| Format  | ![Conventional Commits](https://img.shields.io/badge/semantic--release-conventional-steelblue?logo=semantic-release&style=for-the-badge) ![Commitlint](https://img.shields.io/badge/commitlint-%E2%9C%93-brightgreen?logo=commitlint&style=for-the-badge) <br> ![Pre Commit](https://img.shields.io/badge/Pre--Commit-%E2%9C%93-brightgreen?style=for-the-badge&logo=precommit) ![Format](https://img.shields.io/badge/Format-Ruff-brightgreen?style=for-the-badge&color=black) ![Linting](https://img.shields.io/endpoint?url=https%3A%2F%2Fraw.githubusercontent.com%2Fcharliermarsh%2Fruff%2Fmain%2Fassets%2Fbadge%2Fv2.json&style=for-the-badge&label=Linting)                                                                                                                                	|
| Legal   | [![FOSSA Status](https://img.shields.io/badge/LICENSE%20SCAN-PASSING-CD2956?style=for-the-badge&logo=fossa)](https://app.fossa.com/projects/git%2Bgithub.com%2FJuanJFarina%2Fgit-stats-report) [![PyPI - License](https://img.shields.io/pypi/l/git-stats-report?style=for-the-badge&logo=opensourceinitiative)](./LICENSE) ![Commercial Use](https://img.shields.io/badge/Comercial_Use-%E2%9C%93-brightgreen?style=for-the-badge)                                                                                                                                                                                                                                                                                                                                                                                  	|

🔍 Git Stats Reports 🔍

## Usage

Use the --help flag for detailed options:

```shell
git-stats-report --help
```

git-stats-report can be used in different ways, the most straightforward one is:

```shell
git-stats-report
```

This will return statistics for each contributor since the last merge commit

## Installation


### With Pipx

Recommended instalation for CICD is through `pipx` with a pinned version:

```shell
pip install pipx==1.2.0
pipx run git-stats-report==0.2.0
```

That command will create a virtual environment just for git-stats-report and return the
report.

### With pip

Instalation can be done with pip as usual:

```shell
pip install git-stats-report
```

Pipenv and poetry equivalents can be used as well.

## F.A.Q.

## License

[![FOSSA Status](https://app.fossa.com/api/projects/git%2Bgithub.com%2FJuanJFarina%2Fgit-stats-report.svg?type=large)](https://app.fossa.com/projects/git%2Bgithub.com%2FJuanJFarina%2Fgit-stats-report)
