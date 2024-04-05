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

from esmf_aspect_meta_model_python.base.characteristics.characteristic import Characteristic


class Collection(Characteristic, ABC):
    """Collection interface class.

    Describes a property that has a group of values of the same type.
    It can have a reference to another characteristic which describes an actual value of the collection.
    The values are not ordered and may include duplicates.
    """

    @property
    @abstractmethod
    def element_characteristic(self) -> Optional[Characteristic]:
        """Element characteristic."""
