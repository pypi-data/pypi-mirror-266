# SPDX-License-Identifier: Apache-2.0

"""Sphinx extension for documenting OpenQASM 2 and 3 programs"""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.util.typing import ExtensionMetadata

from . import _version, domain
from .domain import OpenQASMDomain

__version__ = _version.get_version()

# Setup a basic Sphinx domain for documenting OpenQASM programs.


def setup(app: Sphinx) -> ExtensionMetadata:
    app.add_domain(OpenQASMDomain)
    app.add_node(
        domain.desc_qubitparameterlist,
        html=(
            domain.html_visit_desc_qubitparameterlist,
            domain.html_depart_desc_qubitparameterlist,
        ),
    )
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
