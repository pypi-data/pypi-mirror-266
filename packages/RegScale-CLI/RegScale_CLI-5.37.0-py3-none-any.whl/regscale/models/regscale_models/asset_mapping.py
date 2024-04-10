import logging
from typing import Optional, List

from pydantic import ConfigDict, Field

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models import Asset
from regscale.models.regscale_models.regscale_model import RegScaleModel
from regscale.models.regscale_models.regscale_model import T

logger = logging.getLogger(__name__)


class AssetMapping(RegScaleModel):
    """
    AssetMapping model class.
    """

    _module_slug = "assetmapping"
    _unique_fields = ["componentId", "assetId"]
    _parent_id_field = "componentId"

    id: Optional[int] = 0
    uuid: Optional[str] = None
    assetId: int
    componentId: int
    createdById: Optional[str] = None
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = None
    isPublic: Optional[bool] = True
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)
    tenantsId: Optional[int] = 1

    @staticmethod
    def get_assets(component_id: int) -> List[T]:
        """
        Get assets for a given component ID.

        :param int component_id: The ID of the component
        :return: A list of assets
        :rtype: List[T]
        """
        asset_mappings = AssetMapping.find_mappings(component_id=component_id)
        assets = []
        for asset_mapping in asset_mappings:
            assets.append(Asset.get_object(object_id=asset_mapping.assetId))
        return assets

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the AssetMapping model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            filter_asset_mappings="/api/{model_slug}/filterAssetMappings/{intAsset}/{intComp}/{strSearch}/{intPage}/{intPageSize}",
            find_mappings="/api/{model_slug}/findMappings/{intId}",
            get_mappings_as_components="/api/{model_slug}/getMappingsAsComponents/{intId}",
            get_mappings_as_assets="/api/{model_slug}/getMappingsAsAssets/{intId}/{strSortBy}/{strDirection}/{intPage}/{intPageSize}",
        )

    @classmethod
    def get_all_by_parent(cls, parent_id: int, parent_module: str) -> List[T]:
        """
        Retrieves all asset mappings for a given parent ID and ONLY Components.

        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :return: A list of asset mappings or None
        :rtype: List[T]
        """
        return cls.find_mappings(parent_id)

    @classmethod
    def find_mappings(cls, component_id: int) -> List[T]:
        """
        Retrieves all component mappings for a given component ID.

        :param int component_id: The ID of the component
        :return: A list of component mappings or None
        :rtype: List[T]
        """
        response = cls._api_handler.get(
            endpoint=cls.get_endpoint("find_mappings").format(model_slug=cls.get_module_slug(), intId=component_id)
        )
        if not response or response.status_code in [204, 404]:
            return []
        if response.ok:
            return [cls(**item) for item in response.json()]
        return []

    @classmethod
    def get_mappings_as_components(cls, asset_id: int) -> Optional[List[T]]:
        """
        Retrieves all component mappings for a given asset ID.

        :param int asset_id: The ID of the asset
        :return: A list of component mappings or None
        :rtype: Optional[List[T]]
        """
        response = cls._api_handler.get(
            endpoint=cls.get_endpoint("get_mappings_as_components").format(
                model_slug=cls.get_module_slug(), intId=asset_id
            )
        )
        if not response or response.status_code in [204, 404]:
            return None
        if response.ok:
            return [cls(**item) for item in response.json()]
        return None

    def get_mappings_as_assets(
        self, component_id: int, sort_by: str, direction: str, page: int, page_size: int
    ) -> Optional[List["AssetMapping"]]:
        """
        Retrieves all asset mappings for a given component ID.

        :param int component_id: The ID of the component
        :param str sort_by: The field to sort by
        :param str direction: The direction of sorting ('asc' or 'desc')
        :param int page: The page number for pagination
        :param int page_size: The number of items per page
        :return: A list of asset mappings or None
        :rtype: Optional[List[AssetMapping]]
        """
        response = self._api_handler.get(
            endpoint=self.get_endpoint("get_mappings_as_assets").format(
                model_slug=self._model_slug,
                intId=component_id,
                strSortBy=sort_by,
                strDirection=direction,
                intPage=page,
                intPageSize=page_size,
            )
        )
        if not response or response.status_code in [204, 404]:
            return None
        if response.ok:
            return [self.__class__(**item) for item in response.json()]
        return None
