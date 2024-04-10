#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Aqua RegScale integration"""
from datetime import datetime
from os import PathLike
from pathlib import Path

import click

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.models.integration_models.aqua import Aqua
from regscale.models.integration_models.container_scan import ContainerScan
from regscale.validation.record import validate_regscale_object


@click.group()
def aqua():
    """Performs actions on Aqua Scanner artifacts."""


@aqua.command(name="import_aqua")
@ContainerScan.common_scanner_options(
    message="File path to the folder containing Aqua .csv files to process to RegScale.",
    prompt="File path for Aqua files:",
)
def import_aqua(folder_path: PathLike[str], regscale_ssp_id: int, scan_date: datetime):
    """
    Import Nessus scans, vulnerabilities and assets to RegScale from Aqua files
    """
    app = Application()
    if not validate_regscale_object(regscale_ssp_id, "securityplans"):
        app.logger.warning("SSP #%i is not a valid RegScale Security Plan.", regscale_ssp_id)
        return
    if not scan_date or not ContainerScan.check_date_format(scan_date):
        scan_date = datetime.now()
    if len(list(Path(folder_path).glob("*.csv"))) == 0:
        app.logger.warning("No Aqua(csv) files found in the specified folder.")
        return
    for file in Path(folder_path).glob("*.csv"):
        Aqua(
            name="Aqua",
            app=app,
            file_path=file,
            parent_id=regscale_ssp_id,
            parent_module="securityplans",
            scan_date=scan_date,
        )
