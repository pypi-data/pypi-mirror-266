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

from abc import ABC, abstractmethod
from typing import List, Optional

from esmf_aspect_meta_model_python.base.data_types.data_type import DataType
from esmf_aspect_meta_model_python.base.property import Property
from esmf_aspect_meta_model_python.base.structure_element import StructureElement


class ComplexType(DataType, StructureElement, ABC):
    """Complex Type interface class."""

    @property
    @abstractmethod
    def all_properties(self) -> List[Property]:
        """All properties."""

    @property
    def is_abstract_entity(self) -> bool:
        """Is abstract entity flag."""
        return False

    @property
    @abstractmethod
    def extends(self) -> Optional["ComplexType"]:
        """Extends."""

    @property
    def is_scalar(self) -> bool:
        """Is scalar flag."""
        return False
