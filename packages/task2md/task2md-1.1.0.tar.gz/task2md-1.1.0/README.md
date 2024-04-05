# `task2md`

[![Software License](https://img.shields.io/badge/license-MIT-informational.svg?style=for-the-badge)](LICENSE)
[![semantic-release: angular](https://img.shields.io/badge/semantic--release-angular-e10079?logo=semantic-release&style=for-the-badge)](https://github.com/semantic-release/semantic-release)
[![Pipeline Status](https://gitlab.com/op_so/task/task2md/badges/main/pipeline.svg)](https://gitlab.com/op_so/task/task2md/pipelines)

[![Built with Material for MkDocs](https://img.shields.io/badge/Material_for_MkDocs-526CFE?style=for-the-badge&logo=MaterialForMkDocs&logoColor=white)](https://op_so.gitlab.io/task/task2md/) Source code documentation

A CLI tool to generate from [Task](https://taskfile.dev/) files, some markdown
documentation files for [`mkdocs`](https://squidfunk.github.io/mkdocs-material/) static site.

```bash
Usage: task2md [OPTIONS] COMMAND [ARGS]...

  A CLI tool to generate markdown documentation files from Task files.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  dir   Command to generate a markdown documentation file from a directory.
  file  Command to generate a markdown documentation file from a Task file.
```

## `dir`

Get all files with `yaml/yml` extension from the input directory and generate the
markdown files in the output directory.

```bash
Usage: task2md dir [OPTIONS]

  Command to generate a markdown documentation file from a directory.

  Raises:     click.ClickException: Error when reading input file or writing
  output file

Options:
  -i, --input DIRECTORY  Input directory  [required]
  -d, --dir DIRECTORY    Output markdown documentation files directory.
                         Default current directory.
  --help                 Show this message and exit.
```

Example:

```bash
task2md dir --input Taskfile.d/ -d doc_dir/
```

## `file`

Generate from the input file a markdown file in the output directory.

```bash
Usage: task2md file [OPTIONS]

  Command to generate a markdown documentation file from a Task file.

  Raises:     click.ClickException: Error when reading input file or writing
  output file

Options:
  -i, --input FILE     Input Task yaml file.  [required]
  -d, --dir DIRECTORY  Output markdown documentation files directory. Default
                       current directory.
  --help               Show this message and exit.
```

Example:

```bash
task2md file --input Taskfile.d/lint.yml -d doc_dir/
```

## Installation

### With `Python` environment

To use:

- Minimal Python version: 3.10

Installation with Python `pip`:

```bash
python3 -m pip install task2md
task2md --help
```

## Authors

<!-- vale off -->
- **FX Soubirou** - *Initial work* - [GitLab repositories](https://gitlab.com/op_so)
<!-- vale on -->

## License

<!-- vale off -->
This program is free software: you can redistribute it and/or modify it under the terms of the MIT License (MIT).
See the [LICENSE](https://opensource.org/licenses/MIT) for details.
<!-- vale on -->
