""" Container Scan Abstract """

import ast
import csv
import json
import shutil
from abc import ABC, abstractmethod
from collections import namedtuple
from datetime import date, datetime, timedelta
from typing import Any, Callable, Optional, Sequence, TextIO, Union

import click
import requests
from openpyxl.reader.excel import load_workbook

from regscale.core.app.api import Api
from regscale.core.app.utils.app_utils import (
    check_file_path,
    convert_datetime_to_regscale_string,
    create_progress_object,
    creation_date,
    error_and_exit,
    get_current_datetime,
)
from regscale.integrations.public.cisa import pull_cisa_kev
from regscale.models.regscale_models import Asset, File, Issue, ScanHistory, Vulnerability


class ContainerScan(ABC):
    """
    Abstract class for container scan integration

    :param dict **kwargs: Keyword arguments
    """

    def __init__(self, **kwargs: dict):
        self.field_names = [
            "logger",
            "headers",
            "file_type",
            "app",
            "file_path",
            "name",
            "parent_id",
            "parent_module",
            "scan_date",
            "asset_func",
            "vuln_func",
            "issue_func",
            "extra_headers_allowed",
        ]
        _attributes = namedtuple(
            "Attributes",
            self.field_names,
            defaults=[None] * len(self.field_names),
        )
        self.attributes = _attributes(**kwargs)
        self.file_type = kwargs.get("file_type", ".csv")
        self.extra_headers_allowed = kwargs.get("extra_headers_allowed", False)
        self.scan_date = kwargs.get("scan_date", datetime.now()).date()
        self.attributes.logger.info("Processing %s...", self.attributes.file_path.name)
        self.formatted_headers = None
        self.config = self.attributes.app.config
        self.cisa_kev = pull_cisa_kev()
        self.header, self.file_data = self.file_to_list_of_dicts()
        self.data = {
            "assets": [],
            "issues": [],
            "scans": [],
            "vulns": [],
        }
        self.create_epoch = str(int(creation_date(self.attributes.file_path)))
        self.create_assets(kwargs["asset_func"])  # Pass in the function to create an asset
        self.create_vulns(kwargs["vuln_func"])  # Pass in the function to create a vuln
        self.create_scan()
        self.create_issues(kwargs["issue_func"])  # Pass in the function to create an issue
        self.clean_up()

    def file_to_list_of_dicts(self) -> tuple[Optional[Sequence[str]], list[Any]]:
        """
        Converts a csv file to a list of dictionaries

        :raises AssertionError: If the headers in the csv file do not match the expected headers
        :return: Tuple of header and data from csv file
        :rtype: tuple[Optional[Sequence[str]], list[Any]]
        """
        header = []
        data = []
        with open(self.attributes.file_path, newline="", encoding="utf-8") as file:
            if file.name.endswith(".csv"):
                data, header = self.convert_csv_to_dict(file)
            elif file.name.endswith(".xlsx"):
                header, data = self.convert_xlsx_to_dict(file)
            elif file.name.endswith(".json"):
                try:
                    data = json.load(file)
                except json.JSONDecodeError:
                    raise AssertionError("Invalid JSON file")
            else:
                raise AssertionError("Unsupported file type")
        return header, data

    def convert_csv_to_dict(self, file: TextIO) -> tuple:
        """
        Converts a csv file to a list of dictionaries

        :param TextIO file: The csv file to convert
        :raises AssertionError: If the headers in the csv file do not match the expected headers
        :return: Tuple of header and data from csv file
        :rtype: tuple
        """
        reader = csv.DictReader(file)
        header = reader.fieldnames
        if self.extra_headers_allowed:
            extra_headers = []
            required_headers = []
            for column in header:
                if column not in self.attributes.headers:
                    extra_headers.append(column)
                else:
                    required_headers.append(column)
            print(len(required_headers), len(self.attributes.headers))
            if len(required_headers) != len(self.attributes.headers):
                raise AssertionError(
                    "The headers in the csv file do not match the expected "
                    + f"headers, is this a valid {self.attributes.name} {self.file_type} file?"
                )
            if extra_headers:
                self.attributes.logger.warning(
                    "The following extra columns were found and will be ignored: %s", ", ".join(extra_headers)
                )
        else:
            if self.attributes.headers != header:  # Make sure the expected headers match
                raise AssertionError(
                    f"The headers in the {self.file_type} file do not match the expected "
                    + f"headers, is this a valid {self.attributes.name} {self.file_type} file?"
                )
        data = list(reader)
        return data, header

    def convert_xlsx_to_dict(self, file: TextIO) -> tuple:
        """
        Converts a xlsx file to a list of dictionaries

        :param TextIO file: The xlsx file to convert
        :return: Tuple of header and data from xlsx file
        :rtype: tuple
        """
        # Load the workbook
        workbook = load_workbook(filename=file.name)

        # Select the first sheet
        sheet = workbook.active

        # Get the data from the sheet
        data = list(sheet.values)

        # Get the header from the first row
        header = list(data[0])

        # Get the rest of the data
        data = data[1:]

        # Convert the data to a dictionary
        data_dict = [dict(zip(header, row)) for row in data]

        # Loop through the data and convert any string lists to lists
        for dat in data_dict:
            for key, val in dat.items():
                if isinstance(val, str) and val.startswith("["):
                    dat[key] = ast.literal_eval(dat[key])
        return header, data_dict

    def count_vuln_by_severity(self, severity: str, asset_id: int) -> int:
        """
        Count the number of vulnerabilities by the provided severity

        :param str severity: The severity to count
        :param int asset_id: The asset id to match the vulnerability's parentId
        :return: The number of vulnerabilities
        :rtype: int
        """
        return len([vuln for vuln in self.data["vulns"] if vuln.parentId == asset_id and vuln.severity == severity])

    def create_scan(self) -> None:
        """
        Create scans in RegScale from Nexpose csv file

        :rtype: None
        """
        insert_vulns = []
        scanned_assets = [
            asset for asset in self.data["assets"] if asset.id in {vuln.parentId for vuln in self.data["vulns"]}
        ]

        with create_progress_object() as scan_progress:
            scan_task = scan_progress.add_task(
                f"Creating a scan record  for {len(scanned_assets)} asset(s) in RegScale...", total=len(scanned_assets)
            )
            for asset in scanned_assets:
                count_low = self.count_vuln_by_severity("low", asset.id)
                count_medium = self.count_vuln_by_severity("moderate", asset.id)
                count_high = self.count_vuln_by_severity("high", asset.id)
                count_critical = self.count_vuln_by_severity("critical", asset.id)
                # Create a scan
                scan = ScanHistory(
                    **{
                        "id": 0,
                        "scanningTool": self.name,
                        "scanDate": str(self.scan_date),
                        "scannedIPs": len([ass for ass in scanned_assets if ass.ipAddress == asset.ipAddress]),
                        "checks": count_low + count_medium + count_high + count_critical,
                        "vInfo": 0,
                        "vLow": count_low,
                        "vMedium": count_medium,
                        "vHigh": count_high,
                        "vCritical": count_critical,
                        "parentId": asset.id,
                        "parentModule": "assets",
                        "createdById": self.attributes.app.config["userId"],
                        "lastUpdatedById": self.attributes.app.config["userId"],
                        "isPublic": True,
                        "tenantsId": 0,
                        "dateCreated": get_current_datetime(),
                        "dateLastUpdated": get_current_datetime(),
                    }
                )

                posted_scan = ScanHistory.post_scan(self.attributes.app, Api(), scan)

                if isinstance(posted_scan, ScanHistory):
                    asset_vulns = [vuln for vuln in self.data["vulns"] if vuln.parentId == asset.id]
                    # update vuln scan id
                    for vuln in asset_vulns:
                        vuln.scanId = posted_scan.id
                        insert_vulns.append(vuln)
                scan_progress.advance(scan_task, advance=1)
        Vulnerability.post_vulnerabilities(self.attributes.app, insert_vulns, output_to_console=True)

    def create_assets(self, func: Callable) -> None:
        """
        Create assets in RegScale from csv file

        :param Callable func: Function to create asset
        :rtype: None
        """
        existing_assets = Asset.get_all_by_parent(self.attributes.parent_id, self.attributes.parent_module)

        for dat in self.file_data:
            asset = func(dat)
            if asset not in self.data["assets"]:
                self.data["assets"].append(asset)
        if insert_assets := [asset for asset in self.data["assets"] if asset not in existing_assets]:
            self.attributes.logger.info("Creating %i unique assets in RegScale...", len(insert_assets))
            self.check_status_codes(Asset.batch_create(items=insert_assets))

        for asset in self.data["assets"]:
            if asset in existing_assets:
                asset.id = existing_assets[existing_assets.index(asset)].id
        if update_assets := [asset for asset in self.data["assets"] if asset in existing_assets]:
            self.attributes.logger.info("Updating %i unique assets in RegScale...", len(update_assets))
            self.check_status_codes(Asset.batch_update(items=update_assets))
        # Refresh assets
        self.data["assets"] = Asset.get_all_by_parent(self.attributes.parent_id, self.attributes.parent_module)

    @staticmethod
    def check_status_codes(response_list: list) -> None:
        """
        Check if any of the responses are not 200

        :param list response_list: List of responses
        :raises AssertionError: If any of the responses are not 200
        :rtype: None
        """
        for response in response_list:
            if isinstance(response, requests.Response) and response.status_code != 200:
                raise AssertionError(
                    f"Unable to {response.request.method} asset to RegScale.\n"
                    f"Code: {response.status_code}\nReason: {response.reason}"
                    f"\nPayload: {response.text}"
                )

    def lookup_kev(self, cve: str) -> str:
        """
        Determine if the cve is part of the published CISA KEV list

        :param str cve: The CVE to lookup.
        :return: A string containing the KEV CVE due date.
        :rtype: str
        """
        kev_data = None
        kev_date = None
        if self.cisa_kev:
            try:
                # Update kev and date
                kev_data = next(
                    dat
                    for dat in self.cisa_kev["vulnerabilities"]
                    if "vulnerabilities" in self.cisa_kev and cve and dat["cveID"].lower() == cve.lower()
                )
            except (StopIteration, ConnectionRefusedError):
                kev_data = None
        if kev_data:
            # Convert YYYY-MM-DD to datetime
            kev_date = convert_datetime_to_regscale_string(datetime.strptime(kev_data["dueDate"], "%Y-%m-%d"))
        return kev_date

    def update_due_dt(self, iss: Issue, kev_due_date: str, scanner: str, severity: str) -> Issue:
        """
        Find the due date for the issue

        :param Issue iss: RegScale Issue object
        :param str kev_due_date: The KEV due date
        :param str scanner: The scanner
        :param str severity: The severity of the issue
        :return: RegScale Issue object
        :rtype: Issue
        """
        fmt = "%Y-%m-%d %H:%M:%S"
        if severity == "medium":
            severity = "moderate"
        if kev_due_date and (datetime.strptime(kev_due_date, fmt) > datetime.now()):
            iss.dueDate = kev_due_date
        else:
            iss.dueDate = datetime.strftime(
                datetime.now() + timedelta(days=self.attributes.app.config["issues"][scanner][severity]),
                fmt,
            )
        return iss

    def _check_issue(self, issue: Issue) -> None:
        """
        Check if the issue is in the data

        :param Issue issue: The issue to check to prevent duplicates
        :rtype: None
        """
        if issue and issue not in self.data["issues"]:
            self.data["issues"].append(issue)

    def create_issues(self, func: Callable) -> None:
        """
        Create an issue in RegScale from csv file

        :param Callable func: Function to create issue
        :rtype: None
        """

        existing_issues = Issue.fetch_issues_by_parent(
            app=self.attributes.app,
            regscale_id=self.attributes.parent_id,
            regscale_module=self.attributes.parent_module,
        )
        with create_progress_object() as issue_progress:
            issue_task = issue_progress.add_task("Processing issues...", total=len(self.file_data))
            for dat in self.file_data:
                response = func(dat)
                if isinstance(response, Issue):
                    issue = response
                    self._check_issue(issue)
                if isinstance(response, list):
                    issues = response
                    for iss in issues:
                        self._check_issue(iss)
                issue_progress.advance(issue_task, advance=1)
        self.attributes.logger.info("Found %i issues for processing in RegScale.", len(self.data["issues"]))
        if insert_issues := [issue for issue in self.data["issues"] if issue not in existing_issues]:
            self.attributes.logger.info("Creating %i unique issue(s) in RegScale...", len(insert_issues))
            Issue.bulk_insert(self.attributes.app, insert_issues)
        for issue in self.data["issues"]:
            if issue in existing_issues:
                issue.id = existing_issues[existing_issues.index(issue)].id
        if update_issues := [issue for issue in self.data["issues"] if issue in existing_issues]:
            self.attributes.logger.info("Updating %i unique issue(s) in RegScale...", len(update_issues))
            Issue.bulk_update(self.attributes.app, update_issues)

    def create_vulns(self, func: Callable) -> None:
        """
        Create vulns in RegScale from csv file

        :param Callable func: Function to create vuln
        :rtype: None
        """

        def check_vuln(vuln_to_check: Vulnerability) -> None:
            """
            Check if the vuln is in the data

            :param Vulnerability vuln_to_check: The vulnerability to check to prevent duplicates
            :rtype: None
            """
            if vuln_to_check and vuln_to_check not in self.data["vulns"]:
                self.data["vulns"].append(vuln_to_check)

        with create_progress_object() as vuln_progress:
            vuln_task = vuln_progress.add_task("Processing vulnerabilities...", total=len(self.file_data))
            for dat in self.file_data:
                vuln = func(dat)
                if isinstance(vuln, Vulnerability):
                    check_vuln(vuln)
                if isinstance(vuln, list):
                    for v in vuln:
                        check_vuln(v)
                vuln_progress.advance(vuln_task, advance=1)
        self.attributes.logger.info(
            "Found %i vulnerabilities for processing in RegScale.",
            len(self.data["vulns"]),
        )

    def clean_up(self) -> None:
        """
        Move the Nexpose file to the processed folder

        :rtype: None
        """
        processed_dir = self.attributes.file_path.parent / "processed"
        check_file_path(str(processed_dir.absolute()))
        api = Api()
        try:
            if self.attributes.parent_id:
                file_name = (
                    f"{self.attributes.file_path.stem}_" + f"{get_current_datetime('%Y%m%d-%I%M%S%p')}"
                ).replace(" ", "_")
                # Rename to friendly file name and post to Regscale
                new_file_path = self.attributes.file_path.rename(
                    self.attributes.file_path.parent / (file_name + self.file_type)
                )
                self.attributes.logger.info(
                    "Renaming %s to %s, and uploading it to RegScale...",
                    self.attributes.file_path.name,
                    new_file_path.name,
                )
                File.upload_file_to_regscale(
                    file_name=str(new_file_path.absolute()),
                    parent_id=self.attributes.parent_id,
                    parent_module=self.attributes.parent_module,
                    api=api,
                )
                shutil.move(new_file_path, processed_dir)
                self.attributes.logger.info("File uploaded to RegScale and moved to %s", processed_dir)
        except shutil.Error:
            self.attributes.logger.debug(
                "File %s already exists in %s",
                new_file_path.name,
                processed_dir,
            )

    @abstractmethod
    def create_asset(self):
        """Create an asset"""

    @abstractmethod
    def create_issue(self):
        """Create a scan"""

    @abstractmethod
    def create_vuln(self):
        """Create a Vulnerability"""

    @staticmethod
    def common_scanner_options(message: str, prompt: str) -> Callable[[Callable], click.option]:
        """
        Common options for container scanner integrations

        :param str message: The message to display to the user
        :param str prompt: The prompt to display to the user
        :return: The decorated function
        :rtype: Callable[[Callable], click.option]
        """

        def decorator(this_func) -> Callable[[Callable], click.option]:
            this_func = click.option(
                "--folder_path",
                help=message,
                prompt=prompt,
                type=click.Path(exists=True, dir_okay=True, resolve_path=True),
            )(this_func)
            this_func = click.option(
                "--regscale_ssp_id",
                type=click.INT,
                help="The ID number from RegScale of the System Security Plan.",
                prompt="Enter RegScale System Security Plan ID",
                required=True,
            )(this_func)
            this_func = click.option(
                "--scan_date",
                type=click.DateTime(formats=["%Y-%m-%d"]),
                help="The scan date of the file.",
                required=False,
            )(this_func)
            return this_func

        return decorator

    @staticmethod
    def check_date_format(the_date: Union[datetime, str]) -> bool:
        """
        Check if the date is in the correct format

        :param Union[datetime, str] the_date: Date string or datetime object
        :return: True if the date is in the correct format, False otherwise
        :rtype: Union[datetime, str]
        """
        res = False
        try:
            if isinstance(the_date, str):
                the_date = datetime.strptime(the_date, "%Y-%m-%d")
            # make sure the date is not in the future
            if the_date >= datetime.now():
                error_and_exit("The scan date cannot be in the future.")
            res = True
        except ValueError:
            error_and_exit("Incorrect data format, should be YYYY-MM-DD")
        return res
