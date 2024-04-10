"""
Wiz Inventory Integration class
"""

import dataclasses
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Optional, List, Union, Dict, Any, Tuple

from regscale.core.app.application import Application
from regscale.core.app.logz import create_logger
from regscale.core.app.utils.app_utils import (
    flatten_dict,
    create_progress_object,
)
from regscale.core.app.utils.regscale_utils import (
    verify_provided_module,
)
from regscale.integrations.commercial.cpe import (
    extract_product_name_and_version,
    extract_search_term_from_22_cpe,
    get_cpe_titles,
    get_cpe_title_by_version,
)
from regscale.integrations.integration import Inventory
from regscale.models.integration_models.wiz import (
    AssetCategory,
)
from regscale.models.regscale_models import (
    Asset,
    Property,
    PortsProtocol,
    Component,
    ComponentMapping,
    Metadata,
    AssetMapping,
    Data,
    DataDataType,
    Link,
)
from regscale.utils.graphql_client import PaginatedGraphQLClient
from .constants import (
    CONTENT_TYPE,
    INVENTORY_QUERY,
    DATASOURCE,
    INVENTORY_FILE_PATH,
)

job_progress = create_progress_object()
logger = create_logger()
FULL_INVENTORY = False


@dataclasses.dataclass
class ProcessDataParams:
    """
    Process Data Params
    """

    data: List[Dict]
    existing_asset_dict: Dict[str, Asset]
    wiz_assets_to_create: List[Asset]
    wiz_assets_to_update: List[Asset]
    wiz_prop_map: Dict[str, List[Property]]
    parent_id: int
    parent_module: str
    map_progress: Any
    map_job: Any
    ports_to_create: Dict[str, PortsProtocol]
    components_to_create: List[str]
    links_to_create_for_assets: Dict[str, Link]
    data_objects: Dict


class WizInventory(Inventory):
    """
    Wiz Inventory class
    """

    def __init__(
        self,
        filter_by,
        regscale_id: int,
        regscale_module: str,
        wiz_url: str,
        first: int = 100,
        wiz_projects=None,
        full_inventory: bool = False,
        **kwargs,
    ):
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
        super().__init__(**kwargs)
        app = Application()
        self.config = app.config
        self.full_inventory = full_inventory

    def pull(self) -> None:
        """
        Pull inventory from Wiz and load into RegScale
        :rtype: None
        """
        verify_provided_module(self.regscale_module)
        nodes = self.fetch_wiz_data_if_needed()
        if nodes:
            logger.info(f"Found {len(nodes)} inventory items from Wiz API to sync...")
            self.create_wiz_assets(data=nodes)
        else:
            logger.info("No inventory items found from Wiz API to sync...")

    def fetch_wiz_data_if_needed(self) -> List[Dict]:
        """
        Fetch Wiz data if needed and save to file if not already fetched within the last 8 hours and return the data
        """

        fetch_interval = timedelta(hours=self.config.get("wizFullPullLimitHours", 8))  # Interval to fetch new data
        current_time = datetime.now()

        # Check if the file exists and its last modified time
        if os.path.exists(INVENTORY_FILE_PATH):
            file_mod_time = datetime.fromtimestamp(os.path.getmtime(INVENTORY_FILE_PATH))
            if current_time - file_mod_time < fetch_interval:
                with open(INVENTORY_FILE_PATH, "r", encoding="utf-8") as file:
                    nodes = json.load(file)
                return nodes

        nodes = fetch_wiz_data(
            query=INVENTORY_QUERY,
            variables=self.variables,
            api_endpoint_url=self.wiz_url,
            topic_key="cloudResources",
        )
        with open(INVENTORY_FILE_PATH, "w", encoding="utf-8") as file:
            json.dump(nodes, file)

        return nodes

    def create_wiz_assets(
        self,
        data: List[Dict[str, Any]],
    ) -> Tuple[List[Asset], List[Asset]]:
        """
        Create Wiz Assets from the provided data, updating existing assets and creating new ones as necessary.

        :param List[Dict[str, Any]] data: Wiz data to process.
        :return: A tuple containing lists of created and updated Wiz assets.
        :rtype: Tuple[List[Asset], List[Asset]]
        """
        parent_id = self.regscale_id
        parent_module = self.regscale_module
        wiz_projects = self.wiz_projects
        map_progress = create_progress_object()
        app = Application()
        wiz_assets_to_create = []
        wiz_assets_to_update = []
        existing_assets = Asset.get_all_by_parent(parent_id, parent_module)
        log_existing_assets_info(existing_assets)
        existing_asset_dict = {asset.wizId: asset for asset in existing_assets}
        wiz_prop_map = {}
        components_to_create = []
        ports_to_create = {}
        links_to_create_for_assets = {}
        data_objects = {}
        map_job = map_progress.add_task("[#f68d1f]Mapping Wiz inventory data to RegScale...", total=len(data))
        existing_components = Component.get_all_by_parent(parent_id, parent_module)
        logger.info(f"Found {len(existing_components)} existing components..")
        components_to_create = collect_components_to_create(data, components_to_create)
        params = ProcessDataParams(
            data=data,
            existing_asset_dict=existing_asset_dict,
            wiz_assets_to_create=wiz_assets_to_create,
            wiz_assets_to_update=wiz_assets_to_update,
            wiz_prop_map=wiz_prop_map,
            parent_id=parent_id,
            parent_module=parent_module,
            map_progress=map_progress,
            map_job=map_job,
            ports_to_create=ports_to_create,
            components_to_create=components_to_create,
            links_to_create_for_assets=links_to_create_for_assets,
            data_objects=data_objects,
        )
        threaded_process_rows(params)
        components = create_missing_components(
            components_to_create,
            parent_id,
            app.config.get("userId"),
            wiz_projects,
            existing_components,
        )

        logger.info(f"Created {len(components)} components")
        created_assets, updated_assets = finalize_assets(wiz_assets_to_create, wiz_assets_to_update)
        all_assets = []
        all_assets.extend(updated_assets)
        all_assets.extend(created_assets)
        save_ports(ports_to_create=ports_to_create, assets=all_assets)
        create_asset_component_mappings(created_assets=created_assets, components=components)
        update_asset_component_mappings(assets=updated_assets, components=existing_components)
        if self.full_inventory:
            handle_removed_assets(existing_assets, all_assets)
        create_links_for_assets(links_to_create_for_assets, assets=all_assets)
        create_data_objects(data_objects, assets=all_assets)
        log_final_asset_counts(wiz_assets_to_create, wiz_assets_to_update)
        return created_assets, updated_assets


def map_category(asset_string: str) -> str:
    """
    category mapper

    :param str asset_string:
    :return: Category
    :rtype: str
    """
    try:
        return getattr(AssetCategory, asset_string).value
    except (KeyError, AttributeError) as ex:
        # why map AssetCategory of everything is software?
        logger.debug("Unable to find %s in AssetType enum \n", ex)
        return "Software"


def pull_resource_info_from_props(wiz_entity_properties: Dict) -> Tuple[int, int]:
    """
    Pull memory, cpu from properties
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: Memory, CPU
    :rtype: Tuple[int, int]
    """
    resources = get_resources(wiz_entity_properties)
    memory = parse_memory(resources.get("memory", ""))
    cpu = parse_cpu(resources.get("cpu", 0))
    cpu = parse_cpu(wiz_entity_properties.get("vCPUs", cpu))
    return memory, cpu


def get_resources(wiz_entity_properties: Dict) -> Dict:
    """
    Extract resources from Wiz entity properties
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: Resources dictionary
    :rtype: Dict
    """
    if "resources" in wiz_entity_properties:
        resources_str = wiz_entity_properties.get("resources", "{}")
        try:
            resources = json.loads(resources_str)
            return resources.get("requests", {})
        except json.JSONDecodeError:
            pass
    return {}


def parse_memory(memory_str: str) -> int:
    """
    Parse memory string to integer (GiB to MiB conversion if needed)
    :param str memory_str: Memory string
    :return: Memory in MiB
    :rtype: int
    """
    if memory_str.endswith("Mi"):
        return int(memory_str.replace("Mi", "")) // 1024
    elif memory_str.endswith("Gi"):
        return int(memory_str.replace("Gi", ""))
    return 0


def parse_cpu(cpu_str: Union[str, int]) -> int:
    """
    Parse CPU string to integer
    :param Union[str, int] cpu_str: CPU string
    :return: CPU as integer
    :rtype: int
    """
    try:
        return int(float(cpu_str))
    except ValueError:
        return 0


@lru_cache(maxsize=None, typed=True)
def fetch_cpe_name(wiz_cpe: str) -> Optional[str]:
    """
    Fetch CPE name
    :param str wiz_cpe: Wiz CPE
    :return: CPE name
    :rtype: Optional[str]
    """
    search_term, version = extract_search_term_from_22_cpe(cpe_string=wiz_cpe)
    logger.debug(f"{search_term}")
    logger.debug(version)
    cpe_names_list = get_cpe_titles(search_term)
    logger.debug(f"Nist CPE's found: {len(cpe_names_list)}")
    cpe_name = get_cpe_title_by_version(cpe_names_list, version, take_first=True)
    logger.debug(f"Found CPE Title: {cpe_name}" if cpe_name else "CPE Title not found")
    return cpe_name


def get_software_name_from_cpe(wiz_entity_properties: Dict, name: str) -> Dict:
    """
    Get software name from wiz CPE
    :param Dict wiz_entity_properties: Wiz entity properties
    :param str name: Name
    :return: Software name
    :rtype: Dict
    """
    cpe_info_dict = {
        "name": name,
        "software_name": None,
        "software_version": None,
        "software_vendor": None,
    }
    if "cpe" in wiz_entity_properties.keys() and wiz_entity_properties.get("cpe"):
        cpe_info_dict = extract_product_name_and_version(wiz_entity_properties.get("cpe", ""))
        cpe_info_dict["name"] = name
    return cpe_info_dict


def get_ip_address(
    wiz_entity_properties: Dict,
) -> Tuple[Union[str, None], Union[str, None], Union[str, None], Union[str, None]]:
    """
    Get ip address from wiz entity properties
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: IP4 address, IP6 address, DNS, URL
    :rtype: Tuple[Union[str, None], Union[str, None], Union[str, None], Union[str, None]]
    """
    ip4_address = None
    ip6_address = None
    dns = None
    url = None
    if "address" in wiz_entity_properties.keys():
        if wiz_entity_properties.get("addressType") == "IPV4":
            ip4_address = wiz_entity_properties.get("address")
        elif wiz_entity_properties.get("addressType") == "IPV6":
            ip6_address = wiz_entity_properties.get("address")
        elif wiz_entity_properties.get("addressType") == "DNS":
            dns = wiz_entity_properties.get("address")
        elif wiz_entity_properties.get("addressType") == "URL":
            url = wiz_entity_properties.get("address")

    return ip4_address, ip6_address, dns, url


def get_notes_from_wiz_props(wiz_entity_properties: Dict, external_id: str) -> str:
    """
    Get notes from wiz properties
    :param Dict wiz_entity_properties: Wiz entity properties
    :param str external_id: External ID
    :return: Notes
    :rtype: str
    """
    notes = []
    notes.append(f"External ID: {external_id}") if external_id else None
    (
        notes.append(f"Cloud Platform: {wiz_entity_properties.get('cloudPlatform')}")
        if wiz_entity_properties.get("cloudPlatform")
        else None
    )
    (
        notes.append(f"Provider Unique ID: {wiz_entity_properties.get('providerUniqueId')}")
        if wiz_entity_properties.get("providerUniqueId")
        else None
    )
    (
        notes.append(
            f"""cloudProviderURL:<a href="{wiz_entity_properties.get("cloudProviderURL")}"
                            target="_blank">{wiz_entity_properties.get("cloudProviderURL")}</a>"""
        )
        if wiz_entity_properties.get("cloudProviderURL")
        else None
    )
    (
        notes.append(f"Vertex ID: {wiz_entity_properties.get('_vertexID')}")
        if wiz_entity_properties.get("_vertexID")
        else None
    )
    (
        notes.append(f"Severity Name: {wiz_entity_properties.get('severity_name')}")
        if wiz_entity_properties.get("severity_name")
        else None
    )
    (
        notes.append(f"Severity Description: {wiz_entity_properties.get('severity_description')}")
        if wiz_entity_properties.get("severity_description")
        else None
    )
    return "<br>".join(notes)


def map_wiz_status(wiz_status: Union[str, None]) -> str:
    """
    Map Wiz status to RegScale status if unknown they are active
    :param Union[str, None] wiz_status: Wiz status
    :return: RegScale status
    :rtype: str
    """
    status = "Active (On Network)"
    if wiz_status and wiz_status == "Inactive":
        return "Off-Network"
    return status


def create_asset_type(asset_type: str) -> str:
    """
    Create asset type if it does not exist and reformat the string to Title Case ie
        ( "ASSET_TYPE" or "asset_type" -> "Asset Type")
    :param str asset_type: Asset type
    :return: Asset type
    :rtype: str
    """
    #
    asset_type = asset_type.title().replace("_", " ")
    meta_data_list = Metadata.get_metadata_by_module_field(module="assets", field="Asset Type")
    if not any(meta_data.value == asset_type for meta_data in meta_data_list):
        Metadata(
            field="Asset Type",
            module="assets",
            value=asset_type,
        ).create()
    return asset_type


def create_or_get_component(
    parent_id: int,
    component_title: str,
    user_id: str,
    wiz_projects: List[str],
    existing_components: List[Component],
) -> Component:
    """
    Create or get component
    :param int parent_id: Parent ID
    :param str component_title: Component
    :param str user_id: User ID
    :param List[str] wiz_projects: Wiz project ID
    :param List[Component] existing_components: Existing components
    :return: Component or None
    :rtype: Component
    """
    mappable_component_name = component_title.upper().replace(" ", "_")
    existing_component_dict = {c.title: c for c in existing_components}
    component = existing_component_dict.get(component_title)
    if component:
        return component
    component = Component(
        title=component_title,
        description=component_title,
        securityPlansId=parent_id,
        componentOwnerId=user_id,
        componentType=map_category(mappable_component_name),
        status="Active",
        defaultAssessmentDays=365,
        createdById=user_id,
        lastUpdatedById=user_id,
        externalId=", ".join(wiz_projects) if wiz_projects else None,
    ).create()
    ComponentMapping(
        securityPlanId=parent_id,
        componentId=component.id,
        createdById=user_id,
        lastUpdatedById=user_id,
    ).create()
    return component


def map_asset(
    row: Dict,
    asset_type: str,
    wiz_entity_properties: Dict,
    existing_asset: Asset,
    parent_id: int,
    parent_module: str,
    external_id: str,
    wiz_id: str,
) -> Asset:
    """
    Create an asset from Wiz data
    :param Dict row: Row
    :param str asset_type: Asset type
    :param Dict wiz_entity_properties: Wiz entity properties
    :param Asset existing_asset: Existing asset
    :param int parent_id: Parent ID
    :param str parent_module: Parent module
    :param str external_id: External ID
    :param str wiz_id: Wiz ID
    :return: Asset
    :rtype: Asset
    """
    app = Application()
    user_id = app.config.get("userId")
    software_name_dict = handle_cpe_name(wiz_entity_properties, row)
    network_dict = get_network_info(wiz_entity_properties)
    memory, cpu = pull_resource_info_from_props(wiz_entity_properties)
    status = map_wiz_status(wiz_entity_properties.get("status"))
    handle_provider_dict = handle_provider(wiz_entity_properties)
    notes = get_notes_from_wiz_props(wiz_entity_properties, external_id)
    disk_storage = get_disk_storage(wiz_entity_properties)
    asset_category = map_category(row.get("type"))
    name = software_name_dict.get("name", row.get("name"))
    r_asset = Asset(
        name=name,
        otherTrackingNumber=external_id,
        wizId=wiz_id,
        assetTagNumber=external_id,
        wizInfo=None,
        parentId=parent_id,
        parentModule=parent_module,
        ipAddress=network_dict.get("ip4_address") or network_dict.get("ip6_address"),
        uri=network_dict.get("url"),
        model=wiz_entity_properties.get("nativeType"),
        macAddress=wiz_entity_properties.get("macAddress"),
        operatingSystem=wiz_entity_properties.get("operatingSystem"),
        awsIdentifier=handle_provider_dict.get("awsIdentifier"),
        azureIdentifier=handle_provider_dict.get("azureIdentifier"),
        googleIdentifier=handle_provider_dict.get("googleIdentifier"),
        otherCloudIdentifier=handle_provider_dict.get("otherCloudIdentifier"),
        diskStorage=disk_storage or 0,
        cpu=cpu or 0,
        ram=memory or 0,
        osVersion=handle_os_version(wiz_entity_properties, asset_category),
        endOfLifeDate=wiz_entity_properties.get("versionEndOfLifeDate"),
        assetOwnerId=user_id,
        vlanId=wiz_entity_properties.get("zone"),
        status=status,
        assetCategory=asset_category,
        assetType=asset_type,
        serialNumber=get_product_ids(wiz_entity_properties),
        softwareVendor=software_name_dict.get("software_vendor"),
        softwareVersion=handle_software_version(wiz_entity_properties, asset_category),
        softwareName=software_name_dict.get("software_name"),
        patchLevel=get_latest_version(wiz_entity_properties),
        managementType=handle_management_type(wiz_entity_properties),
        softwareAcronym=wiz_entity_properties.get("techName"),
        location=network_dict.get("region"),
        bPublicFacing=wiz_entity_properties.get("directlyInternetFacing", False),
        notes=notes,
        cpe=wiz_entity_properties.get("cpe"),
    )
    if existing_asset:
        r_asset.id = existing_asset.id
    return r_asset


def handle_cpe_name(wiz_entity_properties: Dict, row: Dict) -> Dict:
    """
    Handle CPE name
    :param Dict wiz_entity_properties: Wiz entity properties
    :param Dict row: Row
    :return: CPE name
    :rtype: Dict
    """
    if "cpe" in wiz_entity_properties:
        cpe_title = fetch_cpe_name(wiz_entity_properties.get("cpe"))
        software_name_dict = get_software_name_from_cpe(wiz_entity_properties, row.get("name"))
        software_name_dict["name"] = cpe_title if cpe_title else row.get("name")
        software_name_dict["software_name"] = cpe_title if cpe_title else row.get("name")
    else:
        software_name_dict = get_software_name_from_cpe(wiz_entity_properties, row.get("name"))
    return software_name_dict


def handle_management_type(wiz_entity_properties: Dict) -> str:
    """
    Handle management type
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: Management type
    :rtype: str
    """
    return "External/Third Party Managed" if wiz_entity_properties.get("isManaged") else "Internally Managed"


def handle_software_version(wiz_entity_properties: Dict, asset_category: str) -> Optional[str]:
    """
    Handle software version

    :param Dict wiz_entity_properties: Wiz entity properties
    :param str asset_category: Asset category
    :return: Software version
    :rtype: Optional[str]
    """
    return (
        wiz_entity_properties.get("version")
        if wiz_entity_properties.get("version") and asset_category == "Software"
        else None
    )


def handle_os_version(wiz_entity_properties: Dict, asset_category: str) -> Optional[str]:
    """
    Handle OS version
    :param Dict wiz_entity_properties: Wiz entity properties
    :param str asset_category: Asset category
    :return: OS version
    :rtype: Optional[str]
    """
    return (
        wiz_entity_properties.get("version")
        if wiz_entity_properties.get("operatingSystem") or asset_category == "Hardware"
        else None
    )


def handle_provider(wiz_entity_properties: Dict) -> Dict:
    """
    Handle provider
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: Provider
    :rtype: Dict
    """
    provider, identifier = get_cloud_identifier(wiz_entity_properties)
    return {
        "awsIdentifier": identifier if provider == "aws" else None,
        "azureIdentifier": identifier if provider == "azure" else None,
        "googleIdentifier": identifier if provider == "google" else None,
        "otherCloudIdentifier": identifier if provider == "other" else None,
    }


def get_asset_names(wiz_entity_properties: Dict, row: Dict) -> Dict:
    """
    Extract asset names and versions.
    :param Dict wiz_entity_properties: Wiz entity properties
    :param Dict row: Row
    :return: Asset names and versions
    :rtype: Dict
    """
    name = row.get("name")
    software_name_dict = {
        "name": name,
        "software_name": None,
        "software_version": None,
        "software_vendor": None,
    }
    if "cpe" in wiz_entity_properties:
        software_name_dict = get_software_name_from_cpe(wiz_entity_properties, name)
    return software_name_dict


def get_network_info(wiz_entity_properties: Dict) -> Dict:
    """
    Extract network information.
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: Network information
    :rtype: Dict
    """
    region = wiz_entity_properties.get("region")
    ip4_address, ip6_address, dns, url = get_ip_address(wiz_entity_properties)
    return {
        "region": region,
        "ip4_address": ip4_address,
        "ip6_address": ip6_address,
        "dns": dns,
        "url": url,
    }


def get_disk_storage(wiz_entity_properties: Dict) -> int:
    """
    Extract disk storage information.
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: Disk storage
    :rtype: int
    """
    try:
        return int(wiz_entity_properties.get("totalDisks", 0))
    except ValueError:
        return 0


def get_product_ids(wiz_entity_properties: Dict) -> Optional[str]:
    """
    Get product IDs from Wiz entity properties
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: Product IDs
    :rtype: Optional[str]
    """
    product_ids = wiz_entity_properties.get("_productIDs")
    if product_ids and isinstance(product_ids, list):
        return ", ".join(product_ids)
    return product_ids


def get_latest_version(wiz_entity_properties: Dict) -> Optional[str]:
    """
    Get the latest version from Wiz entity properties
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: Latest version
    :rtype: Optional[str]
    """
    # Retrieve the latest version and current version
    latest_version = wiz_entity_properties.get("latestVersion")
    current_version = wiz_entity_properties.get("version")

    # Return the latest version if it exists, otherwise return the current version
    return latest_version if latest_version is not None else current_version


def get_cloud_identifier(
    wiz_entity_properties: Dict,
) -> Tuple[Optional[str], Optional[str]]:
    """
    Get cloud identifier
    :param Dict wiz_entity_properties: Wiz entity properties
    :return: Cloud identifier
    :rtype: Tuple[Optional[str], Optional[str]]
    """
    # Define common keywords for each provider
    aws_keywords = ["aws", "amazon", "ec2"]
    azure_keywords = ["azure", "microsoft"]
    google_keywords = ["google", "gcp", "google cloud"]

    provider_unique_id = (
        wiz_entity_properties.get("providerUniqueId").lower() if wiz_entity_properties.get("providerUniqueId") else ""
    )

    # Check for AWS identifiers
    if any(keyword in provider_unique_id for keyword in aws_keywords):
        return "aws", provider_unique_id

    # Check for Azure identifiers
    if any(keyword in provider_unique_id for keyword in azure_keywords):
        return "azure", provider_unique_id

    # Check for Google identifiers
    if any(keyword in provider_unique_id for keyword in google_keywords):
        return "google", provider_unique_id

    # If none of the above, check if there is any providerUniqueId
    if provider_unique_id:
        return "other", provider_unique_id

    # Return None if no identifier is found
    return None, None


def process_row(
    row: Dict,
    params: ProcessDataParams,
) -> None:
    """
    Process a row of Wiz data
    :param Dict row: Row
    :param ProcessDataParams params: Process data parameters
    :return: None
    :rtype: None
    """
    try:
        map_progress = params.map_progress
        external_id = row.get("subscriptionExternalId")
        wiz_id = row.get("id")
        params.data_objects[wiz_id] = row
        existing_asset = params.existing_asset_dict.get(wiz_id)
        wiz_entity = row.get("graphEntity") or {}
        wiz_entity_properties = wiz_entity.get("properties", {})
        if wiz_entity_properties.get("cloudProviderURL"):
            params.links_to_create_for_assets[wiz_id] = Link(
                url=wiz_entity_properties.get("cloudProviderURL"),
                title="Cloud Provider URL",
            )
        asset_type = create_asset_type(row.get("type"))
        regscale_asset = map_asset(
            row=row,
            asset_type=asset_type,
            wiz_entity_properties=wiz_entity_properties,
            existing_asset=existing_asset,
            parent_id=params.parent_id,
            parent_module=params.parent_module,
            external_id=external_id,
            wiz_id=wiz_id,
        )
        if existing_asset:
            params.wiz_assets_to_update.append(regscale_asset)
        else:
            params.wiz_assets_to_create.append(regscale_asset)
        params.wiz_prop_map[wiz_id] = create_props_from_wiz_props(wiz_entity_properties)
        handle_port_mapping(
            wiz_entity_properties,
            wiz_entity,
            wiz_id,
            params.parent_id,
            params.parent_module,
            params.ports_to_create,
        )
        handle_component_title(row, params.components_to_create)
        map_progress.advance(params.map_job, 1)
    except Exception as ex:
        logger.error(f"Error processing row: {ex}", exc_info=True)


def handle_component_title(row: Dict, components_to_create: List[str]) -> None:
    """
    Handle component title
    :param Dict row: Row
    :param List[str] components_to_create: Components to create
    :return: None
    :rtype: None
    """
    try:
        component_title = row.get("type").title().replace("_", " ") if row.get("type") else None
        if component_title and component_title not in components_to_create:
            components_to_create.append(component_title)
    except Exception as ex:
        logger.warning(f"Error handling component title: {ex}", exc_info=True)


def handle_port_mapping(
    wiz_entity_properties: Dict,
    wiz_entity: Dict,
    wiz_id: str,
    parent_id: int,
    parent_module: str,
    ports_to_create: Dict[str, PortsProtocol],
) -> None:
    """
    Handle port mapping
    :param Dict wiz_entity_properties: Wiz entity properties
    :param Dict wiz_entity: Wiz entity
    :param str wiz_id: Wiz ID
    :param int parent_id: Parent ID
    :param str parent_module: Parent module
    :param Dict[str, PortsProtocol] ports_to_create: Ports to create
    :return: None
    """
    wiz_entity_properties.get("portStart")
    if start_port := wiz_entity_properties.get("portStart"):
        protocol = wiz_entity_properties.get("protocols", wiz_entity_properties.get("protocol"))
        end_port = wiz_entity_properties.get("portEnd") if wiz_entity_properties.get("portEnd") else start_port
        ports_to_create[wiz_id] = PortsProtocol(
            service=wiz_entity.get("name"),
            startPort=start_port,
            endPort=end_port,
            protocol=protocol,
        )
        create_port(
            service=wiz_entity.get("name"),
            start_port=start_port,
            end_port=end_port,
            protocol=protocol,
            parent_id=parent_id,
            parent_module=parent_module,
        )


def handle_removed_assets(existing_assets: List[Asset], all_assets: List[Asset]) -> None:
    """
    Handle removed assets
    :param List[Asset] existing_assets: Existing assets
    :param List[Asset] all_assets: All assets
    :rtype: None
    """
    to_delete = [asset for asset in existing_assets if asset not in all_assets]
    delete_progress = create_progress_object()
    delete_job = delete_progress.add_task("[#f68d1f]Deleting assets that are no longer in Wiz...", total=len(to_delete))
    for asset in to_delete:
        asset.delete()
        delete_progress.advance(delete_job, 1)


def create_data_objects(data_objects: Dict, assets: List[Asset]) -> None:
    """
    Create data objects for Wiz assets.
    :param Dict data_objects: Data objects
    :param List[Asset] assets: Assets
    :return: None
    :rtype: None
    """
    app = Application()
    data_objects_to_create = []
    data_objects_to_update = []
    building_progress = create_progress_object()
    total_items = len(assets)
    building_job = building_progress.add_task(
        "[#f68d1f]Gathering RegScale Data Objects to process...",
        total=total_items,
    )
    with building_progress:
        for asset in assets:
            existing_data_objects = Data.get_all_by_parent(asset.id, "assets")
            data = data_objects.get(asset.wizId)
            if data:
                data_json_str = json.dumps(data)
                existing_data = next(
                    (d for d in existing_data_objects if d.dataSource == DATASOURCE),
                    None,
                )
                if existing_data:
                    existing_data.rawData = data_json_str
                    data_objects_to_update.append(existing_data)
                else:
                    data_objects_to_create.append(
                        Data(
                            parentId=asset.id,
                            parentModule="assets",
                            dataSource=DATASOURCE,
                            dataType=DataDataType.JSON.value,
                            rawData=data_json_str,
                            lastUpdatedById=app.config.get("userId"),
                            createdById=app.config.get("userId"),
                        )
                    )
            building_progress.advance(building_job, 1)
    if data_objects_to_update and len(data_objects_to_update) > 0:
        Data.batch_update(data_objects_to_update)
    if data_objects_to_create and len(data_objects_to_create) > 0:
        Data.batch_create(data_objects_to_create)


def create_links_for_assets(
    links_to_create_for_assets: Dict[str, Link],
    assets: List[Asset],
) -> None:
    """
    Create links for assets
    :param Dict[str, Link] links_to_create_for_assets: Links to create for assets
    :param List[Asset] assets: List of assets
    :return: None
    :rtype: None
    """
    total_items = len(assets)
    create_link_progress = create_progress_object()
    create_link_job = create_link_progress.add_task(
        "[#f68d1f]Creating RegScale Links in Assets to Source Cloud Resources...",
        total=total_items,
    )
    with create_link_progress:
        for asset in assets:
            existing_links = Link.get_all_by_parent(asset.id, "assets")
            link_names = [link.title for link in existing_links]
            link = links_to_create_for_assets.get(asset.wizId)
            if link and link.title not in link_names:
                link.parentID = asset.id
                link.parentModule = "assets"
                link.create()
            create_link_progress.advance(create_link_job, advance=1)


def create_properties(wiz_prop_map: Dict, assets: List[Asset]) -> None:
    """
    Create properties for Wiz assets.
    :param Dict wiz_prop_map: Wiz property map
    :param List[Asset] assets: Assets
    :return: None
    :rtype: None
    """

    for asset in assets:
        props_to_create = []
        props_to_update = []
        existing_props = Property.get_all_by_parent(asset.id, "assets")
        for prop in wiz_prop_map.get(asset.wizId, []):
            prop.parentId = asset.id
            prop.parentModule = "assets"
            if prop not in existing_props:
                props_to_create.append(prop)
            else:
                props_to_update.append(prop)
        Property.batch_create(props_to_create)
        Property.batch_update(props_to_update)


def create_asset_component_mappings(created_assets: List[Asset], components: List[Component]) -> None:
    """
    Create mappings between assets and components.
    :param List[Asset] created_assets: List of created assets.
    :param List[Component] components: List of components.
    :return: None
    :rtype: None
    """
    logger.info(f"Creating {len(created_assets)} asset-component mappings...")
    component_dict = {component.title: component for component in components}
    # Create a progress object and add a task for asset-component mapping
    map_asset_comp_progress = create_progress_object()
    total_items = len(created_assets)
    map_asset_comp_task = map_asset_comp_progress.add_task(
        f"[#f68d1f]Creating {total_items} asset-component mappings...",
        total=total_items,
    )

    with map_asset_comp_progress:
        for asset in created_assets:
            component = component_dict.get(asset.assetType)
            if component:
                _create_asset_component_mapping(asset, component)
            map_asset_comp_progress.advance(map_asset_comp_task, advance=1)


def _create_asset_component_mapping(asset: Asset, component: Component) -> None:
    """
    Create a mapping between an asset and a component.

    :param Asset asset: The asset object.
    :param Component component: The component object.
    :return: None
    :rtype: None
    """
    AssetMapping(
        assetId=asset.id,
        componentId=component.id,
    ).create()


def update_asset_component_mappings(assets: List[Asset], components: List[Component]) -> None:
    """
    Update the mapping between an asset and a component.

    :param List[Asset] assets: List of assets.
    :param List[Component] components: List of components.
    :return: None
    :rtype: None
    """
    logger.info(f"Updating {len(assets)} asset-component mappings...")
    component_dict = {component.title: component for component in components}
    # Create a progress object and add a task for asset-component mapping
    map_asset_comp_progress = create_progress_object()
    total_items = len(assets)
    map_asset_comp_task = map_asset_comp_progress.add_task(
        f"[#f68d1f]Updating {total_items} asset-component mappings...",
        total=total_items,
    )
    existing_mapping_dict = {}
    for component in components:
        existing_mappings = AssetMapping.find_mappings(component_id=component.id)
        existing_mapping_dict[component.id] = [m.assetId for m in existing_mappings]

    with map_asset_comp_progress:
        for asset in assets:
            component = component_dict.get(asset.assetType)
            has_asset_mapping = False
            if asset.id in existing_mapping_dict.get(component.id, []):
                has_asset_mapping = True
            if component and not has_asset_mapping:
                _create_asset_component_mapping(asset, component)
            map_asset_comp_progress.advance(map_asset_comp_task, advance=1)


def create_missing_components(
    components_to_create: List[str],
    parent_id: int,
    user_id: str,
    wiz_projects: List[str],
    existing_components: List[Component],
) -> List[Component]:
    """
    Create or get missing components based on the provided list of component titles.
    If a component does not exist in the existing components list, it will be created.

    :param List[str] components_to_create: List of component titles to create.
    :param int parent_id: Parent ID.
    :param str user_id: User ID.
    :param List[str] wiz_projects: List of Wiz project IDs.
    :param List[Component] existing_components: List of existing components.
    :rtype: List[Component]
    """
    existing_component_titles = {component.title for component in existing_components}
    components = []
    for component_title in components_to_create:
        if component_title not in existing_component_titles:
            components.append(
                create_or_get_component(
                    parent_id=parent_id,
                    component_title=component_title,
                    user_id=user_id,
                    wiz_projects=wiz_projects,
                    existing_components=existing_components,
                )
            )
    return components


def log_existing_assets_info(existing_assets: List[Asset]) -> None:
    """
    Log information about existing assets.

    :param List[Asset] existing_assets: List of existing assets.
    :return: None
    :rtype: None
    """
    if existing_assets:
        logger.info(f"Found {len(existing_assets)} existing assets..")
    else:
        logger.info("No existing assets found..")


def collect_components_to_create(data: List[Dict[str, Any]], components_to_create: List[str]) -> List[str]:
    """
    Collect unique component titles to create from the data.

    :param List[Dict[str, Any]] data: List of Wiz data.
    :param List[str] components_to_create: List of component titles to create.
    :return: List of unique component titles to create.
    :rtype: List[str]
    """
    for row in data:
        component_title = row.get("type", "").title().replace("_", " ")
        if component_title and component_title not in components_to_create:
            components_to_create.append(component_title)
    return list(set(components_to_create))


def process_data(params: ProcessDataParams) -> None:
    """
    Process the Wiz data concurrently, mapping it to RegScale assets.
    :param ProcessDataParams params: ProcessDataParams object containing the necessary parameters.
    :return: None
    :rtype: None
    """
    with params.map_progress:
        for row in params.data:
            process_row(row, params)


def threaded_process_rows(params: ProcessDataParams, max_workers: int = 10) -> List:
    """
    Process the data concurrently using a ThreadPoolExecutor.
    :param ProcessDataParams params: ProcessDataParams object containing the necessary parameters.
    :param int max_workers: Maximum number of workers for the ThreadPoolExecutor.
    :return: List of results from processing the data.
    :rtype: List
    """

    def process_row_wrapper(row):
        process_row(row, params)
        params.map_progress.advance(params.map_job, 1)

    with params.map_progress:
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(process_row_wrapper, params.data)

    return list(results)


def save_ports(ports_to_create: Dict, assets: List[Asset]) -> None:
    """
    Create ports from the list of ports to create.

    :param Dict ports_to_create: Dictionary containing ports to create.
    :param List[Asset] assets: List of assets.
    :return: None
    :rtype: None
    """
    create_ports_progress = create_progress_object()
    create_ports_job = create_ports_progress.add_task("[#f68d1f]Creating ports for assets...", total=len(assets))
    with create_ports_progress:
        for asset in assets:
            existing_ports = PortsProtocol.get_all_by_parent(asset.id, "assets")
            if port := ports_to_create.get(asset.wizId):
                if not any(p.service == port.service for p in existing_ports):
                    port.parentId = asset.id
                    port.parentModule = "assets"
                    port.create()
            create_ports_progress.advance(create_ports_job, advance=1)


def finalize_assets(
    wiz_assets_to_create: List[Asset], wiz_assets_to_update: List[Asset]
) -> Tuple[List[Asset], List[Asset]]:
    """
    Finalize the creation and updating of Wiz assets.

    :param List[Asset] wiz_assets_to_create: List of Wiz assets to create.
    :param List[Asset] wiz_assets_to_update: List of Wiz assets to update.
    :return: Tuple of lists containing created and updated assets.
    :rtype: Tuple[List[Asset], List[Asset]]
    """
    created_assets, updated_assets = [], []
    if wiz_assets_to_create and len(wiz_assets_to_create) > 0:
        created_assets = Asset.batch_create(items=wiz_assets_to_create)
    if wiz_assets_to_update and len(wiz_assets_to_update) > 0:
        updated_assets = Asset.batch_update(items=wiz_assets_to_update)
    logger.info(f"{len(created_assets)} Wiz Assets created")
    return created_assets, updated_assets


def log_final_asset_counts(wiz_assets_to_create: List[Asset], wiz_assets_to_update: List[Asset]) -> None:
    """
    Log the final counts of created and updated assets.

    :param List[Asset] wiz_assets_to_create: List of Wiz assets to create.
    :param List[Asset] wiz_assets_to_update: List of Wiz assets to update.
    :return: None
    :rtype: None
    """
    if wiz_assets_to_create:
        logger.info(f"{len(wiz_assets_to_create)} Wiz Assets created")
    if wiz_assets_to_update:
        logger.info(f"{len(wiz_assets_to_update)} Wiz Assets updated")


def create_port(
    start_port: int,
    end_port: int,
    protocol: str,
    service: Optional[str],
    parent_id: int,
    parent_module: str,
) -> None:
    """
    Create ports from Wiz entity properties in Parent ID and Parent Module not asset

    :param int start_port: Start port
    :param int end_port: End port
    :param str protocol: Protocol
    :param Optional[str] service: Service
    :param int parent_id: Parent ID
    :param str parent_module: Parent module
    :return: None
    :rtype: None
    """
    existing_ports = PortsProtocol.get_all_by_parent(parent_id, parent_module)
    logger.debug(f"service: {service} for {start_port} - {end_port} - {protocol}")
    if not any(p.service == service for p in existing_ports):
        PortsProtocol(
            service=service,
            startPort=start_port,
            endPort=end_port,
            protocol=protocol,
            parentId=parent_id,
            parentModule=parent_module,
        ).create()


def fetch_existing_assets(parent_id: int, parent_module: str) -> Dict[str, Asset]:
    """
    Fetch existing assets
    :param int parent_id: Parent id
    :param str parent_module: Parent module
    :return: Existing assets
    :rtype: Dict[str, Asset]
    """
    existing_assets = Asset.get_all_by_parent(parent_id, parent_module)
    return {asset.wizId: asset for asset in existing_assets}


def fetch_wiz_data(
    query: str,
    variables: dict,
    topic_key: str,
    api_endpoint_url: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Sends a paginated GraphQL request to Wiz.

    :param str query: The GraphQL query to send.
    :param dict variables: The variables to use in the GraphQL request.
    :param str topic_key: The topic key to use in the paginated request.
    :param Optional[str] api_endpoint_url: The API endpoint URL to use in the request.
    :raises ValueError: If the Wiz access token is missing.
    :return: Response from the paginated GraphQL request.
    :rtype: List[Dict[str, Any]]
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
        data = client.fetch_all(
            variables=variables,
            topic_key=topic_key,
        )

        return data
    raise ValueError("Your Wiz access token is missing.")


def create_props_from_wiz_props(wiz_props: Dict) -> List[Property]:
    """
    Create properties from Wiz properties

    :param Dict wiz_props: Wiz properties
    :return: List of properties
    :rtype: List[Property]
    """
    if not wiz_props:
        return []
    props = []
    flattened_props = flatten_dict(wiz_props)
    for k, v in flattened_props.items():
        if v:
            props.append(Property(key=k, value=v))
    return props
