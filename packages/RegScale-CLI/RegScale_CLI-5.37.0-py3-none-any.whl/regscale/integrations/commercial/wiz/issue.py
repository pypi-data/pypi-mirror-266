""" Wiz Issue Integration class """

import json
import os
from datetime import timedelta, datetime
from typing import List, Dict, Optional, Tuple

from regscale.core.app.utils.app_utils import create_progress_object
from regscale.models import (
    Issue,
    IssueSeverity,
    Link,
    IssueStatus,
    Data,
    DataDataType,
    Comment,
)
from regscale.core.app.application import Application
from regscale.utils.graphql_client import PaginatedGraphQLClient
from regscale.integrations.integration.issue import IntegrationIssue
from .constants import (
    CONTENT_TYPE,
    ISSUE_QUERY,
    DATASOURCE,
    ISSUES_FILE_PATH,
    SEVERITY_MAP,
)
from regscale.utils.dict_utils import get_value
import logging

logger = logging.getLogger(__name__)


class WizIssue(IntegrationIssue):
    """
    Wiz Issue class
    """

    def __init__(
        self,
        filter_by,
        regscale_id: int,
        regscale_module: str,
        wiz_url: str,
        first: int = 100,
        wiz_projects=None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if wiz_projects is None:
            wiz_projects = []
        self.variables = {
            "first": first,
            "filterBy": filter_by,
        }
        self.regscale_id = regscale_id
        self.regscale_module = regscale_module
        self.wiz_projects = wiz_projects
        self.wiz_url = wiz_url
        app = Application()
        self.config = app.config
        self.issue_to_create = []
        self.issues_to_update = []
        self.additional_data = {}
        self.additional_data_updated = {}

    def pull(self):
        """
        Pull issues from Wiz for the given project ids
        """
        wiz_issues = self.fetch_wiz_data_if_needed()
        logger.info(f"Found {len(wiz_issues)} issues from Wiz")

        self.create_issues(
            wiz_issues=wiz_issues,
        )
        all_issues = []
        try:
            if self.issue_to_create:
                created_issues = Issue.batch_create(items=self.issue_to_create)
                all_issues.extend(created_issues)
                logger.info(f"Created {len(created_issues)} new issues.")
            if self.issues_to_update:
                updated_issues = Issue.batch_update(items=self.issues_to_update)
                all_issues.extend(updated_issues)
                logger.info(f"Updated {len(updated_issues)} issues.")
        except Exception as e:
            logger.error(f"Error during issue batch operation: {e}")

        logger.info(f"Total issues processed: {len(all_issues)}")
        # if self.issue_to_create:
        #     self._process_additional_data_create(issues=all_issues)
        # if self.issues_to_update:
        self._process_additional_data_create_or_update(issues=all_issues)

    def _process_additional_data_create_or_update(self, issues: List[Issue]) -> None:
        """
        Process additional data for updates

        :param List[Issue] issues: Issues
        :return None: None
        :rtype None: None
        """
        data_list: List[Data] = []
        links: List[Link] = []
        comments: List[Comment] = []
        logger.info(f"Processing additional data for {len(issues)} issues")
        for issue in issues:
            if wiz_id := issue.wizId:
                self._handle_updating_additional_data(
                    data_dict=self.additional_data_updated.get(wiz_id, {}),
                    issue=issue,
                    data_list=data_list,
                    links=links,
                    comments=comments,
                )
            if data_list:
                update_data_progress = create_progress_object()
                update_data_task = update_data_progress.add_task(
                    "[#f68d1f]Updating additional data...", total=len(data_list)
                )
                with update_data_progress:
                    self._create_data(data_list=data_list, issue_id=issue.id)
                    update_data_progress.advance(update_data_task, advance=1)

            if links:
                update_links_progress = create_progress_object()
                update_links_task = update_links_progress.add_task(
                    "[#f68d1f]Updating additional links...", total=len(links)
                )
                with update_links_progress:
                    self._create_links(links=links, issue_id=issue.id)
                    update_links_progress.advance(update_links_task, advance=1)

            if comments:
                update_comments_progress = create_progress_object()
                update_comments_task = update_comments_progress.add_task(
                    "[#f68d1f]Updating additional comments...", total=len(comments)
                )
                with update_comments_progress:
                    self._create_comments(comments=comments, issue_id=issue.id)
                    update_comments_progress.advance(update_comments_task, advance=1)

    @staticmethod
    def _create_data(data_list: List[Data], issue_id: int) -> None:
        """
        Create data for the given issue

        :param List[Data] data_list: List of data
        :param int issue_id: Issue ID
        """
        existing_data = Data.get_all_by_parent(parent_id=issue_id, parent_module="issues")
        existing_data_dict = {d.rawData: d for d in existing_data if d.dataSource == DATASOURCE}
        for data in data_list:
            if not existing_data_dict.get(data.rawData):
                data.create()

    @staticmethod
    def _create_links(links: List[Link], issue_id: int) -> None:
        """
        Create links for the given issue
        :param List[Link] links: List of links
        :param int issue_id: Issue ID
        :rtype: None
        """
        existing_link = Link.get_all_by_parent(parent_id=issue_id, parent_module="issues")
        existing_link_dict = {link.url: link for link in existing_link}
        for link in links:
            if not existing_link_dict.get(link.url):
                link.create()

    @staticmethod
    def _create_comments(comments: List[Comment], issue_id: int) -> None:
        """
        Create comments for the given issue
        :param List[Comment] comments: List of comments
        :param int issue_id: Issue ID
        :rtype: None
        """
        existing_link = Comment.get_all_by_parent(parent_id=issue_id, parent_module="issues")
        existing_link_dict = {c.comment: c for c in existing_link}
        for comment in comments:
            if not existing_link_dict.get(comment.comment):
                comment.create()

    def _process_additional_data_create(self, issues: List[Issue]) -> None:
        """
        Process additional data
        :param List[Issue] issues: Issues
        :rtype: None
        """
        data_list = []
        links = []
        comments = []
        for issue in issues:
            if wiz_id := issue.wizId:
                self._handle_creating_additional_data(
                    data_dict=self.additional_data.get(wiz_id, {}),
                    issue=issue,
                    data_list=data_list,
                    links=links,
                    comments=comments,
                )

        if data_list:
            # create progress object here for the following for loop
            create_data_progress = create_progress_object()
            create_data_task = create_data_progress.add_task(
                "[#f68d1f]Creating additional data...", total=len(data_list)
            )
            with create_data_progress:
                for data in data_list:
                    data.create()
                    create_data_progress.advance(create_data_task, advance=1)
            # Data.batch_create(data_list)
        if links:
            create_link_progress = create_progress_object()
            create_link_task = create_link_progress.add_task(  # create progress object here for the following for loop
                "[#f68d1f]Creating additional links...", total=len(links)
            )
            with create_link_progress:
                for link in links:
                    link.create()
                    create_link_progress.advance(create_link_task, advance=1)
            # Link.batch_create(links)
        if comments:
            create_comment_progress = create_progress_object()
            create_comment_task = create_comment_progress.add_task(
                "[#f68d1f]Creating additional comments...", total=len(comments)
            )
            with create_comment_progress:
                for comment in comments:
                    comment.create_or_update()
                    create_comment_progress.advance(create_comment_task, advance=1)
            # Comment.batch_create(comments)

    def _handle_updating_additional_data(
        self,
        data_dict: Dict,
        issue: Issue,
        data_list: List,
        links: List,
        comments: List,
    ) -> None:
        """
        Handle updating additional data
        :param Dict data_dict: Data dictionary
        :param Issue issue: Issue
        :param List data_list: Data list
        :param List links: Links
        :param List comments: Comments
        :rtype None: None
        """
        existing_data = Data.get_all_by_parent(parent_id=issue.id, parent_module="issues")
        existing_links = Link.get_all_by_parent(parent_id=issue.id, parent_module="issues")
        existing_comments = Comment.get_all_by_parent(parent_id=issue.id, parent_module="issues")
        filtered_data: List[Data] = list(
            filter(
                lambda d: d.dataSource == DATASOURCE,
                existing_data,
            )
        )
        filtered_links = list(
            filter(
                lambda elink: "Wiz Entity:" in elink.title,
                existing_links,
            )
        )
        for data in filtered_data:
            data.delete()
        for link in filtered_links:
            link.delete()
        for comment in existing_comments:
            comment.delete()
        self._handle_creating_additional_data(
            data_dict=data_dict,
            issue=issue,
            data_list=data_list,
            links=links,
            comments=comments,
        )

    @staticmethod
    def _handle_creating_additional_data(
        data_dict: Dict, issue: Issue, data_list: List, links: List, comments: List
    ) -> None:
        """
        Handle pulling additional data to list add appropriate id's from created issues
        :param Dict data_dict: Dict
        :param Issue issue: Issue
        :param List data_list: Data list
        :param List links: Links
        :param List comments: Comments
        :rtype: None
        """
        if data := data_dict.get("data"):
            data.parentId = issue.id
            data_list.append(data)
        if link := data_dict.get("link"):
            link.parentID = issue.id
            links.append(link)
        if comment_list := data_dict.get("comments"):
            comments.extend(comment_list)

    def fetch_wiz_data_if_needed(self) -> List[Dict]:
        """
        Fetch Wiz data if needed and save to file if not already fetched within the last 8 hours and return the data
        :return List[Dict]: The fetched data
        :rtype List[Dict]: List[Dict]
        """

        fetch_interval = timedelta(hours=1)  # Interval to fetch new data
        current_time = datetime.now()

        # Check if the file exists and its last modified time
        if os.path.exists(ISSUES_FILE_PATH):
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(ISSUES_FILE_PATH))
            if current_time - file_mod_time < fetch_interval:
                with open(ISSUES_FILE_PATH, "r") as file:
                    nodes = json.load(file)
                return nodes

        nodes = self.fetch_wiz_data(
            query=ISSUE_QUERY,
            variables=self.variables,
            api_endpoint_url=self.wiz_url,
            topic_key="issues",
        )
        with open(ISSUES_FILE_PATH, "w") as file:
            json.dump(nodes, file)

        return nodes

    @staticmethod
    def fetch_wiz_data(query: str, variables: Dict, api_endpoint_url: str, topic_key: str) -> List[Dict]:
        """
        Fetch Wiz data for the given query and variables
        :param str query: The query to fetch data
        :param Dict variables: The variables for the query
        :param str api_endpoint_url: The Wiz API endpoint URL
        :param str topic_key: The key for the topic in the response data
        :raises ValueError: If the Wiz access token is missing
        :return: The fetched data
        :rtype: List[Dict]
        """
        logger.debug("Sending a paginated request to Wiz API")
        app = Application()
        api_endpoint_url = app.config["wizUrl"] if api_endpoint_url is None else api_endpoint_url

        if token := app.config.get("wizAccessToken"):
            client = PaginatedGraphQLClient(
                endpoint=api_endpoint_url,
                query=query,
                headers={
                    "Content-Type": CONTENT_TYPE,
                    "Authorization": "Bearer " + token,
                },
            )

            # Fetch all results using the client's pagination logic
            data = client.fetch_all(variables=variables, topic_key=topic_key)

            return data
        raise ValueError("Your Wiz access token is missing.")

    @staticmethod
    def group_issues(wiz_issues: List[Dict]) -> Dict:
        """
        Group Wiz issues by data sourceRule.id
        :param List[Dict] wiz_issues: List of Wiz issues
        :return Dict: Dict with key of data sourceRule.id containing a list of Wiz issues
        :rtype Dict: Dict
        """
        issues = {}
        for wiz_issue in wiz_issues:
            source_id = get_value(wiz_issue, "sourceRule.id")
            if not issues.get(source_id):
                issues[source_id] = [wiz_issue]
            else:
                issues[source_id].append(wiz_issue)
        return issues

    def create_issues(self, wiz_issues: List[Dict]) -> None:
        """
        Map Wiz issues to RegScale issues
        :param List[Dict] wiz_issues: List of Wiz issues
        :rtype: None
        """
        app = Application()
        config = app.config
        user_id = config.get("userId")
        create_progress = create_progress_object()
        total_items = len(wiz_issues)
        create_job = create_progress.add_task("[#f68d1f]Mapping RegScale issues...", total=total_items)
        with create_progress:
            existing_issues = Issue.get_all_by_parent(parent_id=self.regscale_id, parent_module=self.regscale_module)
            existing_issues_dict = {i.wizId: i for i in existing_issues}
            logger.info(f"Found {len(existing_issues)} existing issues")
            issues_to_create = []
            issues_to_update = []
            for wiz_issue in wiz_issues:
                new_issue, existing_issue = self.create_issue(
                    issue=wiz_issue,
                    user_id=user_id,
                    parent_id=self.regscale_id,
                    parent_module=self.regscale_module,
                    identifier=f"<p>{get_value(wiz_issue, 'entitySnapshot.name')}</p>",
                    existing_issues_dict=existing_issues_dict,
                )
                if new_issue:
                    issues_to_create.append(new_issue)
                if existing_issue:
                    issues_to_update.append(existing_issue)

                create_progress.advance(create_job, advance=1)

    @staticmethod
    def dedupe(list_with_dups: List) -> List:
        """
        Deduplicate a list
        :param List list_with_dups: List with duplicates
        :return List: Deduplicated list
        :rtype List: List
        """
        return list(set(list_with_dups))

    def create_issue(
        self,
        issue: Dict,
        user_id: str,
        parent_id: int,
        parent_module: str,
        identifier: str,
        existing_issues_dict: Dict,
    ) -> Tuple[Optional[Issue], Optional[Issue]]:
        """
        Create a RegScale issue from a Wiz issue
        :param issue: Wiz issue dictionary
        :param user_id: User ID to assign the issue to
        :param parent_id the regscale model to which the issue is attached
        :param parent_module the regscale model to which the issue is attached
        :param identifier: Asset identifiers
        :param existing_issues_dict: Existing issues to update
        :return: RegScale Tuple new_issue, existing_issue
        :rtype: Tuple[Optional[Issue], Optional[Issue]]
        """
        due_date_str = self.process_issue_due_date(get_value(issue, "severity"))
        unknown_title = (
            f"unknown - {issue.get('id')} - type: {issue.get('type')} - entity_id: {issue.get('entitySnapshot.id')}"
        )

        existing_issue = existing_issues_dict.get(get_value(issue, "id"))
        new_issue = None
        if existing_issue:
            self._update_issue(
                existing_issue=existing_issue,
                issue=issue,
                user_id=user_id,
                parent_id=parent_id,
                parent_module=parent_module,
                identifier=identifier,
                unknown_title=unknown_title,
                due_date_str=due_date_str,
            )
        else:
            new_issue = self._create_issue(
                issue=issue,
                user_id=user_id,
                parent_id=parent_id,
                parent_module=parent_module,
                identifier=identifier,
                unknown_title=unknown_title,
                due_date_str=due_date_str,
            )
        return new_issue, existing_issue

    def _update_issue(self, **kwargs) -> None:
        """
        Update a RegScale issue from a Wiz issue
        :param existing_issue Issue: RegScale issue object
        :param issue: Wiz issue dictionary
        :param user_id: User ID to assign the issue to
        :param parent_id the regscale model to which the issue is attached
        :param parent_module the regscale model to which the issue is attached
        :param identifier: Asset identifiers
        :param unknown_title: Unknown title
        :rtype: None
        """
        issue = kwargs.get("issue")
        wiz_id = get_value(issue, "id")
        existing_issue: Issue = kwargs.get("existing_issue")
        user_id = kwargs.get("user_id")
        identifier = kwargs.get("identifier")
        unknown_title = kwargs.get("unknown_title")
        due_date_str = self.process_issue_due_date(get_value(issue, "severity"))
        existing_issue.title = get_value(issue, "sourceRule.name") or unknown_title
        existing_issue.description = get_value(issue, "sourceRule.cloudConfigurationRuleDescription")
        existing_issue.dateLastUpdated = get_value(issue, "updatedAt")
        existing_issue.status = self.map_status(get_value(issue, "status"))
        existing_issue.severityLevel = self.map_severity_level(issue)
        existing_issue.recommendedActions = get_value(issue, "sourceRule.remediationInstructions")
        existing_issue.dueDate = due_date_str
        existing_issue.dateCompleted = get_value(issue, "resolvedAt")
        existing_issue.lastUpdatedById = user_id
        existing_issue.assetIdentifier = identifier
        self.issues_to_update.append(existing_issue)
        self.additional_data_updated[wiz_id] = self.prepare_additional_data(
            issue=issue,
            user_id=user_id,
        )

    @staticmethod
    def prepare_additional_data(issue: Dict, user_id: str) -> Dict:
        """
        Prepare additional data for a Wiz issue before creating or updating the RegScale issue.

        :param Dict issue: The Wiz issue dictionary.
        :param str user_id: The user ID to associate with the created data.
        :return Dict: A dictionary containing prepared additional data.
        :rtype Dict: Dict
        """
        additional_data = {
            "data": None,
            "link": None,
            "comments": [],
        }

        # Prepare comments based on Wiz issue notes.
        wiz_notes = get_value(issue, "notes")
        comments = [
            Comment(
                parentID=0,  # Temporarily set to 0; will be updated after issue creation.
                parentModule="issues",
                comment=f"{note.get('email')}: {note.get('text')}",
                commentDate=note.get("createdAt"),
                createdById=user_id,
                lastUpdatedById=user_id,
            )
            for note in wiz_notes or []
        ]

        # Prepare data object.
        data = Data(
            parentId=0,  # Temporarily set to 0; will be updated after issue creation.
            parentModule="issues",
            dataSource=DATASOURCE,
            dataType=DataDataType.JSON.value,
            rawData=json.dumps(issue),
            createdById=user_id,
            lastUpdatedById=user_id,
        )

        # Prepare link if available.
        link = None
        if url := get_value(issue, "entitySnapshot.cloudProviderURL"):
            link = Link(
                parentID=0,  # Temporarily set to 0; will be updated after issue creation.
                parentModule="issues",
                url=url,
                title=f"Wiz Entity: {get_value(issue, 'entitySnapshot.name')}",
                createdById=user_id,
                lastUpdatedById=user_id,
            )

        additional_data["data"] = data
        additional_data["link"] = link
        additional_data["comments"] = comments

        return additional_data

    def _create_issue(self, **kwargs) -> Issue:
        """
        Create a RegScale issue from a Wiz issue
        :param issue: Wiz issue dictionary
        :param user_id: User ID to assign the issue to
        :param parent_id the regscale model to which the issue is attached
        :param parent_module the regscale model to which the issue is attached
        :param identifier: Asset identifiers
        :param unknown_title: Unknown title
        :param due_date_str: Due date string
        """
        issue = kwargs.get("issue")
        wiz_id = get_value(issue, "id")
        user_id = kwargs.get("user_id")
        parent_id = kwargs.get("parent_id")
        parent_module = kwargs.get("parent_module")
        identifier = kwargs.get("identifier")
        unknown_title = kwargs.get("unknown_title")
        due_date_str = kwargs.get("due_date_str")
        additional_data = self.prepare_additional_data(
            issue=issue,
            user_id=user_id,
        )
        new_issue = Issue(
            title=get_value(issue, "sourceRule.name") or unknown_title,
            description=get_value(issue, "sourceRule.cloudConfigurationRuleDescription"),
            dateCreated=get_value(issue, "createdAt"),
            dateLastUpdated=get_value(issue, "updatedAt"),
            status=self.map_status(get_value(issue, "status")),
            severityLevel=self.map_severity_level(issue),
            recommendedActions=get_value(issue, "sourceRule.remediationInstructions"),
            assetIdentifier=identifier,
            dueDate=due_date_str,
            issueOwnerId=user_id,
            createdById=user_id,
            lastUpdatedById=user_id,
            parentId=parent_id,
            parentModule=parent_module,
            dateCompleted=get_value(issue, "resolvedAt"),
            identification="Assessment/Audit (Internal)",
            sourceReport="Wiz",
            wizId=get_value(issue, "id"),
            otherIdentifier=get_value(issue, "entitySnapshot.externalId"),
        )
        self.issue_to_create.append(new_issue)
        self.additional_data[wiz_id] = additional_data
        return new_issue

    @staticmethod
    def map_status(status: str) -> str:
        """
        Map Wiz status to RegScale status
        :param str status: Wiz status
        :return str: RegScale status
        :rtype str: str
        """
        wiz_status = status
        if wiz_status == "OPEN":
            return IssueStatus.Open.value
        if wiz_status == "RESOLVED":
            return IssueStatus.Closed.value
        if wiz_status == "IN_PROGRESS":
            return IssueStatus.Open.value
        if wiz_status == "REJECTED":
            return IssueStatus.Cancelled.value
        return IssueStatus.Open.value

    @staticmethod
    def process_issue_due_date(
        severity_level: str,
    ) -> str:
        """
        Process issue due date
        :param str severity_level: Severity level
        :return: due date str
        :rtype: str
        """
        app = Application()
        config = app.config
        fmt = "%Y-%m-%d %H:%M:%S"

        # Default days setting for unspecified severity levels
        default_days = config.get("issues", {}).get("wiz", {}).get("default", 0)
        days = config.get("issues", {}).get("wiz", {}).get(severity_level.lower(), default_days)

        try:
            days = int(days)
        except ValueError:
            # Handle non-integer 'days' gracefully
            days = default_days

        due_date = datetime.now() + timedelta(days=days)
        return due_date.strftime(fmt)

    @staticmethod
    def map_severity_level(wiz_issue: Dict) -> str:
        """
        Map Wiz severity level to RegScale severity level
        :param Dict wiz_issue: Wiz issue dictionary containing the severity level
        :return str: RegScale severity level
        :rtype str: str
        """
        severity = get_value(wiz_issue, "severity")
        if not severity:
            return IssueSeverity.NotAssigned.value
        if isinstance(severity, str):
            return SEVERITY_MAP.get(severity, "Low")
        return IssueSeverity.NotAssigned.value

    @staticmethod
    def build_link(data: Dict) -> Optional[Link]:
        """
        Build a link to the Wiz issue
        :param Dict data: The Wiz issue data
        :return Optional[Link]: The link to the Wiz issue or None if the link is not found
        :rtype Optional[Link]: Optional[Link]
        """
        url = get_value(data, "entitySnapshot.cloudProviderURL")
        if not url and not isinstance(url, str):
            return None
        return Link(url=url, title=f"Wiz Entity: {get_value(data, 'entitySnapshot.name')}")
