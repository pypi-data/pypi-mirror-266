# Overview

RepMan or Repository Manager is written on python to serve as GitHub Repo Manager for the end users.

Have a lot of repositories you've been working on? Is it a hassle? RepMan is your solution.

## What RepMan offers

- RepMan will organize all the github repos you have under one management.
- RepMan will help you find your repositories and update them (add, commit and push the changes.)
- RepMan will help you start working on your project right away with just one command.
- More to come.

## Requirements

- python>=3.9

### Note

- Currently supports only Visual Studio Code as the default editor.
- In MacOS arm64 and Debian Linux aarch64, if vscode and git are not installed, it will be automatically installed using `-i` or `--init` option of RepMan.
- In other Operating Systems, it is recommended to have Visual Studio Code and Git pre-installed.

- Git Installations
    ```bash
    # for Debian Linux,
    sudo apt install git

    # for macOS, use homebrew or other package managers

    # for windows, download the windows installer from the git-scm website.

    # for installation using homebrew
    brew install git
    ```
    For Other Operating systems, visit the official site of [ [git](https://git-scm.com/downloads) ] to download respective supported versions of git.

- Visual Studio Code Installation

    ```bash
    # if you have home brew
    brew install --cask visual-studio-code
    ```
    Else, Go to [ [Visual Studio Code](https://code.visualstudio.com/download) ] to download for your OS.

- Supports all versions of Apple Laptops with Apple Silicon chip and arm64 architecture.

### Git setup Note

Git requires git credential manager to log in to your account so that you can clone private repositories. In windows, it is by default installed while installing git using the gui installer. But in other Operating Systems, it needs to be installed and configured manually.

I'd suggest to use GitHub Cli instead to manage your credentials.

- Installation:
    ```bash
    # using homebrew,
    brew install gh

    # or in debian Linux,
    sudo apt install gh
    ```
- setup
    ```bash
    # run the following command in terminal and follow the steps 
    gh auth login
    ```

## Installation

RepMan is very easy to install.

```bash
# install using pip

pip install RepMan
```
```bash
# install by cloning this git repository.

git clone https://github.com/d33pster/RepMan.git
cd RepMan
pip install .
```

After installation, run the following command. (make sure to install vscode and git if you're not using the supported OS.)
```bash
repman -i

# or

repman --init
```

## Usage

For usage, run

```bash
repman -h

# or

repman --help
```

For option specific help, run

```bash
repman <option> -h

# or 

repman <option> --help
```

## Supported OS and architectures and notes
- MacOS (Apple Silicon Chip - M series) (Arch - arm64) (Requires Homebrew)
- Linux (Debian) (Arch - aarch64)
- **If your OS and arch is not listed here, just make sure to install VSCode and git on your own, rest is same.**

## Uninstall

Uninstall using pip
```bash
pip uninstall RepMan
```