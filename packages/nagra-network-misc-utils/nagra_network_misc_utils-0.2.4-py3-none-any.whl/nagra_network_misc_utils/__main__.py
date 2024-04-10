import logging

import click

from . import backend_checker
from .logger import set_default_logger


@click.version_option("0.1.0", prog_name="Pipelines")
@click.group()
def cli():
    logging.getLogger().setLevel(logging.INFO)
    set_default_logger()


cli.add_command(backend_checker.check_pipeline_status)
cli.add_command(backend_checker.trigger_pipeline)

if __name__ == "__main__":
    cli()
