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
from typing import Optional, Set

from esmf_aspect_meta_model_python.base.base import Base
from esmf_aspect_meta_model_python.base.quantity_kind import QuantityKind


class Unit(Base, ABC):
    """Unit interface class.

    A unit is used to specify the magnitude of a physical quantity.
    Examples for units are meter, millimeter, inch, or volts. A Unit in the SAMM.
    """

    @property
    @abstractmethod
    def symbol(self) -> Optional[str]:
        """Symbol."""

    @property
    @abstractmethod
    def code(self) -> Optional[str]:
        """Code."""

    @property
    @abstractmethod
    def reference_unit(self) -> Optional[str]:
        """Reference unit."""

    @property
    @abstractmethod
    def conversion_factor(self) -> Optional[str]:
        """Conversion factor."""

    @property
    @abstractmethod
    def quantity_kinds(self) -> Set[QuantityKind]:
        """Quantity kinds."""
