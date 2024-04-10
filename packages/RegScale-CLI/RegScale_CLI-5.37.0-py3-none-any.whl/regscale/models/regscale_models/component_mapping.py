""" This module contains the ComponentMapping model. """

import logging
from functools import lru_cache
from typing import Optional, List, cast

from pydantic import Field, ConfigDict
from requests import Response

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.models.regscale_models import RegScaleModel, T

logger = logging.getLogger(__name__)


class ComponentMapping(RegScaleModel):
    _module_slug = "componentmapping"
    _parent_id_field = "securityPlanId"
    _unique_fields = ["componentId", "securityPlanId"]
    id: Optional[int] = None
    uuid: Optional[str] = None
    securityPlanId: int
    componentId: int
    createdById: str = Field(default_factory=RegScaleModel._api_handler.get_user_id)
    dateCreated: str = Field(default_factory=get_current_datetime)
    lastUpdatedById: str = Field(default_factory=RegScaleModel._api_handler.get_user_id)
    dateLastUpdated: str = Field(default_factory=get_current_datetime)
    tenantsId: int = 1
    isPublic: bool = True

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the ComponentMapping model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            filter_component_mappings="/api/{model_slug}/filterComponentMappings/{intComponent}/{intSP}/{strSearch}/{intPage}/{intPageSize}",
            delete_component_mapping_delete="/api/{model_slug}/{id}",
            find_mappings="/api/{model_slug}/findMappings/{intID}",
            get_mappings_as_components="/api/{model_slug}/getMappingsAsComponents/{intID}",
            get_mappings_as_security_plans="/api/{model_slug}/getMappingsAsSecurityPlans/{intID}",
        )

    @classmethod
    def find_mappings(cls, security_plan_id: int) -> List["ComponentMapping"]:
        """
        Find mappings for a given component

        :param int security_plan_id: Security Plan ID
        :return: List of mappings
        :rtype: List["ComponentMapping"]
        """
        return cls._handle_list_response(
            cls._api_handler.get(
                cls.get_endpoint("get_mappings_as_components").format(
                    intID=security_plan_id,
                )
            ),
            security_plan_id=security_plan_id,
        )

    @classmethod
    def get_all_by_parent(cls, parent_id: int, parent_module: str) -> List["ComponentMapping"]:
        """
        Get all ComponentMappings by parent

        :param int parent_id: Parent ID
        :param str parent_module: Parent module
        :return: List of ComponentMappings
        :rtype: List["ComponentMapping"]
        """
        return cls.find_mappings(security_plan_id=parent_id)

    @classmethod
    def _handle_list_response(cls, response: Response, security_plan_id: int) -> List["ComponentMapping"]:
        """
        Handle list response

        :param response: Response from API
        :param int security_plan_id: Security Plan ID
        :type response: Response
        :return: List of ComponentMappings
        :rtype: List["ComponentMapping"]
        """
        if not response or response.status_code in [204, 404]:
            return []
        if response.ok:
            json_response = response.json()
            if isinstance(json_response, dict):
                json_response = json_response.get("items", [])
            return cast(
                List[T],
                [cls(securityPlanId=security_plan_id, **o) for o in json_response],
            )
        else:
            logger.error(f"Failed to get {cls.get_module_slug()} for {cls.__name__}")
            return []
