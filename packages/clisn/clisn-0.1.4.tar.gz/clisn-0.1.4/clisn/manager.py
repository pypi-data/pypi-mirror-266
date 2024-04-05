"""Custom rdflib.NamespaceManager for CLSInfra."""

import sys

from rdflib import Graph, Namespace
from rdflib.namespace import NamespaceManager
from rdflib._type_checking import _NamespaceSetString

from clisn import namespaces


_namespaces = {
    key: value for key, value
    in sys.modules[namespaces.__name__].__dict__.items()
    if isinstance(value, Namespace)
}


class CLSInfraNamespaceManager(NamespaceManager):
    """Custom NamespaceManager for CLSInfra.

    Useage e.g. for creating a namespaced graph:
    ```
    graph = rdflib.Graph
    clisn.CLSInfraNamespaceManager(graph)
    ```
    """

    def __init__(self,
                 graph: Graph,
                 bind_namespaces: "_NamespaceSetString" = "rdflib"):
        """Call init.super and add CLSInfra namespaces."""
        super().__init__(graph=graph, bind_namespaces=bind_namespaces)

        for prefix, ns in _namespaces.items():
            graph.bind(prefix, ns)
