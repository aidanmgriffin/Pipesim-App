#1/23 todo: calculate histogram for all particles.


import numpy as np
import math
import copy
import random
from multiprocessing import cpu_count
import ete3
from ete3.treeview.faces import AttrFace
from multiprocessing import Lock
import multiprocessing as mp
from multiprocessing import Pool, Process
from multiprocessing.pool import ThreadPool
import threading
import time
import collections
import csv

# test log file
logfile = "ParticleDiffusion.log"
logfile = open(logfile, 'a')

# test single particle log
particlelogfile = "SingleParticle.csv"
particlelogfile = open(particlelogfile, 'a')
writer = csv.writer(particlelogfile, 'excel')
# writer.writerow(["ParticleID", "Modifier"])

pipeIndex: dict = {}  # this stores all the pipes in the pipe system. pipes can be accessed by name, which must be unique.
random.seed(a=None, version=float)
  # minute/timestep. 60 = 1 sec. we assume that input rates are "gallons per minute" units, but we
CUBIC_INCHES_PER_GALLON = 231

# this is intended to be used as a static class to count the passage of time
# within the simulation environment. this was implemented so that
# the time value could be accessed more easily across modules (files).
class counter:
    t = 0
    @staticmethod
    def get_time():
        return counter.t
    @staticmethod
    def increment_time():
        counter.t += 1
    @staticmethod
    def reset():
        counter.t = 0

class ParticleManager():
    def __init__(self, time):
        # global variables to track number of particles generated. Each particle is given a unique particle ID based on this number.
        # it should not be decremented if we want an accurate count of the number of particles generated. Note it is redundant
        # to create more than one particle per second at the root.
        self.numParticles: int = 0
        # deletedparticles counts the number of particles that have been garbage collected.
        self.deletedParticles: int = 0
        # elapsedTime: int = 0  # time unit? assuming seconds.
        # want to calculate one second intervals.
        self.particleIndex: dict = {}  # this stores all the particles in the pipe system. Particle objects can be accessed by ID.
        self.expendedParticles: dict = {}  # stores all particles that have passed through an endpoint, for data collection.
        self.expelledParticleData: dict = {} # stores data about which particles were expelled from which endpoints and
        self.particlePositions: dict = {} # stores lists of which particles are in which pipes. keys are pipe names.
        self.pipeAggregates: dict = {} # stores details about the particles in each pipe in a tuple of the following
                                       # form: (min_age, max_age, average_age, num_particles). Keys are pipe names.
        self.diffusionActive = False
        self.time = time
        self.time.reset()
        self.tolerance = math.pow(2, -16)
        self.process_max = cpu_count()
        self.timeStep: int = 60
        self.diffusionCoefficient: float = 0 #stores diffusion coefficient.

        self.bins = []

        #self.pool = cf.ProcessPoolExecutor(max_workers = self.process_max)

    #creates a particle that is registered to the particle manager and
    def particle(self, container):
        return Particle(container, self)

    def setTimeStep(self, step: int):
            self.timeStep = step

    def update_caller(self, particle):
        name, part = particle.update()
        #rval.append((name, part))
        return name, part

    # def diffusionVars(self, diffusionCoefficient):
    #     self.diffusionCoefficient = diffusionCoefficient
    #     return diffusionCoefficient

    # updates particle age data, particle positions, and aggregate particle data for particles in each pipe (every 1000 tics)
    def update_particles(self):
        #pool = Pool(processes = cpu_count())
        index = self.particleIndex.copy()
        particles = list(index.values())
        #start = time.time()
        # the following line is slow or deadlocks
        #particlePositions = self.pool.map(self.update_caller, particles)
        # the following line is fast
        rval = map(self.update_caller, particles)

        #elapsed = time.time()
        #elapsed = elapsed - start
        #print("particle updates completed in ", elapsed, "seconds.")
        #pool.close()
        #pool.join()
        self.particlePositions = self.particle_update_helper(rval)
        if self.time.get_time() % 1000 == 999:
            self.update_particle_info()

    # an assistant function for the update_particles function that helps to assign particles to the correct list
    # within the pipe dictionary (or creates a new list if the correct dictionary entry does not exist)
    def particle_update_helper(self, particlePositions):
        dic = {}
        for key, value in particlePositions:
            if dic.get(key) is None:
                dic[key] = [value]
            else:
                dic[key].append(value)
        return dic

    # each pipe tracks particles that are inside it and tracks their progress along it.
    # this function is meant to be called by the root pipe. fills pipe with particles
    # with one particle every 0.1 inches.
    def add_particles(self, density: float, root):
        particles = self.particlePositions.get(root.name)
        if particles == None:
            self.particlePositions[root.name] = particles = []
        if len(particles) < 1:
            min_distance = root.length
        else:
            min_distance = min(part.position for part in particles)
        current_distance = 0
        while current_distance < min_distance + density:
            part = self.particle(root)
            part.position = current_distance
            current_distance += density

    # generates aggregate data about particles by pipe membership and assigns it to the pipeAggregates dictionary.
    def update_particle_info(self):
        for pipeName in self.particlePositions.keys():
            contents = self.particlePositions.get(pipeName)
            ages = self.particle_age_builder(contents)
            min_age, max_age, average_age = self.particle_age_calculator(ages)
            num_particles = len(ages)
            self.pipeAggregates[pipeName] = (min_age, max_age, average_age, num_particles)

    # builds a list with the age values of particles given a list of them.
    def particle_age_builder(self, particles):
        ages = [x.age for x in particles]
        return ages

    # calculates minimum, maximum, and average age values given a list of particle ages.
    def particle_age_calculator(self, input):
        minimum = 0
        maximum = 0
        avg = 0
        if len(input) > 0:
            minimum = min(input)
            maximum = max(input)
            avg = sum(input) / len(input)
            avg = float(f"{avg:0.4f}")
        return minimum, maximum, avg

    def output_status(self):
        return self.pipeAggregates

# the particle class tracks what happens when water flows through the pipe network. Each particle stores information
# about the pipes it travels through and about how long it remains in contact with each pipe.
class Particle:
    # this constructor requires a container (pipe object) to instantiate, because particles should always be tied to one
    # pipe. upon creation, the particle assigns itself an id based on the global numParticles variable, adds itself to
    # the particle dictionary, stores it's parent object, and sets it's age at 0.
    def __init__(self, container, manager):
        self.manager = manager
        self.ID: int = self.manager.numParticles
        self.manager.numParticles += 1
        self.contact: dict = {container.material: 0} # contact stores the number of seconds the particle has been in
        # contact with each material it has touched, starting at 0.
        self.container: pipe = container  # records current parent container
        self.position: float = 0 # stores particle position within pipe
        self.sumDistance: float = 0 # stores total distance travelled by particle
        self.route: list = [container.name]
        self.age: int = 0
        self.freechlorine: float = 1.0 #for now this is starting concentration
        self.manager.particleIndex[self.ID] = self

    # the update function increments the particle age and increments contact record according to the current container
    # material type. If the particle container is active (flowing) then calls the movement function to compute particle flow.
    def update(self):
        self.age += 1
        timeStep = self.manager.timeStep
        #lambda will change depending on the pipe it is in (area and material)
        #eventually display graph of the concentration and later density in each pipe
        lamb = 0.1 #see comments above about changing
        containerName = self.container.name

        selectedParticle = None
        if selectedParticle != None:
            if self.ID == selectedParticle:
                print('Particle:' ,str(selectedParticle), ' : ' ,containerName, ' : ', self.container.material, ' : ', self.container.area, ' : ', str(self.age), ' : ', str(self.freechlorine))
        # print(containerName, ' : ', self.container.material, ' : ', self.container.area)


        #Switch cases for different lambdas
        #access to container. (area, length, type, and more)
        # if containerName == "Pipe1":
        #     lamb = 0.1

        self.freechlorine = self.freechlorine * math.exp(-lamb*timeStep) 
        #For Free chlorine decay:
        #Get the Time Granularity for Delta T
        #Use rate of decay
        #Cnew = self.freechlorine
        #Use function Cnew = Cold * exp(-rate*deltaT)
        #update the freechlorine (self.freechlorine = Cnew)
        #if self.manager.time.get_time() > 999:
            #print("time")
        if (self.contact.get(self.container.material) is not None):
            self.contact[self.container.material] += 1
        elif(self.contact.get(self.container.material) is None):
            self.contact.update({self.container.material: 0})
            self.contact[self.container.material] += 1
            
        if self.route.count(self.container.name) < 1:
            self.route.append(self.container.name)
            # Originally checks if container is active (water is flowing) before checking diffusion value. With issue 165
            # this is reversed. If diffusion is active then dispersion function will be called in lieu of movement. 
            # (The two are similar, but dispersion includes diffusive activity.)


        if self.manager.diffusionActive:
            if self.container.isActive:
                containerName = self.disperse()
            else:
                containerName = self.diffuse()

        elif self.container.isActive:
            containerName = self.movement()
        return containerName, self

    # The particle movement code is really the heart of this entire application. Everything depends on this being accurate and
    # performant because scientific results are drawn from how and when particles traverse the network. This function
    # is intended to simulate how a particle might be carried along with a stream of water and updates the particle according
    # to how much flow should occur within a given time segment. Every particle traveling through the network will call
    # this function every time-step that it flows down the network.
    def movement(self):
        remainingTime = 1
        containerName = self.container.name
        while remainingTime > self.manager.tolerance:  # calculate particle movement until flow consumes available time (1 second)
            if self.container.type != "endpoint":
                flow = self.container.flow * remainingTime
                position = self.position
                newPosition = (flow * (CUBIC_INCHES_PER_GALLON / self.container.area)) + position
                if newPosition > self.container.length:
                    # travelledDistance = newPosition - self.container.length
                    travelledDistance = self.container.length - self.position
                    partialFlow = remainingTime * (travelledDistance / CUBIC_INCHES_PER_GALLON) * self.container.area
                    elapsedTime = partialFlow / flow
                    remainingTime = remainingTime - elapsedTime
                else:
                    travelledDistance = newPosition - position
                    remainingTime = 0
                    self.position = newPosition
                self.sumDistance += travelledDistance
                if remainingTime > 0:
                    self.container = self.container.select_child()
                    self.position = 0
                    containerName = self.container.name
                # print("updating particle", self.ID, "in pipe", self.container.name)
            elif self.container.type == "endpoint":
                # print("expelling particle", self.ID, "from pipe", self.container.name)
                particleInfo = []
                time = self.manager.time.get_time()
                particleInfo.append(time)
                expelledTime = self.age + (1 - remainingTime)
                self.age = expelledTime
                # print(expelledTime)
                particleInfo.append(self.age)
                particleInfo.append(self.freechlorine)
                particleInfo.append(self.ID)
                if self.manager.expelledParticleData.get(self.container.name) is None:
                    self.manager.expelledParticleData[self.container.name] = []
                dataset = self.manager.expelledParticleData.get(self.container.name)
                dataset.append(particleInfo)
                self.manager.particleIndex.pop(self.ID)
                self.manager.expendedParticles[self.ID] = self
                containerName = None
                break
        return containerName

    # diffusion math is very tricky because it depends on the strength of the concentration gradient, on the current
    # temperature, and on the types of liquids involved. For simplicity, some assumptions have been made. If needed,
    # this function could be expanded in future to take in some of the data mentioned above. For now, assumptions are
    # made.
    def diffuse(self):

        global logfile
        
        # diffusion rate is 8.28 * 10^-4 cm^2/min or 2.14 * 10^-6 in^2 / sec uses an assumption of 20 degrees Celsius for free chlorine in water. 
        # diffusion_rate = 2.14 * math.pow(10, -6) 
        try:
            diffusion_rate = self.manager.diffusionCoefficient
        except:
            diffusion_rate = 2.14 * math.pow(10, -6) 

        avg_distance = 4 * self.manager.timeStep * diffusion_rate
        # initialize with a random seed for added randomness
        generator = random.Random()
        standard_dev = math.sqrt(avg_distance)
        modifier = generator.normalvariate(mu=0.0, sigma=standard_dev)
        movement = modifier
        logfile.write("Calculating diffusion for particle " + str(self.ID) + " in pipe " + self.container.name + " of length " + str(self.container.length) + " from position " + str(self.position) + " with modifier: " + str(modifier) + "\n")
        position = self.position
        newPosition = position + movement

        if newPosition < 0:
            remainingMovement = newPosition
            while remainingMovement < 0:
                newContainer = self.container.parent
                if newContainer == None:
                    logfile.write(str(self.ID) + " bumped into the root!\n")
                    self.position = 0
                    break
                else:
                    newPosition = self.container.length + remainingMovement
                if newPosition < 0:  # movement direction is upstream (movement is negative, position is negative)
                    remainingMovement = newPosition
                    self.position = 0
                else:
                    remainingMovement = 0
                    self.position = newPosition
        elif newPosition > self.container.length:
            remainingMovement = newPosition - self.container.length
            while remainingMovement > 0:
                newContainer = self.select_random_child()
                if newContainer == None:
                    logfile.write(str(self.ID) + " bumped into an endpoint!\n")
                    self.position = self.container.length
                    break
                else:
                    newPosition = 0 + remainingMovement
                if newPosition > self.container.length:
                    remainingMovement = newPosition - self.container.length
                    self.position = self.container.length
                else:
                    remainingMovement = 0
                    self.position = newPosition
        else: self.position = newPosition
        
        return self.container.name

#Advection, diffusion-dispersion during flow events.
    def disperse(self):
        global writer
        global logfile
        remainingTime = 1
        containerName = self.container.name
        while remainingTime > self.manager.tolerance:  # calculate particle movement until flow consumes available time (1 second)
            if self.container.type != "endpoint":

                flow = self.container.flow * remainingTime

                diffusion_rate = self.manager.diffusionCoefficient
                avg_distance = 4 * self.manager.timeStep * diffusion_rate
                # initialize with a random seed for added randomness
                generator = random.Random()
                standard_dev = math.sqrt(avg_distance)
                modifier = generator.normalvariate(mu=0.0, sigma=standard_dev)
                position = self.position + modifier
                newPosition = (flow * (CUBIC_INCHES_PER_GALLON / self.container.area)) + position

                if newPosition > self.container.length:
                    # travelledDistance = newPosition - self.container.length
                    travelledDistance = self.container.length - self.position
                    partialFlow = remainingTime * (travelledDistance / CUBIC_INCHES_PER_GALLON) * self.container.area
                    elapsedTime = partialFlow / flow
                    remainingTime = remainingTime - elapsedTime

                else:
                    travelledDistance = newPosition - position
                    remainingTime = 0
                    self.position = newPosition
                self.sumDistance += travelledDistance
                if remainingTime > 0:
                    self.container = self.container.select_child()
                    self.position = 0 
                    containerName = self.container.name
                

                logfile.write("updating particle" + str(self.ID) + "in pipe" + str(self.container.name) + "\n")
            elif self.container.type == "endpoint":
                logfile.write("expelling particle" + str(self.ID) + "from pipe" + str(self.container.name) + "\n")
                particleInfo = []
                time = self.manager.time.get_time()
                particleInfo.append(time)
                expelledTime = self.age + (1 - remainingTime)
                self.age = expelledTime
                # print(expelledTime)
                particleInfo.append(self.age)
                particleInfo.append(self.freechlorine)
                particleInfo.append(self.ID)
                if self.manager.expelledParticleData.get(self.container.name) is None:
                    self.manager.expelledParticleData[self.container.name] = []
                dataset = self.manager.expelledParticleData.get(self.container.name)
                dataset.append(particleInfo)
                self.manager.particleIndex.pop(self.ID)
                self.manager.expendedParticles[self.ID] = self
                containerName = None
                
                # logfile.write("Calculating dispersion for particle " + str(self.ID) + " at time " + str(expelledTime) + " from position " + str(self.position) + " with modifier: " + str(modifier) + " to new position " + str(newPosition) + "\n")

                break

            
        
        if self.ID == 0:
            writer.writerow([self.ID, position, modifier])
            self.manager.bins.append(modifier)
               
        return containerName

    # function to select random children of pipes. Note that the functionality is different than the pipe
    # select_child function because this can select active or inactive pipes but will not select endpoints.
    # the assumption here is that this function is called by diffuse function, which in turn only activates on
    # inactive pipes. thus downstream endpoints should be "off" and allowing particles to enter the endpoint
    # would be like simulating a leaky faucet.
    def select_random_child(self):
        selected = False
        # choices = copy(self.container.children)
        choices = self.container.children.copy()
        # print("choices: ", choices)
        
        while not selected:
            if len(choices) < 1:
                return None
            selection = random.choice(choices)
            if selection.type == "endpoint":
                if len(choices) == 1:
                    return None
                else:
                    choices.remove(selection)
                    continue
            else:
                return selection





    # this function can create a deep copy of a particle object, but assigns it a new unique particle id.
    # this is used when particles arrive at a fork with two active (flowing) pipes, a duplicate should be made
    # to simulate water traveling down both pipes.
    def __copy__(self, container):
        global numParticles
        p = Particle(container)
        p.ID = self.manager.numParticles
        p.contact = copy.deepcopy(self.contact)
        p.age = self.age
        self.manager.numParticles += 1
        self.manager.particleIndex[p.ID] = p
        p.route = copy.deepcopy(self.route)
        return p

    # this function deletes the particle and increments the deletedparticles count.
    def __del__(self):
        self.manager.deletedParticles += 1
        #print('lifetime: ' + str(self.age))
        #for each in self.contact:
        #    print('contacted materials: ' + each + " " + str(self.contact[each]))
        # particleIndex.pop(self.ID)
        # numParticles -= 1 # cannot decrement numParticles because this will create duplicate particle IDs

    # getOutput returns a tuple that contains the data stored in the particle. can be used to read out at the end
    # of the particle's journey, or query along the way for testing.
    def getOutput(self):
        keys = self.contact.keys()
        values = self.contact.values()
        rval = [self.ID, self.age, self.container.name]
        for key in keys:
            rval.append(key)
            rval.append(self.contact[key])
        for elem in self.route:
            rval.append(elem)
        return rval

    # prints details about the particle. included for testing purposes. Not used.
    def print_part(self):
        tup = self.getOutput()
        output = ""
        for each in tup:
            output = output + " | " + str(each)
        print(output)

# the pipe class is basically a tree data structure, but it is an n-way tree. on top of that, each pipe has properties
# necessary for plumbing, such as a diameter, material type, length, diameter, cross-sectional-area (CSA) and an activated
# flag. this last one is used to track whether the pipe is part of a series of pipes that are currently flowing, or
# whether it contains stagnant water.
class pipe:

    # the constructor takes in the pipe name, dimensions, and parent.
    def __init__(self, name, length, width, material, parent, manager):
        global pipeIndex
        self.manager = manager
        self.name = name
        self.length: float = length * 12
        self.width: float = width # in inches
        self.radius = self.width / 2
        self.material: str = material
        self.parent: pipe = parent
        self.area: float = np.pi * math.pow((self.radius), 2) #cross-sectional-area
        self.children: list[pipe] = []
        self.isActive = False
        self.activity = 0
        self.type = "pipe"
        self.flowRate: int = 0  # gallons per minute
        self.flow: np.long = 0  # gallons per time unit
        pipeIndex[self.name] = self
        # pipe no longer tracks member particles
        #self.particles: dict = {} #particle id = position
        #self.average_age = 0
        #self.min_age = 0
        #self.max_age = 0
    # to create a root, initialize with parent = None.

    # function to track activations for a pipe. if activity is positive,
    # one or more endpoints downstream from this pipe are active (flowing)
    # so this pipe contains flowing water.
    def activate(self):
        self.activity += 1
        self.set_activity()

    # does not actually deactivate the pipe, but decrements activity when
    # an endpoint is shut off.
    def deactivate(self):
        self.activity -= 1
        self.set_activity()

    # if activity is nonpositive, deactivates pipe (no downstream endpoints are flowing).
    # pipe contains stagnant water.
    def set_activity(self):
        if self.activity > 0:
            self.isActive = True
        else:
            self.isActive = False

    # this function is used by the builder. creates a pipe and inserts it as a child
    # of the parent pipe, with this pipe as the parent of the child pipe.
    def create_child(self,name,length,diameter,material):
        p = pipe(name,length,diameter,material,self)
        self.children.append(p)
        return p

    # this function is used by the builder to create an endpoint as a child the current pipe object.
    def create_end(self, name):
        p = endpoint(self, name)
        self.children.append(p)
        return p

    # this function randomly selects from available active child pipes and returns the selected child.
    # used to randomly assign particle paths at branches down the pipe, but only along branches with
    # active flow.
    def select_child(self):
        selected = None
        candidates = []
        for child in self.children:
            if child.isActive:
                candidates.append(child)
        if len(candidates) > 0:
            selected = random.choice(candidates)
            #selected.lock.acquire()
        return selected

    # compiles a list where each node reports it's depth in the tree, returns that list.
    def peek_helper(self, dim, depth):
        dim.append(depth)
        for each in self.children:
            each.peek_helper(dim, depth + 1)
        return dim

    # returns the depth of the tree, and the maximum number of nodes at the same depth.
    # used for establishing the size of the grid to lay out the graph on.
    def peek_children(self):
        if self.parent != None:
            return self.parent.peek_children()
        dim = []
        dim = self.peek_helper(dim, 0)
        data = collections.Counter(dim)
        height = data.most_common(1)[0][1] # most_common returns a tuple with (mode, frequency)
        depth = max(dim)
        return depth, height

    # this function creates and returns an ete3 tree based on the current pipes model. the ete3 tree is used to
    # create a graphical representation of the model.
    def generate_tree(self):
        return self.tree_builder(self)

    # the tree_builder function does the actual creation of the ete3 tree. It recursively explores the current pipe
    # model and transcribes relevant properties of the model into new ete3 tree nodes and inserts them into the
    # representative model.
    def tree_builder(self, root):
        t = ete3.Tree()
        style = ete3.NodeStyle()
        style["size"] = int(max(self.width*5,10))
        style["fgcolor"] = "#3f7c00"
        style["shape"] = "sphere"
        style["vt_line_type"] = 0
        style["hz_line_type"] = 0
        style.show_branch_length=True
        style.show_leaf_name=False
        t.add_feature("num_particles", 0)
        t.add_feature("avg_age", 0)
        t.add_feature("max_age", 0)
        t.add_feature("min_age", 0)
        t.add_feature("length",root.length)
        t.add_feature("active", 0)
        t.set_style(style)
        self.tree_helper(t, root.children)
        return t

    # the tree_helper class performs the recursive exploration of the pipes model for tree_builder. It also adds more
    # properties to each node and creates differentiation between endpoints and non-endpoints. Note that ete3 tree nodes
    # inherit properties from parent nodes, which is why some properties are set by tree_builder (these apply to the
    # entire tree) and more are set by tree_helper. These apply to individual nodes. Tree_helper inserts data about
    # each pipe in the pipe model into the node data, but also assists with creating the first layer of layout data
    # (formatting). the layout data is later augmented just before rendering so that it can reflect the current state
    # of the model.
    def tree_helper(self, tree, iterable):
        if iterable is not None:
            for each in iterable:
                if each is not None:
                    child = tree.add_child(name=each.name)
                    child.dist = each.length
                    style = ete3.NodeStyle()
                    if each.type != "endpoint":
                        self.tree_helper(child, each.children)
                        style["fgcolor"] = "#3f7c00"
                    else:
                        style["fgcolor"] = "#f9dc00"
                        label = AttrFace("name")
                        label.margin_top=1
                        label.margin_bottom=1
                        label.margin_left=1
                        label.margin_right=1
                        label.fsize=6
                        label.fgcolor="blue"
                        child.add_face(label, column=2, position="branch-right")
                    style["shape"] = "circle"
                    style["size"] = int(max(each.width*5,10))
                    style["vt_line_type"] = 0
                    style["hz_line_type"] = 0
                    child.add_feature("num_particles", 0)
                    child.add_feature("avg_age", 0)
                    child.add_feature("max_age", 0)
                    child.add_feature("min_age", 0)
                    child.add_feature("length", each.length)
                    child.add_feature("active",0)
                    active = AttrFace("active")
                    active.margin_top = 1
                    active.margin_bottom = 1
                    active.margin_left = 1
                    active.margin_right = 1
                    active.fsize = 6
                    active.fgcolor = "gray"
                    child.add_face(active, column=1, position="branch-right")
                    child.set_style(style)

# the endpoint class is the control class for the pipe and initiates or ends flow events, sets flow rates,
# and triggers activation for all other pipes upstream from it. inherits from pipe.
class endpoint(pipe):
    # constructor function is simplified from the standard pipe because it has no need for usual pipe properties
    # such as storing and tracking position of particles.
    def __init__(self, parent, name, manager):
        super().__init__(name, 0, 0, None, parent, manager)
        self.type = "endpoint"

    # overrides the function in the parent class to produce an error and otherwise do nothing
    # endpoints should not have pipes downstream from them.
    def create_child(self, name, length, diameter, material):
        print("Cannot create child pipes past an endpoint.")
        pass

    # endpoints should not have more endpoints downstream from them. overrides the pipe class to
    # instead produce an error and otherwise do nothing.
    def create_end(self, name):
        print("Cannot create endpoint past an endpoint.")
        pass

    # function to increase activation for self and upstream pipes to make water flow possible.
    def activate_pipes(self, newFlow=None):
        self.activate()
        if newFlow is not None:
            self.update_flow_rate(newFlow)
        else:
            self.update_flow_rate(self.flowRate)
        p = self.parent
        while p is not None:
            p.activate()
            p = p.parent

    # deactivates self and reduces activation for upstream pipes.
    def deactivate_pipes(self):
        self.deactivate()
        #old_flow = self.flow
        #self.flowRate = 0
        #self.flow = 0
        #self.update_pipe_flow_rates(old_flow)
        self.update_flow_rate(0)
        p = self.parent
        while p is not None:
            p.deactivate()
            p = p.parent

    # function to change the flow rate of this pipe. currently, the endpoint flow rates
    # dictate the flow rates through all upstream pipes.
    def update_flow_rate(self, new_flow: float):
        flow_change = new_flow - self.flowRate
        rate_change = flow_change / self.manager.timeStep
        self.flowRate = new_flow
        self.flow = new_flow / self.manager.timeStep
        p = self.parent
        while p is not None:
            p.flowRate += flow_change
            p.flow += rate_change
            #for testing
            #assert(p.flowRate <= 6.0)
            if not p.flowRate >= 0:
                if p.flowRate > (-1*self.manager.tolerance):
                    self.flow = 0
                    self.flowRate = 0
                else:
                    print("negative flow rate error: pipe ", p.name, "has flow rate of", p.flowRate)
            p = p.parent

    # when deactivating, we want to decrease the flow rate of all the parent pipes by the
    # flow rate of the endpoint that has deactivated (
    # so we instead update the flow rates of all of the parent pipes to subtract the flow
    def update_pipe_flow_rates(self, old_flow: float):
        global timeStep
        flow_change = self.flowRate - old_flow
        rate_change = flow_change / timeStep
        p = self.parent
        while p is not None:
            p.flowRate += flow_change
            p.flow += rate_change
            p = p.parent

