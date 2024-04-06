from shexer.shaper import Shaper
from shexer.consts import TURTLE, SHACL_TURTLE

raw_graph = """
@prefix geo:   <http://www.opengis.net/ont/geosparql#> .
@prefix rr:    <http://www.w3.org/ns/r2rml#> .
@prefix cidoc: <http://erlangen-crm.org/current/> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix b2022: <https://ont.virtualtreasury.ie/ontology#> .
@prefix geom:  <http://data.ordnancesurvey.co.uk/ontology/geometry/> .


<https://kb.virtualtreasury.ie/geo/modern-townland/appellation-assignment/C_10_B_06_P_02_260322_DALKEY>
        a                    cidoc:E13_Attribute_Assignment ;
        cidoc:P140_assigned_attribute_to
                <https://kb.virtualtreasury.ie/geo/modern-townland/C_10_B_06_P_02_260322_DALKEY> ;
        cidoc:P141_assigned  <https://kb.virtualtreasury.ie/geo/modern-townland/appellation/C_10_B_06_P_02_260322_DALKEY> ;
        cidoc:P2_has_type    b2022:AppellationAssignment .




"""

shaper = Shaper(
    # graph_file_input="/home/beyza/dalkey-geo-example.ttl",
    raw_graph=raw_graph,
    all_classes_mode=True,
    input_format=TURTLE)
str_result = shaper.shex_graph(string_output=True, output_format=SHACL_TURTLE)
print(str_result)
