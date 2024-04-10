#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Dataclass for a Microsoft Defender 365 recommendations """

# standard python imports
from dataclasses import dataclass
from typing import Any


@dataclass
class Recommendations:
    """Recommendations Model"""

    id: str  # Required
    data: dict  # Required
    analyzed: bool = False
    created: bool = False

    def __getitem__(self, key: Any) -> Any:
        """
        Get attribute from Pipeline

        :param Any key: Key to retrieve value from
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
