import csv
import particles
# import numpy as np

# function imports a csv file containing data about the pipe network to be simulated.
# skips first line (where header information is stored)
# loads data from each line into a list. creates a list of lists.
def load_csv(filename):
    with open(filename,"r") as file:
        csvfile = csv.reader(file,dialect="excel")
        start = 0
        rval = []
        for line in csvfile:
            # print("line: ", line)
            if start == 0:
                start = 1
                continue
            rval.append(line)
        return rval

# creates a pipe using the pipe data stored in the csv file. Note that at this point,
# each pipe is separate so parent and child pipes (connections) are filled with strings
def create_node(np, manager):
    node = None
    endpointStatus = False
    parent = np[4]
    width = float(np[2])
    length = float(np[3])
    name = np[0]
    isRoot = np[5]
    isEnd = np[6]
    d_inf = float(np[7])
    alpha = float(np[8])
    try:
        freeChlorineLambda = float(np[9])
    except: freeChlorineLambda = 0
    try: 
        kv1Lambda = float(np[10])
    except: kv1Lambda = 0
    try:
        kv2Lambda = float(np[11])
    except: kv2Lambda = 0
    try: 
        kv3Lambda = float(np[12])
    except: kv1Lambda = 0
    try:
        kv5Lambda = float(np[13])
    except: kv2Lambda = 0
    try: 
        kv7Lambda = float(np[14])
    except: kv1Lambda = 0
    try:
        doc1Lambda = float(np[15])
    except: kv3Lambda = 0   
    try: 
        doc2Lambda = float(np[16])
    except: doc2Lambda = 0

    if parent == "NONE" or isRoot == "TRUE":
        parent = None
    if isEnd == "TRUE":
        node = particles.endpoint(parent, name, manager)
        endpointStatus = True
    else:
        node = particles.pipe(name, length, width, np[1], parent, d_inf, alpha, manager, freeChlorineLambda, kv1Lambda, kv2Lambda, kv3Lambda, kv5Lambda, kv7Lambda, doc1Lambda, doc2Lambda)
    return node, endpointStatus

# this function performs a tree search beginning at the root on the network
# and searches for a pipe with the name defined in the parent field (as a string)
# and then inserts that node as a child of the parent node, and replaces the text
# string in the child node with a reference to the parent node, thus linking the
# new node into the tree structure.
def insert_node(root, new_node):
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

# This function is deprecated. Endpoints are now established in the model file, which makes it easier to
# write a presets file (since endpoint names are now user-defined).
# this function performs a recursive search through the pipe network and inserts
# special endpoint nodes at the end of each branch of the tree, then returns
# a list containing all the endpoints inserted.
def add_endpoints(root, list):
    if (len(root.children) < 1):
        newname = root.name + "-endpoint"
        end = root.create_end(newname)
        list.append(end)
    else:
        for child in root.children:
            add_endpoints(child,list)
    return list

# main driver function for the pipe network building module
# imports a filename of a csv that contains information about
# the pipe network to be built, and builds that network as a
# tree data structure.
def build(filename, man = None):
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
        # print("each: ", each)
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
        #print(success, node.name)
        if not success:
            message = "Error in file at" , node.name + ". Malformed pipes file. Aborting."
            print(message)
            return message
            # raise Exception
    # the file includes all pipes, but not control spigots.
    # the endpoints are added here, which provide a way to control each pipe fork.
    #endpoints = add_endpoints(root, [])
    # returns the root node (where particles are inserted) and a list containing the endpoint objects
    if man == None:
        return root, endpoints, manager, timer
    else:
        return root, endpoints

# this function loads a csv file with endpoint activations. the format of a recognized file
# is as follows: the first line contains headers (unused). the 2nd line contains the first
# endpoint activation instructions in the order of endpoint name, activation time, deactivation
# time, flow rate, and the maximum time the simulation should run (in seconds).
# succeeding lines contain the same information in the same order except they do not contain
# the max simulation time. each endpoint should only have one activation instruction for
# a given second, but you may set intervals with adjoining begin and end times if you
# wish to adjust the flow rate "midstream".
def load_sim_preset(filename):
    contents = load_csv(filename)
    firstline = True
    maxTime = 0
    endpointActivations = {}
    for line in contents:
        if firstline is True:
            firstline = False
            maxTime = line[4]
        if endpointActivations.get(line[0]) is None:
            endpointActivations[line[0]] = []
        name = line[0]
        start = float(line[1])
        end_by = float(line[2])
        flow_rate = float(line[3])
        endpointActivations[line[0]].append((start, end_by, flow_rate))
    for value in endpointActivations.values():
        #print(value)
        value.sort(key = lambda x: x[0])
        #print(value)
    #print(maxTime)
    maxTime = float(maxTime)
    return maxTime, endpointActivations

#load_sim_preset("PACCAR-kitchens-presets.csv")
