import math
import copy
import random
from igraph import *
import matplotlib.pyplot as plt
from multiprocessing import cpu_count
from multiprocessing import Pool, Process
import collections

logfile = "ParticleDiffusion.log"
logfile = open(logfile, 'a')

pipeIndex: dict = {}  # this stores all the pipes in the pipe system. pipes can be accessed by name, which must be unique.
random.seed(a=None, version=float)
CUBIC_INCHES_PER_GALLON = 231

class counter:
    """
    this is intended to be used as a static class to count the passage of time
    within the simulation environment. this was implemented so that
    the time value could be accessed more easily across modules (files).
    """

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
    """
    A class that manages particles in a pipe system. It keeps track of particle positions, ages, and aggregate data by pipe membership.
    """

    def __init__(self, time):
        # global variables to track number of particles generated. Each particle is given a unique particle ID based on this number.
        # it should not be decremented if we want an accurate count of the number of particles generated. Note it is redundant
        # to create more than one particle per second at the root.
        self.numParticles: int = 0
        self.deletedParticles: int = 0
        self.particleIndex: dict = {}  # this stores all the particles in the pipe system. Particle objects can be accessed by ID.
        self.expendedParticles: dict = {}  # stores all particles that have passed through an endpoint, for data collection.
        self.expelledParticleData: dict = {} # stores data about which particles were expelled from which endpoints and
        self.particlePositions: dict = {} # stores lists of which particles are in which pipes. keys are pipe names.
        self.pipeAggregates: dict = {} # stores details about the particles in each pipe in a tuple of the following. form: (min_age, max_age, average_age, num_particles). Keys are pipe names.

       #Run Preferences (specified by user)
        self.diffusionActive = False
        self.diffusionActiveStagnant = False
        self.diffusionActiveAdvective = False 
        self.decayActiveFreeChlorine = False
        self.decayActiveMonochloramine = False

        # Timestep vars
        self.time = time
        self.time.reset()
        self.tolerance = math.pow(2, -16)
        self.timeStep: int = 60

        #Decay function vars
        self.molecularDiffusionCoefficient: float = None
        self.monochloramineBase: float = 1
        self.dichloramineBase: float = 1
        self.ammoniaBase: float = 1
        self.chlorideBase: float = 1
        self.iodineBase: float = 1
        self.hypochlorousAcidBase: float = 1
        self.docbBase: float = 1
        self.docboxBase: float = 1
        self.docwBase: float = 1
        self.docwoxBase: float = 1
        self.chlorineBase: float = 1
        self.d_m : float = None

        #Particle accumulation vars
        self.bins = []
        self.flowNum: int = 0 
        self.time_since = {}
        self.pipeString: str = ""
        self.edgeList: list = []
        self.endpointList: list = []
        
        # Vars affecting pipe class
        self.rootarea = 0
        self.rootflow = 0
        self.newpos = 0
        self.rootlength = 0
        self.prevFlow = 0
        self.prevArea = 0
        self.prevLength = 0

    def particle(self, container, freeChlorineInit):
        """
        Creates a new particle object and registers it with the particle manager.
        """
        
        global logfile
        return Particle(container, self, freeChlorineInit)

    def setDiffusionCoefficient(self, diffusionCoefficient: float):
        """
        Sets the molecular diffusion coefficient of the particle and calculates the diffusion coefficient
        based on the time step.
        """
        
        self.molecularDiffusionCoefficient = float(diffusionCoefficient)
        self.d_m = self.molecularDiffusionCoefficient / self.timeStep
    
    def setTimeStep(self, timeStep: int):
        """
        Sets the time step of the particle manager. Called from Driver
        """

        self.timeStep = timeStep

    def update_caller(self, particle):
        """
        Calls the update function of the particle object.
        """

        name, part = particle.update()
        return name, part

    def update_particles(self, time_since):
        """
        updates particle age data, particle positions, and aggregate particle data for particles in each pipe (every 1000 tics)
        """
        global logfile
        self.time_since = time_since
        index = self.particleIndex.copy()
        particles = list(index.values())
        rval = map(self.update_caller, particles)
        self.particlePositions = self.particle_update_helper(rval)
        if self.time.get_time() % 1000 == 999:
            self.update_particle_info()

    def particle_update_helper(self, particlePositions):
        """
        an assistant function for the update_particles function that helps to assign particles to the correct list
        within the pipe dictionary (or creates a new list if the correct dictionary entry does not exist)
        """

        dic = {}
        for key, value in particlePositions:
            if dic.get(key) is None:
                dic[key] = [value]
            else:
                dic[key].append(value)
        return dic

    def add_particles(self, density: float, root, time_since):
        """
        each pipe tracks particles that are inside it and tracks their progress along it.
        this function is meant to be called by the root pipe. fills pipe with particles
        with one particle every 0.1 inches.
        """
        
        global logfile 

        particles = self.particlePositions.get(root.name)
        
        freeChlorineInit = 1.0
        if particles == None:
            self.particlePositions[root.name] = particles = []

        if len(particles) < 1:
            freeChlorineInit = 1.0
            min_distance = root.length
        else:
            min_distance = min(part.position for part in particles)
        current_distance = 0

        while current_distance < min_distance + density:
            part = self.particle(root, freeChlorineInit)
            part.position = current_distance
            current_distance += density

    def update_particle_info(self):
        """
        generates aggregate data about particles by pipe membership and assigns it to the pipeAggregates dictionary.
        """
    
        for pipeName in self.particlePositions.keys():
            contents = self.particlePositions.get(pipeName)
            ages = self.particle_age_builder(contents)
            min_age, max_age, average_age = self.particle_age_calculator(ages)
            num_particles = len(ages)
            self.pipeAggregates[pipeName] = (min_age, max_age, average_age, num_particles)

    def particle_age_builder(self, particles):
        """
        builds a list with the age values of particles given a list of them.
        """
        
        ages = [x.age for x in particles]
        return ages

    def particle_age_calculator(self, input):
        """
        calculates minimum, maximum, and average age values given a list of particle ages.
        """
        
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

class Particle:
    """
    the particle class tracks what happens when water flows through the pipe network. Each particle stores information
    about the pipes it travels through and about how long it remains in contact with each pipe.
    """
    
    def __init__(self, container, manager, freeChlorineInit):
        """
        this constructor requires a container (pipe object) to instantiate, because particles should always be tied to one
        pipe. upon creation, the particle assigns itself an id based on the global numParticles variable, adds itself to
        the particle dictionary, stores it's parent object, and sets it's age at 0.
        """

        self.manager = manager
        self.ID: int = self.manager.numParticles
        self.manager.numParticles += 1
        self.contact: dict = {container.material: 0} # contact stores the number of seconds the particle has been in
        self.ages: dict = {container.name: 0} # contact with each material it has touched, starting at 0.
        self.container: pipe = container  # records current parent container
        self.position: float = 0 # stores particle position within pipe
        self.sumDistance: float = 0 # stores total distance travelled by particle
        self.route: list = [container.name]
        self.age: float = 0
        self.manager.particleIndex[self.ID] = self
        self.d_m = self.manager.d_m
        self.freechlorine : float = freeChlorineInit #1.0 #for now this is starting concentration
        self.hypochlorousAcid : float = self.manager.hypochlorousAcidBase
        self.ammonia : float = self.manager.ammoniaBase
        self.monochloramine : float = self.manager.monochloramineBase
        self.dichloramine : float = self.manager.dichloramineBase
        self.iodine : float = self.manager.iodineBase
        self.docb : float = self.manager.docbBase
        self.docbox : float = self.manager.docboxBase
        self.docw : float = self.manager.docwBase
        self.docwox : float = self.manager.docwoxBase
        self.chlorine : float = self.manager.chlorineBase
        global logfile

    
    def monochloramine_network_decay(self):
        """
        This function calculates the decay of monochloramine network based on the given parameters.
        """
        
        self.hypochlorousAcid = self.hypochlorousAcid + self.age * (- self.container.kv1Lambda * (self.hypochlorousAcid * self.ammonia) + (self.container.kv2Lambda * self.monochloramine) - ( self.container.kv3Lambda * self.hypochlorousAcid * self.monochloramine) )
        self.ammonia = self.ammonia + self.age * ((-self.container.kv1Lambda * self.hypochlorousAcid * self.ammonia) + (self.container.kv2Lambda * self.monochloramine) + (self.container.kv5Lambda * math.pow(self.monochloramine, 2)) + (self.container.doc1Lambda * self.hypochlorousAcid * self.monochloramine) )#math.pow(self.monochloramine, 2) + (self.hypochlorousAcid * self.monochloramine) )
        self.monochloramine = self.monochloramine + self.age * ((self.container.kv1Lambda * self.hypochlorousAcid * self.monochloramine)  - self.container.kv2Lambda * self.monochloramine - (self.container.kv3Lambda * self.hypochlorousAcid * self.monochloramine)) - (2 * self.container.kv5Lambda * math.pow(self.monochloramine, 2)) - (self.container.doc1Lambda * self.hypochlorousAcid * self.monochloramine) - (self.container.doc1Lambda * self.container.areavelocity * self.hypochlorousAcid * self.monochloramine) #(2 * math.pow(self.monochloramine, 2)) - (self.hypochlorousAcid * self.monochloramine) - (self.container.areavelocity * self.hypochlorousAcid * self.monochloramine) )
        self.dichloramine = self.dichloramine + self.age * ( (self.container.kv3Lambda * self.hypochlorousAcid * self.monochloramine) + (self.container.doc1Lambda * math.pow(self.monochloramine, 2)) - (self.container.kv7Lambda * self.dichloramine))
        self.iodine = self.iodine + self.age * ( self.container.kv7Lambda * self.dichloramine )
        self.docb = self.docb + self.age * ( - ( self.container.doc1Lambda * self.hypochlorousAcid * self.monochloramine))
        self.docbox = self.docbox + self.age * ( self.container.doc1Lambda * self.hypochlorousAcid * self.monochloramine)
        self.docw = self.docw + self.age * ( - self.container.doc1Lambda * self.container.areavelocity * self.hypochlorousAcid * self.monochloramine)
        self.docwox = self.docwox + self.age * (self.container.doc1Lambda * self.container.areavelocity * self.hypochlorousAcid * self.monochloramine)
        self.chlorine = self.chlorine + self.age * ( (self.container.doc1Lambda * self.hypochlorousAcid * self.monochloramine) + (self.container.doc1Lambda * self.container.areavelocity * self.hypochlorousAcid * self.monochloramine))

    def free_chlorine_decay(self):
        """
        Calculates the decay of free chlorine in the container based on the lambda value of the container and the time step.
        The lambda value is specific to the area and material of the pipe.
        """

        freeChlorineLambda = self.container.freeChlorineLambda
        self.freechlorine = self.freechlorine * math.exp(-freeChlorineLambda*timeStep)
        
    def update(self):
        """
        The update function increments the particle age and increments contact record according to the current container material type. If the particle container is active (flowing) then calls the movement function to compute particle flow.
        """

        self.age += 1

        if self.manager.decayActiveMonochloramine:
            self.monochloramine_network_decay()

        containerName = self.container.name

        # Track pipes (including pipe type) of pipes that the particle has been in contact with.
        if self.contact.get(self.container.material) is not None:
            self.contact[self.container.material] += 1
        else:
            self.contact.update({self.container.material: 0})
            self.contact[self.container.material] += 1

        if self.container.name not in self.route:
            self.route.append(self.container.name)

        self.ages.setdefault(containerName, 0)
        self.ages[containerName] += 1

        # Originally checks if container is active (water is flowing) before checking diffusion value. With issue 165
        # this is reversed. If diffusion is active then dispersion function will be called in lieu of movement. 
        # (The two are similar, but dispersion includes diffusive activity.)
        if self.manager.diffusionActive:
            if self.container.isActive:
                if self.manager.diffusionActiveAdvective:
                    containerName = self.disperse()
                else:
                    containerName = self.movement()
            elif self.manager.diffusionActiveStagnant:
                containerName = self.diffuse()
        elif self.container.isActive:
            containerName = self.movement()

        return containerName, self

    def movement(self):
        """
        The particle movement code is really the heart of this entire application. Everything depends on this being accurate and
        performant because scientific results are drawn from how and when particles traverse the network. This function
        is intended to simulate how a particle might be carried along with a stream of water and updates the particle according
        to how much flow should occur within a given time segment. Every particle traveling through the network will call
        this function every time-step that it flows down the network.
        """
        
        remainingTime = 1
        containerName = self.container.name
        while remainingTime > self.manager.tolerance:  # calculate particle movement until flow consumes available time (1 second)
            if self.container.type != "endpoint":
                flow = self.container.flow * remainingTime
                position = self.position
                newPosition = (flow * (CUBIC_INCHES_PER_GALLON / self.container.area)) + position
                if newPosition > self.container.length:
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
            elif self.container.type == "endpoint":
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

    def diffuse(self):
        """
        Diffusion math is very tricky because it depends on the strength of the concentration gradient, on the current
        temperature, and on the types of liquids involved. For simplicity, some assumptions have been made. If needed,
        this function could be expanded in future to take in some of the data mentioned above. For now, assumptions are
        made. Diffusion coefficient is originally assumed to be 2.14 * 10^-6
        """

        global logfile
        d_m = self.d_m

        # Originally 4 * D_m * timestep. With D_m being divided by the timestep, we no longer multiply by timestep.
        avg_distance = 4 * d_m

        # initialize with a random seed for added randomness
        generator = random.Random()
        standard_dev = math.sqrt(avg_distance)
        modifier = generator.normalvariate(mu=0.0, sigma=standard_dev)
        movement = modifier
        position = self.position
        newPosition = position + movement

        if newPosition < 0:
            remainingMovement = newPosition
            while remainingMovement < 0:
                newContainer = self.container.parent
                if newContainer == None:
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

    def disperse(self):
        """
        Advection, diffusion-dispersion during flow events. Combines movement of particle with diffusive actions. Calculates age of particle through each flow event.
        """

        global writer
        global logfile

        remainingTime = 1
        containerName = self.container.name
        area = self.container.area
        while remainingTime > self.manager.tolerance:  # calculate particle movement until flow consumes available time (1 second)
            if self.container.type != "endpoint":
                flow = self.container.flow * remainingTime

                flow_endpoint_list = list(self.manager.time_since.keys())
                
                #Particles i that already in the pipe system versus particles that enter the pipe system during the kth flow event.
                if self.age >= self.manager.time_since[flow_endpoint_list[-1]]:
                    min_t = (counter.get_time() - (counter.get_time() - self.manager.time_since[flow_endpoint_list[-1]]))
                else:
                    min_t = (counter.get_time() - (counter.get_time() - self.age))
                
                d_inf = self.container.d_inf 
                alpha = self.container.alpha 
                d_m = self.d_m 

                #Diffusion rate for particle i during the kth flow event considering the d_inf and d_m values for the pipe segment.
                diffusion_rate_i = (d_inf - d_m) * (1 - math.exp((-min_t / alpha))) + d_m

                # initialize with a random seed for added randomness
                avg_distance = 4 * diffusion_rate_i 
                generator = random.Random()
                standard_dev = math.sqrt(avg_distance)
                modifier = generator.normalvariate(mu=0.0, sigma=standard_dev)
                position = self.position + modifier
                newPosition = (flow * (CUBIC_INCHES_PER_GALLON / self.container.area)) + position
                if newPosition > self.container.length:
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
                    
                self.manager.prevFlow = self.container.flow
                self.manager.prevArea =   math.pi * (1/2)**2
                self.manager.newpos = newPosition
                if self.container.length > 0:
                    self.manager.prevLength = self.container.length
                    
                
            elif self.container.type == "endpoint":
                particleInfo = []
                time = self.manager.time.get_time()
                particleInfo.append(time)
                expelledTime = self.age + (1 - remainingTime)

                # Remove the time that the particle has been accounted for while being expelled from the system. The length, flow, and area of the endpoint is irrelevant and not used in the calculation.
                em = ( self.manager.newpos - self.manager.prevLength) / (self.manager.prevFlow / self.manager.prevArea) 
                expelledTime -= em
                self.age = expelledTime
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

            self.manager.bins.append(modifier)
               
        return containerName

    def select_random_child(self):
        """
        function to select random children of pipes. Note that the functionality is different than the pipe
        select_child function because this can select active or inactive pipes but will not select endpoints.
        the assumption here is that this function is called by diffuse function, which in turn only activates on
        inactive pipes. thus downstream endpoints should be "off" and allowing particles to enter the endpoint
        would be like simulating a leaky faucet.
        """
        selected = False
        choices = self.container.children.copy()
        
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

    def __copy__(self, container):
        """
        this function can create a deep copy of a particle object, but assigns it a new unique particle id.
        this is used when particles arrive at a fork with two active (flowing) pipes, a duplicate should be made
        to simulate water traveling down both pipes.
        """
        global numParticles
        p = Particle(container)
        p.ID = self.manager.numParticles
        p.contact = copy.deepcopy(self.contact)
        p.ages = copy.deepcopy(self.ages)
        p.age = self.age
        self.manager.numParticles += 1
        self.manager.particleIndex[p.ID] = p
        p.route = copy.deepcopy(self.route)
        return p

    # this function deletes the particle and increments the deletedparticles count.
    def __del__(self):
        self.manager.deletedParticles += 1

    # getOutput returns a tuple that contains the data stored in the particle. can be used to read out at the end
    # of the particle's journey, or query along the way for testing.
    def getOutput(self):
        add_contacts = []
        add_ages = []
        keys = self.contact.keys()
        values = self.contact.values()
        rval = [self.ID, self.age, self.container.name]
        for key in keys:
            add_contacts.append([key, self.contact[key]])
        rval.append(add_contacts)
        for pipe in self.ages.keys():
            add_ages.append([pipe, self.ages[pipe]])
        rval.append(add_ages)
        rval.append(self.freechlorine)
        return rval

    # prints details about the particle. included for testing purposes. Not used.
    def print_part(self):
        tup = self.getOutput()
        output = ""
        for each in tup:
            output = output + " | " + str(each)
        print(output)

class pipe:
    """
    the pipe class is basically a tree data structure, but it is an n-way tree. on top of that, each pipe has properties
    necessary for plumbing, such as a diameter, material type, length, diameter, cross-sectional-area (CSA) and an activated
    flag. this last one is used to track whether the pipe is part of a series of pipes that are currently flowing, or
    whether it contains stagnant water.
    """

    # the constructor takes in the pipe name, dimensions, and parent.
    def __init__(self, name, length, width, material, parent, d_inf, alpha, manager, freeChlorineLambda, kv1Lambda, kv2Lambda, kv3Lambda, kv5Lambda, kv7Lambda, doc1Lambda, doc2Lambda):
        # print("init pipe")
        global pipeIndex
        self.manager = manager
        self.name = name
        self.length: float = length * 12
        self.width: float = width # in inches
        self.radius = self.width / 2
        self.material: str = material
        self.parent: pipe = parent
        self.d_inf: float = d_inf / self.manager.timeStep # Set to 0.01946 in initial integration.
        self.alpha: float = alpha / self.manager.timeStep # set to 114 in initial integration
        self.freeChlorineLambda: float = freeChlorineLambda
        self.kv1Lambda: float = kv1Lambda
        self.kv2Lambda: float = kv2Lambda
        self.kv3Lambda: float = kv3Lambda
        self.kv5Lambda: float = kv5Lambda
        self.kv7Lambda: float = kv7Lambda
        self.doc1Lambda: float = doc1Lambda
        self.doc2Lambda: float = doc2Lambda
        self.area: float = math.pi * math.pow((self.radius), 2) #cross-sectional-area
        self.children: list[pipe] = []
        self.isActive = False
        self.activity = 0
        self.type = "pipe"
        self.flowRate: int = 0  # gallons per minute
        self.flow: float = 0  # gallons per time unit
        pipeIndex[self.name] = self
        print("WidtH: ", self.width, "Radius: ", self.radius, "Area: ", self.area)
        if self.area == 0:
            self.velocity = 0
        else: 
            self.velocity = self.flow / self.area
        
        if self.velocity == 0:
            self.areavelocity = 0
        else:
            self.areavelocity = self.area / self.velocity

    def activate(self):
        """
        function to track activations for a pipe. if activity is positive,
        one or more endpoints downstream from this pipe are active (flowing)
        so this pipe contains flowing water.
        """

        self.activity += 1
        self.set_activity()

    def deactivate(self):
        """
        does not actually deactivate the pipe, but decrements activity when
        an endpoint is shut off.
        """
        self.activity -= 1
        self.set_activity()

    def set_activity(self):
        """
        if activity is nonpositive, deactivates pipe (no downstream endpoints are flowing).
        pipe contains stagnant water.
        """

        if self.activity > 0:
            self.isActive = True
        else:
            self.isActive = False

    def create_child(self,name,length,diameter,material):
        """
        this function is used by the builder. creates a pipe and inserts it as a child
        of the parent pipe, with this pipe as the parent of the child pipe.
        """
        p = pipe(name,length,diameter,material,self)
        self.children.append(p)
        return p

    def create_end(self, name):
        """
        this function is used by the builder to create an endpoint as a child the current pipe object.
        """

        p = endpoint(self, name)
        self.children.append(p)
        return p

    def select_child(self):
        """
        this function randomly selects from available active child pipes and returns the selected child.
        used to randomly assign particle paths at branches down the pipe, but only along branches with
        active flow.
        """

        selected = None
        candidates = []
        for child in self.children:
            if child.isActive:
                candidates.append(child)
        if len(candidates) > 0:
            selected = random.choice(candidates)
        return selected

    def peek_helper(self, dim, depth):
        """
        compiles a list where each node reports it's depth in the tree, returns that list.
        """

        dim.append(depth)
        for each in self.children:
            each.peek_helper(dim, depth + 1)
        return dim

    def peek_children(self):
        """
        returns the depth of the tree, and the maximum number of nodes at the same depth.
        used for establishing the size of the grid to lay out the graph on.
        """

        if self.parent != None:
            return self.parent.peek_children()
        dim = []
        dim = self.peek_helper(dim, 0)
        data = collections.Counter(dim)
        height = data.most_common(1)[0][1] # most_common returns a tuple with (mode, frequency)
        depth = max(dim)
        return depth, height

    def generate_tree(self):
        """
        this function creates and returns a list of edges forming a tree based on the current pipes model. This tree is used to
        create a graphical representation of the model.
        """

        if self.children is not None:
            for child in self.children:
                if child is not None and child.type != "endpoint":
                    level = [self.name, child.name]
                    self.manager.edgeList.append(level)
                    child.generate_tree()
                elif self.parent is None:
                        level = ['Base', self.name]
                        self.manager.edgeList.append(level)
                        if(child.type == "endpoint"):
                            self.manager.endpointList.append(child.name)
                elif child.type == "endpoint":
                    self.manager.endpointList.append(child.name)
                

           
    def show_tree(self, path, ageDict):
        """
        Take list of edges and creates an igraph tree and visual representation. Graph edges are labeled with (Pipe name, average age))
        The graph is saved as graph_scaled.png and takes on a tree structure of the pipe network.
        """
        
        pipeEdges = ['Base']
        for edge in self.manager.edgeList:
            for num, pipe in enumerate(edge):
                if pipe not in pipeEdges:
                    pipeEdges.append(pipe)
                    edge[num] = pipeEdges.index(pipe)
                else:
                    edge[num] = pipeEdges.index(pipe)
        
        if self.manager.edgeList[0][0] != 0:
            self.manager.edgeList.insert(0, [0,1])
        
        g = Graph(edges = self.manager.edgeList)
        pipeEdges.pop(0)
        ages = [0.0] * len(pipeEdges)
        for entry in ageDict.keys():
            ages[pipeEdges.index(entry)] = round(ageDict[entry][0] / ageDict[entry][1], 2)
        
        x = 0
        
        for i in range(1, len(pipeEdges) + 1):
                if(g.degree(i) == 1):
                    g.vs(i)["label"] = self.manager.endpointList[x]
                    g.vs(i)["color"] = "blue"
                    x += 1
        
        pipeTuples = zip(pipeEdges, ages)
        g.es["pipeTuples"] = list(pipeTuples)
        g.es["label"] = g.es["pipeTuples"]
        plot(g, "static/plots/graph_scaled.png", bbox = (800,800), margin = 150, layout= g.layout_reingold_tilford(root=[0]))
        plot(g, path, bbox = (800,800), margin = 150, layout= g.layout_reingold_tilford(root=[0]))

class endpoint(pipe):
    """
    the endpoint class is the control class for the pipe and initiates or ends flow events, sets flow rates,
    and triggers activation for all other pipes upstream from it. inherits from pipe.  
    """

    def __init__(self, parent, name, manager):
        """
        constructor function is simplified from the standard pipe because it has no need for usual pipe properties
        such as storing and tracking position of particles.
        """
        
        super().__init__(name, 0, 0, None, parent, 0, 0, manager, 0, 0, 0,0, 0, 0, 0, 0)
        self.type = "endpoint"

    def create_child(self, name, length, diameter, material):
        """
        overrides the function in the parent class to produce an error and otherwise do nothing
        endpoints should not have pipes downstream from them.
        """

        print("Cannot create child pipes past an endpoint.")
        pass

    def create_end(self, name):
        """
        endpoints should not have more endpoints downstream from them. overrides the pipe class to
        instead produce an error and otherwise do nothing.
        """
        
        print("Cannot create endpoint past an endpoint.")
        pass

    def activate_pipes(self, newFlow=None):
        """
        function to increase activation for self and upstream pipes to make water flow possible.
        """
        
        self.manager.flowNum += 1
        self.activate()
        if newFlow is not None:
            self.update_flow_rate(newFlow)
        else:
            self.update_flow_rate(self.flowRate)
        p = self.parent
        while p is not None:
            p.activate()
            p = p.parent

    def deactivate_pipes(self):
        """
        deactivates self and reduces activation for upstream pipes.   
        """

        self.deactivate()
        self.update_flow_rate(0)
        p = self.parent
        while p is not None:
            p.deactivate()
            p = p.parent

    def update_flow_rate(self, new_flow: float):
        """
        dictate the flow rates through all upstream pipes.
        function to change the flow rate of this pipe. currently, the endpoint flow rates
        """
        
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

    def update_pipe_flow_rates(self, old_flow: float):
        """
        when deactivating, we want to decrease the flow rate of all the parent pipes by the
        flow rate of the endpoint that has deactivated (
        so we instead update the flow rates of all of the parent pipes to subtract the flow
        """

        global timeStep
        flow_change = self.flowRate - old_flow
        rate_change = flow_change / timeStep
        p = self.parent
        while p is not None:
            p.flowRate += flow_change
            p.flow += rate_change
            p = p.parent


def main():
    sim = pipe("sim", 0, 0, None, None, 0, 0, 0, None)
    pipe.show_tree(sim)

if __name__ == "__main__":
    main()