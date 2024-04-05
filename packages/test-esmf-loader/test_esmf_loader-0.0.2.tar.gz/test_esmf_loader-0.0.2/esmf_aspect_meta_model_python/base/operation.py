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

from esmf_aspect_meta_model_python.base.base import Base
from esmf_aspect_meta_model_python.base.property import Property


class Operation(Base, ABC):
    """Operation interface class.

    Meta Model element which represents an operation of an aspect.
    An operation has a number of input properties and one optional output property.
    """

    @property
    @abstractmethod
    def input_properties(self) -> List[Property]:
        """Input properties."""

    @property
    @abstractmethod
    def output_property(self) -> Optional[Property]:
        """Output property."""
