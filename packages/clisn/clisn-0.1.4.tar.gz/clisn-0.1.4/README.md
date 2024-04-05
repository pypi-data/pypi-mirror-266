# CLiSN <:books:>:sparkles:
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![PyPI version](https://badge.fury.io/py/clisn.svg)](https://badge.fury.io/py/clisn)

A collection of [RDFLib](https://rdflib.readthedocs.io/en/stable/) namespaces for the [Computational Literary Studies Infrastructure](https://clsinfra.io/) project.

## Requirements
* Python >=3.11

## Installation
```shell
pip install clisn
```

## Usage

### Namespaces
CLiSN provides `rdflib.Namespaces` for the CLSInfra project.

```python
from rdflib import Graph
from rdflib.namespace import RDF

from clisn import crm, crmcls, corpus_base

base_ns = corpus_base("SweDraCor")
attrassign_uri = base_ns["attrassign/1"]

triples = [
    (
        attrassign_uri,
        RDF.type,
        crm["E13_Attribute_Assignment"]
    ),
    (
        attrassign_uri,
        crm["P140_assigned_attribute_to"],
        base_ns["corpus"]
    ),
    (
        attrassign_uri,
        crm["P177_assigned_property_of_type"],
        crmcls["Z8_corpus_has_corpus_type"]
    )
]

graph = Graph()

for triple in triples:
    graph.add(triple)

print(graph.serialize())
```

Output:
```ttl
@prefix ns1: <http://www.cidoc-crm.org/cidoc-crm/> .

<https://swedracor.clscor.io/entity/attrassign/1> a ns1:E13_Attribute_Assignment ;
    ns1:P140_assigned_attribute_to <https://swedracor.clscor.io/entity/corpus> ;
    ns1:P177_assigned_property_of_type <https://clscor.io/ontologies/CRMcls/Z8_corpus_has_corpus_type> .
```


### NamespaceManager

`clisn` features a custom [NamespaceManager](https://rdflib.readthedocs.io/en/stable/apidocs/rdflib.namespace.html#rdflib.namespace.NamespaceManager) for CLSInfra namespaces.
This e.g. allows to easily generate a namespaced `rdflib.Graph` like so:

```python
from rdflib import Graph, URIRef, Literal
from clisn import CLSInfraNamespaceManager, crm

graph = Graph()
CLSInfraNamespaceManager(graph)

graph.add(
    (
        URIRef("https://subject.xyz/example/"),
        crm["p90_has_value"],
        Literal("some value")
    )
)

print(graph.serialize())
```

Output: 
```ttl
@prefix crm: <http://www.cidoc-crm.org/cidoc-crm/> .

<https://subject.xyz/example/> crm:p90_has_value "some value" .
```
