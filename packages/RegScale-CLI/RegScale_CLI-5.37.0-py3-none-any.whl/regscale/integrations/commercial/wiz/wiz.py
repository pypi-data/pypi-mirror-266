#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Integrates Wiz.io into RegScale"""

# standard python imports
import codecs
import csv
import logging
import os
import time
import traceback
from contextlib import closing
from typing import Any, Dict, List, Optional

import click
import requests
from pydantic import ValidationError

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.utils.app_utils import (
    check_license,
    create_progress_object,
    format_dict_to_html,
    get_current_datetime,
)
from regscale.core.app.utils.regscale_utils import (
    error_and_exit,
)
from regscale.integrations.commercial.wiz.constants import (
    CONTENT_TYPE,
    RATE_LIMIT_MSG,
    CREATE_REPORT_QUERY,
    CHECK_INTERVAL_FOR_DOWNLOAD_REPORT,
    MAX_RETRIES,
    REPORTS_QUERY,
    DOWNLOAD_QUERY,
)
from regscale.integrations.commercial.wiz.wiz_integration import WizIntegration
from regscale.models import regscale_id, regscale_module
from regscale.models.integration_models.wiz import (
    ComplianceReport,
    ComplianceCheckStatus,
)
from regscale.models.regscale_models import Catalog
from regscale.models.regscale_models.assessment import Assessment
from regscale.models.regscale_models.asset import Asset
from regscale.models.regscale_models.control_implementation import ControlImplementation
from .wiz_auth import wiz_authenticate

logger = logging.getLogger(__name__)
job_progress = create_progress_object()
url_job_progress = create_progress_object()
regscale_job_progress = create_progress_object()
compliance_job_progress = create_progress_object()


@click.group()
def wiz():
    """Integrates continuous monitoring data from Wiz.io."""


@wiz.command()
@click.option("--client_id", default=None, hide_input=False, required=False)
@click.option("--client_secret", default=None, hide_input=True, required=False)
def authenticate(client_id, client_secret):
    """Authenticate to Wiz."""
    wiz_authenticate(client_id, client_secret)


@wiz.command()
@click.option(
    "--wiz_project_id",
    "-p",
    required=True,
    type=str,
    help="Comma Seperated list of one or more Wiz project ids to pull inventory for.",
)
@click.option("--regscale_id", "-i", help="Regscale id to push inventory to in RegScale.")
@click.option(
    "--regscale_module",
    "-m",
    help="Regscale module to push inventory to in RegScale.",
)
@click.option(
    "--filter_by_override",
    "-f",
    default=None,
    type=str,
    required=False,
    help="""Filter by override to use for pulling inventory you can use one or more of the following.
    IE: --filter_by='{projectId: ["1234"], type: ["VIRTUAL_MACHINE"], subscriptionExternalId: ["1234"],
         providerUniqueId: ["1234"], updatedAt: {after: "2023-06-14T14:07:06Z"}, search: "test-7"}' """,
)
@click.option(
    "--client_id",
    "-ci",
    help="Wiz Client ID, or can be set as environment variable WizClientID",
    default=os.environ.get("WizClientID"),
    hide_input=False,
    required=True,
)
@click.option(
    "--client_secret",
    "-cs",
    help="Wiz Client Secret, or can be set as environment variable WizClientSecret",
    default=os.environ.get("WizClientSecret"),
    hide_input=False,
    required=True,
)
@click.option(
    "--full_inventory",
    "-fi",
    is_flag=True,
    help="Pull full inventory list. this disregards the last pull date.",
    required=False,
    default=False,
)
def inventory(
    wiz_project_id: str,
    regscale_id: int,
    regscale_module: str,
    filter_by_override: str,
    client_id: str,
    client_secret: str,
    full_inventory: bool,
) -> None:
    """Process inventory from Wiz and create assets in RegScale."""
    wiz_integration = WizIntegration()
    wiz_integration.inventory(
        wiz_project_ids=wiz_project_id.split(","),
        regscale_id=regscale_id,
        regscale_module=regscale_module,
        filter_by_override=filter_by_override,
        client_id=client_id,
        client_secret=client_secret,
        full_inventory=full_inventory,
    )


@wiz.command()
@click.option(
    "--wiz_project_id",
    prompt="Enter the project ID for Wiz",
    default=None,
    required=True,
)
@regscale_id(help="RegScale will create and update issues as children of this record.")
@regscale_module()
@click.option(
    "--client_id",
    help="Wiz Client ID, or can be set as environment variable WizClientID",
    default=None,
    hide_input=False,
    required=False,
)
@click.option(
    "--client_secret",
    help="Wiz Client Secret, or can be set as environment variable WizClientSecret",
    default=None,
    hide_input=True,
    required=False,
)
@click.option(
    "--filter_by_override",
    "-f",
    default=None,
    type=str,
    required=False,
    help="""Filter by override to use for pulling inventory you can use one or more of the following.
    IE: --filter_by='{projectId: ["1234"], type: ["VIRTUAL_MACHINE"], subscriptionExternalId: ["1234"],
         providerUniqueId: ["1234"], updatedAt: {after: "2023-06-14T14:07:06Z"}, search: "test-7"}' """,
)
def issues(
    wiz_project_id: str,
    regscale_id: int,
    regscale_module: str,
    client_id: str,
    client_secret: str,
    filter_by_override: str = None,
) -> None:
    """
    Process Issues from Wiz into RegScale
    """
    wiz_integration = WizIntegration()
    wiz_integration.issues(
        wiz_project_id=wiz_project_id,
        regscale_id=regscale_id,
        regscale_module=regscale_module,
        filter_by_override=filter_by_override,
        client_id=client_id,
        client_secret=client_secret,
    )


@wiz.command()
@click.option(
    "--wiz_project_id",
    prompt="Enter the project ID for Wiz",
    default=None,
    required=True,
)
@regscale_id(help="RegScale will create and update issues as children of this record.")
@regscale_module()
@click.option(
    "--client_id",
    help="Wiz Client ID, or can be set as environment variable WizClientID",
    default=None,
    hide_input=False,
    required=False,
)
@click.option(
    "--client_secret",
    help="Wiz Client Secret, or can be set as environment variable WizClientSecret",
    default=None,
    hide_input=True,
    required=False,
)
@click.option(
    "--filter_by_override",
    "-f",
    default=None,
    type=str,
    required=False,
    help="""Filter by override to use for pulling inventory you can use one or more of the following.
    IE: --filter_by='{projectId: ["1234"], type: ["VIRTUAL_MACHINE"], subscriptionExternalId: ["1234"],
         providerUniqueId: ["1234"], updatedAt: {after: "2023-06-14T14:07:06Z"}, search: "test-7"}' """,
)
def sbom(
    wiz_project_id: str,
    regscale_id: int,
    regscale_module: str,
    client_id: str,
    client_secret: str,
    filter_by_override: str = None,
) -> None:
    """
    Process SBOM from Wiz into RegScale
    """
    wiz_integration = WizIntegration()
    wiz_integration.sbom(
        wiz_project_id=wiz_project_id,
        regscale_id=regscale_id,
        regscale_module=regscale_module,
        filter_by_override=filter_by_override,
        client_id=client_id,
        client_secret=client_secret,
    )


@wiz.command()
def threats():
    """Process threats from Wiz -> Coming soon"""
    check_license()
    logger.info("Threats - COMING SOON")


@wiz.command()
def vulnerabilities():
    """Process vulnerabilities from Wiz -> Coming soon"""
    check_license()
    logger.info("Vulnerabilities - COMING SOON")


def fetch_report_id(app: Application, query: str, variables: Dict, url: str) -> str:
    """
    Fetch report ID from Wiz

    :param Application app: Application instance
    :param str query: Query string
    :param Dict variables: Variables
    :param str url: Wiz URL
    :return str: Wiz ID
    :rtype str: str
    """
    try:
        resp = send_request(
            app=app,
            query=query,
            variables=variables,
            api_endpoint_url=url,
        )
        if "error" in resp.json().keys():
            error_and_exit(f'Wiz Error: {resp.json()["error"]}')
        return resp.json()["data"]["createReport"]["report"]["id"]
    except (requests.RequestException, AttributeError, TypeError) as rex:
        logger.error("Unable to pull report id from requests object\n%s", rex)
    return ""


def get_framework_names(wiz_frameworks: List) -> List:
    """
    Get the names of frameworks and replace spaces with underscores.

    :param List wiz_frameworks: List of Wiz frameworks.
    :return List: List of framework names.
    :rtype List: list
    """
    return [framework["name"].replace(" ", "_") for framework in wiz_frameworks]


def check_reports_for_frameworks(reports: List, frames: List) -> bool:
    """
    Check if any reports contain the given frameworks.

    :param List reports: List of reports.
    :param List frames: List of framework names.
    :return bool: Boolean indicating if any report contains a framework.
    :rtype bool: bool
    """
    return any(frame in item["name"] for item in reports for frame in frames)


def create_report_if_needed(
    app: Application, wiz_project_id: str, frames: List, wiz_frameworks: List, reports: List, snake_framework: str
) -> List:
    """
    Create a report if needed and return report IDs.

    :param Application app: Application instance.
    :param str wiz_project_id: Wiz Project ID.
    :param List frames: List of framework names.
    :param List wiz_frameworks: List of Wiz frameworks.
    :param List reports: List of reports.
    :param str snake_framework: Framework name with spaces replaced by underscores.
    :return List: List of Wiz report IDs.
    :rtype List: list
    """
    if not check_reports_for_frameworks(reports, frames):
        selected_frame = snake_framework
        selected_index = frames.index(selected_frame)
        wiz_framework = wiz_frameworks[selected_index]
        wiz_report_id = create_compliance_report(
            app=app,
            wiz_project_id=wiz_project_id,
            report_name=f"{selected_frame}_project_{wiz_project_id}",
            framework_id=wiz_framework.get("id"),
        )
        logger.info(f"Wiz compliance report created with ID {wiz_report_id}")
        return [wiz_report_id]

    return [report["id"] for report in reports if any(frame in report["name"] for frame in frames)]


def fetch_and_process_report_data(wiz_report_ids: List) -> List:
    """
    Fetch and process report data from report IDs.

    :param List wiz_report_ids: List of Wiz report IDs.
    :return List: List of processed report data.
    :rtype List: List
    """
    report_data = []
    for wiz_report in wiz_report_ids:
        download_url = get_report_url_and_status(wiz_report)
        logger.debug(f"Download url: {download_url}")
        with closing(requests.get(url=download_url, stream=True, timeout=10)) as data:
            logger.info("Download URL fetched. Streaming and parsing report")
            reader = csv.DictReader(codecs.iterdecode(data.iter_lines(), encoding="utf-8"), delimiter=",")
            for row in reader:
                report_data.append(row)
    return report_data


def fetch_framework_report(app: Application, wiz_project_id: str, snake_framework: str) -> List[Any]:
    """
    Fetch Framework Report from Wiz.

    :param Application app: Application instance.
    :param str wiz_project_id: Wiz Project ID.
    :param str snake_framework: Framework name with spaces replaced by underscores.
    :return: List containing the framework report data.
    :rtype: List[Any]
    """
    wiz_frameworks = fetch_frameworks(app)
    frames = get_framework_names(wiz_frameworks)
    reports = list(query_reports(app))

    wiz_report_ids = create_report_if_needed(app, wiz_project_id, frames, wiz_frameworks, reports, snake_framework)
    return fetch_and_process_report_data(wiz_report_ids)


def fetch_frameworks(app: Application) -> list:
    """
    Fetch frameworks from Wiz

    :param Application app: Application Instance
    :raises General Error: If error in API response
    :return: List of frameworks
    :rtype: list
    """
    query = """
        query SecurityFrameworkAutosuggestOptions($policyTypes: [SecurityFrameworkPolicyType!],
        $onlyEnabledPolicies: Boolean) {
      securityFrameworks(
        first: 500
        filterBy: {policyTypes: $policyTypes, enabled: $onlyEnabledPolicies}
      ) {
        nodes {
          id
          name
        }
      }
    }
    """
    variables = {
        "policyTypes": "CLOUD",
        "first": 500,
    }
    resp = send_request(
        app=app,
        query=query,
        variables=variables,
        api_endpoint_url=app.config["wizUrl"],
    )

    if resp.ok:
        # ["data"]["securityFrameworks"]["nodes"]
        data = resp.json()
        return data.get("data", {}).get("securityFrameworks", {}).get("nodes")
    else:
        error_and_exit(f"Wiz Error: {resp.status_code if resp else None} - {resp.text if resp else 'No response'}")
        return []


def query_reports(app: Application) -> list:
    """
    Query Report table from Wiz

    :param Application app: RegScale Application instance
    :return: list object from an API response from Wiz
    :rtype: list
    """

    # The variables sent along with the above query
    variables = {"first": 100, "filterBy": {}}

    res = send_request(
        app,
        query=REPORTS_QUERY,
        variables=variables,
        api_endpoint_url=app.config["wizUrl"],
    )
    result = []
    try:
        if "errors" in res.json().keys():
            error_and_exit(f'Wiz Error: {res.json()["errors"]}')
        json_result = res.json()
        result = json_result.get("data", {}).get("reports", {}).get("nodes")
    except requests.JSONDecodeError:
        error_and_exit(f"Unable to fetch reports from Wiz: {res.status_code}, {res.reason}")
    return result


def send_request(
    app: Application,
    query: str,
    variables: Dict,
    api_endpoint_url: Optional[str] = None,
) -> requests.Response:
    """
    Send a graphQL request to Wiz.

    :param Application app:
    :param str query: Query to use for GraphQL
    :param Dict variables:
    :param Optional[str] api_endpoint_url: Wiz GraphQL URL Default is None
    :raises ValueError: Value Error if the access token is missing from wizAccessToken in init.yaml
    :return requests.Response: response from post call to provided api_endpoint_url
    :rtype requests.Response: requests.Response
    """
    logger.debug("Sending a request to Wiz API")
    api = Api()
    payload = dict({"query": query, "variables": variables})
    if api_endpoint_url is None:
        api_endpoint_url = app.config["wizUrl"]
    if app.config["wizAccessToken"]:
        return api.post(
            url=api_endpoint_url,
            headers={
                "Content-Type": CONTENT_TYPE,
                "Authorization": "Bearer " + app.config["wizAccessToken"],
            },
            json=payload,
        )
    raise ValueError("An access token is missing.")


def rerun_report(app: Application, report_id: str) -> str:
    """
    Rerun a Wiz Report

    :param Application app: Application instance
    :param str report_id: report id
    :return: Wiz report ID
    :rtype: str
    """
    rerun_report_query = """
        mutation RerunReport($reportId: ID!) {
            rerunReport(input: { id: $reportId }) {
                report {
                    id
                }
            }
        }
    """
    variables = {"reportId": report_id}
    rate = 0.5
    while True:
        response = send_request(app, query=rerun_report_query, variables=variables)
        content_type = response.headers.get("content-type")
        if content_type and CONTENT_TYPE in content_type:
            if "errors" in response.json():
                if RATE_LIMIT_MSG in response.json()["errors"][0]["message"]:
                    rate = response.json()["errors"][0]["extensions"]["retryAfter"]
                    time.sleep(rate)
                    continue
                error_info = response.json()["errors"]
                variables_info = variables
                query_info = rerun_report_query
                error_and_exit(f"Error info: {error_info}\nVariables:{variables_info}\nQuery:{query_info}")
            report_id = response.json()["data"]["rerunReport"]["report"]["id"]
            logger.info("Report was re-run successfully. Report ID: %s", report_id)
            break
        time.sleep(rate)
    config = app.config
    config.setdefault("wizIssuesReportId", {})
    config["wizIssuesReportId"]["report_id"] = report_id
    config["wizIssuesReportId"]["last_seen"] = get_current_datetime()
    app.save_config(config)
    return report_id


def create_compliance_report(
    app: Application,
    report_name: str,
    wiz_project_id: str,
    framework_id: str,
) -> str:
    """Create Wiz compliance report

    :param Application app: Application instance
    :param str report_name: Report name
    :param str wiz_project_id: Wiz Project ID
    :param str framework_id: Wiz Framework ID
    :return str: Compliance Report id
    :rtype str: str
    """
    report_variables = {
        "input": {
            "name": report_name,
            "type": "COMPLIANCE_ASSESSMENTS",
            "csvDelimiter": "US",
            "projectId": wiz_project_id,
            "complianceAssessmentsParams": {"securityFrameworkIds": [framework_id]},
            "emailTargetParams": None,
            "exportDestinations": None,
        }
    }

    return fetch_report_id(app, CREATE_REPORT_QUERY, report_variables, url=app.config["wizUrl"])


def get_report_url_and_status(report_id: str) -> str:
    """
    Generate Report URL from Wiz report

    :param str report_id: Wiz report ID
    :raises: requests.RequestException if download failed and exceeded max # of retries
    :return: URL of report
    :rtype: str
    """
    for attempt in range(MAX_RETRIES):
        if attempt:
            logger.info(
                "Report %s is still updating, waiting %.2f seconds", report_id, CHECK_INTERVAL_FOR_DOWNLOAD_REPORT
            )
            time.sleep(CHECK_INTERVAL_FOR_DOWNLOAD_REPORT)

        response = download_report({"reportId": report_id})
        if not response or not response.ok:
            raise requests.RequestException("Failed to download report")

        response_json = response.json()
        errors = response_json.get("errors")
        if errors:
            message = errors[0]["message"]
            if RATE_LIMIT_MSG in message:
                rate = errors[0]["extensions"]["retryAfter"]
                logger.warning("Sleeping %i seconds due to rate limit", rate)
                time.sleep(rate)
                continue

            logger.error(errors)
        else:
            status = response_json.get("data", {}).get("report", {}).get("lastRun", {}).get("status")
            if status == "COMPLETED":
                return response_json["data"]["report"]["lastRun"]["url"]

    raise requests.RequestException("Download failed, exceeding the maximum number of retries")


def download_report(variables: Dict) -> requests.Response:
    """
    Return a download URL for a provided Wiz report id

    :param Dict variables: Variables for Wiz request
    :return: response from Wiz API
    :rtype: requests.Response
    """
    app = Application()
    response = send_request(app, DOWNLOAD_QUERY, variables=variables)
    return response


def get_asset_by_external_id(wiz_external_id: str, existing_ssp_assets: list[Asset]) -> Optional[Asset]:
    """
    Returns a single asset by the wiz external ID

    :param str wiz_external_id: Wiz external ID
    :param list[Asset] existing_ssp_assets: List of existing SSP assets
    :return: Asset if found, else None
    :rtype: Optional[Asset]
    """
    asset = None
    for existing_ssp_asset in existing_ssp_assets:
        if existing_ssp_asset["wizId"] == wiz_external_id:
            asset = existing_ssp_asset
    return asset


@wiz.command("sync_compliance")
@click.option(
    "--wiz_project_id",
    "-p",
    prompt="Enter the Wiz project ID",
    help="Enter the Wiz Project ID.  Options include: projects, \
          policies, supplychain, securityplans, components.",
    required=True,
)
@regscale_id(help="RegScale will create and update issues as children of this record.")
@regscale_module()
@click.option(
    "--client_id",
    "-i",
    help="Wiz Client ID. Can also be set as an environment variable: WIZ_CLIENT_ID",
    default=os.environ.get("WIZ_CLIENT_ID"),
    hide_input=False,
    required=False,
)
@click.option(
    "--client_secret",
    "-s",
    help="Wiz Client Secret. Can also be set as an environment variable: WIZ_CLIENT_SECRET",
    default=os.environ.get("WIZ_CLIENT_SECRET"),
    hide_input=True,
    required=False,
)
@click.option(
    "--catalog_id",
    "-c",
    help="RegScale Catalog ID for the selected framework.",
    prompt="RegScale Catalog ID",
    hide_input=False,
    required=True,
)
@click.option(
    "--framework",
    "-f",
    type=click.Choice(["CSF", "NIST800-53R5", "NIST800-53R4"], case_sensitive=False),
    help="Choose either one of the Frameworks",
    default="NIST800-53R5",
    required=True,
)
@click.option(
    "--include_not_implemented",
    "-n",
    is_flag=True,
    help="Include not implemented controls",
    default=False,
)
def sync_compliance(
    wiz_project_id,
    regscale_id,
    regscale_module,
    client_id,
    client_secret,
    catalog_id,
    framework,
    include_not_implemented,
):
    """Sync compliance posture from Wiz to RegScale"""
    with compliance_job_progress:
        _sync_compliance(
            wiz_project_id=wiz_project_id,
            regscale_id=regscale_id,
            regscale_module=regscale_module,
            include_not_implemented=include_not_implemented,
            client_id=client_id,
            client_secret=client_secret,
            catalog_id=catalog_id,
            framework=framework,
        )


def _sync_compliance(
    wiz_project_id: str,
    regscale_id: int,
    regscale_module: str,
    include_not_implemented: bool,
    client_id: str,
    client_secret: str,
    catalog_id: int,
    framework: Optional[str] = "NIST800-53R5",
) -> List[ComplianceReport]:
    """
    Sync compliance posture from Wiz to RegScale

    :param str wiz_project_id: Wiz Project ID
    :param int regscale_id: RegScale ID
    :param str regscale_module: RegScale module
    :param bool include_not_implemented: Include not implemented controls
    :param str client_id: Wiz Client ID
    :param str client_secret: Wiz Client Secret
    :param int catalog_id: Catalog ID, defaults to None
    :param Optional[str] framework: Framework, defaults to NIST800-53R5
    :return: List of ComplianceReport objects
    :rtype: List[ComplianceReport]
    """

    app = Application()
    logger.info("Syncing compliance from Wiz with project ID %s", wiz_project_id)
    wiz_authenticate(
        client_id=client_id,
        client_secret=client_secret,
    )
    report_job = compliance_job_progress.add_task("[#f68d1f]Fetching Wiz compliance report...", total=1)
    fetch_regscale_data_job = compliance_job_progress.add_task(
        "[#f68d1f]Fetching RegScale Catalog info for framework...", total=1
    )
    logger.info("Fetching Wiz compliance report for project ID %s...", wiz_project_id)
    compliance_job_progress.update(report_job, completed=True, advance=1)

    framework_mapping = {
        "CSF": "NIST CSF v1.1",
        "NIST800-53R5": "NIST SP 800-53 Revision 5",
        "NIST800-53R4": "NIST SP 800-53 Revision 4",
    }
    sync_framework = framework_mapping.get(framework)
    snake_framework = sync_framework.replace(" ", "_")
    logger.info(snake_framework)
    logger.info("Fetching Wiz compliance report for project ID %s", wiz_project_id)
    report_data = fetch_framework_report(app, wiz_project_id, snake_framework)
    report_models = []
    compliance_job_progress.update(report_job, completed=True, advance=1)

    catalog = Catalog.get_with_all_details(catalog_id=catalog_id)
    controls = catalog.get("controls")
    passing_controls = dict()
    failing_controls = dict()
    controls_to_reports = dict()
    existing_implementations = ControlImplementation.get_existing_control_implementations(parent_id=regscale_id)
    compliance_job_progress.update(fetch_regscale_data_job, completed=True, advance=1)
    logger.info(f"Analyzing ComplianceReport for framework {sync_framework} from Wiz")
    running_compliance_job = compliance_job_progress.add_task(
        "[#f68d1f]Building compliance posture from wiz report...",
        total=len(report_data),
    )
    for row in report_data:
        try:
            cr = ComplianceReport(**row)
            if cr.framework == sync_framework:
                check_compliance(
                    cr,
                    controls,
                    passing_controls,
                    failing_controls,
                    controls_to_reports,
                )
                report_models.append(cr)
                compliance_job_progress.update(running_compliance_job, advance=1)
        except ValidationError as e:
            logger.error(f"Error creating ComplianceReport: {e}")
    try:
        saving_regscale_data_job = compliance_job_progress.add_task("[#f68d1f]Saving RegScale data...", total=1)
        ControlImplementation.create_control_implementations(
            controls=controls,
            parent_id=regscale_id,
            parent_module=regscale_module,
            existing_implementation_dict=existing_implementations,
            full_controls=passing_controls,
            partial_controls={},
            failing_controls=failing_controls,
            include_not_implemented=include_not_implemented,
        )
        create_assessment_from_compliance_report(
            controls_to_reports=controls_to_reports,
            regscale_id=regscale_id,
            regscale_module=regscale_module,
            controls=controls,
        )
        compliance_job_progress.update(saving_regscale_data_job, completed=True, advance=1)

    except Exception as e:
        logger.error(f"Error creating ControlImplementations from compliance report: {e}")
        traceback.print_exc()
    return report_models


def check_compliance(
    cr: ComplianceReport,
    controls: List[Dict],
    passing: Dict,
    failing: Dict,
    controls_to_reports: Dict,
) -> None:
    """
    Check compliance report for against controls

    :param ComplianceReport cr: Compliance Report
    :param List[Dict] controls: Controls List
    :param Dict passing: Passing controls
    :param Dict failing: Failing controls
    :param Dict controls_to_reports: Controls to reports
    :return: None
    :rtype: None
    """
    for control in controls:
        if f"{control.get('controlId').lower()} " in cr.compliance_check.lower():
            _add_controls_to_controls_to_report_dict(control, controls_to_reports, cr)
            if cr.result == ComplianceCheckStatus.PASS.value:
                if control.get("controlId").lower() not in passing:
                    passing[control.get("controlId").lower()] = control
            else:
                if control.get("controlId").lower() not in failing:
                    failing[control.get("controlId").lower()] = control
    _clean_passing_list(passing, failing)


def _add_controls_to_controls_to_report_dict(control: Dict, controls_to_reports: Dict, cr: ComplianceReport) -> None:
    """
    Add controls to dict to process assessments from later

    :param Dict control: Control
    :param Dict controls_to_reports: Controls to reports
    :param ComplianceReport cr: Compliance Report
    :return: None
    :rtype: None
    """
    if control.get("controlId").lower() not in controls_to_reports.keys():
        controls_to_reports[control.get("controlId").lower()] = [cr]
    else:
        controls_to_reports[control.get("controlId").lower()].append(cr)


def _clean_passing_list(passing: Dict, failing: Dict) -> None:
    """
    Clean passing list. Ensures that controls that are passing are not also failing

    :param Dict passing: Passing controls
    :param Dict failing: Failing controls
    :return: None
    :rtype: None
    """
    for control_id in failing:
        if control_id in passing:
            passing.pop(control_id, None)


def create_assessment_from_compliance_report(
    controls_to_reports: Dict, regscale_id: int, regscale_module: str, controls: List
) -> None:
    """
    Create assessment from compliance report

    :param Dict controls_to_reports: Controls to reports
    :param int regscale_id: RegScale ID
    :param str regscale_module: RegScale module
    :param List controls: Controls
    :return: None
    :rtype: None
    """
    implementations = ControlImplementation.get_all_by_parent(parent_module=regscale_module, parent_id=regscale_id)
    for control_id, reports in controls_to_reports.items():
        control_record_id = None
        for control in controls:
            if control.get("controlId").lower() == control_id:
                control_record_id = control.get("id")
                break
        filtered_results = [x for x in implementations if x.controlID == control_record_id]
        create_report_assessment(filtered_results, reports, control_id)


def create_report_assessment(filtered_results: List, reports: List, control_id: str) -> None:
    """
    Create report assessment

    :param List filtered_results: Filtered results
    :param List reports: Reports
    :param str control_id: Control ID
    :return: None
    :rtype: None
    """
    implementation = filtered_results[0] if len(filtered_results) > 0 else None
    for report in reports:
        html_summary = format_dict_to_html(report.dict())
        if implementation:
            Assessment(
                leadAssessorId=implementation.createdById,
                title=f"Wiz compliance report assessment for {control_id}",
                assessmentType="Control Testing",
                plannedStart=get_current_datetime(),
                plannedFinish=get_current_datetime(),
                actualFinish=get_current_datetime(),
                assessmentResult=report.result,
                assessmentReport=html_summary,
                status="Complete",
                parentId=implementation.id,
                parentModule="controls",
                isPublic=True,
            ).create()
