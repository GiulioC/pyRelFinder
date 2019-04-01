from relfinder import Relfinder
import relfinder_utils as relu
import html, pprint

source = 'Immanuel_Kant'
dest = 'Georg_Wilhelm_Friedrich_Hegel'
out_file = 'relations.csv'
ignored_props = ['22-rdf-syntax-ns#type', 'owl#sameAs', 'DUL.owl#NaturalPerson', 'owl#equivalentClass']

first = 'http://dbpedia.org/resource/{}'.format(source)
second = 'http://dbpedia.org/resource/{}'.format(dest)

rf = Relfinder()

maxDistance = 4

queries = rf.getQueries(first, second, maxDistance, 10, [], ['http://www.w3.org/1999/02/22-rdf-syntax-ns#type','http://www.w3.org/2004/02/skos/core#subject'], True)

path_count = 0
for distance in range (1,maxDistance+1):
    for query in queries[distance]:

        result = rf.executeSparqlQuery(query);
        paths = relu.parse_dbpedia_response(source, dest, result)

        relu.save_paths_to_file(paths, out_file, path_count, ignored_props)
        path_count += len(paths)
