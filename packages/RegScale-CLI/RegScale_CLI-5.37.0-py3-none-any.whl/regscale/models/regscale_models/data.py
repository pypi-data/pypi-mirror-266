""" Data model class """

from enum import Enum
from typing import List, Optional, cast

from pydantic import Field, ConfigDict
from requests import Response

from regscale.core.app.utils.app_utils import (
    get_current_datetime,
    create_progress_object,
)
from .regscale_model import RegScaleModel, T


class DataListItem(RegScaleModel):
    """
    Data list item model class
    """

    id: int
    dateCreated: str
    dataType: str
    dataSource: str


class DataDataType(str, Enum):
    """
    Data data type enum
    """

    JSON = "JSON"
    XML = "XML"
    YAML = "YAML"

    def __str__(self):
        return self.value


class Data(RegScaleModel):
    """
    Data model class
    """

    _module_slug = "data"
    _unique_fields = ["parentId", "parentModule", "dataSource", "dataType", "rawData"]

    id: Optional[int] = None
    createdById: Optional[str] = Field(default_factory=RegScaleModel._api_handler.get_user_id)
    dateCreated: str = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel._api_handler.get_user_id)
    isPublic: bool = True
    dataSource: str
    dataType: Optional[str] = None
    rawData: Optional[str] = None
    parentId: int
    parentModule: str
    tenantsId: int = 1
    dateLastUpdated: str = Field(default_factory=get_current_datetime)

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get additional endpoints for the Data model.

        :return: A dictionary of additional endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            batch_create="/api/{model_slug}/batchCreate",
            batch_update="/api/{model_slug}/batchUpdate",
        )

    @classmethod
    def batch_create(cls, data_list: List["Data"]) -> List["Data"]:
        """
        Batch create data

        :param List[Data] data_list: the data to create
        :return: the created data
        :rtype: List[Data]
        """
        create_progress = create_progress_object()
        batch_size = 100
        results = []
        total_items = len(data_list)
        create_job = create_progress.add_task("[#f68d1f]Creating RegScale data objects...", total=total_items)
        with create_progress:
            for i in range(0, total_items, batch_size):
                batch = data_list[i : i + batch_size]
                results.extend(
                    cls._handle_list_response(
                        cls._api_handler.post(
                            endpoint=cls.get_endpoint("batch_create"),
                            data=[item.dict() for item in batch],
                        )
                    )
                )
                progress_increment = min(batch_size, total_items - i)
                create_progress.advance(create_job, progress_increment)
        return results

    @classmethod
    def batch_update(cls, data_list: List["Data"]) -> List["Data"]:
        """
        Batch create data

        :param List[Data] data_list: the data to create
        :return: the created data
        :rtype: List[Data]
        """
        create_progress = create_progress_object()
        batch_size = 100
        results = []
        total_items = len(data_list)
        create_job = create_progress.add_task("[#f68d1f]Updating RegScale data objects...", total=total_items)
        with create_progress:
            for i in range(0, total_items, batch_size):
                batch = data_list[i : i + batch_size]
                results.extend(
                    cls._handle_list_response(
                        cls._api_handler.put(
                            endpoint=cls.get_endpoint("batch_update"),
                            data=[item.dict() for item in batch],
                        )
                    )
                )
                progress_increment = min(batch_size, total_items - i)
                create_progress.advance(create_job, progress_increment)
        return results

    @classmethod
    def get_all_by_parent(cls, parent_id: int, parent_module: str) -> List[T]:
        """
        Get a list of objects by parent.

        :param int parent_id: The ID of the parent
        :param str parent_module: The module of the parent
        :return: A list of objects
        :rtype: List[T]
        """
        results = cls._handle_get_all_list_response(
            cls._api_handler.get(
                endpoint=cls.get_endpoint("get_all_by_parent").format(
                    intParentID=parent_id,
                    strModule=parent_module,
                )
            )
        )
        return [cls.get_object(r.id) for r in results]

    @classmethod
    def _handle_get_all_list_response(cls, response: Response, suppress_error: bool = False) -> List[T]:
        """
        Handle a list response.
        :param Response response: The response
        :param bool suppress_error: Whether to suppress the error, defaults to False
        :return: A list of objects or an empty List
        :rtype: List[T]
        """
        if not response or response.status_code in [204, 404]:
            return []
        if response.ok:
            json_response = response.json()
            if isinstance(json_response, dict) and "items" in json_response:
                json_response = json_response.get("items", [])
            return cast(List[DataListItem], [DataListItem(**o) for o in json_response])
        else:
            cls.log_response_error(response, suppress_error=False)
            return []
