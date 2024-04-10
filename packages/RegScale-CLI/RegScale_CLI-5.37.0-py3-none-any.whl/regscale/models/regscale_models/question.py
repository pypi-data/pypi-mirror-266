"""
This module contains the Questions model for RegScale.
"""

from typing import Optional, List, Dict
from pydantic import ConfigDict, Field
from regscale.core.app.utils.app_utils import get_current_datetime
from .regscale_model import RegScaleModel


class AnswerOptions(RegScaleModel):
    answerOption: Optional[str]
    answerScore: Optional[int] = 0


class Questions(RegScaleModel):
    """
    A class to represent the Questions model in RegScale.
    """

    _model_slug = "questions"

    id: Optional[int]
    parentQuestionnaireId: int
    uuid: Optional[str]
    questionType: int
    name: Optional[str]
    label: Optional[str]
    prompt: Optional[str]
    tenantsId: Optional[int]
    createdById: Optional[str]
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    dateLastUpdated: Optional[str] = Field(default_factory=get_current_datetime)
    isPublic: bool = True
    lastUpdatedById: Optional[str]
    controlNumber: Optional[str]
    section: int = 0
    staticAnswerOptions: Optional[List[Dict]]  # Adjust the type if it's not a string
    askQuestion: bool = True
    quid: Optional[str]
    required: bool = True
    sectionIndex: int = 0
    uploadEnabled: bool = False
    response: Optional[str]  # Adjust the type if it's not a string

    @staticmethod
    def _get_additional_endpoints() -> ConfigDict:
        """
        Get endpoints for the Question model.

        :return: A dictionary of endpoints
        :rtype: ConfigDict
        """
        return ConfigDict(
            get_all_by_parent_get="/api/{model_slug}/getAllByParent",
            get="/api/{model_slug}/find/{id}",
            insert="/api/{model_slug}/create",
            update="/api/{model_slug}/update",
            delete="/api/{model_slug}/delete/{id}",
            get_new_section_index_post="/api/{model_slug}/getNewSectionIndex",
            update_origin_section_put="/api/{model_slug}/updateOriginSection",
            section_update_from_insert_put="/api/{model_slug}/sectionUpdateFromInsert",
            section_update_from_cancel_put="/api/{model_slug}/sectionUpdateFromCancel",
            index_up_put="/api/{model_slug}/indexUp",
            index_down_put="/api/{model_slug}/indexDown",
        )
