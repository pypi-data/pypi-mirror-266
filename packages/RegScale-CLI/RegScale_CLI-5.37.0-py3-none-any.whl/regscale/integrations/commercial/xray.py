#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""xray RegScale integration"""
from pathlib import Path

import click

from regscale.core.app.application import Application
from regscale.models.integration_models.xray import XRay


@click.group()
def xray():
    """Performs actions on xray files."""


@xray.command(name="import_xray")
@click.option(
    "--folder_path",
    help="File path to the folder containing XRay JSON files to process to RegScale.",
    prompt="File path for xray files",
    type=click.Path(exists=True, dir_okay=True, resolve_path=True),
)
@click.option(
    "--regscale_ssp_id",
    type=click.INT,
    help="The ID number from RegScale of the System Security Plan.",
    prompt="Enter RegScale System Security Plan ID",
    required=True,
)
def import_xray(folder_path: click.Path, regscale_ssp_id: click.INT):
    """
    Import JFrog XRay scans, vulnerabilities and assets to RegScale from XRay .json files
    """
    # click.types.Path to pathlib.Path
    folder_path = Path(folder_path)
    app = Application()
    if len(list(folder_path.glob("*.json"))) == 0:
        app.logger.warning("No xray(JSON) files found in the specified folder.")
        return
    for file in list(folder_path.glob("*.json")):
        XRay(name="Xray", app=app, file_path=file, regscale_ssp_id=regscale_ssp_id)
