#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prisma RegScale integration"""
from datetime import datetime
from os import PathLike
from pathlib import Path

import click

from regscale.core.app.application import Application
from regscale.models.integration_models.container_scan import ContainerScan
from regscale.models.integration_models.prisma import Prisma
from regscale.validation.record import validate_regscale_object


@click.group()
def prisma():
    """Performs actions on Prisma export files."""


@prisma.command(name="import_prisma")
@ContainerScan.common_scanner_options(
    message="File path to the folder containing Nexpose .csv files to process to RegScale.",
    prompt="File path for Prisma files:",
)
def import_prisma(folder_path: PathLike[str], regscale_ssp_id: int, scan_date: datetime):
    """
    Import scans, vulnerabilities and assets to RegScale from Prisma export files
    """
    app = Application()
    if not validate_regscale_object(regscale_ssp_id, "securityplans"):
        app.logger.warning("SSP #%i is not a valid RegScale Security Plan.", regscale_ssp_id)
        return
    if not scan_date or not ContainerScan.check_date_format(scan_date):
        scan_date = datetime.now()
    if len(list(Path(folder_path).glob("*.csv"))) == 0:
        app.logger.warning("No Prisma(csv) files found in the specified folder.")
        return
    for file in Path(folder_path).glob("*.csv"):
        Prisma(name="Prisma", app=app, file_path=str(file), regscale_ssp_id=regscale_ssp_id, scan_date=scan_date)
