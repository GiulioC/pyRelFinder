def reorder_list(list, left):
    """In some cases paths coming from reconstruct_vars_order are not ordered,
    so they are ordered here

    e.g.
        ['of1', 'pf1', 'of2', 'pf2', 'pf3']
    instead of
        ['pf1', 'of1', 'pf2', 'of2', 'pf3']

    So they have to be reordered

    Parameters
    ----------
    list: list
        the list of objects and relations to be reordered
    left: boolean
        if True, handles left lists, else right lists

    Returns
    -------
    ordered list
    """

    print("reorder:", list)
    list_ord = []
    if left:
        prop = 'pf'
        obj = 'of'
    else:
        prop = 'ps'
        obj = 'os'
    cnt = 1
    list.remove(prop+str(cnt))
    list_ord.append(prop+str(cnt))
    while True:
        if len(list) == 0:
            return list_ord
        else:
            list.remove(obj+str(cnt))
            list_ord.append(obj+str(cnt))
            cnt += 1
            list.remove(prop+str(cnt))
            list_ord.append(prop+str(cnt))

def reconstruct_vars_order(var_list):
    """Reconstruct the correct left and right paths

    e.g.
        ['src', 'of1', 'pf1', 'of2', 'pf2', 'middle', 'pf3', 'ps1', 'dst']
    becomes:
        left: ['src', 'pf1', 'of1', 'pf2', 'of2', 'pf3', 'middle']
        right: ['dst', 'ps1', 'middle']

    Parameters
    ----------
    var_list: list
        the original list of objects and relations as returned by relfinder

    Returns
    -------
    left and right ordered lists
    """

    print(var_list)
    left = []
    right = []
    for elem in var_list[1:-1]:
        if elem[1] == 'f':
            left.append(elem)
        elif elem[1] == 's':
            right.append(elem)
        elif elem == 'middle':
            pass
    left = reorder_list(left, True)
    right = reorder_list(right, False)
    print("left:",left)
    print("right:", right)
    print("\n")
    left.insert(0,var_list[0])
    left.append('middle')
    right.insert(0,'middle')
    right.append(var_list[-1])
    right.reverse()
    return left, right

def split_list(list):
    """If src and dst are connected via a middle object, split the path into a
    left (from src to middle) and right (from dst to middle) path

    Parameters
    ----------
    list: list
        the original list of objects and relations as returned by relfinder

    Returns
    -------
    list of paths connecting scr and dst (either direct path or a left and right
    path through a middle object)
    """

    if 'middle' in list:
        return reconstruct_vars_order(list)
    else:
        return [list]

def compose_triple(triple_names, triple_values):
    """Creates a triple given the object (of/os) and properties names (pf/ps)
    and their corresponding value.

    e.g.
        ('of1', 'pf2', 'of2')
    becomes:
        ('Immanuel_Kant', 'influencedBy', 'Georg_Wilhelm_Friedrich_Hegel')

    Parameters
    ----------
    triple_names: list
        list of object and property keywords (of/os, pf/ps)
    triple_values: dict
        mapping of keywords to DBpedia uri values

    Returns
    -------
    the triple as s, p, o
    """

    try:
        s = triple_values[triple_names[0]]['value']
    except KeyError:
        s = triple_names[0]
    p = triple_values[triple_names[1]]['value']
    try:
        o = triple_values[triple_names[2]]['value']
    except KeyError:
        o = triple_names[2]
    return s, p, o

def parse_dbpedia_response(src, dst, response):
    """Parses the JSON response of the SPARQL query sent to the DBpedia endpoint.

    Parameters
    ----------
    src: str
        name of source entity
    dst: str
        name of destination entity
    response: dict
        JSON response

    Returns
    -------
    the list of paths connecting scr and dst. A path is a list of triples
    """

    var_list = response['head']['vars']
    var_list.insert(0, src)
    var_list.append(dst)

    path_lists = split_list(var_list)

    paths = []
    for path_values in response['results']['bindings']:
        path = []
        for list in path_lists:
            offset = 0
            offset_limit = len(list) - 3
            triples = []

            while offset <= offset_limit:
                path_step = list[offset:(offset+3)]
                subj, rel, obj = compose_triple(path_step, path_values)
                triples.append((subj, rel, obj))
                offset += 2

            path.extend(triples)
        paths.append(path)

    return paths

def save_paths_to_file(paths, file, num, ignore):
    """Save paths retrieved by relfinder to a tsv file.

    save format is:
        path_number \t s \t p \t o

    Parameters
    ----------
    paths: list
        list of paths connecting source and destination
    file: str
        destination file
    num: str
        current path number
    ignore: list
        list of properties to ignore. If a path contains at least one of these,
        it is not saved to file
    """

    with open(file, "a") as f:
        for path in paths:
            ignore_path = False
            path_string = ""
            for triple in path:
                if triple[1].split("/")[-1] in ignore:
                    ignore_path = True
                else:
                    path_string = path_string + str(num)+"\t"+str(triple[0])+"\t"+str(triple[1])+"\t"+str(triple[2])+"\n"
            if not ignore_path:
                f.write(path_string)
            num += 1
