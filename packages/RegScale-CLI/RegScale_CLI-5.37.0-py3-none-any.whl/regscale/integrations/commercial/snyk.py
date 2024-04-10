#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Snyk RegScale integration"""
from datetime import datetime
from os import PathLike
from pathlib import Path

import click

from regscale.core.app.application import Application
from regscale.models.integration_models.container_scan import ContainerScan
from regscale.models.integration_models.snyk import Snyk
from regscale.validation.record import validate_regscale_object


@click.group()
def snyk():
    """Performs actions on Snyk export files."""


@snyk.command(name="import_snyk")
@ContainerScan.common_scanner_options(
    message="File path to the folder containing Snyk .xlsx files to process to RegScale.",
    prompt="File path for Snyk files:",
)
def import_snyk(folder_path: PathLike[str], regscale_ssp_id: int, scan_date: datetime):
    """
    Import scans, vulnerabilities and assets to RegScale from Snyk export files

    """
    app = Application()
    if not validate_regscale_object(regscale_ssp_id, "securityplans"):
        app.logger.warning("SSP #%i is not a valid RegScale Security Plan.", regscale_ssp_id)
        return
    if not scan_date or not ContainerScan.check_date_format(scan_date):
        scan_date = datetime.now()
    if len(list(Path(folder_path).glob("*.xlsx"))) == 0:
        app.logger.warning("No Snyk files found in the specified folder.")
        return
    for file in Path(folder_path).glob("*.xlsx"):
        Snyk(
            name="Snyk",
            app=app,
            file_path=file,
            parent_id=regscale_ssp_id,
            parent_module="securityplans",
            scan_date=scan_date,
        )
