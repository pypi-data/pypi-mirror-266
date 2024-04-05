"""Namespaces for CLSInfra."""

import sys

from rdflib import Graph, Namespace


# namespaces
crm = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
crmcls = Namespace("https://clscor.io/ontologies/CRMcls/")
clscore = Namespace("https://clscor.io/entity/")

frbroo = Namespace("http://iflastandards.info/ns/fr/frbr/frbroo/")
crmdig = Namespace("http://www.ics.forth.gr/isl/CRMdig/")
lrm = Namespace("http://iflastandards.info/ns/lrm/lrmoo/")
pem = Namespace("http://parthenos.d4science.org/CRMext/CRMpe.rdfs")


def corpus_base(corpus_key: str) -> Namespace:
    """Generate a corpus base URI given a corpus_key (the corpus acronym).

    Pattern: https://{corpus_key}.clscor.io/entity/{entity-type}/{hash-id}.
    """
    corpus_key = corpus_key.lower()

    return Namespace(f"https://{corpus_key}.clscor.io/entity/")
