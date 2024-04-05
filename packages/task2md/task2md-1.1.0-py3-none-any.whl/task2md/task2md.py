# -*- coding: utf-8 -*-

import os
from typing import List

import click

from task2md.template.file import File
from task2md.template.index import Index
from task2md.util.dir import Dir


@click.group()
@click.version_option("1.1.0", prog_name="task2md")
def cli() -> None:
    """A CLI tool to generate markdown documentation files from Task files."""
    pass


@cli.command()
@click.option(
    "-i",
    "--input",
    "input_dir",
    type=click.Path(exists=True, file_okay=False, dir_okay=True),
    required=True,
    help="Input directory",
)
@click.option(
    "-d",
    "--dir",
    "output_dir",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True),
    required=False,
    help="Output markdown documentation files directory. Default current directory.",
)
def dir(
    input_dir: click.Path,
    output_dir: click.Path,
) -> None:
    """Command to generate a markdown documentation file from a directory.

    Raises:
        click.ClickException: Error when reading input file or writing output file
    """
    task_files: List[str] = []
    in_dir = click.format_filename(str(input_dir))
    for filename in os.listdir(in_dir):
        if filename.endswith(".yml") or filename.endswith(".yaml"):
            task_files.append(filename)

    if len(task_files) == 0:
        click.echo(f"No yaml file found in: {in_dir}")
    else:
        try:
            out_dir = Dir(output_dir, True)

        except OSError as error:
            raise click.ClickException(
                "Output directory can not be created!\n" + str(error)
            )

        try:
            index_file = Index()
            for filename in task_files:
                task_file = File(path=f"{in_dir}/{filename}")
                task_file.generate(out_dir)

                index_file.task_files.append(task_file)

                click.echo(
                    f"Task documentation generated: {task_file.get_filename()}.md"
                )
            filename = "index"
            index_file.generate(out_dir)
            click.echo("Index documentation generated: index.md")

        except ValueError as ve:
            raise click.ClickException(
                "Error on reading or writing file {} :\n {}".format(filename, str(ve))
            )


@cli.command()
@click.option(
    "-i",
    "--input",
    "input_file",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
    help="Input Task yaml file.",
)
@click.option(
    "-d",
    "--dir",
    "output_dir",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True),
    required=False,
    help="Output markdown documentation files directory. Default current directory.",
)
def file(
    input_file: click.Path,
    output_dir: click.Path,
) -> None:
    """Command to generate a markdown documentation file from a Task file.

    Raises:
        click.ClickException: Error when reading input file or writing output file
    """
    input_filename = click.format_filename(str(input_file))
    task_file = File(path=input_filename)

    try:
        dir = Dir(output_dir, True)

    except OSError as error:
        raise click.ClickException(
            "Output directory can not be created!\n" + str(error)
        )

    try:
        task_file.generate(dir)

        click.echo(f"Task documentation generated: {task_file.get_filename()}.md")

    except ValueError as ve:
        raise click.ClickException(
            "Error on reading file {} :\n {}".format(input_filename, str(ve))
        )


if __name__ == "__main__":
    cli()  # pragma: no cover
