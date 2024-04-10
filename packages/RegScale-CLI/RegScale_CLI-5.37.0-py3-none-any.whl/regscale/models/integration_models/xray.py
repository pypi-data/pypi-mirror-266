"""
Nexpose Scan information
"""

from pathlib import Path
from typing import List, Optional

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import epoch_to_datetime, get_current_datetime
from regscale.models.integration_models.container_scan import ContainerScan
from regscale.models.regscale_models.asset import Asset
from regscale.models.regscale_models.issue import Issue
from regscale.models.regscale_models.vulnerability import Vulnerability


class XRay(ContainerScan):
    """JFrog Xray Scan information

    :param str name: Name of the scan
    :param Application app: RegScale Application object
    :param str file_path: Path to the JSON files
    :param int regscale_ssp_id: RegScale System Security Plan ID
    """

    def __init__(self, name: str, app: Application, file_path: str, regscale_ssp_id: int):
        self.name = name
        self.cvss3_score = "cvss_v3_score"
        self.vuln_title = "cve"
        logger = create_logger()
        super().__init__(
            logger=logger,
            app=app,
            file_path=Path(file_path),
            name=self.name,
            headers=None,
            parent_id=regscale_ssp_id,
            parent_module="securityplans",
            asset_func=self.create_asset,
            vuln_func=self.create_vuln,
            issue_func=self.create_issue,
            file_type=".json",
        )

    def create_issue(self, dat: dict = None) -> List[Issue]:
        """
        Create an issue from a row in the JFrog Xray JSON file

        :param dict dat: Data row from JSON file
        :return: A list of RegScale Issue object
        :rtype: List[Issue]
        """
        issues = []
        severity = (
            Vulnerability.determine_cvss3_severity_text(float(dat[self.cvss3_score]))
            if dat.get(self.cvss3_score)
            else "low"
        )
        kev_due_date = None
        for cve in dat.get("cves", []):
            if self.attributes.app.config.get("issues", {}).get(self.name.lower(), {}).get("useKev", False):
                kev_due_date = self.lookup_kev(cve[self.vuln_title])
            iss = Issue(
                isPoam=severity in ["low", "moderate", "high", "critical"],
                title=cve[self.vuln_title],
                description=dat.get("summary", "No description available."),
                status="Open",
                severityLevel=Issue.assign_severity(severity),
                issueOwnerId=self.attributes.app.config["userId"],
                pluginId=dat["issue_id"][5:] if dat.get("issue_id") else None,
                assetIdentifier=dat.get("impacted_artifact"),
                securityPlanId=(
                    self.attributes.parent_id if self.attributes.parent_module == "securityplans" else None
                ),
                recommendedActions=(
                    f"Upgrade to a fixed version: {', '.join(dat['fixed_versions'])}"
                    if dat.get("fixed_versions")
                    else "No solution available"
                ),
                cve=cve.get(self.vuln_title),
                autoApproved="No",
                parentId=self.attributes.parent_id,
                parentModule=self.attributes.parent_module,
                # Set issue due date to the kev date if it is in the kev list
            )
            iss.originalRiskRating = iss.assign_risk_rating(severity)
            # Date not provided, we must use the creation date of the file
            iss.dateFirstDetected = epoch_to_datetime(self.create_epoch)
            iss.basisForAdjustment = f"{self.name} import"
            iss = self.update_due_dt(iss=iss, kev_due_date=kev_due_date, scanner="xray", severity=severity)
            issues.append(iss)

        return issues

    def create_asset(self, dat: Optional[dict] = None) -> Optional[Asset]:
        """
        Create an asset from a row in the Xray JSON file

        :param Optional[dict] dat: Data row from JSON file, defaults to None
        :return: RegScale Asset object
        :rtype: Optional[Asset]
        """

        if asset_name := dat.get("impacted_artifact") if isinstance(dat, dict) else dat:
            return Asset(
                **{
                    "id": 0,
                    "name": asset_name,
                    "ipAddress": "0.0.0.0",
                    "isPublic": True,
                    "status": "Active (On Network)",
                    "assetCategory": "Software",
                    "bLatestScan": True,
                    "bAuthenticatedScan": True,
                    "scanningTool": self.name,
                    "assetOwnerId": self.config["userId"],
                    "assetType": "Other",
                    "fqdn": None,
                    "operatingSystem": "Linux",
                    "systemAdministratorId": self.config["userId"],
                    "parentId": self.attributes.parent_id,
                    "parentModule": self.attributes.parent_module,
                }
            )
        return None

    def create_vuln(self, dat: Optional[dict] = None) -> List[Vulnerability]:
        """
        Create a vulnerability from a row in the JFrog Xray JSON file

        :param Optional[dict] dat: Data row from JSON file, defaults to None
        :return: List of RegScale Vulnerability object, if any
        :rtype: List[Vulnerability]
        """
        asset_match = [asset for asset in self.data["assets"] if asset.name == dat.get("impacted_artifact")]
        asset = asset_match[0] if asset_match else None
        vulns = []
        for vuln in dat.get("cves", []):
            # CVE IS A VULN, A VULN IS A CVE, Finkle is Einhorn
            regscale_vuln = None
            severity = (
                Vulnerability.determine_cvss3_severity_text(float(vuln[self.cvss3_score]))
                if vuln.get(self.cvss3_score)
                else "low"
            )
            if asset_match:
                cves = [c["cve"] for c in dat["cves"] if c.get("cve")]
                regscale_vuln = Vulnerability(
                    id=0,
                    scanId=0,  # set later
                    parentId=asset.id,
                    parentModule="assets",
                    ipAddress="0.0.0.0",  # No ip address available
                    lastSeen=get_current_datetime(),
                    firstSeen=epoch_to_datetime(self.create_epoch),
                    daysOpen=None,
                    dns=dat.get("impacted_artifact"),
                    mitigated=None,
                    operatingSystem="Linux",
                    severity=severity,
                    plugInName=dat.get("issue_id", "XRay"),
                    plugInId=int(dat.get("issue_id", "Xray-0000")[5:]),
                    cve=",".join(cves) if cves else None,
                    vprScore=None,
                    tenantsId=0,  # Need a way to figure this out programmatically
                    title=f"{dat.get('issue_id', 'Xray Vuln')} on asset {asset.name}",
                    description=dat.get("summary"),
                    plugInText=vuln.get("cve"),
                    extra_data={
                        "references": dat.get("references", "None"),
                        "solution": dat.get("fixed_versions", "None"),
                    },
                )
            vulns.append(regscale_vuln)
        return vulns
