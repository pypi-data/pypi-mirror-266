# SPDX-FileCopyrightText: Copyright DB InfraGO AG
# SPDX-License-Identifier: Apache-2.0
"""Implementation of the Capella model and its elements."""

__import__("warnings").warn(
    (
        f"The {__name__} module is experimental and may change at any time."
        " Productive use is not yet recommended. Use at your own risk."
    ),
    UserWarning,
    stacklevel=2,
)

from ._meta import *
from ._model import *
from ._obj import *
