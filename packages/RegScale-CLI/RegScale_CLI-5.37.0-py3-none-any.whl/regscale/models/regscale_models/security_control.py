#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Dataclass for Security Control in the application """

from dataclasses import asdict
from typing import Any, List, Optional

from pydantic import Field

from regscale.core.app.utils.app_utils import get_current_datetime
from regscale.core.app.api import Api
from regscale.core.app.application import Application
from regscale.models.regscale_models import RegScaleModel


class SecurityControl(RegScaleModel):
    """Security Control

    :return: A RegScale Security Control instance
    """

    _module_slug = "securitycontrols"
    _unique_fields = ["controlId", "catalogueId"]

    id: Optional[int] = 0
    isPublic: bool = True
    uuid: Optional[str] = None
    controlId: Optional[str] = None
    sortId: Optional[str] = None
    controlType: Optional[str] = None
    references: Optional[str] = None
    relatedControls: Optional[str] = None
    subControls: Optional[str] = None
    enhancements: Optional[str] = None
    family: Optional[str] = None
    mappings: Optional[str] = None
    assessmentPlan: Optional[str] = None
    weight: float
    catalogueId: int
    practiceLevel: Optional[str] = None
    objectives: Optional[List[object]] = None
    tests: Optional[List[object]] = None
    parameters: Optional[List[object]] = None
    archived: bool = False
    createdById: Optional[str] = Field(default_factory=RegScaleModel._api_handler.get_user_id)
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastUpdatedById: Optional[str] = Field(default_factory=RegScaleModel._api_handler.get_user_id)
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)

    @staticmethod
    def from_dict(obj: Any) -> "SecurityControl":
        """
        Creates a SecurityControl instance from a dictionary.

        This method simplifies the process of creating a SecurityControl instance by extracting
        the necessary information from a dictionary and handling missing or optional fields
        gracefully.

        :param obj: A dictionary containing the data for the SecurityControl.
        :type obj: Any
        :return: An instance of SecurityControl populated with the data from the dictionary.
        :rtype: SecurityControl
        """

        def get_value(key, cast_type, default=None):
            """Helper function to extract and cast a value from the dictionary."""
            value = obj.get(key)
            if value is None:
                return default
            try:
                return cast_type(value)
            except ValueError:
                return default

        _id = get_value("id", int)
        _is_public = get_value("isPublic", bool, False)
        _uuid = get_value("uuid", str)
        _control_id = get_value("controlId", str)
        _sort_id = get_value("sortId", str)
        _control_type = get_value("controlType", str)
        _title = get_value("title", str)
        _description = get_value("description", str, "")
        _references = get_value("references", str, "")
        _related_controls = get_value("relatedControls", str, "")
        _sub_controls = get_value("subControls", str, "")
        _enhancements = get_value("enhancements", str, "")
        _family = get_value("family", str, "")
        _mappings = get_value("mappings", str, "")
        _assessment_plan = get_value("assessmentPlan", str, "")
        _weight = get_value("weight", float)
        _catalogue_id = get_value("catalogueID", int)
        _practice_level = get_value("practiceLevel", str)
        _archived = get_value("archived", bool, False)
        _created_by_id = get_value("createdById", str)
        _date_created = get_value("dateCreated", str)
        _last_updated_by_id = get_value("lastUpdatedById", str)
        _date_last_updated = get_value("dateLastUpdated", str)

        return SecurityControl(
            id=_id,
            isPublic=_is_public,
            uuid=_uuid,
            controlId=_control_id,
            sortId=_sort_id,
            controlType=_control_type,
            title=_title,
            description=_description,
            references=_references,
            relatedControls=_related_controls,
            subControls=_sub_controls,
            enhancements=_enhancements,
            family=_family,
            mappings=_mappings,
            assessmentPlan=_assessment_plan,
            weight=_weight,
            catalogueID=_catalogue_id,
            practiceLevel=_practice_level,
            objectives=[],
            tests=[],
            parameters=[],
            archived=_archived,
            createdById=_created_by_id,
            dateCreated=_date_created,
            lastUpdatedById=_last_updated_by_id,
            dateLastUpdated=_date_last_updated,
        )

    def __hash__(self) -> hash:
        """
        Enable object to be hashable

        :return: Hashed SecurityControl
        :rtype: hash
        """
        return hash((self.controlId, self.catalogueId))

    def __getitem__(self, key: Any) -> Any:
        """
        Get attribute from Pipeline

        :param Any key: Key to get value for
        :return: value of provided key
        :rtype: Any
        """
        return getattr(self, key)

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set attribute in Pipeline with provided key

        :param Any key: Key to change to provided value
        :param Any value: New value for provided Key
        :rtype: None
        """
        return setattr(self, key, value)

    def __eq__(self, other: "SecurityControl") -> bool:
        """
        Update items in SecurityControl class

        :param SecurityControl other: SecurityControl Object to compare to
        :return: Whether the two objects are equal
        :rtype: bool
        """
        return self.controlId == other.controlId and self.catalogueId == other.catalogueID

    def dict(self) -> dict:
        """
        Create a dictionary from the SecurityControl dataclass

        :return: Dictionary of SecurityControl
        :rtype: dict
        """
        return {k: v for k, v in asdict(self).items()}

    @staticmethod
    def lookup_control(
        app: Application,
        control_id: int,
    ) -> "SecurityControl":
        """
        Return a Security Control in RegScale via API

        :param Application app: Application Instance
        :param int control_id: ID of the Security Control to look up
        :return: A Security Control from RegScale
        :rtype: SecurityControl
        """
        api = Api()
        control = api.get(url=app.config["domain"] + f"/api/securitycontrols/{control_id}").json()
        return SecurityControl.from_dict(control)

    @staticmethod
    def lookup_control_by_name(app: Application, control_name: str, catalog_id: int) -> Optional["SecurityControl"]:
        """
        Lookup a Security Control by name and catalog ID

        :param Application app: Application instance
        :param str control_name: Name of the security control
        :param int catalog_id: Catalog ID for the security control
        :return: A Security Control from RegScale, if found
        :rtype: Optional[SecurityControl]
        """
        api = Api()
        config = api.config
        res = api.get(config["domain"] + f"/api/securitycontrols/findByUniqueId/{control_name}/{catalog_id}")
        return SecurityControl.from_dict(res.json()) if res.status_code == 200 else None
