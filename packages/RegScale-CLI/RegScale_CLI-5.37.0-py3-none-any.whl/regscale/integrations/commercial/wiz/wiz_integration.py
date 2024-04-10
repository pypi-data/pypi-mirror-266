"""
Wiz Integration class
"""

import datetime
import json
import logging
from os import environ
from typing import List

from regscale.core.app.utils.app_utils import check_license
from regscale.integrations import Integration
from regscale.integrations.commercial.wiz.inventory import WizInventory
from regscale.integrations.commercial.wiz.issue import WizIssue
from regscale.integrations.commercial.wiz.wiz_auth import wiz_authenticate

logger = logging.getLogger(__name__)


class WizIntegration(Integration):
    """
    Wiz Integration class
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.last_inventory_pull = (
            self.config.get("wizLastInventoryPull")
            if self.config.get("wizLastInventoryPull") != "<wizLastInventoryPull>"
            else None
        )
        self.filter_by_override = (
            self.config.get("wizIssueFilterBy") if self.config.get("wizIssueFilterBy") != "<wizIssueFilterBy>" else None
        )
        self.wiz_url = self.config.get("wizUrl")
        self.is_authenticated = False

    def authenticate(
        self,
        client_id: str = environ.get("WizClientId"),
        client_secret: str = environ.get("WizClientId"),
    ) -> bool:
        """
        Authenticate to Wiz using the client id and client secret
        """
        if not self.is_authenticated:
            self.is_authenticated = wiz_authenticate(client_id, client_secret)
        return self.is_authenticated

    def inventory(
        self,
        wiz_project_ids: List[str],
        regscale_id: int,
        regscale_module: str,
        filter_by_override: str,
        client_id: str,
        client_secret: str,
        full_inventory: bool,
    ):
        """
        Pull inventory from Wiz for the given project ids
        """
        check_license()
        self.authenticate(client_id, client_secret)
        wiz_projects = wiz_project_ids
        if filter_by_override:
            filter_by = json.loads(filter_by_override)
        else:
            filter_by = {
                "projectId": wiz_projects,
            }
            if self.last_inventory_pull and not full_inventory:
                filter_by["updatedAt"] = {"after": self.last_inventory_pull}

        inventory = WizInventory(
            filter_by=filter_by,
            regscale_id=regscale_id,
            regscale_module=regscale_module,
            wiz_projects=wiz_projects,
            wiz_url=self.wiz_url,
            full_inventory=full_inventory,
        )
        inventory.pull()
        self.last_inventory_pull = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.config["wizLastInventoryPull"] = self.last_inventory_pull
        self.save_config(self.config)

    def issues(
        self,
        wiz_project_id: str,
        regscale_id: int,
        regscale_module: str,
        filter_by_override: str,
        client_id: str,
        client_secret: str,
    ):
        check_license()
        self.authenticate(client_id, client_secret)

        if self.filter_by_override:
            filter_by = json.loads(filter_by_override)
        else:
            filter_by = {
                "project": wiz_project_id,
            }

        wiz_issue_integration = WizIssue(
            filter_by=filter_by,
            regscale_id=regscale_id,
            regscale_module=regscale_module,
            wiz_projects=wiz_project_id,
            wiz_url=self.wiz_url,
        )
        wiz_issue_integration.pull()

    def sbom(
        self,
        wiz_project_id: str,
        regscale_id: int,
        regscale_module: str,
        filter_by_override: str,
        client_id: str,
        client_secret: str,
    ):
        # SBOM coming coon
        pass
