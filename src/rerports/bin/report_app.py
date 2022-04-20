# -*- coding: utf-8 -*-
from pathlib import Path
from typing import Optional

import typer

from reports.config import get_logger, set_logging
from reports.controllers.run_report import generate_master
from reports.spotfire.tank_measurement import get_tank_volume

logger = get_logger(__name__)

app = typer.Typer()


@app.command("master-report")
def master_report(logging_file: Optional[Path] = None):
    set_logging(logging_file, log=True)
    logger.info("Starting master report")
    generate_master()


@app.command("tank-volume")
def tank_volume():
    get_tank_volume()


def main():
    app()


if __name__ == "__main__":
    typer.run(main)
