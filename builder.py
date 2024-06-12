"""
This module contains functions that build a pipe network from a csv file.
"""

import csv
import particles

def load_csv(filename):
    """
    Function imports a csv file containing data about the pipe network to be simulated.
    skips first line (where header information is stored)
    loads data from each line into a list. creates a list of lists.

    :param filename: name of csv file to be imported
    :return: list of lists containing data from csv file
    """

    with open(filename,"r") as file:
        csvfile = csv.reader(file,dialect="excel")
        start = 0
        rval = []
        for line in csvfile:
            if start == 0:
                start = 1
                continue
            rval.append(line)
        return rval

def create_node(np, manager):
    """
    Creates a pipe using the pipe data stored in the csv file. Note that at this point,
    each pipe is separate so parent and child pipes (connections) are filled with strings

    :param np: list containing data about a pipe
    :param manager: particle manager object
    :return: pipe object, boolean indicating whether the pipe is an endpoint
    """

    node = None
    endpoint_status = False
    parent = np[4]
    width = float(np[2])
    length = float(np[3])
    name = np[0]
    is_root = np[5]
    isEnd = np[6]
    d_inf = float(np[7])
    alpha = float(np[8])
    try:
        free_chlorine_lambda = float(np[9])
    except: free_chlorine_lambda = 0
    try: 
        kv1_lambda = float(np[10])
    except: kv1_lambda = 0
    try:
        kv2_lambda = float(np[11])
    except: kv2_lambda = 0
    try: 
        kv3_lambda = float(np[12])
    except: kv3_lambda = 0
    try:
        kv5_lambda = float(np[13])
    except: kv5_lambda = 0
    try: 
        kv7_lambda = float(np[14])
    except: kv7_lambda = 0
    try:
        doc1_lambda = float(np[15])
    except: doc1_lambda = 0   
    try: 
        doc2_lambda = float(np[16])
    except: doc2_lambda = 0

    if parent == "NONE" or is_root == "TRUE":
        parent = None
    if isEnd == "TRUE":
        node = particles.Endpoint(parent, name, manager)
        endpoint_status = True
    else:
        node = particles.Pipe(name, length, width, np[1], parent, d_inf, alpha, manager, free_chlorine_lambda, kv1_lambda, kv2_lambda, kv3_lambda, kv5_lambda, kv7_lambda, doc1_lambda, doc2_lambda)
    return node, endpoint_status

def insert_node(root, new_node):
    """
    This function performs a tree search beginning at the root on the network
    and searches for a pipe with the name defined in the parent field (as a string)
    and then inserts that node as a child of the parent node, and replaces the text
    string in the child node with a reference to the parent node, thus linking the
    new node into the tree structure.

    :param root: root node of the tree
    :param new_node: node to be inserted into the tree
    :return: boolean indicating whether the node was successfully inserted
    """

    rval = False
    if root == None:
        root = new_node
        return True
    elif root.name == new_node.parent:
        new_node.parent = root
        root.children.append(new_node)
        return True
    for child in root.children:
        result = insert_node(child,new_node)
        if result == True:
            rval = True
            break
        else:
            continue
    return rval

def add_endpoints(root, list):
    """
    This function is deprecated. Endpoints are now established in the model file, which makes it easier to
    write a presets file (since endpoint names are now user-defined).
    this function performs a recursive search through the pipe network and inserts
    special endpoint nodes at the end of each branch of the tree, then returns
    a list containing all the endpoints inserted.

    :param root: root node of the tree
    :param list: list of endpoints
    :return: list of endpoints
    """

    if (len(root.children) < 1):
        newname = root.name + "-endpoint"
        end = root.create_end(newname)
        list.append(end)
    else:
        for child in root.children:
            add_endpoints(child,list)
    return list

def build(filename, man = None):
    """
    Main driver function for the pipe network building module
    imports a filename of a csv that contains information about
    the pipe network to be built, and builds that network as a
    tree data structure.

    :param filename: name of csv file containing pipe network data
    :param man: particle manager object
    :return: root node of the tree, list of endpoints
    """
    if man == None:
        timer = particles.counter()
        manager = particles.ParticleManager(timer)
    else:
        manager = man
    contents = load_csv(filename)
    root = None
    endpoints = []
    type = None
    for each in contents:
        # the first node in the file is created as the root node
        if root == None:
            root, type = create_node(each, manager)
            continue
        node, type = create_node(each, manager)
        if type == True:
            endpoints.append(node)

        # this is where pipes are joined together. Note that failure to join
        # a pipe will cause the program to fail.
        success = insert_node(root, node)
        if not success:
            message = "Error in file at" , node.name + ". Malformed pipes file. Aborting."
            print(message)
            return message
        
    # the file includes all pipes, but not control spigots.
    # the endpoints are added here, which provide a way to control each pipe fork.
    #endpoints = add_endpoints(root, [])
    # returns the root node (where particles are inserted) and a list containing the endpoint objects
    if man == None:
        return root, endpoints, manager, timer
    else:
        return root, endpoints

def load_sim_preset(filename):
    """
    This function loads a csv file with endpoint activations. the format of a recognized file
    is as follows: the first line contains headers (unused). the 2nd line contains the first
    endpoint activation instructions in the order of endpoint name, activation time, deactivation
    time, flow rate, and the maximum time the simulation should run (in seconds).
    succeeding lines contain the same information in the same order except they do not contain
    the max simulation time. each endpoint should only have one activation instruction for
    a given second, but you may set intervals with adjoining begin and end times if you
    wish to adjust the flow rate "midstream".

    :param filename: name of csv file containing endpoint activation instructions
    :return: max simulation time (in seconds), dictionary containing endpoint activation instructions
    """

    contents = load_csv(filename)
    firstline = True
    max_time = 0
    endpoint_activations = {}
    for line in contents:
        if firstline is True:
            firstline = False
            max_time = line[4]
        if endpoint_activations.get(line[0]) is None:
            endpoint_activations[line[0]] = []
        name = line[0]
        start = float(line[1])
        end_by = float(line[2])
        flow_rate = float(line[3])
        endpoint_activations[line[0]].append((start, end_by, flow_rate))

    for value in endpoint_activations.values():
        value.sort(key = lambda x: x[0])

    # max_time = float(max_time)
    time_split = max_time.split(":")

    try : 
        max_time = int(time_split[0]) * 60 + int(time_split[1])
    except:
        max_time = int(time_split[0]) * 60

    return max_time, endpoint_activations
