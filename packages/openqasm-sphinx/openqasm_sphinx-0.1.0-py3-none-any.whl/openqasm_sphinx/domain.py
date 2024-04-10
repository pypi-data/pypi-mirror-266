# SPDX-License-Identifier: Apache-2.0

from __future__ import annotations

import re
import typing

from sphinx import addnodes
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, ObjType
from sphinx.roles import XRefRole
from sphinx.util import logging
from sphinx.util.nodes import make_id, make_refnode

if typing.TYPE_CHECKING:
    from sphinx.writers.html import HTML5Translator
    from sphinx.writers.latex import LaTeXTranslator

_LOG = logging.getLogger(__name__)


class desc_qubitparameterlist(addnodes.desc_parameterlist):  # pylint: disable=invalid-name
    """Specialised node to handle the qubit arguments to gates."""


def html_visit_desc_qubitparameterlist(
    self: HTML5Translator, node: desc_qubitparameterlist
) -> None:
    # pylint: disable=protected-access
    self._visit_sig_parameter_list(node, addnodes.desc_parameter, "", "")


def html_depart_desc_qubitparameterlist(
    self: HTML5Translator, node: desc_qubitparameterlist
) -> None:
    # pylint: disable=protected-access
    self._depart_sig_parameter_list(node)


class OpenQASMGate(ObjectDescription):
    # Parsing code through superset regexes - good enough for docs, where we can assume there
    # weren't any syntax errors.
    SIGNATURE = re.compile(
        r"(?P<name>\w+)\s*(\((?P<params>(\s*\w+,?)*)\))?(?P<qubits>(\s*\w+,?)*)",
        flags=re.U,
    )

    def _object_hierarchy_parts(self, sig_node):
        return (sig_node["name"],)

    def _toc_entry_node(self, sig_node):
        return sig_node["name"]

    def add_target_and_index(self, name, sig: str, signode):
        node_id = make_id(self.env, self.state.document, "", name)
        signode["ids"].append(node_id)
        domain = typing.cast(OpenQASMDomain, self.env.domains["oq"])
        domain.index_object(name, "gate", node_id)
        self.indexnode["entries"].append(("single", name, node_id, "", None))

    def handle_signature(self, sig: str, signode):
        if (m := self.SIGNATURE.match(sig)) is None:
            raise ValueError(f"bad gate signature: '{sig}'")
        name = m["name"]
        params = (
            [param.strip() for param in m["params"].split(",")] if m["params"] is not None else []
        )
        qubits = [qubit.strip() for qubit in m["qubits"].split(",")]

        # This isn't perfect (there's semantics missing), but good enough for proof-of-concept.
        signode["name"] = name
        signode += addnodes.desc_annotation(
            "", "", addnodes.desc_sig_keyword_type("gate", "gate"), addnodes.desc_sig_space()
        )
        signode += addnodes.desc_name(name, name)
        if params:
            params_node = addnodes.desc_parameterlist(m["params"])
            for param in params:
                params_node += addnodes.desc_parameter("", param)
            signode += params_node
        if qubits:
            signode += addnodes.desc_sig_space()
            qubits_node = desc_qubitparameterlist(m["qubits"])
            for qubit in qubits:
                qubits_node += addnodes.desc_parameter("", qubit)
            signode += qubits_node
        return name


class OpenQASMDomain(Domain):
    """OpenQASM language domain."""

    name = "oq"
    label = "OpenQASM"
    object_types = {
        "gate": ObjType("gate", "gate"),
    }
    directives = {
        "gate": OpenQASMGate,
    }
    roles = {
        "gate": XRefRole(),
    }
    initial_data = {
        "objects": {},
    }

    def clear_doc(self, docname):
        self.data["objects"] = {
            fullname: (obj_docname, node_id, objtype)
            for fullname, (obj_docname, node_id, objtype) in self.data["objects"].items()
            if obj_docname != docname
        }

    def get_objects(self):
        for fullname, (docname, _, objtype) in self.data["objects"].items():
            yield (fullname, fullname, objtype, docname, fullname, 1)

    def index_object(self, name: str, objtype: str, node_id: str):
        if name in self.data["objects"]:
            _LOG.warning("[oq] duplicate entry for '%s'", name)
            return
        self.data["objects"][name] = (self.env.docname, node_id, objtype)

    def merge_domaindata(self, docnames, otherdata):
        docnames = set(docnames)
        self_objects = self.data["objects"]
        for fullname, (docname, node_id, objtype) in otherdata["objects"].items():
            if docname not in docnames:
                continue
            if fullname in self_objects:
                _LOG.warning("[oq] during merge: duplicate entry for '%s'", fullname)
            self_objects[fullname] = docname, node_id, objtype

    def resolve_xref(self, env, fromdocname, builder, typ, target, node, contnode):
        if (lookup := self.data["objects"].get(target)) is None:
            return None
        name, node_id, objtype = lookup
        if objtype != typ:
            return None
        return make_refnode(builder, fromdocname, name, node_id, [contnode], name)

    def resolve_any_xref(self, env, fromdocname, builder, target, node, contnode):
        if (lookup := self.data["objects"].get(target)) is None:
            return []
        name, node_id, objtype = lookup
        return [(objtype, make_refnode(builder, fromdocname, name, node_id, contnode, name))]
