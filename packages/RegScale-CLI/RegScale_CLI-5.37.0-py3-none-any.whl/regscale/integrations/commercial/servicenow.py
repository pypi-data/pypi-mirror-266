#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Integration of ServiceNow into RegScale CLI tool """
# standard python imports
import sys
from concurrent.futures import CancelledError, ThreadPoolExecutor, as_completed
from copy import deepcopy
from json import JSONDecodeError
from pathlib import Path
from threading import Lock
from typing import List, Optional, Tuple
from urllib.parse import urljoin

import click
import requests
from rich.progress import track

from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.api_handler import APIUpdateError
from regscale.core.app.utils.app_utils import (
    check_file_path,
    check_license,
    create_progress_object,
    error_and_exit,
    save_data_to,
)
from regscale.core.app.utils.regscale_utils import verify_provided_module
from regscale.models import regscale_id, regscale_module
from regscale.models.regscale_models import Issue

job_progress = create_progress_object()
logger = create_logger()
APPLICATION_JSON = "application/json"


# Create group to handle ServiceNow integration
@click.group()
def servicenow():
    """Auto-assigns incidents in ServiceNow for remediation."""
    check_license()


####################################################################################################
#
# PROCESS ISSUES TO ServiceNow
# ServiceNow REST API Docs:
# https://docs.servicenow.com/bundle/paris-application-development/page/build/applications/concept
# /api-rest.html
# Use the REST API Explorer in ServiceNow to select table, get URL, and select which fields to
# populate
#
####################################################################################################
@servicenow.command()
@regscale_id()
@regscale_module()
@click.option(
    "--snow_assignment_group",
    type=click.STRING,
    help="RegScale will sync the issues for the record to this ServiceNow assignment group.",
    prompt="Enter the name of the project in ServiceNow",
    required=True,
)
@click.option(
    "--snow_incident_type",
    type=click.STRING,
    help="Enter the ServiceNow incident type to use when creating new issues from RegScale.",
    prompt="Enter the ServiceNow incident type",
    required=True,
)
def issues(
    regscale_id: int,
    regscale_module: str,
    snow_assignment_group: str,
    snow_incident_type: str,
):
    """Process issues to ServiceNow."""
    sync_snow_to_regscale(
        regscale_id=regscale_id,
        regscale_module=regscale_module,
        snow_assignment_group=snow_assignment_group,
        snow_incident_type=snow_incident_type,
    )


@servicenow.command(name="sync_work_notes")
def sync_work_notes():
    """Sync work notes from ServiceNow to existing issues."""
    sync_notes_to_regscale()


def get_issues_data(reg_api: Api, url_issues: str) -> List[dict]:
    """
    Fetch the full issue list from RegScale

    :param Api reg_api: RegScale API object
    :param str url_issues: URL for RegScale issues
    :return: List of issues
    :rtype: List[dict]
    """
    logger.info("Fetching full issue list from RegScale.")
    issue_response = reg_api.get(url_issues)
    result = []
    if issue_response.status_code == 204:
        logger.warning("No existing issues for this RegScale record.")
    else:
        try:
            result = issue_response.json()
        except JSONDecodeError as rex:
            error_and_exit(f"Unable to fetch issues from RegScale.\\n{rex}")
    return result


def create_snow_incident(snow_api: Api, incident_url: str, snow_incident: dict) -> dict:
    """
    Create a new incident in ServiceNow

    :param Api snow_api: ServiceNow API object
    :param str incident_url: URL for ServiceNow incidents
    :param dict snow_incident: Incident data
    :return: Incident response
    :rtype: dict
    """
    result = {}
    try:
        response = snow_api.post(
            url=incident_url,
            headers={"Content-Type": APPLICATION_JSON, "Accept": APPLICATION_JSON},
            json=snow_incident,
        )
        if not response.raise_for_status():
            result = response.json()
    except requests.exceptions.RequestException as ex:
        logger.error("Unable to create incident %s in ServiceNow...\n%s", snow_incident, ex)
    return result


def sync_snow_to_regscale(
    regscale_id: int,
    regscale_module: str,
    snow_assignment_group: str,
    snow_incident_type: str,
) -> None:
    """
    Sync issues from ServiceNow to RegScale via API
    :param int regscale_id: ID # of record in RegScale to associate issues with
    :param str regscale_module: RegScale module to associate issues with
    :param str snow_assignment_group: Snow assignment group to filter for
    :param str snow_incident_type: Snow incident type to filter for
    :rtype: None
    """
    # initialize variables
    app = Application()
    reg_api = Api()
    verify_provided_module(regscale_module)
    config = app.config

    # Group related variables into a dictionary
    snow_config = {
        "reg_config": config,
        "url": config["snowUrl"],
        "user": config["snowUserName"],
        "pwd": config["snowPassword"],
        "reg_api": reg_api,
        "api": deepcopy(reg_api),
    }
    snow_config["api"].auth = (snow_config["user"], snow_config["pwd"])

    url_issues = urljoin(
        config["domain"],
        f"api/issues/getAllByParent/{str(regscale_id)}/{str(regscale_module).lower()}",
    )

    if issues_data := get_issues_data(reg_api, url_issues):
        check_file_path("artifacts")
        save_data_to(
            file=Path("./artifacts/existingRecordIssues.json"),
            data=issues_data,
        )
        logger.info(
            "Writing out RegScale issue list for Record # %s to the artifacts folder "
            + "(see existingRecordIssues.json).",
            regscale_id,
        )
        logger.info(
            "%s existing issues retrieved for processing from RegScale.",
            len(issues_data),
        )

        int_new, int_skipped = process_issues(
            issues_data,
            snow_config,
            snow_assignment_group,
            snow_incident_type,
        )

        logger.info(
            "%i new issue incidents opened in ServiceNow and %i issues already exist and were skipped.",
            int_new,
            int_skipped,
        )
    else:
        logger.warning("No issues found for this record in RegScale. No issues were processed.")


def create_snow_assignment_group(snow_assignment_group: str, snow_config: dict) -> None:
    """
    Create a new assignment group in ServiceNow or if one already exists,
    a 403 is returned from SNOW.

    :param str snow_assignment_group: ServiceNow assignment group
    :param dict snow_config: ServiceNow configuration
    :rtype: None
    """
    # Create a service now assignment group. The api will not allow me create dups
    snow_api = snow_config["api"]
    payload = {
        "name": snow_assignment_group,
        "description": "An automatically generated Service Now assignment group from RegScale.",
        "active": True,
    }
    url = urljoin(snow_config["url"], "api/now/table/sys_user_group")
    response = snow_api.post(
        url=url,
        headers={"Content-Type": APPLICATION_JSON, "Accept": APPLICATION_JSON},
        json=payload,
    )
    if response.status_code == 201:
        logger.info("ServiceNow Assignment Group %s created.", snow_assignment_group)
    elif response.status_code == 403:
        # I expect a 403 for a duplicate code already found
        logger.debug("ServiceNow Assignment Group %s already exists.", snow_assignment_group)
    else:
        error_and_exit(
            f"Unable to create ServiceNow Assignment Group {snow_assignment_group}. "
            f"Status code: {response.status_code}"
        )


def get_service_now_incidents(snow_config: dict, query: str) -> List[dict]:
    """
    Get all incidents from ServiceNow

    :param dict snow_config: ServiceNow configuration
    :param str query: Query string
    :return: List of incidents
    :rtype: List[dict]
    """
    snow_api = snow_config["api"]
    incident_url = urljoin(snow_config["url"], "api/now/table/incident")
    offset = 0
    limit = 500
    data = []

    while True:
        result, offset = query_incidents(
            api=snow_api,
            incident_url=incident_url,
            offset=offset,
            limit=limit,
            query=query,
        )
        data += result
        if not result:
            break

    return data


def process_issues(
    issues_data: List[dict],
    snow_config: dict,
    snow_assignment_group: str,
    snow_incident_type: str,
) -> Tuple[int, int]:
    """
    Process issues and create new incidents in ServiceNow

    :param List[dict] issues_data: List of issues
    :param dict snow_config: ServiceNow configuration
    :param str snow_assignment_group: ServiceNow assignment group
    :param str snow_incident_type: ServiceNow incident type
    :return: Number of new incidents created, plus number of skipped incidents
    :rtype: Tuple[int, int]
    """
    config = snow_config["reg_config"]
    int_new = 0
    int_skipped = 0
    # Need a lock for int_new
    lock = Lock()
    # Make sure the assignment group exists
    create_snow_assignment_group(snow_assignment_group, snow_config)

    with job_progress:
        with ThreadPoolExecutor(max_workers=10) as executor:
            if issues_data:
                task = job_progress.add_task(
                    f"[#f8b737]Syncing {len(issues_data)} RegScale issues to ServiceNow",
                    total=len(issues_data),
                )

            futures = [
                executor.submit(
                    create_incident,
                    iss,
                    snow_config,
                    snow_assignment_group,
                    snow_incident_type,
                    config,
                )
                for iss in issues_data
            ]
            for future in as_completed(futures):
                try:
                    snow_response = future.result()
                    with lock:
                        if snow_response:
                            iss = snow_response["originalIssue"]
                            int_new += 1
                            logger.debug(snow_response)
                            logger.info(
                                "SNOW Incident ID %s created.",
                                snow_response["result"]["sys_id"],
                            )
                            iss["serviceNowId"] = snow_response["result"]["sys_id"]
                            try:
                                Issue(**iss).save()
                            except APIUpdateError as ex:
                                logger.error(
                                    "Unable to update issue in RegScale: %s\n%s",
                                    iss,
                                    ex,
                                )
                        else:
                            int_skipped += 1
                        job_progress.update(task, advance=1)
                except CancelledError as e:
                    logger.error("Future was cancelled: %s", e)

    return int_new, int_skipped


def create_incident(
    iss: dict,
    snow_config: dict,
    snow_assignment_group: str,
    snow_incident_type: str,
    config: dict,
) -> Optional[dict]:
    """
    Create a new incident in ServiceNow

    :param dict iss: Issue data
    :param dict snow_config: ServiceNow configuration
    :param str snow_assignment_group: ServiceNow assignment group
    :param str snow_incident_type: ServiceNow incident type
    :param dict config: Application config
    :return: Response dataset from ServiceNow or None
    :rtype: Optional[dict]
    """
    response = None

    try:
        str_issue_url = f'{config["domain"]}/issues/form/{iss["id"]}'
        if "serviceNowId" not in iss:
            iss["serviceNowId"] = ""
        if iss["serviceNowId"] == "":
            snow_incident = {
                "description": iss["description"],
                "short_description": iss["title"],
                "assignment_group": snow_assignment_group,
                "due_date": iss["dueDate"],
                "comments": "RegScale Issue #" + str(iss["id"]) + " - " + str_issue_url,
                "state": "New",
                "urgency": snow_incident_type,
            }
            incident_url = urljoin(snow_config["url"], "api/now/table/incident")
            response = create_snow_incident(snow_config["api"], incident_url, snow_incident)
    except KeyError as kex:
        logger.error("Unable to find key: %s.", kex)
    if response:
        response["originalIssue"] = iss
    return response


def sync_notes_to_regscale() -> None:
    """
    Sync work notes from ServiceNow to existing issues

    :rtype: None
    """
    app = Application()
    reg_api = Api()
    # get secrets
    snow_url = app.config["snowUrl"]
    snow_user = app.config["snowUserName"]
    snow_pwd = app.config["snowPassword"]
    snow_api = deepcopy(reg_api)  # no need to instantiate a new config, just copy object
    snow_api.auth = (snow_user, snow_pwd)
    snow_config = {"url": snow_url, "api": snow_api}
    query = "&sysparm_query=GOTO123TEXTQUERY321=regscale"
    data = get_service_now_incidents(snow_config, query=query)
    process_work_notes(config=app.config, api=reg_api, data=data)


def process_work_notes(config: dict, api: Api, data: list) -> None:
    """
    Process and Sync the worknotes to RegScale

    :param dict config: Application config
    :param Api api: API object
    :param list data: list of data from ServiceNow to sync with RegScale
    :rtype: None
    """
    update_issues = []
    for dat in track(
        data,
        description=f"Processing {len(data):,} ServiceNow incidents",
    ):
        sys_id = str(dat["sys_id"])
        try:
            regscale_response = api.get(url=config["domain"] + f"/api/issues/findByServiceNowId/{sys_id}")
            if regscale_response.raise_for_status():
                logger.warning("Cannot find RegScale issue with a incident %s.", sys_id)
            else:
                logger.debug("Processing ServiceNow Issue # %s", sys_id)
                if work_item := dat["work_notes"]:
                    issue = regscale_response.json()[0]
                    if work_item not in issue["description"]:
                        logger.info(
                            "Updating work item for RegScale issue # %s and ServiceNow incident " + "# %s.",
                            issue["id"],
                            sys_id,
                        )
                        issue["description"] = (
                            f"<strong>ServiceNow Work Notes: </strong>{work_item}<br/>" + issue["description"]
                        )
                        update_issues.append(issue)
        except requests.HTTPError:
            logger.warning(
                "HTTP Error: Unable to find RegScale issue with ServiceNow incident ID of %s.",
                sys_id,
            )
    if len(update_issues) > 0:
        logger.info(update_issues)
        api.update_server(
            url=urljoin(config["domain"], "/api/issues"),
            message=f"Updating {len(update_issues)} issues..",
            json_list=update_issues,
        )
    else:
        logger.warning("No ServiceNow work items found, No RegScale issues were updated.")
        sys.exit(0)


def query_incidents(api: Api, incident_url: str, offset: int, limit: int, query: str) -> Tuple[list, int]:
    """
    Paginate through query results

    :param Api api: API object
    :param str incident_url: URL for ServiceNow incidents
    :param int offset: Used in URL for ServiceNow API call
    :param int limit: Used in URL for ServiceNow API call
    :param str query: Query string for ServiceNow API call
    :return: Tuple[Result data from API call, offset integer provided]
    :rtype: Tuple[list, int]
    """
    offset_param = f"&sysparm_offset={offset}"
    url = urljoin(incident_url, f"?sysparm_limit={limit}{offset_param}{query}")
    logger.debug(url)
    result = api.get(url=url).json()["result"]
    offset += limit
    logger.debug(len(result))
    return result, offset
