from shexer.shaper import Shaper
from shexer.consts import NT, MIXED_INSTANCES

namespaces = {
    "http://purl.org/dc/terms/" : "dc",
    "http://rdfs.org/ns/void#" : "void",
    "http://www.w3.org/2001/XMLSchema#" : "xsd",
    "http://www.w3.org/1999/02/22-rdf-syntax-ns#" : "rdf",
    "http://purl.org/pav/" : "pav",
    "http://www.w3.org/ns/dcat#" : "dcat",
    "http://xmlns.com/foaf/0.1/" : "foaf",
    "http://www.w3.org/2002/07/owl#" : "owl",
    "http://www.w3.org/2000/01/rdf-schema#": "rdfs",
    "http://www.w3.org/2004/02/skos/core#" : "skos"
}



######################

file_endings = [
"xaaaaaa", "xaaaaab", "xaaaaac", "xaaaaad", "xaaaaae", "xaaaaaf", "xaaaaag", "xaaaaah", "xaaaaai",
    "xaaaaaj", "xaaaaak", "xaaaaal", "xaaaaam", "xaaaaan", "xaaaaao", "xaaaaap", "xaaaaaq", "xaaaaar",
    "xaaaaas", "xaaaaat", "xaaaaau", "xaaaaav", "xaaaaaw", "xaaaaax", "xaaaaay", "xaaaaaz", "xaaaaba",
    "xaaaabb", "xaaaabc", "xaaaabd", "xaaaabe", "xaaaabf", "xaaaabg", "xaaaabh", "xaaaabi", "xaaaabj",
    "xaaaabk", "xaaaabl", "xaaaabm", "xaaaabn", "xaaaabo", "xaaaabp", "xaaaabq", "xaaaabr", "xaaaabs",
    "xaaaabt", "xaaaabu", "xaaaabv", "xaaaabw", "xaaaabx", "xaaaaby", "xaaaabz", "xaaaaca", "xaaaacb",
    "xaaaacc", "xaaaacd", "xaaaace", "xaaaacf", "xaaaacg", "xaaaach", "xaaaaci", "xaaaacj", "xaaaack",
    "xaaaacl", "xaaaacm", "xaaaacn", "xaaaaco", "xaaaacp", "xaaaacq", "xaaaacr", "xaaaacs", "xaaaact",
    "xaaaacu", "xaaaacv", "xaaaacw", "xaaaacx", "xaaaacy", "xaaaacz", "xaaaada", "xaaaadb", "xaaaadc",
    "xaaaadd", "xaaaade", "xaaaadf" ]

for an_ending in file_endings:
    shaper = Shaper(all_classes_mode=True,
                    graph_file_input=r"C:\Users\Dani\Documents\datasets\uniprotkb_reviewed_eukaryota_opisthokonta_metazoa_33208_0.rdf\split\{}".format(an_ending),
                    input_format=NT,
                    namespaces_dict=namespaces,
                    instances_report_mode=MIXED_INSTANCES,
                    )
    shaper.shex_graph(output_file=r"C:\Users\Dani\Documents\datasets\uniprotkb_reviewed_eukaryota_opisthokonta_metazoa_33208_0.rdf\split\resulteukaryota_{}.shex".format(an_ending),
                      verbose=True
                      )
    print("Done {}".format(an_ending))
print("Ultra done!!!")

shaper = Shaper(all_classes_mode=True,
                graph_file_input=r"C:\Users\Dani\Documents\datasets\uniprotkb_reviewed_eukaryota_opisthokonta_metazoa_33208_0.rdf\partial_uniprot.nt",
                input_format=NT,
                namespaces_dict=namespaces,
                instances_report_mode=MIXED_INSTANCES
                )

shaper.shex_graph(output_file="eukariota_single_file.shex", verbose=True)
print("Done!")

