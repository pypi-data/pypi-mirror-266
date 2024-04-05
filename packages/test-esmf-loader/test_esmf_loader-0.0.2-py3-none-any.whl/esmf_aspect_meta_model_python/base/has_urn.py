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
from typing import Optional


class HasUrn(ABC):
    """Has Urn interface class.

    Base class from which all Meta Model Elements inherit.
    Class prescribes method to get the element urn and samm version.
    """

    @property
    @abstractmethod
    def urn(self) -> Optional[str]:
        """URN."""

    @property
    @abstractmethod
    def meta_model_version(self) -> str:
        """Meta model version."""
