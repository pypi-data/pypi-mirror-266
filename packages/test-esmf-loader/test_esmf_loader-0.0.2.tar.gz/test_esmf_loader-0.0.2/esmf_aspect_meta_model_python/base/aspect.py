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
from typing import List

from esmf_aspect_meta_model_python.base.event import Event
from esmf_aspect_meta_model_python.base.operation import Operation
from esmf_aspect_meta_model_python.base.structure_element import StructureElement


class Aspect(StructureElement, ABC):
    """Aspect interface class.

    An aspect is the root class for a digital twin.
    It has a number of properties and operations.
    An Aspect Model is described in RDF Turtle.
    """

    @property
    @abstractmethod
    def operations(self) -> List[Operation]:
        """Operations."""

    @property
    @abstractmethod
    def events(self) -> List[Event]:
        """Events."""

    @property
    def is_collection_aspect(self) -> bool:
        """Is collection aspect flag."""
        return False
