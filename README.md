Copyright Updater
===================

## Overview
Add or replace license/copyright boilerplate in source code files.

## Features
- Add multiple source code directories.
- Autodetect file type and update with proper format.
- Custom configuration for more file type and copyright format.
- Python 2 and 3 supported.

## Usage
Configure the `rule.yaml` first. And then
```shell
python copyright.py -c rule.yaml
```

## Notice
If your copyright/license comment adheres to your other comment without any blank lines,
your comment will be erased. So leave a blank line between your copyright/license and other comments.
