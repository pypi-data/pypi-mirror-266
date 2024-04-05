#  Copyright (c) 2023 Robert Bosch Manufacturing Solutions GmbH
#
#  See the AUTHORS file(s) distributed with this work for additional
#  information regarding authorship.
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at https://mozilla.org/MPL/2.0/.
#
#   SPDX-License-Identifier: MPL-2.0

import abc

from typing import Dict, List, Optional

from esmf_aspect_meta_model_python.base.base import Base
from esmf_aspect_meta_model_python.loader.meta_model_base_attributes import MetaModelBaseAttributes


class BaseImpl(Base, metaclass=abc.ABCMeta):
    """Base Implemented class."""

    def __init__(self, meta_model_base_attributes: MetaModelBaseAttributes):
        self._meta_model_version = meta_model_base_attributes.meta_model_version
        self._urn = meta_model_base_attributes.urn
        self._name = meta_model_base_attributes.name
        self._preferred_names = meta_model_base_attributes.preferred_names
        self._descriptions = meta_model_base_attributes.descriptions
        self._see = meta_model_base_attributes.see
        self._parent_elements: Optional[list[Base]] = None

    @property
    def parent_elements(self) -> Optional[list[Base]]:
        """Parent elements."""
        return self._parent_elements

    @parent_elements.setter
    def parent_elements(self, elements: list[Base]) -> None:
        if self._parent_elements:
            self._parent_elements = elements

    def append_parent_element(self, element: Base) -> None:
        """Extend parent_elements list."""
        if self._parent_elements:
            self._parent_elements.append(element)
            return
        self._parent_elements = [element]

    @property
    def meta_model_version(self) -> str:
        """Meta model version."""
        return self._meta_model_version

    @property
    def preferred_names(self) -> Dict[str, str]:
        """Preferred names."""
        return self._preferred_names

    @property
    def descriptions(self) -> Dict[str, str]:
        """Descriptions."""
        return self._descriptions

    @property
    def see(self) -> List[str]:
        """See."""
        return self._see

    @property
    def urn(self) -> Optional[str]:
        """URN."""
        return self._urn

    @property
    def name(self) -> str:
        """Name."""
        return self._name
