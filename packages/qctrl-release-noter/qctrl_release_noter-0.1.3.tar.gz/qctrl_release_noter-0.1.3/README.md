# Q-CTRL Release Noter

The Q-CTRL Release Noter Python package provides a command line tool that generates the recommended release notes for a GitHub package from Q-CTRL.

## Installation

Install the Q-CTRL Release Noter with:

```shell
pip install qctrl-release-noter
```

## Usage

In the repository whose release notes you want to generate, run:

```shell
release_noter
```

You can also specify the path of the repository:

```shell
release_noter /path/to/repository
```

To prefill the information on the GitHub release page, use:

```shell
release_noter --github
```
