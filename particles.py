"""
This module contains the particle, particle manager, and pipe classes.
These control the charactor and behavior of particles in the pipe network. 
"""

import math
import copy
import numpy as np
import random
from igraph import *
import collections

logfile = "ParticleDiffusion.log"
logfile = open(logfile, 'a')

pipe_index: dict = {}  # This stores all the pipes in the pipe system. pipes can be accessed by name, which must be unique.
random.seed(a=None, version=float)
CUBIC_INCHES_PER_GALLON = 231

class Counter:
    """
    this is intended to be used as a static class to count the passage of time
    within the simulation environment. this was implemented so that
    the time value could be accessed more easily across modules (files).
    """

    t = 0
    @staticmethod
    def get_time():
        return Counter.t
    @staticmethod
    def increment_time():
        Counter.t += 1
    @staticmethod
    def reset():
        Counter.t = 0

class ParticleManager():
    """
    A class that manages particles in a pipe system. It keeps track of particle positions, ages, and aggregate data by pipe membership.
    """

    def __init__(self, time):
        """
        Global variables to track number of particles generated. Each particle is given a unique particle ID based on this number.
        it should not be decremented if we want an accurate count of the number of particles generated. Note it is redundant
        to create more than one particle per second at the root.

        :param time: the time object that tracks the passage of time in the simulation.
        """
        
        self.num_particles: int = 0
        self.deleted_particles: int = 0
        self.particle_index: dict = {}  # this stores all the particles in the pipe system. Particle objects can be accessed by ID.
        # self.expended_particles: dict = {}  # stores all particles that have passed through an endpoint, for data collection.
        self.expended_particles: list = []
        self.expelled_particles: list = []
        self.expelled_particle_data: dict = {} # stores data about which particles were expelled from which endpoints and
        self.particle_positions: dict = {} # stores lists of which particles are in which pipes. keys are pipe names.
        self.pipe_aggregates: dict = {} # stores details about the particles in each pipe in a tuple of the following. form: (min_age, max_age, average_age, num_particles). Keys are pipe names.
        self.reuse_stack = []

       #Run Preferences (specified by user)
        self.diffusion_active = False
        self.diffusion_active_stagnant = False
        self.diffusion_active_advective = False 
        self.decay_active_free_chlorine = False
        self.decay_active_monochloramine = False

        

        # timestep vars
        self.time = time
        self.time.reset()
        self.tolerance = math.pow(2, -16)
        self.timestep: int = 60

        #Decay function vars
        self.molecular_diffusion_coefficient: float = None
        self.d_m : float = None
        self.starting_particles_free_chlorine_concentration: float = 1.0
        self.injected_particles_free_chlorine_concentration: float = 1.0
        self.decay_monochloramine_dict: dict = {}
        self.concentration_dict: dict = {}
    
        #Particle accumulation vars
        self.bins = []
        self.flow_num: int = 0 
        self.time_since = {}
        # self.pipe_string: str = ""
        self.edge_list: list = []
        self.endpoint_list: list = []
        
        # Vars affecting pipe class
        self.new_pos = 0
        self.prev_flow = 0
        self.prev_area = 0
        self.prev_length = 0

        self.pipe_net: list = []
        self.pipe_densities: dict = {}
        self.particle_layout: dict = {}




    def particle(self, container, concentration_dict):
        """
        Creates a new particle object and registers it with the particle manager.

        :param container: the pipe object that the particle is being created in.
        :param concentration_dict: a dictionary of the concentrations of each particle type.
        :return: the particle object that was created.
        """
        
        global logfile
        return Particle(container, self, concentration_dict=concentration_dict)

    def set_diffusion_coefficient(self, diffusionCoefficient: float):
        """
        Sets the molecular diffusion coefficient of the particle and calculates the diffusion coefficient
        based on the time step.

        :param diffusionCoefficient: the molecular diffusion coefficient of the particle.
        """
        
        self.molecular_diffusion_coefficient = float(diffusionCoefficient)
        self.d_m = self.molecular_diffusion_coefficient / self.timestep
    
    def set_timestep(self, timestep: int):
        """
        Sets the time step of the particle manager. Called from Driver

        :param timestep: the time step of the particle manager.
        """

        self.timestep = timestep

    def update_caller(self, particle):
        """
        Calls the update function of the particle object.

        :param particle: the particle object to be updated.
        :return: the name of the pipe that the particle is in and the particle object.
        """

        name, part = particle.update()
        return name, part

    def update_particles(self, time_since):
        """
        updates particle age data, particle positions, and aggregate particle data for particles in each pipe (every 1000 tics)

        :param time_since: a dictionary of the time since the last flow event for each endpoint.
        """

        global logfile
        self.time_since = time_since
        index = self.particle_index.copy()
        particles = list(index.values())
        # print(len(particles))
        rval = map(self.update_caller, particles)
        self.particle_positions = self.particle_update_helper(rval)
        if self.time.get_time() % 1000 == 999:
            self.update_particle_info()

    def particle_update_helper(self, particle_positions_list):
        """
        an assistant function for the update_particles function that helps to assign particles to the correct list
        within the pipe dictionary (or creates a new list if the correct dictionary entry does not exist)

        :param particle_positions_list: a list of tuples containing the name of the pipe and the particle object.
        :return: a dictionary of lists of particles by pipe name.
        """

        particle_positions_by_pipe = {}
        for pipe_name, particle_object in particle_positions_list:
            if particle_positions_by_pipe.get(pipe_name) is None:
                particle_positions_by_pipe[pipe_name] = [particle_object]
            else:
                particle_positions_by_pipe[pipe_name].append(particle_object)
        return particle_positions_by_pipe
    
    def init_add_particles(self, density: float, root):

        particles = self.particle_positions.get(root.name)
    
        if particles == None:
            self.particle_positions[root.name] = particles = []

        free_chlorine_init = self.starting_particles_free_chlorine_concentration
        hypochlorous_acid_init = self.decay_monochloramine_dict['starting-particles-concentration-hypochlorous']
        ammonia_init = self.decay_monochloramine_dict['starting-particles-concentration-ammonia']
        monochloramine_init = self.decay_monochloramine_dict['starting-particles-concentration-monochloramine']
        dichloramine_init = self.decay_monochloramine_dict['starting-particles-concentration-dichloramine']
        iodine_init = self.decay_monochloramine_dict['starting-particles-concentration-iodine']
        docb_init = self.decay_monochloramine_dict['starting-particles-concentration-docb']
        docbox_init = self.decay_monochloramine_dict['starting-particles-concentration-docbox']
        docw_init = self.decay_monochloramine_dict['starting-particles-concentration-docw']
        docwox_init = self.decay_monochloramine_dict['starting-particles-concentration-docwox']
        chlorine_init = self.decay_monochloramine_dict['starting-particles-concentration-chlorine']


        self.concentration_dict['free_chlorine'] = free_chlorine_init
        self.concentration_dict['hypochlorous_acid'] = hypochlorous_acid_init
        self.concentration_dict['ammonia'] = ammonia_init
        self.concentration_dict['monochloramine'] = monochloramine_init
        self.concentration_dict['dichloramine'] = dichloramine_init
        self.concentration_dict['iodine'] = iodine_init
        self.concentration_dict['docb'] = docb_init
        self.concentration_dict['docbox'] = docbox_init
        self.concentration_dict['docw'] = docw_init
        self.concentration_dict['docwox'] = docwox_init
        self.concentration_dict['chlorine'] = chlorine_init

        for pipe in self.pipe_net[::-1]:
            
            dx = pipe.length / (self.pipe_densities[pipe] + 1)

            min_distance = pipe.length

            current_position = min_distance

            if(pipe.type == "pipe"):
                while current_position > 0 + dx:
                
                    part = self.particle(pipe, concentration_dict=self.concentration_dict)

                    part.position = current_position

                    self.particle_positions.setdefault(pipe.name, [])
                    self.particle_positions[pipe.name].append(part)

                    current_position -= dx
    

    def add_particles(self, density: float, root):
        """
        each pipe tracks particles that are inside it and tracks their progress along it.
        this function is meant to be called by the root pipe. fills pipe with particles
        with one particle every 0.1 inches.

        :param density: the number of particles per inch of pipe.
        :param root: the root pipe object.
        """
        
        global logfile 

        particles = self.particle_positions.get(root.name)
        # particles = self.particle_layout.get(root.name)

        # print("particles: ", len(particles))
        
        free_chlorine_init = self.injected_particles_free_chlorine_concentration
        hypochlorous_acid_init = self.decay_monochloramine_dict['starting-particles-concentration-hypochlorous']
        ammonia_init = self.decay_monochloramine_dict['starting-particles-concentration-ammonia']
        monochloramine_init = self.decay_monochloramine_dict['starting-particles-concentration-monochloramine']
        dichloramine_init = self.decay_monochloramine_dict['starting-particles-concentration-dichloramine']
        iodine_init = self.decay_monochloramine_dict['starting-particles-concentration-iodine']
        docb_init = self.decay_monochloramine_dict['starting-particles-concentration-docb']
        docbox_init = self.decay_monochloramine_dict['starting-particles-concentration-docbox']
        docw_init = self.decay_monochloramine_dict['starting-particles-concentration-docw']
        docwox_init = self.decay_monochloramine_dict['starting-particles-concentration-docwox']
        chlorine_init = self.decay_monochloramine_dict['starting-particles-concentration-chlorine']

        if particles == None:
            self.particle_positions[root.name] = particles = []

        if len(particles) < 1:
            free_chlorine_init = self.starting_particles_free_chlorine_concentration
            hypochlorous_acid_init = self.decay_monochloramine_dict['starting-particles-concentration-hypochlorous']
            ammonia_init = self.decay_monochloramine_dict['starting-particles-concentration-ammonia']
            monochloramine_init = self.decay_monochloramine_dict['starting-particles-concentration-monochloramine']
            dichloramine_init = self.decay_monochloramine_dict['starting-particles-concentration-dichloramine']
            iodine_init = self.decay_monochloramine_dict['starting-particles-concentration-iodine']
            docb_init = self.decay_monochloramine_dict['starting-particles-concentration-docb']
            docbox_init = self.decay_monochloramine_dict['starting-particles-concentration-docbox']
            docw_init = self.decay_monochloramine_dict['starting-particles-concentration-docw']
            docwox_init = self.decay_monochloramine_dict['starting-particles-concentration-docwox']
            chlorine_init = self.decay_monochloramine_dict['starting-particles-concentration-chlorine']

            min_distance = root.length
        else:
            min_distance = min(part.position for part in particles)
        current_distance = 0

        self.concentration_dict['free_chlorine'] = free_chlorine_init
        self.concentration_dict['hypochlorous_acid'] = hypochlorous_acid_init
        self.concentration_dict['ammonia'] = ammonia_init
        self.concentration_dict['monochloramine'] = monochloramine_init
        self.concentration_dict['dichloramine'] = dichloramine_init
        self.concentration_dict['iodine'] = iodine_init
        self.concentration_dict['docb'] = docb_init
        self.concentration_dict['docbox'] = docbox_init
        self.concentration_dict['docw'] = docw_init
        self.concentration_dict['docwox'] = docwox_init
        self.concentration_dict['chlorine'] = chlorine_init

        dx = root.length / (self.pipe_densities[root] + 1)

        current_position = min_distance

        while current_position > 0 + dx:

            if(len(self.reuse_stack) > 0):
                part = self.reuse_stack.pop(0)

                part.manager = self
                container = root
                concentration_dict = self.concentration_dict
                self.num_particles += 1
                part.contact: dict = {container.material: 0} # contact stores the number of seconds the particle has been in
                part.ages: dict = {container.name: 0} # contact with each material it has touched, starting at 0.
                part.container: Pipe = container  # records current parent container
                part.position: float = 0 # stores particle position within pipe
                part.sum_distance: float = 0 # stores total distance travelled by particle
                part.route: list = [container.name]
                part.age: float = 0
                part.time: int = self.time.get_time()
                self.particle_index[part.ID] = part

                part.d_m = self.d_m
                part.free_chlorine : float = concentration_dict['free_chlorine'] #1.0 #for now this is starting concentration
                part.hypochlorous_acid : float = concentration_dict['hypochlorous_acid']
                part.ammonia : float = concentration_dict['ammonia']
                part.monochloramine : float = concentration_dict['monochloramine']
                part.dichloramine : float = concentration_dict['dichloramine']
                part.iodine : float = concentration_dict['iodine']
                part.docb : float = concentration_dict['docb']
                part.docbox : float = concentration_dict['docbox']
                part.docw : float = concentration_dict['docw']
                part.docwox : float = concentration_dict['docwox']
                part.chlorine : float = concentration_dict['chlorine']

            else:
                part = self.particle(root, concentration_dict=self.concentration_dict)

            part.position = current_position

            current_position -= dx

    def update_particle_info(self):
        """
        generates aggregate data about particles by pipe membership and assigns it to the pipe_aggregates dictionary.
        """
    
        for pipeName in self.particle_positions.keys():
            contents = self.particle_positions.get(pipeName)
            ages = self.particle_age_builder(contents)
            min_age, max_age, average_age = self.particle_age_calculator(ages)
            num_particles = len(ages)
            self.pipe_aggregates[pipeName] = (min_age, max_age, average_age, num_particles)

    def particle_age_builder(self, particles):
        """
        builds a list with the age values of particles given a list of them.

        :param particles: a list of particle objects.
        """
        
        ages = [x.age for x in particles]
        return ages

    def particle_age_calculator(self, particle_ages):
        """
        Calculates minimum, maximum, and average age values given a list of particle ages.

        :param particle_ages: A list of particle ages.
        """
        
        min_age = 0
        max_age = 0
        avg_age = 0
        if len(particle_ages) > 0:
            min_age = min(particle_ages)
            max_age = max(particle_ages)
            avg_age = sum(particle_ages) / len(particle_ages)
            avg_age = float(f"{avg_age:0.4f}")
        return min_age, max_age, avg_age
    

    def output_status(self):
        """
        Returns pipe_aggregates dictionary.

        :return: pipe_aggregates dictionary.
        """
        
        return self.pipe_aggregates

class Particle:
    """
    The particle class tracks what happens when water flows through the pipe network. Each particle stores information
    about the pipes it travels through and about how long it remains in contact with each pipe.
    """
    
    def __init__(self, container, manager, concentration_dict, ID = None):
        """
        This constructor requires a container (pipe object) to instantiate, because particles should always be tied to one
        pipe. upon creation, the particle assigns itself an id based on the global num_particles variable, adds itself to
        the particle dictionary, stores it's parent object, and sets it's age at 0.

        :param container: the pipe object that the particle is being created in.
        :param manager: the particle manager object that the particle is being created in.
        :param concentration_dict: a dictionary of the concentrations of each particle type.
        """

        self.manager = manager
        if ID:
            self.ID = ID
        else:
            self.ID: int = self.manager.num_particles
        self.manager.num_particles += 1
        self.contact: dict = {container.material: 0} # contact stores the number of seconds the particle has been in
        self.ages: dict = {container.name: 0} # contact with each material it has touched, starting at 0.
        self.container: Pipe = container  # records current parent container
        self.position: float = 0 # stores particle position within pipe
        self.sum_distance: float = 0 # stores total distance travelled by particle
        self.route: list = [container.name]
        self.age: float = 0
        self.time: int = 0
        self.manager.particle_index[self.ID] = self
        
        self.d_m = self.manager.d_m
        self.free_chlorine : float = concentration_dict['free_chlorine'] #1.0 #for now this is starting concentration
        self.hypochlorous_acid : float = concentration_dict['hypochlorous_acid']
        self.ammonia : float = concentration_dict['ammonia']
        self.monochloramine : float = concentration_dict['monochloramine']
        self.dichloramine : float = concentration_dict['dichloramine']
        self.iodine : float = concentration_dict['iodine']
        self.docb : float = concentration_dict['docb']
        self.docbox : float = concentration_dict['docbox']
        self.docw : float = concentration_dict['docw']
        self.docwox : float = concentration_dict['docwox']
        self.chlorine : float = concentration_dict['chlorine']
        global logfile

    
    def monochloramine_network_decay(self):
        """
        This function calculates the decay of monochloramine network based on the given parameters.
        """
        
        self.hypochlorous_acid = round((self.hypochlorous_acid + self.age * (- self.container.kv1_lambda * (self.hypochlorous_acid * self.ammonia) + (self.container.kv2_lambda * self.monochloramine) - ( self.container.kv3_lambda * self.hypochlorous_acid * self.monochloramine) )), 5)
        self.ammonia = round((self.ammonia + self.age * ((-self.container.kv1_lambda * self.hypochlorous_acid * self.ammonia) + (self.container.kv2_lambda * self.monochloramine) + (self.container.kv5_lambda * math.pow(self.monochloramine, 2)) + (self.container.doc1_lambda * self.hypochlorous_acid * self.monochloramine) )), 5)#math.pow(self.monochloramine, 2) + (self.hypochlorous_acid * self.monochloramine) )
        self.monochloramine = round((self.monochloramine + self.age * ((self.container.kv1_lambda * self.hypochlorous_acid * self.monochloramine)  - self.container.kv2_lambda * self.monochloramine - (self.container.kv3_lambda * self.hypochlorous_acid * self.monochloramine)) - (2 * self.container.kv5_lambda * math.pow(self.monochloramine, 2)) - (self.container.doc1_lambda * self.hypochlorous_acid * self.monochloramine) - (self.container.doc1_lambda * self.container.areavelocity * self.hypochlorous_acid * self.monochloramine)), 5) #(2 * math.pow(self.monochloramine, 2)) - (self.hypochlorous_acid * self.monochloramine) - (self.container.areavelocity * self.hypochlorous_acid * self.monochloramine) )
        self.dichloramine = round((self.dichloramine + self.age * ( (self.container.kv3_lambda * self.hypochlorous_acid * self.monochloramine) + (self.container.doc1_lambda * math.pow(self.monochloramine, 2)) - (self.container.kv7_lambda * self.dichloramine))), 5)
        self.iodine = round((self.iodine + self.age * ( self.container.kv7_lambda * self.dichloramine )), 5)
        self.docb = round((self.docb + self.age * ( - ( self.container.doc1_lambda * self.hypochlorous_acid * self.monochloramine))), 5)
        self.docbox = round((self.docbox + self.age * ( self.container.doc1_lambda * self.hypochlorous_acid * self.monochloramine)), 5)
        self.docw = round((self.docw + self.age * ( - self.container.doc1_lambda * self.container.areavelocity * self.hypochlorous_acid * self.monochloramine)), 5)
        self.docwox = round((self.docwox + self.age * (self.container.doc1_lambda * self.container.areavelocity * self.hypochlorous_acid * self.monochloramine)), 5)
        self.chlorine = round((self.chlorine + self.age * ( (self.container.doc1_lambda * self.hypochlorous_acid * self.monochloramine) + (self.container.doc1_lambda * self.container.areavelocity * self.hypochlorous_acid * self.monochloramine))), 5)

    def free_chlorine_decay(self):
        """
        Calculates the decay of free chlorine in the container based on the lambda value of the container and the time step.
        The lambda value is specific to the area and material of the pipe.
        """

        free_chlorine_lambda = self.container.free_chlorine_lambda
        self.free_chlorine = float(self.free_chlorine) * math.exp(-float(free_chlorine_lambda)*float(self.manager.timestep))
        
    def update(self):
        """
        The update function increments the particle age and increments contact record according to the current container material type. If the particle container is active (flowing) then calls the movement function to compute particle flow.
        
        :return: the name of the pipe that the particle is in and the particle object.
        """

        self.age += 1

        if self.manager.decay_active_free_chlorine:
            self.free_chlorine_decay()

        if self.manager.decay_active_monochloramine:
            self.monochloramine_network_decay()

        container_name = self.container.name

        # Track pipes (including pipe type) of pipes that the particle has been in contact with.
        if self.contact.get(self.container.material) is not None:
            self.contact[self.container.material] += 1
        else:
            self.contact.update({self.container.material: 0})
            self.contact[self.container.material] += 1

        if self.container.name not in self.route:
            self.route.append(self.container.name)

        self.ages.setdefault(container_name, 0)
        self.ages[container_name] += 1

        if self.ID == 1000: 
            # print("update")
            logfile.write("all_position" + str(self.position) + str(self.manager.time.get_time()) + "\n")
               

        # Originally checks if container is active (water is flowing) before checking diffusion value. With issue 165
        # this is reversed. If diffusion is active then dispersion function will be called in lieu of movement. 
        # (The two are similar, but dispersion includes diffusive activity.)
        if self.manager.diffusion_active:
            if self.container.is_active:
                if self.manager.diffusion_active_advective:
                    container_name = self.disperse()
                else:
                    container_name = self.movement()
            elif self.manager.diffusion_active_stagnant:
                container_name = self.diffuse()
        elif self.container.is_active:
            container_name = self.movement()

        

        return container_name, self

    def movement(self):
        """
        The particle movement code is really the heart of this entire application. Everything depends on this being accurate and
        performant because scientific results are drawn from how and when particles traverse the network. This function
        is intended to simulate how a particle might be carried along with a stream of water and updates the particle according
        to how much flow should occur within a given time segment. Every particle traveling through the network will call
        this function every time-step that it flows down the network.

        :return: the name of the pipe that the particle is in.
        """
        
        remaining_time = 1
        container_name = self.container.name
        while remaining_time > self.manager.tolerance:  # calculate particle movement until flow consumes available time (1 second)
            if self.container.type != "endpoint":
                flow = self.container.flow * remaining_time
                position = self.position
                
                new_position = (flow * (CUBIC_INCHES_PER_GALLON / self.container.area)) + position
                if new_position > self.container.length:
                    travelled_distance = self.container.length - self.position
                    partial_flow = remaining_time * (travelled_distance / CUBIC_INCHES_PER_GALLON) * self.container.area
                    elapsed_time = partial_flow / flow
                    remaining_time = remaining_time - elapsed_time
                else:
                    travelled_distance = new_position - position
                    remaining_time = 0
                    self.position = new_position
                self.sum_distance += travelled_distance
                if remaining_time > 0:
                    self.container = self.container.select_child()
                    self.position = 0
                    container_name = self.container.name
            elif self.container.type == "endpoint":
                particle_info = []
                self.time = self.manager.time.get_time()
                expelledTime = self.age + (1 - remaining_time)
                self.age = expelledTime
                particle_info.append(self.ID)
                particle_info.append(self.time)
                particle_info.append(self.age)
                particle_info.append(self.container.name)
                contact_list = []
                for key in self.contact.keys():
                    contact_list.append([key, self.contact[key]])
                particle_info.append(contact_list)

                if(self.manager.decay_active_free_chlorine):
                    particle_info.append(self.free_chlorine)
                
                if(self.manager.decay_active_monochloramine):
                    particle_info.append(self.hypochlorous_acid)
                    particle_info.append(self.ammonia)
                    particle_info.append(self.monochloramine)
                    particle_info.append(self.dichloramine)
                    particle_info.append(self.iodine)
                    particle_info.append(self.docb)
                    particle_info.append(self.docbox)
                    particle_info.append(self.docw)
                    particle_info.append(self.docwox)
                    particle_info.append(self.chlorine)
                
                if self.manager.expelled_particle_data.get(self.container.name) is None:
                    self.manager.expelled_particle_data[self.container.name] = []
                dataset = self.manager.expelled_particle_data.get(self.container.name)
                dataset.append(particle_info)
                self.manager.reuse_stack.append(self)
                self.manager.particle_index.pop(self.ID)
                self.manager.expended_particles.append(self)
                self.manager.expelled_particles.append(particle_info)
                container_name = None
                break
        return container_name

    def diffuse(self):
        """
        Diffusion math is very tricky because it depends on the strength of the concentration gradient, on the current
        temperature, and on the types of liquids involved. For simplicity, some assumptions have been made. If needed,
        this function could be expanded in future to take in some of the data mentioned above. For now, assumptions are
        made. Diffusion coefficient is originally assumed to be 2.14 * 10^-6

        :return: the name of the pipe that the particle is in.
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
        new_position = position + movement

        if new_position < 0:
            remaining_movement = new_position
            while remaining_movement < 0:
                new_container = self.container.parent
                if new_container == None:
                    self.position = 0
                    break
                else:
                    new_position = self.container.length + remaining_movement
                if new_position < 0:  # movement direction is upstream (movement is negative, position is negative)
                    remaining_movement = new_position
                    self.position = 0
                else:
                    remaining_movement = 0
                    self.position = new_position
        elif new_position > self.container.length:
            remaining_movement = new_position - self.container.length
            while remaining_movement > 0:
                new_container = self.select_random_child()
                if new_container == None:
                    self.position = self.container.length
                    break
                else:
                    new_position = 0 + remaining_movement
                if new_position > self.container.length:
                    remaining_movement = new_position - self.container.length
                    self.position = self.container.length
                else:
                    remaining_movement = 0
                    self.position = new_position
        else: self.position = new_position
        
        return self.container.name

    def disperse(self):
        """
        Advection, diffusion-dispersion during flow events.Combines movement of particle with diffusive actions. 
        Calculates age of particle through each flow event.

        :return: the name of the pipe that the particle is in.
        """

        global writer
        global logfile

        remaining_time = 1
        container_name = self.container.name
        while remaining_time > self.manager.tolerance:  # calculate particle movement until flow consumes available time (1 second)
            if self.container.type != "endpoint":

                flow = self.container.flow * remaining_time

                flow_endpoint_list = list(self.manager.time_since.keys())
                
                #Particles i that already in the pipe system versus particles that enter the pipe system during the kth flow event.
                if self.age >= self.manager.time_since[flow_endpoint_list[-1]]:
                    min_t = (Counter.get_time() - (Counter.get_time() - self.manager.time_since[flow_endpoint_list[-1]]))
                else:
                    min_t = (Counter.get_time() - (Counter.get_time() - self.age))
                
                d_inf = self.container.d_inf 
                alpha = self.container.alpha 
                d_m = self.d_m 

                #Diffusion rate for particle i during the kth flow event considering the d_inf and d_m values for the pipe segment.
                diffusion_rate_i = (d_inf - d_m) * (1 - math.exp((-min_t / alpha))) + d_m
       
                # initialize with a random seed for added randomness
                avg_distance = 4 * diffusion_rate_i 
                standard_dev = math.sqrt(avg_distance)
                modifier = np.random.normal(0.0, standard_dev)
                position = self.position + modifier
                new_position = (flow * (CUBIC_INCHES_PER_GALLON / self.container.area)) + position

                if self.ID == 1000: 
                    # print("disperse")
                    logfile.write("new_position" + str(new_position) + "modifier : " + str(modifier) + "old position: " + str(position) + "\n")
               
                if new_position > self.container.length:
                    travelled_distance = self.container.length - self.position
                    partial_flow = remaining_time * (travelled_distance / CUBIC_INCHES_PER_GALLON) * self.container.area
                    elapsed_time = partial_flow / flow
                    remaining_time = remaining_time - elapsed_time
                else:
                    travelled_distance = new_position - position
                    remaining_time = 0
                    self.position = new_position
                self.sum_distance += travelled_distance
                if remaining_time > 0:
                    self.container = self.container.select_child()
                    self.position = 0 
                    container_name = self.container.name
                    
                self.manager.prev_flow = self.container.flow
                self.manager.prev_area =   math.pi * (1/2)**2
                self.manager.new_pos = new_position
                if self.container.length > 0:
                    self.manager.prev_length = self.container.length

            elif self.container.type == "endpoint":
                particle_info = []
                self.time = self.manager.time.get_time()
                particle_info.append(self.time)
                expelledTime = self.age + (1 - remaining_time)

                # Remove the time that the particle has been accounted for while being expelled from the system. The length, flow, and area of the endpoint is irrelevant and not used in the calculation.
                em = ( self.manager.new_pos - self.manager.prev_length) / (self.manager.prev_flow / self.manager.prev_area) 
               
                if self.ID == 1000: 
                    # print("disperse")
                    logfile.write("Expelled time: " + str(expelledTime) + " em: " + str(em) + " newpos" + str(self.manager.new_pos - self.manager.prev_length) +"\n")

                # expelledTime -= em
                self.age = expelledTime
                particle_info.append(self.ID)
                particle_info.append(self.age)

               
                
                if(self.manager.decay_active_free_chlorine):
                    particle_info.append(self.free_chlorine)
                
                if(self.manager.decay_active_monochloramine):
                    particle_info.append(self.hypochlorous_acid)
                    particle_info.append(self.ammonia)
                    particle_info.append(self.monochloramine)
                    particle_info.append(self.dichloramine)
                    particle_info.append(self.iodine)
                    particle_info.append(self.docb)
                    particle_info.append(self.docbox)
                    particle_info.append(self.docw)
                    particle_info.append(self.docwox)
                    particle_info.append(self.chlorine)

                if self.manager.expelled_particle_data.get(self.container.name) is None:
                    self.manager.expelled_particle_data[self.container.name] = []
                dataset = self.manager.expelled_particle_data.get(self.container.name)
                dataset.append(particle_info)
                self.manager.reuse_stack.append(self)
                self.manager.particle_index.pop(self.ID)
                self.manager.expended_particles.append(self)
                container_name = None
                break

            self.manager.bins.append(modifier)
               
        return container_name

    def select_random_child(self):
        """
        Function to select random children of pipes. Note that the functionality is different than the pipe
        select_child function because this can select active or inactive pipes but will not select endpoints.
        the assumption here is that this function is called by diffuse function, which in turn only activates on
        inactive pipes. thus downstream endpoints should be "off" and allowing particles to enter the endpoint
        would be like simulating a leaky faucet.

        :return: a random child pipe object.
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

    def __copy__(self, new_container):
        """
        This function can create a deep copy of a particle object, but assigns it a new unique particle id.
        This is used when particles arrive at a fork with two active (flowing) pipes, a duplicate should be made
        to simulate water traveling down both pipes.

        :param new_container: The pipe object that the particle is being created in.
        :return: A deep copy of the particle object.
        """
        
        global num_particles
        new_particle = Particle(new_container)
        new_particle.ID = self.manager.num_particles
        new_particle.contact = copy.deepcopy(self.contact)
        new_particle.ages = copy.deepcopy(self.ages)
        new_particle.age = self.age
        self.manager.num_particles += 1
        self.manager.particle_index[new_particle.ID] = new_particle
        new_particle.route = copy.deepcopy(self.route)
        return new_particle

    def __del__(self):
        """
        This function deletes the particle and increments the deleted_particles count.
        """

        self.manager.deleted_particles += 1

    def get_output(self):
        """
        get_output returns a tuple that contains the data stored in the particle. can be used to read out at the end
        of the particle's journey, or query along the way for testing.

        :return: a tuple containing the particle's ID, time, age, container name, contact, and ages.
        """

        contact_list = []
        age_list = []
        contact_keys = self.contact.keys()
        output = [self.ID, self.time, self.age, self.container.name]
        for key in contact_keys:
            contact_list.append([key, self.contact[key]])
        output.append(contact_list)
        for pipe in self.ages.keys():
            age_list.append([pipe, self.ages[pipe]])
        output.append(age_list)
        if(self.manager.decay_active_free_chlorine):
            output.append(self.free_chlorine)
        if(self.manager.decay_active_monochloramine):
            output.append(self.hypochlorous_acid)
            output.append(self.ammonia)
            output.append(self.monochloramine)
            output.append(self.dichloramine)
            output.append(self.iodine)
            output.append(self.docb)
            output.append(self.docbox)
            output.append(self.docw)
            output.append(self.docwox)
            output.append(self.chlorine)

        return output

class Pipe:
    """
    the pipe class is basically a tree data structure, but it is an n-way tree. on top of that, each pipe has properties
    necessary for plumbing, such as a diameter, material type, length, diameter, cross-sectional-area (CSA) and an activated
    flag. this last one is used to track whether the pipe is part of a series of pipes that are currently flowing, or
    whether it contains stagnant water.
    """

    def __init__(self, name, length, width, material, parent, d_inf, alpha, manager, free_chlorine_lambda, kv1_lambda, kv2_lambda, kv3_lambda, kv5_lambda, kv7_lambda, doc1_lambda, doc2_lambda):
        """
        Pipe Constructor

        :param name: the name of the pipe.
        :param length: the length of the pipe.
        :param width: the width of the pipe.
        :param material: the material of the pipe.
        :param parent: the parent pipe of the pipe.
        :param d_inf: the d_inf value of the pipe.
        :param alpha: the alpha value of the pipe.
        :param manager: the particle manager object.
        :param free_chlorine_lambda: the free chlorine lambda value of the pipe.
        :param kv1_lambda: the kv1 lambda value of the pipe.
        :param kv2_lambda: the kv2 lambda value of the pipe.
        :param kv3_lambda: the kv3 lambda value of the pipe.
        :param kv5_lambda: the kv5 lambda value of the pipe.
        :param kv7_lambda: the kv7 lambda value of the pipe.
        :param doc1_lambda: the doc1 lambda value of the pipe.
        :param doc2_lambda: the doc2 lambda value of the pipe.
        """

        global pipe_index
        self.manager = manager
        self.name = name
        self.length: float = length * 12
        self.width: float = width # in inches
        self.radius = self.width / 2
        self.material: str = material
        self.parent: Pipe = parent
        self.d_inf: float = d_inf / self.manager.timestep # Set to 0.01946 in initial integration.
        self.alpha: float = alpha / self.manager.timestep # set to 114 in initial integration
        self.free_chlorine_lambda: float = free_chlorine_lambda
        self.kv1_lambda: float = kv1_lambda
        self.kv2_lambda: float = kv2_lambda
        self.kv3_lambda: float = kv3_lambda
        self.kv5_lambda: float = kv5_lambda
        self.kv7_lambda: float = kv7_lambda
        self.doc1_lambda: float = doc1_lambda
        self.doc2_lambda: float = doc2_lambda
        self.area: float = math.pi * math.pow((self.radius), 2) #cross-sectional-area
        self.children: list[Pipe] = []
        self.is_active = False
        self.activity = 0
        self.type = "pipe"
        self.flow_rate: int = 0  # gallons per minute
        self.flow: float = 0  # gallons per time unit
        pipe_index[self.name] = self
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
        Function to track activations for a pipe. if activity is positive,
        one or more endpoints downstream from this pipe are active (flowing)
        so this pipe contains flowing water.
        """

        self.activity += 1
        self.set_activity()

    def deactivate(self):
        """
        Does not actually deactivate the pipe, but decrements activity when
        an endpoint is shut off.
        """
        self.activity -= 1
        self.set_activity()

    def set_activity(self):
        """
        If activity is nonpositive, deactivates pipe (no downstream endpoints are flowing).
        pipe contains stagnant water.
        """

        if self.activity > 0:
            self.is_active = True
        else:
            self.is_active = False

    def create_child(self,name, length, diameter, material):
        """
        This function is used by the builder. creates a pipe and inserts it as a child
        of the parent pipe, with this pipe as the parent of the child pipe.

        :param name: the name of the pipe.
        :param length: the length of the pipe.
        :param diameter: the diameter of the pipe.
        :param material: the material of the pipe.
        """

        pipe_child = Pipe(name, length, diameter, material, self)
        self.children.append(pipe_child)
        return pipe_child

    def create_end(self, name):
        """
        This function is used by the builder to create an endpoint as a child the current pipe object.

        :param name: the name of the endpoint.
        :return: the endpoint object.
        """

        pipe_end = Endpoint(self, name)
        self.children.append(pipe_end)
        return pipe_end

    def select_child(self):
        """
        This function randomly selects from available active child pipes and returns the selected child.
        used to randomly assign particle paths at branches down the pipe, but only along branches with
        active flow.

        :return: a randomly selected child pipe object.
        """

        selected = None
        candidates = []
        for child in self.children:
            if child.is_active:
                candidates.append(child)
        if len(candidates) > 0:
            selected = random.choice(candidates)
        return selected

    def peek_helper(self, dim, depth):
        """
        Compiles a list where each node reports it's depth in the tree, returns that list.

        :param dim: the list to be compiled.
        """

        dim.append(depth)
        for each in self.children:
            each.peek_helper(dim, depth + 1)
        return dim

    def peek_children(self):
        """
        returns the depth of the tree, and the maximum number of nodes at the same depth.
        used for establishing the size of the grid to lay out the graph on.

        :return: the depth of the tree, and the maximum number of nodes at the same depth.
        """

        if self.parent != None:
            return self.parent.peek_children()
        dim = []
        dim = self.peek_helper(dim, 0)
        data = collections.Counter(dim)
        height = data.most_common(1)[0][1] # most_common returns a tuple with (mode, frequency)
        depth = max(dim)
        return depth, height
    
    def generate_pipe_net(self):
        """
        This function creates a list of all pipes in the network to calculate total volume for volume-based density calculations.
        """

        if self.children is not None:
            for child in self.children:
                # Append non-root nodes to pipe net.
                if child is not None:
                    self.manager.pipe_net.append(child)
                    child.generate_pipe_net()
                # Append root node to pipe net.
                elif self.parent is None:
                    self.manager.pipe_net.append(self)


    def generate_tree(self):
        """
        this function creates and returns a list of edges forming a tree based on the current pipes model. This tree is used to
        create a graphical representation of the model.
        """

        if self.children is not None:
            for child in self.children:
                # print("child: ", child.name)
                if child is not None and child.type != "endpoint":
                    level = [self.name, child.name]
                    self.manager.edge_list.append(level)
                    child.generate_tree()
                elif self.parent is None:
                        level = ['Base', self.name]
                        self.manager.edge_list.append(level)
                        if(child.type == "endpoint"):
                            self.manager.endpoint_list.append(child.name)
                elif child.type == "endpoint":
                    self.manager.endpoint_list.append(child.name)
                
    def show_tree(self, path, age_dict):
        """
        Take list of edges and creates an igraph tree and visual representation. Graph edges are labeled with (Pipe name, average age))
        The graph is saved as graph_scaled.png and takes on a tree structure of the pipe network.

        :param path: the path to save the graph to.
        :param age_dict: a dictionary of the ages of the particles.
        """
        # print("edge list: ", self.manager.edge_list)
        # for child in self.children:
        #     print(child.name)
        pipe_edges = ['Base']
        for edge in self.manager.edge_list:
            for num, pipe in enumerate(edge):
                if pipe not in pipe_edges:
                    pipe_edges.append(pipe)
                    edge[num] = pipe_edges.index(pipe)
                else:
                    edge[num] = pipe_edges.index(pipe)
        
        if self.manager.edge_list[0][0] != 0:
            self.manager.edge_list.insert(0, [0,1])
        
        g = Graph(edges = self.manager.edge_list)
        pipe_edges.pop(0)
        ages = [0.0] * len(pipe_edges)
        for entry in age_dict.keys():
            ages[pipe_edges.index(entry)] = round(age_dict[entry][0] / age_dict[entry][1], 2)
        
        x = 0
        
        for i in range(1, len(pipe_edges) + 1):
                if(g.degree(i) == 1):
                    g.vs(i)["label"] = self.manager.endpoint_list[x]
                    g.vs(i)["color"] = "blue"
                    x += 1
        
        pipe_tuples = zip(pipe_edges, ages)
        g.es["pipe_tuples"] = list(pipe_tuples)
        g.es["label"] = g.es["pipe_tuples"]
        plot(g, "static/plots/graph_scaled.png", bbox = (800,800), margin = 150, layout= g.layout_reingold_tilford(root=[0]))
        plot(g, path, bbox = (800,800), margin = 150, layout= g.layout_reingold_tilford(root=[0]))

class Endpoint(Pipe):
    """
    the endpoint class is the control class for the pipe and initiates or ends flow events, sets flow rates,
    and triggers activation for all other pipes upstream from it. inherits from pipe.  
    """

    def __init__(self, parent, name, manager):
        """
        constructor function is simplified from the standard pipe because it has no need for usual pipe properties
        such as storing and tracking position of particles.

        :param parent: the parent pipe of the endpoint.
        :param name: the name of the endpoint.
        :param manager: the particle manager object.
        """
        
        super().__init__(name, 0, 0, None, parent, 0, 0, manager, 0, 0, 0,0, 0, 0, 0, 0)
        self.type = "endpoint"

    def create_child(self, name, length, diameter, material):
        """
        overrides the function in the parent class to produce an error and otherwise do nothing
        endpoints should not have pipes downstream from them.

        :param name: the name of the pipe.
        :param length: the length of the pipe.
        :param diameter: the diameter of the pipe.
        :param material: the material of the pipe.
        """

        print("Cannot create child pipes past an endpoint.")
        pass

    def create_end(self, name):
        """
        endpoints should not have more endpoints downstream from them. overrides the pipe class to
        instead produce an error and otherwise do nothing.

        :param name: the name of the endpoint.
        """
        
        print("Cannot create endpoint past an endpoint.")
        pass

    def activate_pipes(self, new_flow_rate=None):
        """
        Function to increase activation for self and upstream pipes to make water flow possible.

        :param new_flow_rate: the new flow rate of the pipe.
        """
        
        self.manager.flow_num += 1
        self.activate()
        if new_flow_rate is not None:
            self.update_flow_rate(new_flow_rate)
        else:
            self.update_flow_rate(self.flow_rate)
        parent_pipe = self.parent
        while parent_pipe is not None:
            parent_pipe.activate()
            parent_pipe = parent_pipe.parent

    def deactivate_pipes(self):
        """
        Deactivates self and reduces activation for upstream pipes.   
        """

        self.deactivate()
        self.update_flow_rate(0)
        parent_pipe = self.parent
        while parent_pipe is not None:
            parent_pipe.deactivate()
            parent_pipe = parent_pipe.parent

    def update_flow_rate(self, new_flow_rate: float):
        """
        Dictate the flow rates through all upstream pipes.
        function to change the flow rate of this pipe. currently, the endpoint flow rates

        :param new_flow_rate: the new flow rate of the pipe.
        """
        
        flow_rate_change = new_flow_rate - self.flow_rate
        flow_change_per_timestep = flow_rate_change / self.manager.timestep
        self.flow_rate = new_flow_rate
        self.flow = new_flow_rate / self.manager.timestep
        parent_pipe = self.parent
        while parent_pipe is not None:
            parent_pipe.flow_rate += flow_rate_change
            parent_pipe.flow += flow_change_per_timestep
            if not parent_pipe.flow_rate >= 0:
                if parent_pipe.flow_rate > (-1*self.manager.tolerance):
                    self.flow = 0
                    self.flow_rate = 0
                else:
                    print("negative flow rate error: pipe ", parent_pipe.name, "has flow rate of", parent_pipe.flow_rate)
            parent_pipe = parent_pipe.parent

    def update_pipe_flow_rates(self, old_flow_rate: float):
        """
        when deactivating, we want to decrease the flow rate of all the parent pipes by the
        flow rate of the endpoint that has deactivated (so we instead update the flow rates of all of the parent pipes to subtract the flow)

        :param old_flow_rate: the old flow rate of the pipe.
        """

        global timestep
        flow_rate_change = self.flow_rate - old_flow_rate
        flow_change_per_timestep = flow_rate_change / timestep
        parent_pipe = self.parent
        while parent_pipe is not None:
            parent_pipe.flow_rate += flow_rate_change
            parent_pipe.flow += flow_change_per_timestep
            parent_pipe = parent_pipe.parent

def main():
    pass

if __name__ == "__main__":
    main()