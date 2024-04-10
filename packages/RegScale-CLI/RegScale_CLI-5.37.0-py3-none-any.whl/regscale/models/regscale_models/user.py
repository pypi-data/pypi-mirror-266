#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Dataclass for a RegScale User """

# standard python imports
import random
import string
from dataclasses import asdict
from typing import Any, Optional

from pydantic import Field

from regscale.core.app.utils.app_utils import get_current_datetime
from .regscale_model import RegScaleModel


def generate_password() -> str:
    """
    Generates a random string that is 12-20 characters long

    :return: random string 12-20 characters long
    :rtype: str
    """
    # select a random password length between 12-20 characters
    length = random.randint(12, 20)

    # get all possible strings to create a password
    all_string_chars = string.ascii_lowercase + string.ascii_uppercase + string.digits + string.punctuation

    # randomly select characters matching the random length
    temp = random.sample(all_string_chars, length)
    # return a string from the temp list of samples
    return "".join(temp)


class User(RegScaleModel):
    """User Model"""

    userName: str  # Required
    email: str  # Required
    firstName: Optional[str]  # Required
    lastName: Optional[str]  # Required
    tenantId: int = 1
    initials: Optional[str] = None
    id: Optional[str] = None
    password: str = Field(default_factory=generate_password)
    name: Optional[str] = None
    workPhone: Optional[str] = None
    mobilePhone: Optional[str] = None
    avatar: Optional[str] = None
    jobTitle: Optional[str] = None
    orgId: Optional[str] = None
    pictureURL: Optional[str] = None
    activated: bool = False
    emailNotifications: bool = True
    ldapUser: bool = False
    externalId: Optional[str] = None
    dateCreated: Optional[str] = Field(default_factory=get_current_datetime)
    lastLogin: Optional[str] = None
    readOnly: bool = True

    def __getitem__(self, key: Any) -> Any:
        """
        Get attribute from Pipeline

        :param Any key: Key to get value from
        :return: value of provided key
        :rtype: Any
        """
        return getattr(self, key)

    def __setitem__(self, key: Any, value: Any) -> None:
        """
        Set attribute in Pipeline with provided key

        :param Any key: Key to change to provided value
        :param Any value: New value for provided Key
        :return: set attribute
        :rtype: None
        """
        return setattr(self, key, value)

    def dict(self) -> dict:
        """
        Create a dictionary from the Asset dataclass

        :return: Dictionary of Asset
        :rtype: dict
        """
        return {k: v for k, v in asdict(self).items()}
