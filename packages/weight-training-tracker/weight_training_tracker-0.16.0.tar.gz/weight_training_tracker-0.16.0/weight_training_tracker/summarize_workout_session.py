"""Parse a workout YAML file and generate a simple summary"""
import click
import logging
import json
import os
import pathlib
import pydantic
import sys
import yaml

from datetime import datetime
from rich.console import Console
from rich.table import Table
from typing import Any, Dict, List, Optional

from . import constants
from .file_utils import check_infile_status
from .parser import Parser

DEFAULT_TIMESTAMP = str(datetime.today().strftime('%Y-%m-%d-%H%M%S'))

DEFAULT_OUTDIR = os.path.join(
    constants.DEFAULT_OUTDIR_BASE,
    os.path.splitext(os.path.basename(__file__))[0],
    constants.DEFAULT_TIMESTAMP
)


error_console = Console(stderr=True, style="bold red")

console = Console()




def summarize_workout_session(
        config: Dict[str, Any],
        infile: str,
        outdir: str,
        verbose: bool,
        logfile: str
    ) -> None:
    """Summarize the workout session.

    Args:
        config (Dict[str, Any]): The configuration.
        infile (str): The input file.
        outdir (str): The output directory.
        verbose (bool): The verbose flag.
        logfile (str): The log file.
    """
    logging.info(f"Will load contents of infile '{infile}'")
    parser = Parser(infile=infile)
    workout_session = parser.get_workout()

    print(f"Workout Date: {workout_session.date}")
    print(f"Start Time: {str(workout_session.start_timestamp).split(' ')[1].split('.')[0]}")
    print(f"End Time: {str(workout_session.end_timestamp).split(' ')[1].split('.')[0]}")
    print(f"Elapsed Time: {workout_session.elapsed_time}")

    table = Table(
        show_header=True,
        header_style="bold #2070b2",
        title="[bold]Workout Summary[/]"
    )

    table.add_column("Exercise", justify="left")
    table.add_column("Set", justify="center")
    table.add_column("L-RPS", justify="right")
    table.add_column("L-WT", justify="right")
    table.add_column("R-RPS", justify="right")
    table.add_column("R-WT", justify="right")
    table.add_column("RPS", justify="right")
    table.add_column("WT", justify="right")


    for exercise in workout_session.exercises:
        exercise_name = exercise.name
        for i, set in enumerate(exercise.sets, start=1):

            leftside_reps = str(set.leftside_reps) if set.leftside_reps is not None else ""
            leftside_weight = str(set.leftside_weight) if set.leftside_weight is not None else ""
            rightside_reps = str(set.rightside_reps) if set.rightside_reps is not None else ""
            rightside_weight = str(set.rightside_weight) if set.rightside_weight is not None else ""
            reps = str(set.reps) if set.reps is not None else ""
            weight = str(set.weight) if set.weight is not None else ""

            table.add_row(
                exercise_name,
                f"{i}",
                leftside_reps,
                leftside_weight,
                rightside_reps,
                rightside_weight,
                reps,
                weight
            )

    console.print(table)


def validate_verbose(ctx, param, value):
    """Validate the validate option.

    Args:
        ctx (Context): The click context.
        param (str): The parameter.
        value (bool): The value.

    Returns:
        bool: The value.
    """

    if value is None:
        click.secho("--verbose was not specified and therefore was set to 'True'", fg='yellow')
        return constants.DEFAULT_VERBOSE
    return value



@click.command()
@click.option('--config_file', type=click.Path(exists=True), help=f"Optional: The configuration file for this project - default is '{constants.DEFAULT_CONFIG_FILE}'")
@click.option('--infile', help="Required: The input workout YAML file to be parsed and summaried.")
@click.option('--logfile', help="Optional: The log file")
@click.option('--outdir', help=f"Optional: The default is the current working directory - default is '{DEFAULT_OUTDIR}'")
@click.option('--verbose', is_flag=True, help=f"Optional: Will print more info to STDOUT - default is '{constants.DEFAULT_VERBOSE}'.", callback=validate_verbose)
def main(
    config_file: str,
    infile: str,
    logfile: str,
    outdir: str,
    verbose: bool
    ):
    """Parse a workout YAML file and generate a simple summary"""
    error_ctr = 0

    if infile is None:
        error_console.print("--infile was not specified")
        error_ctr += 1

    if error_ctr > 0:
        click.echo(click.get_current_context().get_help())
        sys.exit(1)

    if config_file is None:
        config_file = constants.DEFAULT_CONFIG_FILE
        console.print(f"[yellow]--config_file was not specified and therefore was set to '{config_file}'[/]")

    if outdir is None:
        outdir = DEFAULT_OUTDIR
        console.print(f"[yellow]--outdir was not specified and therefore was set to '{outdir}'[/]")

    if not os.path.exists(outdir):
        pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)

        console.print(f"[yellow]Created output directory '{outdir}'[/]")

    if logfile is None:
        logfile = os.path.join(
            outdir,
            os.path.splitext(os.path.basename(__file__))[0] + '.log'
        )
        console.print(f"[yellow]--logfile was not specified and therefore was set to '{logfile}'[/]")


    logging.basicConfig(
        filename=logfile,
        format=constants.DEFAULT_LOGGING_FORMAT,
        level=constants.DEFAULT_LOGGING_LEVEL,
    )

    check_infile_status(config_file, "yaml")

    logging.info(f"Will load contents of config file '{config_file}'")
    config = yaml.safe_load(pathlib.Path(config_file).read_text())

    summarize_workout_session(
        config,
        infile,
        outdir,
        verbose,
        logfile
    )

    if verbose:
        console.print(f"The log file is '{logfile}'")
        console.print(f"[bold green]Execution of '{os.path.abspath(__file__)}' completed[/]")


if __name__ == "__main__":
    main()

