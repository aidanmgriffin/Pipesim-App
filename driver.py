"""
This module contains the driver class, which is responsible for running the simulation.
"""

import os
import csv
import math
import time
import copy
import cairo
import random
import builder
import particles
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
from joblib import Parallel, delayed

class ExecutionArguments:
    """
    simple container object to store configuration options for simulation execution.
    note that it performs no validation on input and may be created with improper values,
    missing values, or incorrect types.
    """

    def __init__(self,
                 settingsfile = None,
                 modelfile = None,
                 presetsfile = None,
                 pathname = None,
                 active_hours = None,
                 activation_range = None,
                 length = None,
                 density = None,
                 diffuse: bool = False,
                 diffuse_stagnant: bool = False,
                 diffuse_advective: bool = False,
                 molecular_diffusion_coefficient = None,
                 instructions = None,
                 decay_free_chlorine_status = False,
                 decay_monochloramine_status = False,
                 starting_particles_free_chlorine_concentration = None,
                 injected_particles_free_chlorine_concentration = None,
                 decay_monochloramine_dict = None,
                 groupby_status = None,
                 timestep_group_size = 1,
                 ):
        self.settingsfile = settingsfile
        self.modelfile = modelfile
        self.presetsfile = presetsfile
        self.pathname = pathname
        self.active_hours = active_hours
        self.activation_range = activation_range
        self.length = length
        self.density = density
        self.molecular_diffusion_coefficient = molecular_diffusion_coefficient
        self.instructions = instructions
        self.diffuse = diffuse
        self.decay_free_chlorine_status = decay_free_chlorine_status
        self.decay_monochloramine_status = decay_monochloramine_status
        self.starting_particles_free_chlorine_concentration = starting_particles_free_chlorine_concentration
        self.injected_particles_free_chlorine_concentration = injected_particles_free_chlorine_concentration
        self.decay_monochloramine_dict = decay_monochloramine_dict
        self.diffuse_advective = diffuse_advective
        self.diffuse_stagnant = diffuse_stagnant
        self.groupby_status = groupby_status
        self.timestep_group_size = int(timestep_group_size)
        self.plt = None

class Graphing:
    """
    The graphing functionality has been broken into it's own class to make it easier to call the graphing functions multiple times with different parameters.
    now we can make the same graph at different resolution scales. The smaller one is displayed in the app, while the larger one is saved to the hard drive
    and can be used for later review. It has a higher level of precision because it is a much higher resolution file.
    """

    def __init__(self, queue):
        """
        initializes a new graphing class instance when provided with a reference to the process messaging queue

        :param queue: The queue to be used for messaging.
        """

        self.Queue = queue
        self.step = 1
        self.line_styles = ["-", "--", "-.", ":"]  # also "" is none
        self.line_markers = [".", "o", "v", "^", "<", ">", "p", "P", "*", "X", "D"]
        self.colors = mcolors.get_named_colors_mapping()
        self.line_colors = list(self.colors.keys())
        for no_vis_color in ["white", "w", "snow", "whitesmoke", "seashell", "floralwhite", "ivory", "ghostwhite", "xkcd:pale lilac"]:
            self.line_colors.remove(no_vis_color)

    def select_color(self):
        """
        Returns a random color from among the available color options (all named colors in matplotlib.colors)

        :return: A random color from among the available color options (all named colors in matplotlib.colors)
        """

        selected = random.choice(self.line_colors)
        self.line_colors.remove(selected)
        return selected

    def graph_age(self, filename, particle_info, counter, flow_list, free_chlorine_decay_status, step):
        """
        Creates a new particle age graph, saves the image, and puts the filepath in the message queue. 
        Seperated by display and log filename due to Flask's req for images to be placed in static folder.

        :param filename: The name of the file to be created.
        :param particle_info: The dictionary of particles to be written to the file. Contain expulsion information for each particle.
        :param counter: The timer for the simulation.
        :param flow_list: The list of flow rates for each endpoint.
        :param free_chlorine_decay_status: The status of free chlorine decay.
        """
        

        self.step = (1 / step) * 60

        age_display = './static/plots/age_graph.png'
        concentration_display = './static/plots/concentration_graph.png'
        flows_display ='./static/plots/flow_graph.png'
        filename_concentration = filename + '/concentration_graph.png'
        filename_large = filename + '/age_graph_large.png'
        filename_standard = filename + '/age_graph.png'
        filename_flows = filename + '/flow_graph.png'

        self.graph_helper([16,12], 300, filename_large, particle_info, counter)
        self.graph_helper([8,6], 92, filename_standard, particle_info, counter)
        self.graph_helper([8,6], 92, age_display, particle_info, counter)
        
        self.flow_graph_helper([8,6], 92, filename_flows, particle_info, counter, flow_list)
        self.flow_graph_helper([8,6], 92, flows_display, particle_info, counter, flow_list)
      
        if(free_chlorine_decay_status == True):
            self.concentration_graph_helper([8,6], 92, concentration_display, particle_info, counter)
            self.concentration_graph_helper([8,6], 92, filename_concentration, particle_info, counter) 

        send = ("graph_completed", filename)
        self.Queue.put(send)

    def graph_helper(self, graph_size, graph_resolution, filename, particle_info, timer):
        """
        assists graph_age by creating the actual graph image according to parameters specified in graph_age.
        typically, this is called twice to produce a low-resolution graph and a high-resolution graph.

        :param graph_size: The size of the graph to be created.
        :param graph_resolution: The resolution of the graph to be created.
        :param filename: The name of the file to be created.
        :param particle_info: The dictionary of particles to be written to the file. Contain expulsion information for each particle.
        :param timer: The timer for the simulation.
        """

        max_time = 0
        max_age = 0
        particle_data = particle_info
        # print("particle data: ", particle_data)
        fig = plt.figure(figsize = graph_size, dpi=graph_resolution)
        xy = fig.add_subplot(111)
        data = [d for d in particle_data.values()]
        names = [n for n in particle_data.keys()]
        legend_names = []
        legend_lines = []

        for i in range(len(data)):
            element = data[i]
            name = names[i]
            x = list(map(lambda a: a[0], element))
            y = list(map(lambda b: b[2], element))
            line = Line2D(x,y)
            line.set_linestyle("")
            line.set_marker(self.line_markers[1])
            line.set_markeredgewidth(0.0)
            line.set_markerfacecolor(self.select_color())
            line.set_markersize(3.0)
            xy.add_line(line)
            max_x = max(x)
            max_y = max(y)
            max_time = max(max_x, max_time)
            max_age = max(max_y, max_age)
            legend_names.append(name)
            legend_lines.append(line)
            i += 1

        # print("max age: ", max_age, "time: ", timer.get_time())
        xy.legend(legend_lines, legend_names)
        xy.set_ylim(0, max_age * 1.1)
        xy.set_xlim(0, max_age * 1.1)
        xy.set_xlim(0, timer.get_time())
        xy.set_xlabel("Simulation Time (%s)" % self.step)
        xy.set_ylabel("Expelled Particle Age")
        try:
            plt.savefig(filename, facecolor='w', edgecolor='w',
                   orientation='portrait', format="png", pad_inches=0.1)
            self.plt = plt

        except:
            print("graph_helper called before containing folder has been created! Unable to create graph.")
            pass

    def flow_graph_helper(self, graph_size, graph_resolution, filename, particle_flow_data, timer, flow_list):
        """
        assists graph_flow by creating the actual graph image according to parameters specified in graph_flow.
        typically, this is called twice to produce a low-resolution graph and a high-resolution graph.

        :param graph_size: The size of the graph to be created.
        :param graph_resolution: The resolution of the graph to be created.
        :param filename: The name of the file to be created.
        :param particle_flow_data: The dictionary of particles to be written to the file. Contain expulsion information for each particle.
        :param timer: The timer for the simulation.
        """
        
        max_flow_rate = 0
        fig = plt.figure(figsize=graph_size, dpi=graph_resolution)
        xy = fig.add_subplot(111)
        data = [d for d in flow_list.values()]
        names = [n for n in flow_list.keys()]
        legend_names = []
        legend_lines = []
        for i, flow in enumerate(data):
            x = []
            y = []
            name = names[i]
            for j in flow:
                x.append(j[0])
                y.append(j[1])

            line = Line2D(x, y)
            line.set_linestyle("")
            line.set_marker(self.line_markers[1])
            line.set_markeredgewidth(0.0)
            line.set_markerfacecolor(self.select_color())
            line.set_markersize(3.0)
            xy.add_line(line)
            max_y = max(y)
            max_flow_rate = max(max_y, max_flow_rate)
            legend_names.append(name)
            legend_lines.append(line)
        xy.legend(legend_lines, legend_names)
        xy.set_ylim(0, max_flow_rate * 1.1)
        xy.set_xlim(0, timer.get_time())
        xy.set_xlabel("Simulation Time (%s)" % self.step)
        xy.set_ylabel("Flow Rate (Gallons per Minute)")
        try:
            plt.savefig(filename, facecolor='w', edgecolor='w',
                        orientation='portrait', format="png", pad_inches=0.1)
            self.plt = plt
        except:
            print("flow_graph_helper called before containing folder has been created! Unable to create graph.")
            pass

    def concentration_graph_helper(self, graph_size, graph_resolution, filename, particle_info, timer):
        """
        Creates an expelled particle free chlorine concentration graph, saves the image, and puts the filepath in the message queue.

        :param graph_size: The size of the graph to be created.
        :param graph_resolution: The resolution of the graph to be created.
        :param filename: The name of the file to be created.
        :param particle_info: The dictionary of particles to be written to the file. Contain expulsion information for each particle.
        :param timer: The timer for the simulation.
        """

        max_time = 0
        max_concentration = 0
        particle_data = particle_info
        fig = plt.figure(figsize = graph_size, dpi=graph_resolution)
        xy = fig.add_subplot(111)
        data = [d for d in particle_data.values()]
        names = [n for n in particle_data.keys()]
        legend_names = []
        legend_lines = []
        for i in range(len(data)):
            particle = data[i]
            name = names[i]
            x = list(map(lambda a: a[0], particle))
            y = list(map(lambda b: b[3], particle))
            line = Line2D(x,y)
            line.set_linestyle("")
            line.set_marker(self.line_markers[1])
            line.set_markeredgewidth(0.0)
            line.set_markerfacecolor(self.select_color())
            line.set_markersize(3.0)
            xy.add_line(line)
            max_x = max(x)
            max_y = max(y)
            max_time = max(max_x, max_time)
            max_concentration = max(max_y, max_concentration)
            legend_names.append(name)
            legend_lines.append(line)
            i += 1

        xy.legend(legend_lines, legend_names)
        xy.set_ylim(0, max_concentration * 1.1)
        xy.set_xlim(0, timer.get_time())
        xy.set_xlabel("Simulation Time (%s)" % self.step)
        xy.set_ylabel("Expelled Particle Concentration (Percentage)")
        try:
            plt.savefig(filename, facecolor='w', edgecolor='w',
                   orientation='portrait', format="png", pad_inches=0.1)
        except:
            print("graph_helper called before containing folder has been created! Unable to create graph.")
            pass
    
    def write_modifier_bins(self, filename, modifier_values):
        """
        Plot a histogram of all particle modifers undertaken through diffusion/dispersion as particles undergo the simulation.
        
        :param filename: The name of the file to be created.
        :param modifier_values: The values of the particle modifiers that have been undertaken through diffusion/dispersion.
        """

        total = 0
        num_modifiers = 0
        for modifier in modifier_values:
            total += modifier
            num_modifiers += 1
        
        color = self.select_color()
        try:
            plt.hist(modifier_values, bins=60, color=color, ec=color, edgecolor='black')
            plt.title("Mean: " + str(total / num_modifiers))
            plt.savefig(filename + '.png', format='png')
        except:
            pass
    
    def write_expel_bins(self, filename, mean, variance, values):
        """
        Create a histogram displaying the exit time of all particles that have been expelled from the system. This should closely replicate the curve created by Dr. Ginn's model.
        
        :param filename: The name of the file to be created.
        :param mean: The mean of the particles that have been expelled from the system.
        :param variance: The variance of the particles that have been expelled from the system.
        :param values: The values of the particles that have been expelled from the system.
        """

        fig = plt.figure()
        total = 0
        num_values = 0
        new_values = []

        print("values: ", values)
        for value in list(values.values())[0]:
            new_values.append(value[2])
 
        for value in new_values:
            total += value
            num_values += 1

        top_values = new_values
        color = self.select_color()
        try:
            plt.hist(top_values, bins=60, color=color, ec=color, density=True, edgecolor='black')
        except Exception as e:
            raise Exception(e)

        try:
            plt.title("Mean: " + str(round(mean, 4)) + "  NP Mean: " + str(round(np.mean(new_values), 4)))
            fig.text(0.5, 0.04, "Variance: " + str(round(variance, 4)) + "  NP Variance: " + str(round(np.var(new_values), 4)), horizontalalignment='center')
        except:
            print("Error generating mean for expel bins.")
            pass
        plt.savefig(filename + '.png', format='png')

def movement_update(timestep0, timestep, root, density, instructions, max_time, keys, time_since, time_since_starts, endpoints, manager, counter, add_activation, sim_endpoint_preset, progress_update, functions):
        # print(timestep, drive_vars.max_time)
        # for timestep in range(0, self.max_time):
        functions.start_time = progress_update(functions.start_time, max_time, timestep)
        # TODO: multiprocessing
        # print("update")
        # print("movement update" , manager.particle_index)
        # print("move expelled: ", manager.expended_particles)

        timestep0[0] += 1
        for key in keys:
            endpoint = endpoints[key]
            actions = instructions[key]
            if timestep >= time_since_starts[key]:
                if key not in time_since:
                    time_since[key] = 0
                else: 
                    time_since[key] += 1 
            if len(actions) > 0:
                first_action = actions[0]
                if timestep == first_action[0]:
                    first_action = actions.pop(0)
                    length = first_action[1] - first_action[0]
                    add_activation(key, length)
                    if not endpoint.is_active:
                        endpoint.activate_pipes(first_action[2])
                    else:
                        endpoint.update_flow_rate(first_action[2])
            else:
                pass

        # print("is root active? ", root.is_active)
        if root.is_active:
            manager.add_particles(density, root)
        counter.increment_time()
        # print("time: ", counter.get_time(), timestep0)
        manager.update_particles(time_since)
        for endpoint in endpoints.values():
            sim_endpoint_preset(endpoint)
        
        # print("timer: ", counter.get_time(), len(manager.particle_index), len(manager.expended_particles))
        # return manager, counter
        # print(timestep)
        # return 4

class Supplemental:
    def __init__(self, manager):
        self.start_time = 0
        self.manager = manager

        # the remaining activation times for active endpoints
        self.activations = {}

    def get_activation(self, endpointName):
        """
        this function returns the value of the remaining time for a specific endpoint
        or -1 if the endpoint has not previously been activated (and sets the activation time
        to -1)

        :param endpointName: The name of the endpoint to be retrieved.
        :return: The remaining activation time for the endpoint.
        """

        activation_time = self.activations.get(endpointName)
        if activation_time is None:
            activation_time = -1
            self.activations[endpointName] = -1
        return activation_time
    
    def add_activation(self, endpointName:str, length:int):
        """
        this function adds an activation for an endpoint according to the activation time indicated.
        if the endpoint is already active, adds to the existing activation time.

        :param endpointName: The name of the endpoint to be activated.
        :param length: The length of time the endpoint should be active.
        """

        activation_time = self.activations.get(endpointName)
        if activation_time is None or activation_time <= 0:
            activation_time = 0
            self.activations[endpointName] = activation_time + length
        else:
            self.activations[endpointName] = activation_time + length
        return self.activations[endpointName]
    
    def depreciate_activation(self, endpointName):
        """
        This function retrieves the remaining activation time for an endpoint
        and deprecates it if it is positive, or sets it to -1 if nonpositive.
        -1 is used as the key that signifies that the endpoint is in inactive state

        :param endpointName: The name of the endpoint to be depreciated.
        :return: The remaining activation time for the endpoint.
        """

        active = self.activations.get(endpointName)
        if active is not None and active > 0:
            active -= 1
            self.activations[endpointName] = active
        elif active <= 0:
            self.activations[endpointName] = active =  -1
        return active
    
    def sim_endpoint_preset(self, endpoint):
        """
        This function simulates an endpoint while in preset mode. this function is simplified
        since it does not handle endpoint activation. particle flow calculations have also been
        removed from this function because they have been removed from pipes.

        :param endpoint: The endpoint to be simulated.
        """

        activation_time = self.get_activation(endpoint.name)
        if activation_time > 0:
            self.depreciate_activation(endpoint.name)
        elif activation_time == 0:
            endpoint.deactivate_pipes()
            print("dectivating \n\n\n\n")
            self.depreciate_activation(endpoint.name)

    def progress_update(self, start_time, max_time, second):
        """
        This function prints to the console with statistics about the simulation and the current simulation speed.
        it also communicates with the display classes via message passing, allowing for
        the gui to update at regular intervals during execution.

        :param start_time: The time at which the simulation started.
        :param max_time: The maximum time the simulation will run for.
        :param second: Current second
        :return: The time at which the simulation started.
        """

        message = ""
        if start_time == None:
            start_time = time.time()

        if second == 0:
            message = "Simulation started."
            send = ("progress_update", message)
            # self.Queue.put(send)

        if second % 1000 == 0 and second > 0:
            end_time = time.time()
            
            elapsed = end_time - start_time
            line1 = "Simulating Timestep " + str(second) + " of " + str(max_time) + " " + str(start_time) + " " + str(end_time) + f" at a rate of 1000 tics per {elapsed:0.4f} seconds.\n"
            message += line1
            pipe_particles = len(self.manager.particle_index)
            expelled_particles = len(self.manager.expended_particles)
            line2 = "There are currently {} particles in the pipe network and {} particles expelled.".format(
                    pipe_particles, expelled_particles)
            message += line2

            with open("static/update-text.txt", "w") as update_text:
                update_text.write(message)
            print(message)
            send = ("progress_update", message)
            # self.Queue.put(send)
            send = ("status_update", self.manager.output_status())
            # self.Queue.put(send)
            start_time = time.time()

        return start_time

class Driver:
    """
    The simulation driver has been encapsulated in a class to make it easier to separate one simulation
    run from the next and simpler to access from other modules.
    """

    def __init__(self, queue = None, timer = None, step = None):
        """
        Establishes initial variables for the simulation.
        """

        # Global values
        self.Queue = queue
        self.ONE_DAY = 0
        self.WORK_START = 0
        self.WORK_END = 0
        self.TIME_STEP = 0
        self.HOUR_LENGTH = 0

        # Global Pipe Model Variables
        self.root = None # First node of the pipe network.
        self.endpoints = None # List of all endpoints (taps).
        self.actives = None # List of ACTIVE endpoints.

        # Global List Variables - Group Output
        self.FCL_MCM = ["AverageAge", "FreeChlorine", "HypochlorousAcid", "Ammonia", "Monochloramine", "Dichloramine", "Iodine", "DOCb", "DOCbox", "DOCw", "DOCwox", "Chlorine", ""]
        self.FCL = ["AverageAge", "FreeChlorine", ""]
        self.MCM = ["AverageAge", "HypochlorousAcid", "Ammonia", "Monochloramine", "Dichloramine", "Iodine", "DOCb", "DOCbox", "DOCw", "DOCwox", "Chlorine", ""]
        self.AGE = ["AverageAge", ""]
        
        # Set step to 1 if not specified
        if step == None:
            step = 1

        self.set_timestep(step)
        self.mode = step #DEPRECATED?
            
        self.rand_low = 1
        self.rand_high = 5

        # # Activations stores the remaining activation times for active endpoints
        # self.activations = {}

        # Flowrates stores the current flow rate for all endpoints (endpoints only flow when active, but have their flow rate always set)
        self.flowrates = {}

        # Stores the activation chance (between 0 and 1) for each endpoint
        self.frequencies = {}

        # Stores the flow rate for each endpoint
        self.flow_list = {}

        # Create and assign timer
        if timer == None:
            self.counter = particles.Counter()

        else:
            self.counter = timer

        # print("time: ", self.counter.get_time())

        self.manager = particles.ParticleManager(self.counter)
        self.arguments = ExecutionArguments()

        #parallelization test
        self.max_time = 0
        self.instructions = None
        self.endpoints = None 
        self.root = None
        self.density = None
        self.time_since = None
        self.keys = None
        self.functions = Supplemental(self.manager)

        
    def set_timestep(self, option: int):
        """
        Updates the time step and related variables to allow for computation on seconds, minutes, or hours.

        :param option: The time step option to be set.
        """
        
        step = 1.0 / float(option)
        self.TIME_STEP = step
        self.ONE_DAY = step * 24 * 60 
        self.HOUR_LENGTH = step * 60 


    def dict_from_endpoints(self, endpoints:list):
        """
        Returns a dictionary object with the endpoints as the value, using the endpoint names as a key.

        :param endpoints: The list of endpoints (taps) in the pipe network.
        :return: A dictionary object with the endpoints as the value, using the endpoint names as a key.
        """

        rval = {}
        for item in endpoints:
            rval[item.name] = item
        return rval
    
    def sim_preset(self, root, endpoints, instructions, max_time, density):
        """
        This function controls the simulation. inputs include the root node,
        the list of endpoint nodes, a list including the indexes for endpoint nodes
        to test, the number of seconds to run the simulation for, and the time increment
        class. once the initial variables are set, this function runs the simulation loop for the specified duration
        only runs for preset mode, since the activations are handled differently.

        :param root: The root node of the pipe network.
        :param endpoints: The list of endpoints (taps) in the pipe network.
        :param instructions: The list of instructions for the simulation.
        :param max_time: The maximum time the simulation will run for.
        :param density: The distance between particles in the pipe network.
        """

        endpoints = self.dict_from_endpoints(endpoints)
        # root = root
        # self.density = density
        # self.instructions = instructions
        # self.max_time = max_time
        
        self.start_time = None
        keys = instructions.keys()
        time_since = {}
        time_since_starts = {}
        for instruction in instructions:
            time_since_starts[instruction] = instructions[instruction][0][0]
        
        flow_instructions = copy.deepcopy(instructions)  
        for timestep in range(0, max_time):
            for instruction in flow_instructions:
                try:
                    self.flow_list.setdefault(instruction, [])
                    if timestep >= flow_instructions[instruction][0][0] and timestep <= flow_instructions[instruction][0][1]:
                        self.flow_list[instruction].append([timestep, flow_instructions[instruction][0][2]])
                    elif timestep > flow_instructions[instruction][0][1]:
                        flow_instructions[instruction].pop(0)
                        self.flow_list[instruction].append([timestep, instructions[instruction][0][2]])
                except Exception as e: 
                    pass
        
       
        manager = self.manager
        # counter = self.counter

        # functions = self.functions

        
        timestep0 = [0]

        # max_time = 80

        # Parallel(n_jobs=2, prefer = "threads")(delayed(movement_update)(timestep0, timestep, root, density, instructions, max_time, keys, time_since, time_since_starts, endpoints, manager, self.counter, self.functions.add_activation, self.functions.sim_endpoint_preset, self.functions.progress_update, self.functions) for timestep in range(0, max_time))
        # Parallel(n_jobs=4)(delayed(movement_update)(timestep0, timestep, root, density, instructions, max_time, keys, time_since, time_since_starts, endpoints, manager, self.counter, self.functions.add_activation, self.functions.sim_endpoint_preset, self.functions.progress_update, self.functions) for timestep in range(0, max_time))
        
        # print("Expended a: " , self.manager.expended_a)    
        # print("not parallel")
# 
        for i in range(0, max_time):
            # print("time: ", i)
            movement_update(timestep0, i, root, density, instructions, max_time, keys, time_since, time_since_starts, endpoints, manager, self.counter, self.functions.add_activation, self.functions.sim_endpoint_preset, self.functions.progress_update, self.functions)
        
        # print("end 0 t0", timestep0)
        
        # for timestep in range(0, max_time):
        #     start_time = self.progress_update(start_time, max_time, timestep)
        #     # TODO: multiprocessing
        #     for key in keys:
        #         endpoint = endpoints[key]
        #         actions = instructions[key]
        #         if timestep >= time_since_starts[key]:
        #             if key not in time_since:
        #                 time_since[key] = 0
        #             else: 
        #                 time_since[key] += 1 
        #         if len(actions) > 0:
        #             first_action = actions[0]
        #             if timestep == first_action[0]:
        #                 first_action = actions.pop(0)
        #                 length = first_action[1] - first_action[0]
        #                 self.add_activation(key, length)
        #                 if not endpoint.is_active:
        #                     endpoint.activate_pipes(first_action[2])
        #                 else:
        #                     endpoint.update_flow_rate(first_action[2])
        #         else:
        #             pass

        #     if root.is_active:
        #         self.manager.add_particles(density, root)
        #     self.counter.increment_time()
        #     self.manager.update_particles(time_since)
        #     for endpoint in endpoints.values():
        #         self.sim_endpoint_preset(endpoint)

    def write_output(self, filename, particles):
        """
        Function to generate output. takes a filename and a dictionary containing particles
        and writes a csv file containing the information stored in those particles.
        
        :param filename: The name of the file to be created.
        :param particles: The dictionary of particles to be written to the file. Contain expulsion information for each particle.
        """

        results = open(filename, 'w')
        writer = csv.writer(results,'excel')
        arguments = self.arguments

        # Print run information in the first row of the output csv file.
        # writer.writerow(["Pipe Model File: ", arguments.modelfile, "Flow Preset File: ", arguments.presetsfile, "d_m: ", str(self.manager.d_m), "d_inf: ", str(self.root.d_inf), "Granularity: ", self.mode, "Time: ", self.counter.get_time()])

        # Print the header row for the particle data. Varies on inclusion of free chlorine / monochloramine decay.
        if(self.manager.decay_active_free_chlorine and self.manager.decay_active_monochloramine):
            writer.writerow(["ParticleID", "Timestamp", "Age", "OutputEndpoint", "AgeByMaterial", "AgeByPipe", "FreeChlorine", "HypochlorousAcid", "Ammonia", "Monochloramine", "Dichloramine", "Iodine", "DOCb", "DOCbox", "DOCw", "DOCwox", "Chlorine" ])
        elif(self.manager.decay_active_free_chlorine and not self.manager.decay_active_monochloramine):
            writer.writerow(["ParticleID", "Timestamp", "Age", "OutputEndpoint", "AgeByMaterial", "AgeByPipe", "FreeChlorine"])
        elif(self.manager.decay_active_monochloramine and not self.manager.decay_active_free_chlorine):
            writer.writerow(["ParticleID", "Timestamp", "Age", "OutputEndpoint", "AgeByMaterial", "AgeByPipe", "HypochlorousAcid", "Ammonia", "Monochloramine", "Dichloramine", "Iodine", "DOCb", "DOCbox", "DOCw", "DOCwox", "Chlorine" ])
        else:
            writer.writerow(["ParticleID", "Timestamp", "Age", "OutputEndpoint", "AgeByMaterial", "AgeByPipe"])

        for key in particles:
            particle = particles[key]
            data = particle.get_output()
            writer.writerow(data)
        results.close()

    def write_groupby_particles_output(self, filename, particles, groupby):
        """
        Handles Output file that is created when the groupby particles option is selected. 
        This output groups by / averages bundles particles instead of time.

        :param filename: The name of the file to be created.
        :param particles: The dictionary of particles to be written to the file. Contain expulsion information for each particle.
        :param groupby: The number of particles to be grouped together in the output file. Specified in UI.
        """

        results = open(filename, 'w')
        writer = csv.writer(results,'excel')

        # Print run information in the first row of the output csv file.
        # writer.writerow(["Pipe Model File: ", self.arguments.modelfile, "Flow Preset File: ", self.arguments.presetsfile, "d_m: ", str(self.manager.d_m), "d_inf: ", str(self.root.d_inf), "Granularity: ", self.mode, "Time: ", self.counter.get_time()])

        # Print the header row for the particle data. Varies on inclusion of free chlorine / monochloramine decay.
        if(self.manager.decay_active_free_chlorine and self.manager.decay_active_monochloramine):
            writer.writerow(["ParticleID", "Age", "FreeChlorine", "HypochlorousAcid", "Ammonia", "Monochloramine", "Dichloramine", "Iodine", "DOCb", "DOCbox", "DOCw", "DOCwox", "Chlorine" ])
        elif(self.manager.decay_active_free_chlorine and not self.manager.decay_active_monochloramine):
            writer.writerow(["ParticleID", "Age", "FreeChlorine"])
        elif(self.manager.decay_active_monochloramine and not self.manager.decay_active_free_chlorine):
            writer.writerow(["ParticleID", "Age", "HypochlorousAcid", "Ammonia", "Monochloramine", "Dichloramine", "Iodine", "DOCb", "DOCbox", "DOCw", "DOCwox", "Chlorine" ])
        else:
            writer.writerow(["ParticleID", "Age"])

        for key in range(0, len(particles), groupby):
            sum_time = 0
            sum_free_chlorine = 0
            sum_hypochlorous_acid = 0
            sum_ammonia = 0
            sum_monochloramine = 0
            sum_dichloramine = 0
            sum_iodine = 0
            sum_DOCb = 0
            sum_DOCbox = 0
            sum_DOCw = 0
            sum_DOCwox = 0
            sum_chlorine = 0

            for i in range(groupby):
                if (key + i) < len(particles):
                    try:
                        particle = particles[key + i]
                    except:
                        break
                    data = particle.get_output()

                    sum_time += data[2]

                    if(self.manager.decay_active_free_chlorine and self.manager.decay_active_monochloramine):
                        sum_free_chlorine += data[6]
                        sum_hypochlorous_acid += data[7]
                        sum_ammonia += data[8]
                        sum_monochloramine += data[9]
                        sum_dichloramine += data[10]
                        sum_iodine += data[11]
                        sum_DOCb += data[12]
                        sum_DOCbox += data[13]
                        sum_DOCw += data[14]
                        sum_DOCwox += data[15]
                        sum_chlorine += data[16]

                    elif(self.manager.decay_active_free_chlorine and not self.manager.decay_active_monochloramine):
                        sum_free_chlorine += data[6]

                    elif(self.manager.decay_active_monochloramine and not self.manager.decay_active_free_chlorine):
                        sum_hypochlorous_acid += data[7]
                        sum_ammonia += data[8]
                        sum_monochloramine += data[9]
                        sum_dichloramine += data[10]
                        sum_iodine += data[11]
                        sum_DOCb += data[12]
                        sum_DOCbox += data[13]
                        sum_DOCw += data[14]
                        sum_DOCwox += data[15]
                        sum_chlorine += data[16]
            
            sum_time /= groupby
            
            if (self.manager.decay_active_free_chlorine and self.manager.decay_active_monochloramine):
                sum_free_chlorine /= groupby
                sum_hypochlorous_acid /= groupby
                sum_ammonia /= groupby
                sum_monochloramine /= groupby
                sum_dichloramine /= groupby
                sum_iodine /= groupby
                sum_DOCb /= groupby
                sum_DOCbox /= groupby
                sum_DOCw /= groupby
                sum_DOCwox /= groupby
                sum_chlorine /= groupby
                writer.writerow([key, sum_time, sum_free_chlorine, sum_hypochlorous_acid, sum_ammonia, sum_monochloramine, sum_dichloramine, sum_iodine, sum_DOCb, sum_DOCbox, sum_DOCw, sum_DOCwox, sum_chlorine])
            
            elif(self.manager.decay_active_free_chlorine and not self.manager.decay_active_monochloramine):
                sum_free_chlorine /= groupby
                writer.writerow([key, sum_time, sum_free_chlorine])

            elif(self.manager.decay_active_monochloramine and not self.manager.decay_active_free_chlorine):
                sum_hypochlorous_acid /= groupby
                sum_ammonia /= groupby
                sum_monochloramine /= groupby
                sum_dichloramine /= groupby
                sum_iodine /= groupby
                sum_DOCb /= groupby
                sum_DOCbox /= groupby
                sum_DOCw /= groupby
                sum_DOCwox /= groupby
                sum_chlorine /= groupby
                writer.writerow([key, sum_time, sum_hypochlorous_acid, sum_ammonia, sum_monochloramine, sum_dichloramine, sum_iodine, sum_DOCb, sum_DOCbox, sum_DOCw, sum_DOCwox, sum_chlorine])
            
            else:
                writer.writerow([key, sum_time])
                
        results.close()

    def write_groupby_time_output(self, filename, particles, groupby):
        """
        Handles Output file that is created when the groupby time option is selected.
        This output groups by / averages particles together by time instead of by particle.

        :param filename: The name of the file to be created.
        :param particles: The dictionary of particles to be written to the file. Contain expulsion information for each particle.
        :param groupby: The amount of time to be grouped together in the output file. Specified in UI.
        """

        # Create the output file.
        results = open(filename, 'w')
        writer = csv.writer(results,'excel')

        # Print run information in the first row of the output csv file.
        # writer.writerow(["Pipe Model File: ", self.arguments.modelfile, "Flow Preset File: ", self.arguments.presetsfile, "d_m: ", str(self.manager.d_m), "d_inf: ", str(self.root.d_inf), "Granularity: ", self.mode, "Time: ", self.counter.get_time()])

        key = 0
        prev_key = 0
        time_dict = {}
        time_dict.setdefault(0, [])
        tap_list = []
        tap_info = {}
        tap_contents = {}
        tap_count = {}

        for key in range(len(particles)- 1):
            try:
                particle = particles[key]
                data = particle.get_output()

                if data[3] not in tap_list:
                    tap_list.append(data[3])

                tap_contents.setdefault(data[3], {})

                tap_count.setdefault(data[3], {})
                # print("data1: ", data[1], "groupby: ", groupby)
                if data[1]  % groupby == 0:
                    time_dict.setdefault(data[1], [])
                    time_dict[data[1]].append(data)
                    prev_key = data[1]
                else:
                    time_dict[prev_key].append(data)
            except:
                pass
        # print("time dict: ", time_dict.keys())

        # Ensure proper orientation when printing the tap list row in the output groups csv file.
        tap_list_row = ['']
        for tap in tap_list:
            tap_list_row.append(tap)
            if(self.manager.decay_active_free_chlorine and self.manager.decay_active_monochloramine):
                tap_list_row.extend([''] * (len(self.FCL_MCM) - 1))
            elif(self.manager.decay_active_free_chlorine and not self.manager.decay_active_monochloramine):
                tap_list_row.extend([''] * (len(self.FCL) - 1))
            elif(self.manager.decay_active_monochloramine and not self.manager.decay_active_free_chlorine):
                tap_list_row.extend([''] * (len(self.MCM) - 1))    
            else:
                tap_list_row.extend([''] * (len(self.AGE)))

        writer.writerow(tap_list_row)

        # Print the header row for the particle data. Varies on inclusion of free chlorine / monochloramine decay.
        if(self.manager.decay_active_free_chlorine and self.manager.decay_active_monochloramine):
            writer.writerow(['Timestep'] + self.FCL_MCM * len(tap_list))
        elif(self.manager.decay_active_free_chlorine and not self.manager.decay_active_monochloramine):
            writer.writerow(['Timestep'] + self.FCL * len(tap_list))
        elif(self.manager.decay_active_monochloramine and not self.manager.decay_active_free_chlorine):
            writer.writerow(['Timestep'] + self.MCM * len(tap_list))
        else:
            writer.writerow(['Timestep'] + self.AGE * len(tap_list))

        for key in time_dict.keys():
            for i in time_dict[key]:
                try:
                    data = i
                except:
                    break

                tap_contents[data[3]].setdefault('sum_time', 0)
                tap_contents[data[3]]['sum_time'] += data[2]
                tap_count[data[3]].setdefault(key, 0)
                tap_count[data[3]][key] += 1

                if(self.manager.decay_active_free_chlorine and self.manager.decay_active_monochloramine):
                    tap_contents[data[3]].setdefault('sum_free_chlorine', 0)
                    tap_contents[data[3]]['sum_free_chlorine'] += data[6]
                    tap_contents[data[3]].setdefault('sum_hypochlorous_acid', 0)
                    tap_contents[data[3]]['sum_hypochlorous_acid'] += data[7]
                    tap_contents[data[3]].setdefault('sum_ammonia', 0)
                    tap_contents[data[3]]['sum_ammonia'] += data[8]
                    tap_contents[data[3]].setdefault('sum_monochloramine', 0)
                    tap_contents[data[3]]['sum_monochloramine'] += data[9]
                    tap_contents[data[3]].setdefault('sum_dichloramine', 0)
                    tap_contents[data[3]]['sum_dichloramine'] += data[10]
                    tap_contents[data[3]].setdefault('sum_iodine', 0)
                    tap_contents[data[3]]['sum_iodine'] += data[11]
                    tap_contents[data[3]].setdefault('sum_DOCb', 0)
                    tap_contents[data[3]]['sum_DOCb'] += data[12]
                    tap_contents[data[3]].setdefault('sum_DOCbox', 0)
                    tap_contents[data[3]]['sum_DOCbox'] += data[13]
                    tap_contents[data[3]].setdefault('sum_DOCw', 0)
                    tap_contents[data[3]]['sum_DOCw'] += data[14]
                    tap_contents[data[3]].setdefault('sum_DOCwox', 0)
                    tap_contents[data[3]]['sum_DOCwox'] += data[15]
                    tap_contents[data[3]].setdefault('sum_chlorine', 0)
                    tap_contents[data[3]]['sum_chlorine'] += data[16]

                elif(self.manager.decay_active_free_chlorine and not self.manager.decay_active_monochloramine):
                    tap_contents[data[3]].setdefault('sum_free_chlorine', 0)
                    tap_contents[data[3]]['sum_free_chlorine'] += data[6]

                elif(self.manager.decay_active_monochloramine and not self.manager.decay_active_free_chlorine):

                    print("list entries",tap_contents[data[3]], data, len(data))

                    tap_contents[data[3]].setdefault('sum_hypochlorous_acid', 0)
                    tap_contents[data[3]]['sum_hypochlorous_acid'] += data[6]
                    tap_contents[data[3]].setdefault('sum_ammonia', 0)
                    tap_contents[data[3]]['sum_ammonia'] += data[7]
                    tap_contents[data[3]].setdefault('sum_monochloramine', 0)
                    tap_contents[data[3]]['sum_monochloramine'] += data[8]
                    tap_contents[data[3]].setdefault('sum_dichloramine', 0)
                    tap_contents[data[3]]['sum_dichloramine'] += data[9]
                    tap_contents[data[3]].setdefault('sum_iodine', 0)
                    tap_contents[data[3]]['sum_iodine'] += data[10]
                    tap_contents[data[3]].setdefault('sum_DOCb', 0)
                    tap_contents[data[3]]['sum_DOCb'] += data[11]
                    tap_contents[data[3]].setdefault('sum_DOCbox', 0)
                    tap_contents[data[3]]['sum_DOCbox'] += data[12]
                    tap_contents[data[3]].setdefault('sum_DOCw', 0)
                    tap_contents[data[3]]['sum_DOCw'] += data[13]
                    tap_contents[data[3]].setdefault('sum_DOCwox', 0)
                    tap_contents[data[3]]['sum_DOCwox'] += data[14]
                    tap_contents[data[3]].setdefault('sum_chlorine', 0)
                    tap_contents[data[3]]['sum_chlorine'] += data[15]

                    
            for tap in tap_contents.keys():
                tap_info.setdefault(tap, {})
                tap_info[tap].setdefault(key, [])

                try:
                    tap_contents[tap]['sum_time'] /= tap_count[tap][key]
                except:
                    pass

                if (self.manager.decay_active_free_chlorine and self.manager.decay_active_monochloramine):
                    try:
                        tap_contents[tap]['sum_free_chlorine'] /= tap_count[tap][key]
                        tap_contents[tap]['sum_hypochlorous_acid'] /= tap_count[tap][key]
                        tap_contents[tap]['sum_ammonia'] /= tap_count[tap][key]
                        tap_contents[tap]['sum_monochloramine'] /= tap_count[tap][key]
                        tap_contents[tap]['sum_dichloramine'] /= tap_count[tap][key]
                        tap_contents[tap]['sum_iodine'] /= tap_count[tap][key]
                        tap_contents[tap]['sum_DOCb'] /= tap_count[tap][key]
                        tap_contents[tap]['sum_DOCbox'] /= tap_count[tap][key]
                        tap_contents[tap]['sum_DOCw'] /= tap_count[tap][key]
                        tap_contents[tap]['sum_DOCwox'] /= tap_count[tap][key]
                        tap_contents[tap]['sum_chlorine'] /= tap_count[tap][key]
                    except:
                        pass

                    try:
                        tap_info[tap][key].append(tap_contents[tap]['sum_time'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_free_chlorine'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_hypochlorous_acid'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_ammonia'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_monochloramine'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_dichloramine'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_iodine'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_DOCb'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_DOCbox'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_DOCw'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_DOCwox'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_chlorine'])
                    except:
                        tap_info[tap][key].extend([0] * len(self.FCL_MCM))
                    
                elif(self.manager.decay_active_free_chlorine and not self.manager.decay_active_monochloramine):
                    try:
                        tap_contents[tap]['sum_free_chlorine'] /= tap_count[tap][key]
                    except:
                        pass

                    try:
                        tap_info[tap][key].append(tap_contents[tap]['sum_time'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_free_chlorine'])
                    except:
                        tap_info[tap][key].extend([0] * len(self.FCL))


                elif(self.manager.decay_active_monochloramine and not self.manager.decay_active_free_chlorine):
                    try:
                        tap_contents[tap]['sum_hypochlorous_acid'] /= tap_count[tap][key]
                        tap_contents[tap]['sum_ammonia'] /= tap_count[tap][key]
                        tap_contents[tap]['sum_monochloramine'] /= tap_count[tap][key]
                        tap_contents[tap]['sum_dichloramine'] /= tap_count[tap][key]
                        tap_contents[tap]['sum_iodine'] /= tap_count[tap][key]
                        tap_contents[tap]['sum_DOCb'] /= tap_count[tap][key]
                        tap_contents[tap]['sum_DOCbox'] /= tap_count[tap][key]
                        tap_contents[tap]['sum_DOCw'] /= tap_count[tap][key]
                        tap_contents[tap]['sum_DOCwox'] /= tap_count[tap][key]
                        tap_contents[tap]['sum_chlorine'] /= tap_count[tap][key]
                    except:
                        pass

                    try:
                        tap_info[tap][key].append(tap_contents[tap]['sum_time'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_hypochlorous_acid'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_ammonia'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_monochloramine'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_dichloramine'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_iodine'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_DOCb'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_DOCbox'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_DOCw'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_DOCwox'])
                        tap_info[tap][key].append(tap_contents[tap]['sum_chlorine'])
                    except:
                        tap_info[tap][key].extend([0] * len(self.MCM))

                else:

                    try:
                        tap_info[tap][key].append(tap_contents[tap]['sum_time'])
                    except:
                        tap_info[tap][key].append(0)
                        pass

            tap_info_list = []
            for tap in tap_info.keys():
                try:
                    if(self.manager.decay_active_free_chlorine and self.manager.decay_active_monochloramine):
                        tap_info_list.append(tap_info[tap][key][0])
                        tap_info_list.append(tap_info[tap][key][1])
                        tap_info_list.append(tap_info[tap][key][2])
                        tap_info_list.append(tap_info[tap][key][3])
                        tap_info_list.append(tap_info[tap][key][4])
                        tap_info_list.append(tap_info[tap][key][5])
                        tap_info_list.append(tap_info[tap][key][6])
                        tap_info_list.append(tap_info[tap][key][7])
                        tap_info_list.append(tap_info[tap][key][8])
                        tap_info_list.append(tap_info[tap][key][9])
                        tap_info_list.append(tap_info[tap][key][10])
                        tap_info_list.append(tap_info[tap][key][11])
                        tap_info_list.append('')
                    elif(self.manager.decay_active_free_chlorine and not self.manager.decay_active_monochloramine):
                        tap_info_list.append(tap_info[tap][key][0])
                        tap_info_list.append(tap_info[tap][key][1])
                        tap_info_list.append('')
                    elif(self.manager.decay_active_monochloramine and not self.manager.decay_active_free_chlorine):
                        tap_info_list.append(tap_info[tap][key][0])
                        tap_info_list.append(tap_info[tap][key][1])
                        tap_info_list.append(tap_info[tap][key][2])
                        tap_info_list.append(tap_info[tap][key][3])
                        tap_info_list.append(tap_info[tap][key][4])
                        tap_info_list.append(tap_info[tap][key][5])
                        tap_info_list.append(tap_info[tap][key][6])
                        tap_info_list.append(tap_info[tap][key][7])
                        tap_info_list.append(tap_info[tap][key][8])
                        tap_info_list.append(tap_info[tap][key][9])
                        tap_info_list.append(tap_info[tap][key][10])
                        tap_info_list.append('')
                    else:
                        tap_info_list.append(tap_info[tap][key][0])
                        tap_info_list.append('')

                except:
                    pass
            writer.writerow([key] + tap_info_list)

            for tap in tap_list:
                try:
                    tap_contents[tap]['sum_time'] = 0
                    tap_contents[tap]['sum_free_chlorine'] = 0
                    tap_contents[tap]['sum_hypochlorous_acid'] = 0
                    tap_contents[tap]['sum_ammonia'] = 0
                    tap_contents[tap]['sum_monochloramine'] = 0
                    tap_contents[tap]['sum_dichloramine'] = 0
                    tap_contents[tap]['sum_iodine'] = 0
                    tap_contents[tap]['sum_DOCb'] = 0
                    tap_contents[tap]['sum_DOCbox'] = 0
                    tap_contents[tap]['sum_DOCw'] = 0
                    tap_contents[tap]['sum_DOCwox'] = 0
                    tap_contents[tap]['sum_chlorine'] = 0
                except:
                    pass
                
        results.close()

    def write_pipe_ages(self, filename, particles):
        """
        Output file that describes the average age of particles in each pipe.

        :param filename: The name of the file to be created.
        :param particles: The dictionary of particles to be written to the file. Contain expulsion information for each particle.
        :return: A dictionary containing the average age of particles in each pipe. This will be used to create the pipe tree.
        """

        results_file = open(filename, 'w')
        writer = csv.writer(results_file, 'excel')
        age_dict = {}
        endpoint_names = [endpoint.name for endpoint in self.endpoints]
        for key in particles:
            particle = particles[key]
            particle_data = particle.get_output()
            pipe_name = particle_data[3]
            if pipe_name not in endpoint_names:
                age_dict.setdefault(pipe_name, [0,0])
                age_dict[pipe_name][0] += particle_data[1]
                age_dict[pipe_name][1] += 1
        
        # Writes rows with columns containing the pipe name, the total age of particles in that pipe (summed time spent in that pipe value for each particle), the number of particles that have flowed through that pipe,
        # and the result of those two values divided from one another ( assumed to be the average age of particles in that pipe. )
        for entry in age_dict:
            writer.writerow([str(entry), str(age_dict[entry]), str(age_dict[entry][0] / age_dict[entry][1])])
        
        return age_dict

    def exec_preset(self, arguments: ExecutionArguments):
        """
        This function executes the simulation in preset mode. This changes how pipes are activated and enables different
        flow rates for each activation.

        :param arguments: The arguments passed to the simulation.
        """

        try:
            modelfile = arguments.modelfile
            presetsfile = arguments.presetsfile
            density = arguments.density
            pathname = arguments.pathname
            self.manager.diffusion_active = arguments.diffuse
            self.manager.diffusion_active_stagnant = arguments.diffuse_stagnant
            self.manager.diffusion_active_advective = arguments.diffuse_advective
            self.manager.decay_active_free_chlorine = arguments.decay_free_chlorine_status
            self.manager.decay_active_monochloramine = arguments.decay_monochloramine_status
            self.manager.starting_particles_free_chlorine_concentration = arguments.starting_particles_free_chlorine_concentration
            self.manager.injected_particles_free_chlorine_concentration = arguments.injected_particles_free_chlorine_concentration
            self.manager.decay_monochloramine_dict = arguments.decay_monochloramine_dict
            # self.manager.gr = arguments.groupby_status
            # self.manager.timestepGroupSize = arguments.timestep_group_size

            send = ("status_started", "Simulation started.")
            self.Queue.put(send)

            self.manager.set_timestep(self.TIME_STEP)
            self.manager.set_diffusion_coefficient(arguments.molecular_diffusion_coefficient)

            self.arguments = arguments
            try:
                self.root, self.endpoints = builder.build(modelfile, self.manager)
            except Exception as e:
                raise Exception("Error building model. Check model file for errors. [" + str(e) + "]")
            
            self.Queue.put(send)
      
            try:
                max_time, instructions = builder.load_sim_preset(presetsfile)
                max_time, instructions = self.parse_instructions(max_time, instructions)
                
            except Exception as e:
                raise Exception("Error loading preset file. Check preset file for errors. [" + str(e) + "]")
            
            try:
                self.sim_preset(self.root, self.endpoints, instructions, max_time, density)
            except Exception as e:
                raise Exception("Error running simulation. Check uploaded files for errors. [" + str(e) + "]" )
            
            try:
                if not os.path.isdir(pathname):
                    os.mkdir(pathname)
                g = Graphing(self.Queue)
                
                # print("Expelled: ", self.manager.expelled_particle_data)
                g.graph_age(pathname, self.manager.expelled_particle_data, self.counter, self.flow_list, self.manager.decay_active_free_chlorine, self.TIME_STEP)
            except Exception as e:
                raise Exception("Error generating graphs. [" + str(e) + "]") 
            
            try:        
                self.write_output(pathname+"\expelled.csv", self.manager.expended_particles)

                if(self.arguments.groupby_status == 1):
                    self.write_groupby_time_output(pathname+"\expelled_groups.csv", self.manager.expended_particles, self.arguments.timestep_group_size)

                # This function slows everything down considerably, and is not currently used. Generates a particle modifier histogram...
                # if self.manager.diffusionActive:
                #     g.write_modifier_bins(".\static\plots\modifier_histogram", self.manager.bins)
              
                #Calculating mean, var, and skew to be added to the histogram of expelled particles. Designed to validate values of onpipe model.
                fr = list(self.flow_list.values())[0][0][1]
                lengthFeet = self.root.length / 12
                areaFeet = math.pi * math.pow((self.root.radius / 12), 2)
                frCFS = fr / 448.309
                velocity = (frCFS / areaFeet) * 60
                mean = lengthFeet / velocity
                var = (2 * lengthFeet * (self.manager.molecular_diffusion_coefficient /144)) / math.pow(velocity, 3)
                skew = 3 * math.sqrt((2 * (self.manager.molecular_diffusion_coefficient /144)) / (lengthFeet * velocity))
                mean *= self.TIME_STEP
                # g.write_expel_bins(pathname+"\expelled_histogram", mean, var, self.manager.expelled_particle_data)
                # g.write_expel_bins(".\static\plots\expelled_histogram", mean, var,  self.manager.expelled_particle_data)
                ageDict = self.write_pipe_ages(pathname+"\pipe_ages.csv", self.manager.expended_particles)
                self.root.generate_tree()
                self.root.show_tree(pathname+"tree_graph.png", ageDict)

            except Exception as e:
                raise Exception("Error writing output files. Check uploaded files for errors and ensure that the output directory is not open in another program. [" + str(e) + "]" )
            
            send = ("status_completed", "Simulation complete.")
            self.Queue.put(send) 
        except Exception as e:
            raise Exception(e)
        

    def parse_instructions(self, max_time, instructions):
        """
        This function translates the instructions from the instructions file (recorded as minutes)
        into the appropriate time scale (seconds, minutes, or hours) as selected.

        :param max_time: The maximum time of the simulation.
        :param instructions: The dictionary of instructions to be parsed.
        :return: The maximum time of the simulation and the parsed instructions.
        """

        max_time = int(max_time * self.ONE_DAY)
        for key in instructions.keys():
            val = instructions.get(key)
            new_val = []
            for each in val:
                new_val.append((int((each[0]*self.TIME_STEP)), int(each[1]*self.TIME_STEP), each[2]))
            instructions[key] = new_val
        return max_time, instructions

