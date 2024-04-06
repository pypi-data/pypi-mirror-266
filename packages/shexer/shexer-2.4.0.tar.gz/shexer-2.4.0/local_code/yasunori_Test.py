from shexer.consts import TURTLE, MIXED_INSTANCES
from shexer.shaper import Shaper
import sys
import argparse

def run(namespaces):

    #shaper = Shaper(graph_file_input='/proc/self/fd/0',
    shaper = Shaper(graph_file_input="test.ttl",
                    all_classes_mode=True,
                    input_format=TURTLE,
                    namespaces_dict=namespaces,
                    disable_exact_cardinality=True,
                    detect_minimal_iri=True,
                    instances_report_mode=MIXED_INSTANCES)

    print(shaper.shex_graph(string_output=True,
                      verbose=True,
                      acceptance_threshold=0.05))

    print("Done!")

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    # namespace-prefix pair to be used in the results
    namespaces_dict = {"http://purl.org/dc/terms/": "dc",
                       "http://rdfs.org/ns/void#": "void",
                       "http://www.w3.org/2001/XMLSchema#": "xsd",
                       "http://www.w3.org/1999/02/22-rdf-syntax-ns#": "rdf",
                       "http://xmlns.com/foaf/0.1/": "foaf",
                       "http://www.w3.org/2002/07/owl#": "owl",
                       "http://www.w3.org/2000/01/rdf-schema#": "rdfs",
                       "http://www.w3.org/2004/02/skos/core#": "skos",
                       }
    run(namespaces=namespaces_dict)