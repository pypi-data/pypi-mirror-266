#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Scanner Integration Class """

import concurrent.futures
import dataclasses
import enum
import logging
import threading
from abc import ABC, abstractmethod
from collections import defaultdict
from typing import List, Optional, Any, Iterator, Union, Tuple

from rich.progress import Progress, TaskID

from regscale.core.app.utils.api_handler import APIHandler
from regscale.core.app.utils.app_utils import (
    get_current_datetime,
    create_progress_object,
)
from regscale.core.utils.date import date_str, days_from_today
from regscale.models import regscale_models

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class IntegrationAsset:
    """
    Dataclass for integration assets.

    Represents an asset to be integrated, including its metadata and associated components.
    If a component does not exist, it will be created based on the names provided in ``component_names``.

    :param str name: The name of the asset.
    :param str identifier: A unique identifier for the asset.
    :param str asset_type: The type of the asset.
    :param str asset_category: The category of the asset.
    :param str component_type: The type of the component, defaults to ``ComponentType.Hardware``.
    :param Optional[int] parent_id: The ID of the parent asset, defaults to None.
    :param Optional[str] parent_module: The module of the parent asset, defaults to None.
    :param str status: The status of the asset, defaults to "Active (On Network)".
    :param str date_last_updated: The last update date of the asset, defaults to the current datetime.
    :param Optional[str] asset_owner_id: The ID of the asset owner, defaults to None.
    :param Optional[str] mac_address: The MAC address of the asset, defaults to None.
    :param Optional[str] fqdn: The Fully Qualified Domain Name of the asset, defaults to None.
    :param Optional[str] ip_address: The IP address of the asset, defaults to None.
    :param List[str] component_names: A list of strings that represent the names of the components associated with the asset, components will be created if they do not exist.
    """

    name: str
    identifier: str
    asset_type: str
    asset_category: str
    component_type: str = regscale_models.ComponentType.Hardware
    parent_id: Optional[int] = None
    parent_module: Optional[str] = None
    status: str = "Active (On Network)"
    date_last_updated: str = dataclasses.field(default_factory=get_current_datetime)
    asset_owner_id: Optional[str] = None
    mac_address: Optional[str] = None
    fqdn: Optional[str] = None
    ip_address: Optional[str] = None
    component_names: List[str] = dataclasses.field(default_factory=list)


@dataclasses.dataclass
class IntegrationFinding:
    """
    Dataclass for integration findings.

    :param list[str] control_labels: A list of control labels associated with the finding.
    :param str title: The title of the finding.
    :param str category: The category of the finding.
    :param regscale_models.IssueSeverity severity: The severity of the finding, based on regscale_models.IssueSeverity.
    :param str description: A description of the finding.
    :param regscale_models.ControlTestResultStatus status: The status of the finding, based on regscale_models.ControlTestResultStatus.
    :param str priority: The priority of the finding, defaults to "Medium".
    :param str issue_type: The type of issue, defaults to "Risk".
    :param str issue_title: The title of the issue, defaults to an empty string.
    :param str date_created: The creation date of the finding, defaults to the current datetime.
    :param str due_date: The due date of the finding, defaults to 60 days from the current datetime.
    :param str date_last_updated: The last update date of the finding, defaults to the current datetime.
    :param str external_id: An external identifier for the finding, defaults to an empty string.
    :param str gaps: A description of any gaps identified, defaults to an empty string.
    :param str observations: Observations related to the finding, defaults to an empty string.
    :param str evidence: Evidence supporting the finding, defaults to an empty string.
    :param str identified_risk: The risk identified by the finding, defaults to an empty string.
    :param str impact: The impact of the finding, defaults to an empty string.
    :param str recommendation_for_mitigation: Recommendations for mitigating the finding, defaults to an empty string.
    :param str asset_identifier: The identifier of the asset associated with the finding, defaults to an empty string.
    :param Optional[str] cci_ref: The Common Configuration Enumeration reference for the finding, defaults to None.
    :param str rule_id: The rule ID of the finding, defaults to an empty string.
    :param str rule_version: The version of the rule associated with the finding, defaults to an empty string.
    :param str results: The results of the finding, defaults to an empty string.
    :param Optional[str] comments: Additional comments related to the finding, defaults to None.
    :param str baseline: The baseline of the finding, defaults to an empty string.
    :param str poam_comments: Comments related to the Plan of Action and Milestones (POAM) for the finding, defaults to an empty string.
    """

    control_labels: List[str]
    title: str
    category: str
    severity: regscale_models.IssueSeverity
    description: str
    status: Union[regscale_models.ControlTestResultStatus, regscale_models.ChecklistStatus]
    priority: str = "Medium"

    # Issues
    issue_title: str = ""
    issue_type: str = "Risk"
    date_created: str = dataclasses.field(default_factory=get_current_datetime)
    date_last_updated: str = dataclasses.field(default_factory=get_current_datetime)
    due_date: str = date_str(days_from_today(60))
    external_id: str = ""
    gaps: str = ""
    observations: str = ""
    evidence: str = ""
    identified_risk: str = ""
    impact: str = ""
    recommendation_for_mitigation: str = ""
    asset_identifier: str = ""
    cci_ref: Optional[str] = None
    rule_id: str = ""
    rule_version: str = ""
    results: str = ""
    comments: Optional[str] = None
    baseline: str = ""
    poam_comments: Optional[str] = None


class ScannerIntegrationType(str, enum.Enum):
    """
    Enumeration for scanner integration types.
    """

    CHECKLIST = "checklist"
    CONTROL_TEST = "control_test"


class ScannerIntegration(ABC):
    """
    Abstract class for scanner integrations.

    :param int plan_id: The ID of the security plan
    """

    options_map_assets_to_components: bool = False

    type = ScannerIntegrationType.CONTROL_TEST
    title = "Scanner Integration"
    asset_identifier_field = ""
    asset_progress: Progress
    finding_progress: Progress
    num_assets_to_process: Optional[int] = None
    num_findings_to_process: Optional[int] = None
    errors: List[str] = []
    finding_status_map: dict[Any, regscale_models.ChecklistStatus] = {}
    finding_severity_map: dict[Any, regscale_models.IssueSeverity] = {}
    asset_map: dict[str, regscale_models.Asset] = {}

    # Maps with Locks
    components: list[Any] = []
    components_lock = threading.Lock()

    asset_map_by_identifier: dict[str, regscale_models.Asset] = {}
    asset_map_by_identifier_lock = threading.Lock()

    existing_issues_map: dict[int, List[regscale_models.Issue]] = defaultdict(list)
    existing_issues_map_lock = threading.Lock()

    checklist_asset_map: dict[int, List[regscale_models.Checklist]] = defaultdict(list)
    checklist_asset_map_lock = threading.Lock()

    components_by_title: dict[str, regscale_models.Component] = {}
    components_by_title_lock = threading.Lock()

    def __init__(self, plan_id: int):
        self.plan_id = plan_id
        self.control_implementation_map = regscale_models.ControlImplementation.get_control_map_by_plan(plan_id=plan_id)
        self.control_map = {v: k for k, v in self.control_implementation_map.items()}
        self.assessment_map = {}
        self.assessor_id = self.get_assessor_id()
        self.asset_progress = create_progress_object()
        self.finding_progress = create_progress_object()
        self.asset_map_by_identifier = self.get_asset_map()

    def get_asset_map(self) -> dict[str, regscale_models.Asset]:
        """
        Retrieves a mapping of asset identifiers to their corresponding Asset objects. This method supports two modes
        of operation based on the `options_map_assets_to_components` flag. If the flag is set, it fetches the asset
        map using a specified key field from the assets associated with the given plan ID. Otherwise, it constructs
        the map by fetching all assets under the specified plan and using the asset identifier field as the key.

        :return: A dictionary mapping asset identifiers to Asset objects.
        :rtype: dict[str, regscale_models.Asset]
        """
        if self.options_map_assets_to_components:
            # Fetches the asset map directly using a specified key field.
            return regscale_models.Asset.get_map(plan_id=self.plan_id, key_field=self.asset_identifier_field)
        else:
            # Constructs the asset map by fetching all assets under the plan and using the asset identifier field as
            # the key.
            return {
                getattr(x, self.asset_identifier_field): x
                for x in regscale_models.Asset.get_all_by_parent(
                    parent_id=self.plan_id, parent_module=regscale_models.SecurityPlan.get_module_string()
                )
            }

    @staticmethod
    def get_assessor_id() -> str:
        """
        Gets the ID of the assessor

        :return: The ID of the assessor
        :rtype: str
        """

        api_handler = APIHandler()
        return api_handler.get_user_id()

    @abstractmethod
    def fetch_findings(self, *args: Tuple, **kwargs: dict) -> List[IntegrationFinding]:
        """
        Fetches findings from the integration

        :param Tuple *args: Additional arguments
        :param dict **kwargs: Additional keyword arguments
        :return: A list of findings
        :rtype: List[IntegrationFinding]
        """
        pass

    @abstractmethod
    def fetch_assets(self, *args: Tuple, **kwargs: dict) -> Iterator[IntegrationAsset]:
        """
        Fetches assets from the integration

        :param Tuple *args: Additional arguments
        :param dict **kwargs: Additional keyword arguments
        :return: A list of assets
        :rtype: Iterator[IntegrationAsset]
        """
        pass

    def get_finding_status(self, status: Optional[str]) -> regscale_models.ChecklistStatus:
        """
        Gets the RegScale checklist status based on the integration finding status

        :param Optional[str] status: The status of the finding
        :return: The RegScale checklist status
        :rtype: regscale_models.ChecklistStatus
        """
        return self.finding_status_map.get(status, regscale_models.ChecklistStatus.NOT_REVIEWED)

    def get_finding_severity(self, severity: Optional[str]) -> regscale_models.IssueSeverity:
        """
        Gets the RegScale issue severity based on the integration finding severity

        :param Optional[str] severity: The severity of the finding
        :return: The RegScale issue severity
        :rtype: regscale_models.IssueSeverity
        """
        return self.finding_severity_map.get(severity, regscale_models.IssueSeverity.NotAssigned)

    def get_or_create_assessment(self, control_implementation_id: int) -> regscale_models.Assessment:
        """
        Gets or creates a RegScale assessment

        :param int control_implementation_id: The ID of the control implementation
        :return: The assessment
        :rtype: regscale_models.Assessment
        """
        logger.info(f"Getting or creating assessment for control implementation {control_implementation_id}")
        assessment: Optional[regscale_models.Assessment] = self.assessment_map.get(control_implementation_id)
        if assessment:
            logger.debug(
                f"Found cached assessment {assessment.id} for control implementation {control_implementation_id}"
            )
        else:
            logger.debug(f"Assessment not found for control implementation {control_implementation_id}")
            assessment = regscale_models.Assessment(
                plannedStart=get_current_datetime(),
                plannedFinish=get_current_datetime(),
                status=regscale_models.AssessmentStatus.COMPLETE.value,
                assessmentResult=regscale_models.AssessmentResultsStatus.FAIL.value,
                actualFinish=get_current_datetime(),
                leadAssessorId=self.assessor_id,
                parentId=control_implementation_id,
                parentModule=regscale_models.ControlImplementation.get_module_string(),
                title=f"{self.title} Assessment",
                assessmentType=regscale_models.AssessmentType.QA_SURVEILLANCE.value,
            ).create()
        self.assessment_map[control_implementation_id] = assessment
        return assessment

    def create_issue_from_finding(
        self,
        title: str,
        parent_id: int,
        parent_module: str,
        finding: IntegrationFinding,
    ) -> regscale_models.Issue:
        """
        Creates a RegScale issue from a finding

        :param str title: The title of the issue
        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :param IntegrationFinding finding: The finding data
        :return: The Issue create from the finding
        :rtype: regscale_models.Issue
        """
        issue_status = (
            regscale_models.IssueStatus.Closed
            if finding.status == regscale_models.ControlTestResultStatus.PASS
            else regscale_models.IssueStatus.Open
        )

        return regscale_models.Issue(
            parentId=parent_id,
            parentModule=parent_module,
            title=title[:450],  # Truncate to 450 characters
            dateCreated=finding.date_created,
            status=issue_status,
            severityLevel=finding.severity,
            issueOwnerId=self.assessor_id,
            securityPlanId=self.plan_id,
            identification="Vulnerability Assessment",
            dateFirstDetected=finding.date_created,
            dueDate=finding.due_date,
            description=finding.description,
            sourceReport="STIG",
            recommendedActions=finding.recommendation_for_mitigation,
            assetIdentifier=finding.asset_identifier,
            securityChecks=finding.external_id,
            remediationDescription=finding.recommendation_for_mitigation,
            otherIdentifier=finding.external_id,
            poamComments=finding.poam_comments,
        ).create()

    @staticmethod
    def update_issues_from_finding(issue: regscale_models.Issue, finding: IntegrationFinding) -> regscale_models.Issue:
        """
        Updates RegScale issues based on the integration findings

        :param regscale_models.Issue issue: The issue to update
        :param IntegrationFinding finding: The integration findings
        :return: The updated issue
        :rtype: regscale_models.Issue
        """
        issue_status = (
            regscale_models.IssueStatus.Closed
            if finding.status == regscale_models.ControlTestResultStatus.PASS
            else regscale_models.IssueStatus.Open
        )
        if issue.status != issue_status:
            issue.status = issue_status
            issue.severityLevel = finding.severity
            issue.dateLastUpdated = finding.date_last_updated
            issue.description = finding.description
            issue.recommendedActions = finding.recommendation_for_mitigation
            issue.dateFirstDetected = finding.date_created
            issue.dueDate = date_str(days_from_today(30))
            issue.assetIdentifier = finding.asset_identifier
            issue.securityChecks = finding.external_id
            issue.remediationDescription = finding.recommendation_for_mitigation
            return issue.save()
        return issue

    def handle_passing_finding(
        self,
        existing_issues: List[regscale_models.Issue],
        finding: IntegrationFinding,
        parent_id: int,
        parent_module: str,
    ) -> None:
        """
        Handles findings that have passed by closing any open issues associated with the finding.

        :param List[regscale_models.Issue] existing_issues: The list of existing issues to check against
        :param IntegrationFinding finding: The finding data that has passed
        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :rtype: None
        """
        logger.info(f"Handling passing finding {finding.external_id} for {parent_id}")
        for issue in existing_issues:
            if issue.identification == finding.external_id and issue.status != regscale_models.IssueStatus.Closed:
                if parent_module == regscale_models.ControlImplementation.get_module_string():
                    logger.info(f"Closing issue {issue.id} for control {self.control_map[parent_id]}")
                else:
                    logger.info(f"Closing issue {issue.id} for asset {parent_id}")
                issue.status = regscale_models.IssueStatus.Closed
                issue.dateCompleted = finding.date_last_updated
                issue.save()

    def handle_failing_finding(
        self,
        issue_title: str,
        existing_issues: List[regscale_models.Issue],
        finding: IntegrationFinding,
        parent_id: int,
        parent_module: str,
    ) -> None:
        """
        Handles findings that have failed by updating an existing open issue or creating a new one.

        :param str issue_title: The title of the issue
        :param List[regscale_models.Issue] existing_issues: The list of existing issues to check against
        :param IntegrationFinding finding: The finding data that has failed
        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :rtype: None
        """
        # logger.info(f"Handling failing finding {finding.external_id} for {parent_id}")

        # Determine the parent type based on the parent module
        parent_type = (
            "control" if parent_module == regscale_models.ControlImplementation.get_module_string() else "asset"
        )
        # Attempt to find an existing open issue that matches the finding's external ID.
        if found_issue := next(
            (
                issue
                for issue in existing_issues
                if issue.otherIdentifier == finding.external_id and issue.status != regscale_models.IssueStatus.Closed
            ),
            None,
        ):
            # If an existing open issue is found, update it with the new finding data.
            logger.info(f"Updating issue {found_issue.id} for {parent_type} {parent_id}")
            self.update_issues_from_finding(issue=found_issue, finding=finding)
        else:
            # If no existing open issue is found, create a new one.
            logger.info(f"Creating issue for {parent_type} {parent_id}")
            self.create_issue_from_finding(
                title=issue_title,
                parent_id=parent_id,
                parent_module=parent_module,
                finding=finding,
            )

    def update_regscale_checklists(self, findings: List[IntegrationFinding]) -> None:
        """
        Process checklists from IntegrationFindings in a threaded manner.

        :param List[IntegrationFinding] findings: The findings to process
        :rtype: None
        """
        logger.info("Updating RegScale checklists...")
        loading_findings = self.finding_progress.add_task(
            f"[#f8b737]Creating and updating checklists from {self.title}.",
        )
        progress_lock = threading.Lock()

        # Set concurrency to 3 to avoid overloading the API
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_to_finding = {executor.submit(self.process_checklist, finding): finding for finding in findings}
            for future in concurrent.futures.as_completed(future_to_finding):
                finding = future_to_finding[future]
                try:
                    # Accessing the result of the future will raise any exceptions that occurred
                    future.result()
                    with progress_lock:
                        # Wait until self.num_findings_to_process is set to set task total.
                        if self.num_findings_to_process and self.finding_progress.tasks[
                            loading_findings
                        ].total != float(self.num_findings_to_process):
                            self.finding_progress.update(
                                loading_findings,
                                total=self.num_findings_to_process,
                                description=f"[#f8b737]Creating and updating {self.num_findings_to_process} checklists from {self.title}.",
                            )
                        self.finding_progress.advance(loading_findings, 1)
                except Exception as exc:
                    self.log_error(
                        f"An error occurred when processing asset {finding.asset_identifier} "
                        f"for finding {finding.external_id}: {exc}"
                    )
        APIHandler().log_api_summary()

    def process_checklist(self, finding: IntegrationFinding) -> None:
        """
        Processes a single checklist item based on the provided finding.

        This method checks if the asset related to the finding exists, updates or creates a checklist item,
        and handles the finding based on its status (pass/fail).

        :param IntegrationFinding finding: The finding to process
        :rtype: None
        """
        logger.info(f"Processing checklist {finding.external_id}")
        asset = self.asset_map_by_identifier.get(finding.asset_identifier)
        if not asset:
            self.log_error(f"Asset not found for identifier {finding.asset_identifier}, skipping finding")
            return

        asset_module_string = regscale_models.Asset.get_module_string()

        with self.checklist_asset_map_lock:
            # Clear the cache if it grows too large to prevent memory issues
            if len(self.checklist_asset_map) > 30:
                self.checklist_asset_map.clear()

            # Check if the asset's checklists are already in the cache
            if not (checklists := self.checklist_asset_map.get(asset.id)):
                # If not, fetch and cache the checklists
                self.checklist_asset_map[asset.id] = regscale_models.Checklist.get_all_by_parent(
                    parent_id=asset.id, parent_module=asset_module_string
                )
                # Now, checklists will always fetch from the cache, avoiding unnecessary database calls
                checklists = self.checklist_asset_map[asset.id]

        found_checklist = next(
            (
                checklist
                for checklist in checklists
                if checklist.vulnerabilityId == finding.external_id
                and checklist.tool == regscale_models.ChecklistTool.STIGs
            ),
            None,
        )

        if not found_checklist:
            regscale_models.Checklist(
                status=finding.status,
                assetId=asset.id,
                tool=regscale_models.ChecklistTool.STIGs,
                baseline=finding.baseline,
                vulnerabilityId=finding.external_id,
                results="??",  # TODO: Determine what to put here
                check=finding.title,
                cci=finding.cci_ref,  # TODO: Fix CCI
                ruleId=finding.rule_id,
                version=finding.rule_version,
                comments=finding.comments,
                datePerformed=finding.date_created,
            ).create()
        else:
            found_checklist.status = finding.status
            found_checklist.results = finding.results
            found_checklist.comments = finding.comments
            found_checklist.save()

        with self.existing_issues_map_lock:
            # Check if the asset's issues are already in the cache
            if asset.id not in self.existing_issues_map:
                # If not, fetch and cache the issues
                self.existing_issues_map[asset.id] = regscale_models.Issue.get_all_by_parent(
                    parent_id=asset.id, parent_module=asset_module_string
                )
            # Now, existing_issues will always fetch from the cache, avoiding unnecessary database calls
            existing_issues = self.existing_issues_map[asset.id]

            # Optionally clear the cache if it grows too large
            if len(self.existing_issues_map) > 30:
                self.existing_issues_map.clear()

        if finding.status == regscale_models.ChecklistStatus.PASS:
            self.handle_passing_finding(existing_issues, finding, asset.id, asset_module_string)
        else:
            self.handle_failing_finding(
                issue_title=finding.issue_title or finding.title,
                existing_issues=existing_issues,
                finding=finding,
                parent_id=asset.id,
                parent_module=asset_module_string,
            )

    def update_regscale_findings(self, findings: List[IntegrationFinding]) -> None:
        """
        Updates RegScale findings based on the integration findings

        :param List[IntegrationFinding] findings: The integration findings
        :rtype: None
        """
        for finding in findings:
            if finding:
                for control_label in finding.control_labels:
                    if not (control_implementation_id := self.control_implementation_map.get(control_label)):
                        logger.error(f"Control Implementation for {control_label} not found in RegScale")
                        continue
                    assessment = self.get_or_create_assessment(control_implementation_id)
                    control_test = regscale_models.ControlTest(
                        uuid=finding.external_id,
                        parentControlId=control_implementation_id,
                        testCriteria=finding.description,
                    ).get_or_create()
                    regscale_models.ControlTestResult(
                        parentTestId=control_test.id,
                        parentAssessmentId=assessment.id,
                        uuid=finding.external_id,
                        result=finding.status,  # type: ignore
                        dateAssessed=finding.date_created,
                        assessedById=self.assessor_id,
                        gaps=finding.gaps,
                        observations=finding.observations,
                        evidence=finding.evidence,
                        identifiedRisk=finding.identified_risk,
                        impact=finding.impact,
                        recommendationForMitigation=finding.recommendation_for_mitigation,
                    ).create()
                    logger.info(
                        f"Created or Updated assessment {assessment.id} for control "
                        f"{self.control_map[control_implementation_id]}"
                    )
                    existing_issues: list[regscale_models.Issue] = regscale_models.Issue.get_all_by_parent(
                        parent_id=control_implementation_id,
                        parent_module=regscale_models.ControlImplementation.get_module_string(),
                    )
                    if finding.status == regscale_models.ControlTestResultStatus.PASS:
                        self.handle_passing_finding(
                            existing_issues=existing_issues,
                            finding=finding,
                            parent_id=control_implementation_id,
                            parent_module=regscale_models.ControlImplementation.get_module_string(),
                        )
                    else:
                        self.handle_failing_finding(
                            issue_title=f"Finding {finding.external_id} failed",
                            existing_issues=existing_issues,
                            finding=finding,
                            parent_id=control_implementation_id,
                            parent_module=regscale_models.ControlImplementation.get_module_string(),
                        )

    def get_components(self) -> List[regscale_models.Component]:
        """
        Get all components from the integration

        :return: A list of components
        :rtype: List[regscale_models.Component]
        """
        if any(self.components):
            return self.components
        self.components = regscale_models.Component.get_all_by_parent(
            parent_id=self.plan_id,
            parent_module=regscale_models.SecurityPlan.get_module_string(),
        )
        return self.components

    def get_component_by_title(self) -> dict:
        """
        Get all components from the integration

        :return: A dictionary of components
        :rtype: dict
        """
        return {component.title: component for component in self.get_components()}

    def set_asset_defaults(self, asset: IntegrationAsset) -> IntegrationAsset:
        """
        Set default values for the asset (Thread Safe)

        :param IntegrationAsset asset: The integration asset
        :return: The asset with which defaults should be set
        :rtype: IntegrationAsset
        """
        if not asset.asset_owner_id:
            asset.asset_owner_id = self.get_assessor_id()
        if not asset.status:
            asset.status = "Active (On Network)"
        return asset

    def update_regscale_assets(self, assets: Iterator[IntegrationAsset]) -> None:
        """
        Updates RegScale assets based on the integration assets

        :param Iterator[IntegrationAsset] assets: The integration assets
        :rtype: None
        """

        self.asset_map_by_identifier = regscale_models.Asset.get_map(
            plan_id=self.plan_id, key_field=self.asset_identifier_field
        )

        logger.info("Updating RegScale assets...")
        loading_assets = self.asset_progress.add_task(
            f"[#f8b737]Creating and updating assets from {self.title}.",
        )
        progress_lock = threading.Lock()

        # Initialize maps
        if self.options_map_assets_to_components:
            # Look up Component by title
            self.components_by_title = self.get_component_by_title()
        self.asset_map_by_identifier = self.get_asset_map()

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_asset = {
                executor.submit(
                    self.process_asset,
                    asset,
                    loading_assets,
                    progress_lock,
                ): asset
                for asset in assets
            }
            for future in concurrent.futures.as_completed(future_to_asset):
                asset = future_to_asset[future]
                try:
                    future.result()
                except Exception as exc:
                    self.log_error(f"An error occurred when processing asset {asset.name}: {exc}")

    def process_asset(
        self,
        asset: IntegrationAsset,
        loading_assets: TaskID,
        progress_lock: threading.Lock,
    ) -> None:
        """
        Safely processes a single asset in a concurrent environment. This method ensures thread safety
        by utilizing a threading lock. It assigns default values to the asset if necessary, maps the asset
        to components if specified, and updates the progress of asset loading.
        (Thread Safe)

        :param IntegrationAsset asset: The integration asset to be processed.
        :param TaskID loading_assets: The identifier for the task tracking the progress of asset loading.
        :param threading.Lock progress_lock: A lock to ensure thread-safe updates to the progress tracking.
        :rtype: None
        """

        # Assign default values to the asset if they are not already set.
        asset = self.set_asset_defaults(asset)

        # If mapping assets to components is enabled and the asset has associated component names,
        # attempt to update or create each asset under its respective component.
        if self.options_map_assets_to_components and any(asset.component_names):
            for component_name in asset.component_names:
                self.update_or_create_asset(asset, component_name)
        else:
            # If no component mapping is required, add the asset directly to the security plan without a component.
            self.update_or_create_asset(asset, None)

        with progress_lock:
            # Ensure the total number of assets to process is reflected in the task's total before advancing the progress.
            if self.num_assets_to_process and self.asset_progress.tasks[loading_assets].total != float(
                self.num_assets_to_process
            ):
                self.asset_progress.update(loading_assets, total=self.num_assets_to_process)
            # Increment the progress for the asset loading task by one.
            self.asset_progress.advance(loading_assets, 1)

    def update_or_create_asset(
        self,
        asset: IntegrationAsset,
        component_name: Optional[str] = None,
    ) -> None:
        """
        This method either updates an existing asset or creates a new one within a thread-safe manner. It handles
        the asset's association with a component, creating the component if it does not exist.
        (Thread Safe)

        :param IntegrationAsset asset: The asset to be updated or created.
        :param Optional[str] component_name: The name of the component to associate the asset with. If None, the asset
                                             is added directly to the security plan without a component association.
        """
        component = None
        if component_name:
            logger.info(f"Searching for component: {component_name}...")
            with self.components_by_title_lock:
                if not (component := self.components_by_title.get(component_name)):
                    logger.info(f"No existing component found with name {component_name}, proceeding to create it...")
                    component = regscale_models.Component(
                        title=component_name,
                        componentType=asset.component_type,
                        securityPlansId=self.plan_id,
                        description=component_name,
                        componentOwnerId=self.get_assessor_id(),
                    ).create()
                    with self.components_lock:
                        self.components.append(component)
                    if component.securityPlansId:
                        regscale_models.ComponentMapping(
                            componentId=component.id,
                            securityPlanId=component.securityPlansId,
                        ).get_or_create()
                self.components_by_title[component_name] = component

        # Check if the asset already exists and update it if necessary, otherwise create a new asset.
        if existing_or_new_asset := self.find_existing_asset(asset):
            self.update_asset_if_needed(asset, existing_or_new_asset)
        else:
            existing_or_new_asset = self.create_new_asset(asset, component=component)

        # If the asset is associated with a component, create a mapping between them.
        if component:
            regscale_models.AssetMapping(
                assetId=existing_or_new_asset.id,
                componentId=component.id,
            ).get_or_create()

    def find_existing_asset(self, asset: IntegrationAsset) -> Optional[regscale_models.Asset]:
        """
        Searches for and retrieves an existing asset within the system that corresponds to the provided integration asset.
        This operation is performed in a thread-safe manner to ensure data integrity during concurrent access.
        (Thread Safe)

        :param IntegrationAsset asset: The integration asset for which an existing match is sought.
        :return: An instance of the matching existing asset if found; otherwise, None.
        :rtype: Optional[regscale_models.Asset]
        """
        with self.asset_map_by_identifier_lock:
            return self.asset_map_by_identifier.get(asset.identifier)

    @staticmethod
    def update_asset_if_needed(asset: IntegrationAsset, existing_asset: regscale_models.Asset) -> None:
        """
        Updates an existing asset if any of its fields differ from the integration asset (Thread Safe)

        :param IntegrationAsset asset: The integration asset
        :param regscale_models.Asset existing_asset: The existing asset
        :rtype: None
        """
        is_updated = False
        if asset.asset_owner_id and existing_asset.assetOwnerId != asset.asset_owner_id:
            existing_asset.assetOwnerId = asset.asset_owner_id
            is_updated = True
        if asset.parent_id and existing_asset.parentId != asset.parent_id:
            existing_asset.parentId = asset.parent_id
            is_updated = True
        if asset.parent_module and existing_asset.parentModule != asset.parent_module:
            existing_asset.parentModule = asset.parent_module
            is_updated = True
        if existing_asset.assetType != asset.asset_type:
            existing_asset.assetType = asset.asset_type
            is_updated = True
        if existing_asset.status != asset.status:
            existing_asset.status = asset.status
            is_updated = True
        if existing_asset.assetCategory != asset.asset_category:
            existing_asset.assetCategory = asset.asset_category
            is_updated = True

        if is_updated:
            existing_asset.dateLastUpdated = asset.date_last_updated
            existing_asset.save()
            logger.info(f"Updated asset {asset.identifier}")
        else:
            logger.info(f"Asset {asset.identifier} is already up to date")

    def create_new_asset(
        self, asset: IntegrationAsset, component: Optional[regscale_models.Component]
    ) -> regscale_models.Asset:
        """
        This method is responsible for creating a new asset in the system based on the provided integration asset details.
        If a component is specified, the new asset will be associated with this component. Otherwise, it will be directly
        associated with the security plan. This process is executed in a thread-safe manner to ensure data integrity.
        (Thread Safe)

        :param IntegrationAsset asset: The integration asset from which the new asset will be created.
        :param Optional[regscale_models.Component] component: The component to which the new asset should be linked,
                                                              or None if it should be linked directly to the security plan.
        :return: The newly created asset instance.
        :rtype: regscale_models.Asset
        """
        new_asset = regscale_models.Asset(
            name=asset.name,
            assetOwnerId=asset.asset_owner_id or "Unknown",
            parentId=component.id if component else self.plan_id,
            parentModule=(
                regscale_models.Component.get_module_string()
                if component
                else regscale_models.SecurityPlan.get_module_string()
            ),
            assetType=asset.asset_type,
            dateLastUpdated=asset.date_last_updated,
            status=asset.status,
            assetCategory=asset.asset_category,
        )
        if self.asset_identifier_field:
            setattr(new_asset, self.asset_identifier_field, asset.identifier)
        new_asset = new_asset.create()
        with self.asset_map_by_identifier_lock:
            self.asset_map_by_identifier[asset.identifier] = new_asset
        logger.info(f"Created new asset with identifier {asset.identifier}")

        # Create an AssetMapping if the new asset is associated with a component
        if component:
            regscale_models.AssetMapping(
                assetId=new_asset.id,
                componentId=component.id,
            ).get_or_create()

        return new_asset

    def log_error(self, error: str, exc_info: bool = True) -> None:
        """
        Logs an error along with the stack trace.

        :param str error: The error message
        :param bool exc_info: If True, includes the stack trace of the current exception in the log.
        :rtype: None
        """
        self.errors.append(error)
        logger.error(error, exc_info=exc_info)

    @classmethod
    def sync_findings(cls, plan_id: int, **kwargs: dict) -> None:
        """
        Syncs findings from the integration to RegScale

        :param int plan_id: The ID of the security plan
        :param dict **kwargs: Additional keyword arguments
        :rtype: None
        """
        logger.info(f"Syncing {cls.title} findings...")
        instance = cls(plan_id)
        instance.finding_progress = create_progress_object()
        with instance.finding_progress:
            if cls.type == ScannerIntegrationType.CHECKLIST:
                instance.update_regscale_checklists(findings=instance.fetch_findings(**kwargs))
            else:
                instance.update_regscale_findings(findings=instance.fetch_findings(**kwargs))
            if instance.errors:
                logger.error("Summary of errors encountered:")
                for error in instance.errors:
                    logger.error(error)
            else:
                logger.info("All findings have been processed successfully.")

    @classmethod
    def sync_assets(cls, plan_id: int, **kwargs: dict) -> None:
        """
        Syncs assets from the integration to RegScale

        :param int plan_id: The ID of the security plan
        :param dict **kwargs: Additional keyword arguments
        :rtype: None
        """
        logger.info(f"Syncing {cls.title} assets...")
        instance = cls(plan_id)
        instance.asset_progress = create_progress_object()
        with instance.asset_progress:
            instance.update_regscale_assets(assets=instance.fetch_assets(**kwargs))

        if instance.errors:
            logger.error("Summary of errors encountered:")
            for error in instance.errors:
                logger.error(error)
        else:
            logger.info("All assets have been processed successfully.")
