import os

import builder
import random
import particles
import csv
import time
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
# from multiprocessing import Process, Pool, Queue
import random

# simple container object to store configuration options for simulation execution.
# note that it performs no validation on input and may be created with improper values,
# missing values, or incorrect types.
class execution_arguments:
    def __init__(self,
                 settingsfile = None,
                 modelfile = None,
                 presetsfile = None,
                 pathname = None,
                 active_hours = None,
                 activation_range = None,
                 length = None,
                 density = None,
                 molecularDiffusionCoefficient = None,
                 instructions = None,
                 diffuse: bool = False):
        self.settingsfile = settingsfile
        self.modelfile = modelfile
        self.presetsfile = presetsfile
        self.pathname = pathname
        self.active_hours = active_hours
        self.activation_range = activation_range
        self.length = length
        self.density = density
        self.molecularDiffusionCoefficient = molecularDiffusionCoefficient
        self.instructions = instructions
        self.diffuse = diffuse
        self.plt = None

# The graphing functionality has been broken into it's own class to make it easier to call the graphing functions multiple times with different parameters.
# now we can make the same graph at different resolution scales. The smaller one is displayed in the app, while the larger one is saved to the hard drive
# and can be used for later review. It has a higher level of precision because it is a much higher resolution file.
class graphing:

    # initializes a new graphing class instance when provided with a reference to the process messaging queue
    def __init__(self, queue, mode):
        # self.controller = source
        self.Queue = queue
        self.line_styles = ["-", "--", "-.", ":"]  # also "" is none
        self.line_markers = [".", "o", "v", "^", "<", ">", "p", "P", "*", "X", "D"]
        # self.lowvisibilitycolors = 
        self.colors = mcolors.get_named_colors_mapping()
        self.line_colors = list(self.colors.keys())
        for no_vis_color in ["white", "w", "snow", "whitesmoke", "seashell", "floralwhite", "ivory", "ghostwhite"]:
            self.line_colors.remove(no_vis_color)
        self.mode = mode
        self.mode_name = {1:"Seconds", 2:"Minutes", 3:"Hours"}


    # returns a random color from among the available color options (all named colors in matplotlib.colors)
    def select_color(self):
        selected = random.choice(self.line_colors)
        self.line_colors.remove(selected)
        return selected

    # creates a new particle age graph, saves the image, and puts the filepath in the message queue.
    def graph_age(self, particleInfo, counter, filename="/logs/"):
        age_display = './static/plots/age_graph.png'
        concentration_display = './static/plots/concentration_graph.png'
        filename_concentration = filename + '/concentration_graph.png'
        filename_large = filename + '/age_graph_large.png'
        filename_standard = filename + '/age_graph.png'

        # print("displayname: ", displayname)
        self.graph_helper([16,12], 300, filename_large, particleInfo, counter)
        self.graph_helper([8,6], 92, filename_standard, particleInfo, counter)
        self.graph_helper([8,6], 92, age_display, particleInfo, counter)
        self.concentration_graph_helper([8,6], 92, concentration_display, particleInfo, counter)
        self.concentration_graph_helper([8,6], 92, filename_concentration, particleInfo, counter) #Concentration
        # self.graph_helper([16,12], 300, filename, particleInfo, counter, 1) --- For Larger Graph / Better Quality

        # self.controller.event_generate("<<graph_completed>>", when="tail")
        send = ("graph_completed", filename)
        self.Queue.put(send)

    # assists graph_age by creating the actual graph image according to parameters specified in graph_age.
    # typically, this is called twice to produce a low-resolution graph and a high-resolution graph.
    def graph_helper(self, size, res, filename, particleInfo, counter):
        maxTime = 0
        maxAge = 0
        particleData = particleInfo
        fig = plt.figure(figsize = size, dpi=res)
        xy = fig.add_subplot(111)
        data = [d for d in particleData.values()]
        names = [n for n in particleData.keys()]
        legend_names = []
        legend_lines = []
        for i in range(len(data)):
            element = data[i]
            name = names[i]
            x = list(map(lambda a: a[0], element))
            y = list(map(lambda b: b[1], element))
            line = Line2D(x,y)
            line.set_linestyle("")
            line.set_marker(self.line_markers[1])
            line.set_markeredgewidth(0.0)
            line.set_markerfacecolor(self.select_color())
            line.set_markersize(3.0)
            xy.add_line(line)
            maxX = max(x)
            maxY = max(y)
            maxTime = max(maxX, maxTime)
            maxAge = max(maxY, maxAge)
            legend_names.append(name)
            legend_lines.append(line)
            i += 1

        xy.legend(legend_lines, legend_names)
        xy.set_ylim(0, maxAge * 1.1)
        xy.set_xlim(0, counter.get_time())
        xy.set_xlabel("Simulation Time ({})".format(self.mode_name.get(self.mode)))
        xy.set_ylabel("Expelled Particle Age ({})".format(self.mode_name.get(self.mode)))
        try:
            print("saving ", filename)
            plt.savefig(filename, facecolor='w', edgecolor='w',
                   orientation='portrait', format="png", pad_inches=0.1)
            self.plt = plt
            # plt.show()
        except:
            print("graph_helper called before containing folder has been created! Unable to create graph.")
            pass

    def concentration_graph_helper(self, size, res, filename, particleInfo, counter):
        maxTime = 0
        maxAge = 0
        particleData = particleInfo
        fig = plt.figure(figsize = size, dpi=res)
        xy = fig.add_subplot(111)
        data = [d for d in particleData.values()]
        names = [n for n in particleData.keys()]
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
            maxX = max(x)
            maxY = max(y)
            maxTime = max(maxX, maxTime)
            maxAge = max(maxY, maxAge)
            legend_names.append(name)
            legend_lines.append(line)
            i += 1

        xy.legend(legend_lines, legend_names)
        xy.set_ylim(0, maxAge * 1.1)
        xy.set_xlim(0, counter.get_time())
        xy.set_xlabel("Simulation Time ({})".format(self.mode_name.get(self.mode)))
        xy.set_ylabel("Expelled Particle Concentration (Percentage)".format(self.mode_name.get(self.mode)))
        try:
            print("saving ", filename)
            plt.savefig(filename, facecolor='w', edgecolor='w',
                   orientation='portrait', format="png", pad_inches=0.1)
        except:
            print("graph_helper called before containing folder has been created! Unable to create graph.")
            pass

    
    #temporary testing function to create a csv file and write the average of modifiers on all particles.
    #to determine normal distribution.
    def write_bins(self, filename, bins):
        plt.figure()
        total = 0
        j = 0
        for i in bins:
            total += i
            j += 1
        
        color = self.select_color()
        plt.hist(bins, color=color, ec = color)
        plt.title("Mean: " + str(total / j))
        plt.savefig(filename + '.png', format='png')


# the simulation driver has been encapsulated in a class to make it easier to separate one simulation
# run from the next and simpler to access from other modules.
class Driver:
    #establishes initial variables for the simulation.
    def __init__(self, queue = None, timer = None, step = None):
        if step == None:
            step = 1
        # global variables
        # self.controller = controller # originating window that instantiated driver
        self.Queue = queue
        self.ONE_DAY = 0
        self.WORK_START = 0
        self.WORK_END = 0
        self.TIME_STEP = 0
        self.HOUR_LENGTH = 0
        if timer == None:
            self.counter = particles.counter()
        else:
            self.counter = timer
        self.activation_counter = 0
        self.randLow = 1
        self.randHigh = 5
        # activations stores the remaining activation times for active endpoints
        self.activations = {}
        # flowrates stores the current flow rate for all endpoints
        # (endpoints only flow when active, but have their flow rate always set)
        self.flowrates = {}
        # stores the activation chance (between 0 and 1) for each endpoint
        self.frequencies = {}
        # initializes a random number generator to determine whether to activate a pipe or not.
        random.seed(a=None, version=float)
        self.manager = particles.ParticleManager(self.counter)
        self.preview = None
        self.particles = None
        self.root = None
        self.endpoints = None
        self.actives = None # list of active endpoints
        self.set_time_step(step)
        self.mode = step

    # updates the time step and related variables to allow for computation on seconds, minutes, or hours.
    def set_time_step(self, option: int):
        step = 60 # setting for seconds
        if option == 1:
            step = 60
        elif option == 2:
            step = 1
        elif option == 3:
            step = 1.0 / 60.0
        self.TIME_STEP = step
        self.ONE_DAY = step * 24 * 60
        self.HOUR_LENGTH = step * 60


    # this function adds an activation for an endpoint according to the activation time indicated.
    # if the endpoint is already active, adds to the existing activation time.
    def add_activation(self, endpointName:str, length:int):
        activation_time = self.activations.get(endpointName)
        if activation_time is None or activation_time <= 0:
            activation_time = 0
            self.activations[endpointName] = activation_time + length
        else:
            self.activations[endpointName] = activation_time + length
        return self.activations[endpointName]

    # this function returns the value of the remaining time for a specific endpoint
    # or -1 if the endpoint has not previously been activated (and sets the activation time
    # to -1)
    def get_activation(self, endpointName):
        activation_time = self.activations.get(endpointName)
        if activation_time is None:
            activation_time = -1
            self.activations[endpointName] = -1
        return activation_time

    # this function retrieves the remaining activation time for an endpoint
    # and deprecates it if it is positive, or sets it to -1 if nonpositive.
    # -1 is used as the key that signifies that the endpoint is in inactive state
    def depreciate_activation(self, endpointName):
        active = self.activations.get(endpointName)
        if active is not None and active > 0:
            active -= 1
            self.activations[endpointName] = active
            # print("Endpoint", endpointName, "is active for", active, "seconds")
        elif active <= 0:
            self.activations[endpointName] = active =  -1
            # print("Endpoint", endpointName, "is deactivated")
        return active

    # this function simulates an endpoint while in preset mode. this function is simplified
    # since it does not handle endpoint activation. particle flow calculations have also been
    # removed from this function because they have been removed from pipes.
    def sim_endpoint_preset(self, endpoint):
        activation_time = self.get_activation(endpoint.name)
        if activation_time > 0:
            #endpoint.update_pipe(self.counter)
            self.depreciate_activation(endpoint.name)
        elif activation_time == 0:
            endpoint.deactivate_pipes()
            self.depreciate_activation(endpoint.name)

    # this is the function that controls the simulation of water flowing from each endpoint, for each second.
    # uses the global presets and the simulation options to compute whether an endpoint is active or not
    # and either activates and updates, or deactivates an endpoint as appropriate. if endpoint is active,
    # instructs endpoint to update and calculate flow and depreciates the activation time.
    # particle flow calculations have also been removed from this function because they have been removed from pipes.
    def sim_endpoint_random(self, endpoint, active, rate):
        threshold = self.frequencies[endpoint.name]
        activation_time = self.get_activation(endpoint.name)
        if active: # TODO: test that active ranges still function
            activation_chance = random.random()
            if activation_chance <= threshold:
                length = random.randint(self.randLow,self.randHigh)
                activation_time = self.add_activation(endpoint.name, length)
                if not endpoint.isActive:
                    endpoint.activate_pipes(rate)
        if activation_time > 0:
            #endpoint.update_pipe(counter)
            self.depreciate_activation(endpoint.name)
        elif activation_time == 0:
            endpoint.deactivate_pipes()
            self.depreciate_activation(endpoint.name)

    # returns a dictionary object with the endpoints as the value, using the endpoint names as a key.
    def dict_from_endpoints(self, endpoints:list):
        rval = {}
        for item in endpoints:
            rval[item.name] = item
        return rval
    
    # this function controls the simulation. inputs include the root node,
    # the list of endpoint nodes, a list including the indexes for endpoint nodes
    # to test, the number of seconds to run the simulation for, and the time increment
    # class. once the initial variables are set, this function runs the simulation loop for the specified duration
    # only runs for preset mode, since the activations are handled differently.
    def sim_preset(self, root, endpoints, instructions, max_time, density):
        # print("sim preset", max_time)
        endpoints = self.dict_from_endpoints(endpoints)
        # print("e: ", endpoints, "i: ", instructions)
        start_time = None
        keys = instructions.keys()
        
        time_since = {}
        time_since_starts = {}
        for instruction in instructions:
            time_since_starts[instruction] = instructions[instruction][0][0]

        # print("max_time", max_time)        
        for time_step in range(0, max_time):
            start_time = self.progress_update(start_time, max_time, time_step)
            # TODO: multiprocessing
            for key in keys:
                # print("key:", key)
                endpoint = endpoints[key]
                actions = instructions[key]
        
                if time_step >= time_since_starts[key]:
                    if key not in time_since:
                        time_since[key] = 0
                    else: 
                        time_since[key] += 1 

                if len(actions) > 0:
                    first_action = actions[0]
                    if time_step == first_action[0]:
                        first_action = actions.pop(0)
                        #print(first_action)
                        length = first_action[1] - first_action[0]
                        self.add_activation(key, length)
                        if not endpoint.isActive:
                            endpoint.activate_pipes(first_action[2])
        
                        else:
                            endpoint.update_flow_rate(first_action[2])
                else:
                    pass
            if root.isActive:
                self.manager.add_particles(density, root)
            self.manager.update_particles(time_since)
            for endpoint in endpoints.values():
                self.sim_endpoint_preset(endpoint)
            self.counter.increment_time()

            # root.timeStep += 1
            # print("Root time step: ", root.timeStep)
            # print(root.length)

    # this function prints to the console with statistics about the simulation and the current simulation speed.
    # it also communicates with the display classes via message passing, allowing for
    # the gui to update at regular intervals during execution.
    def progress_update(self, start_time, max_time, second):
        message = ""
        mode_name = {1:"second", 2:"minute", 3:"hour"}
        if start_time == None:
            start_time = time.time()
        if second == 0:
            # self.controller.event_generate("<<status_started>>", when = "tail")
            message = "Simulation started."
            send = ("progress_update", message)
            self.Queue.put(send)
        if second % 1000 == 0 and second > 0:
            end_time = time.time()
            elapsed = end_time - start_time
            line1 = "Simulating " + mode_name.get(self.mode) + " " + str(second) + " of " + str(max_time) + f" at a rate of 1000 tics per {elapsed:0.4f} seconds.\n"
            message += line1
            pipe_particles = len(self.manager.particleIndex)
            expelled_particles = len(self.manager.expendedParticles)
            line2 = "There are currently {} particles in the pipe network and {} particles expelled.".format(
                    pipe_particles, expelled_particles)
            message += line2
            print(message)
            # self.controller.setvar(name= "message", value= message)
            # self.controller.event_generate("<<status_update>>", when = "tail")
            # self.controller.event_generate("<<particle_display_update>>", when = "tail")
            send = ("progress_update", message)
            self.Queue.put(send)
            send = ("status_update", self.manager.output_status())
            self.Queue.put(send)
            start_time = time.time()
        return start_time

    # function to generate output. takes a filename and a dictionary containing particles
    # and writes a csv file containing the information stored in those particles.
    def write_output(self, filename, particles):
        results = open(filename, 'w')
        writer = csv.writer(results,'excel')
        for key in particles:
            particle = particles[key]
            data = particle.getOutput()
            writer.writerow(data)
        results.close()

    # creates a csv file report the includes all particles expelled. Also includes
    # the endpoint the particle was expelled from, the time it left the system,
    # the particle age at the time of departure, and the particle ID.
    def write_age_data(self, filename, particleAges):
        results = open(filename, 'w')
        writer = csv.writer(results, 'excel')
        names = particleAges.keys()
        writer.writerow(["Endpoint", "Timestamp", "Age", "ParticleID"])
        for name in names:
            values = particleAges.get(name)
            # x = list(map(lambda a: a[0], values))
            # y = list(map(lambda b: b[1], values))
            for value in values:
                writer.writerow([name, value[0], value[1], value[2]])
        results.close()

    def write_age_and_FreeChlorine_data(self, filename, particleAges):
        results = open(filename, 'w')
        writer = csv.writer(results, 'excel')
        names = particleAges.keys()
        writer.writerow(["Endpoint", "Timestamp", "Age", "FreeChlorine", "ParticleID"])
        for name in names:
            values = particleAges.get(name)
            # x = list(map(lambda a: a[0], values))
            # y = list(map(lambda b: b[1], values))
            for value in values:
                writer.writerow([name, value[0], value[1], value[2], value[3]])
        results.close()

    def write_pipe_ages(self, particles, filename):
        results = open(filename, 'w')
        writer = csv.writer(results, 'excel')
        ageDict = {}
        # names = particleAges.keys()
        for key in particles:
            # print("key: ", key)
            particle = particles[key]
            data = particle.getOutput()
            # print("data: "  , data)
            for pipe in data[4]:
                ageDict.setdefault(pipe[0], [0,0])
                ageDict[pipe[0]][0] += pipe[1]
                ageDict[pipe[0]][1] += 1

        #Column containing the pipe name, the total age of particles in that pipe (summed time spent in that pipe value for each particle), the number of particles that have flowed through that pipe,
        # and the result of those two values divided from one another ( assumed to be the average age of particles in that pipe. )
        for entry in ageDict:
            writer.writerow([str(entry), str(ageDict[entry]), str(ageDict[entry][0] / ageDict[entry][1])])

        return ageDict
    
        print("root: ", self.root)
        self.tree_helper(self.root, self.root.children)
        
    def tree_helper(self, tree, iterable):
        if tree.type != "endpoint":
            print(tree.name)
        if iterable is not None:
            for each in iterable:
                if each is not None:
                    if each.type != "endpoint":
                        self.tree_helper(each, each.children)
                        

            # print(data)
            # values = particleAges.get(name)
            # print(values)
        

    
    # not currently functional as updates to the particle simulation module have broken functionality.
    # control function that sets up the simulation according to user preferences,
    # runs the simulation for the indicated number of days, then writes the output to files.
    # takes a filename as input, and uses this filename to run the builder module to construct the network
    # for simulation.
    # this version runs without a GUI from the command line. Used for early testing versions.
    def exec_randomized_commandline(self, modelfile, logpath):
        root, endpoints = builder.build(modelfile, self.manager)
        i = 0
        for point in endpoints:
            i += 1
            print('[{}]'.format(i), point.name)
        print("select endpoints to test, separated by spaces. e.g. 1 4 5 tests endpoints 1, 4, and 5.")
        entry = input()
        tests = entry.split(sep=" ")
        tests = list(dict.fromkeys(tests))
        density = 0.1
        for t in range(len(tests)):
            test = tests[t]
            try:
                tests[t] = int(test)
                test = tests[t]
            except:
                print("Only integers in range supported.")
                return
            if test < 1 or test > i:
                print("error! Test", test, "out of range.")
                return
        for test in tests:
            title = endpoints[test-1].name
            print("select flow rate (gallons per minute) for test", title)
            flow = input()
            try:
                flow = float(flow)
            except:
                print("numeric input required for flow rate. Aborting.")
                return
            self.flowrates[title] = flow
            endpoints[test-1].update_flow_rate(flow)
            print("flow rate set to", self.flowrates[title])
        print(
            "select activation chance for endpoints within range [0,1]\n with 0 being never active and 1 being always active.")
        for test in tests:
            title = endpoints[test-1].name
            print("select activation chance for", title)
            frequency = input()
            try:
                frequency = float(frequency)
                if frequency < 0.0 or frequency > 1.0:
                    raise Exception
                self.frequencies[title] = frequency
            except:
                print("numeric input required. Aborting.")
                return
            print("activation chance set to", frequency)
            self.frequencies[title] = frequency
        print("how many days would you like to simulate?")
        days = input()
        try:
            days = int(days)
            if days < 1:
                raise Exception
        except:
            print("Number of days must be an integer value greater than 0.")
            return
        print("select active use hours between 0 and 24. note: 7.5 = 7:30, 17.5 = 5:30.")
        active_start = input("Active start: ")
        active_end = input("Active end: ")
        try:
            active_start = float(active_start)
            active_end = float(active_end)
            if active_start < 0 or active_start > 24:
                print("active start is out of range")
                raise Exception
            if active_end < 0 or active_end > 24:
                print("active end is out of range")
                raise Exception
            if active_start > active_end:
                print("active start is greater than active end")
                raise Exception
        except:
            print("numeric input required. Aborting.")
            return
        print("Select particle density per inch. Recommended values in range [0.1, 1]")
        density = input("Particle Density: ")
        try:
            density = float(density)
            if density <= 0:
                raise Exception
        except:
            print("non-numeric density or density not greater than 0. Aborting.")
            return
        active_titles = []
        for test in tests:
            title = endpoints[test-1].name
            active_titles.append(title)
            print("testing", title, "with flowrate:", self.flowrates[title], "and activation chance of", self.frequencies[title])
        # self.sim_randomized(root, endpoints, active_titles, days*self.ONE_DAY, active_start*3600, active_end*3600, density)
        g = graphing(self.Queue, self.mode)
        g.graph_age(self.manager.expelledParticleData, self.counter, logpath)
        self.write_output(logpath + "\expelled.csv",self.manager.expendedParticles)
        self.write_output(logpath + "\pipe_contents.csv", self.manager.particleIndex)
        self.write_age_and_FreeChlorine_data(logpath + "\expelled_particle_ages.csv", self.manager.expelledParticleData)
        if(self.manager.diffusionActive):
            g.write_bins(logpath + "./static/plots/histogram.png", self.manager.bins)

    #this function executes the simulation in random mode. It first establishes flow rates and other simulation variables.
    def exec_randomized(self, arguments: execution_arguments):
        modelfile = arguments.modelfile
        pathname = arguments.pathname
        active_hours = arguments.pathname
        activation_range = arguments.activation_range
        length = arguments.length
        density = arguments.density
        instructions = arguments.instructions

        manager = particles.ParticleManager(self.counter)
        manager.diffusionActive = arguments.diffuse
        manager.diffusionCoefficient = arguments.diffusionCoefficient
        root, endpoints = builder.build(modelfile, manager)
        self.endpoints = endpoints
        self.root = root
        # self.controller.event_generate("<<sim_started>>", when="tail")
        send = ("status_started", "Simulation started.")
        self.Queue.put(send)
        # tree_model = self.root.generate_tree()
        # send = ("start_preview", tree_model)
        self.Queue.put(send)
        self.manager = manager
        time_start, time_end = active_hours
        self.randLow, self.randHigh = activation_range
        self.actives = []
        self.flowrates = {}
        self.frequencies = {}
        for each in instructions:
            self.actives.append(each[0])
            self.frequencies[each[0]] = each[1]
            self.flowrates[each[0]] = each[2]
        manager.setTimeStep(self.TIME_STEP)
        # self.sim_randomized(self.root, self.endpoints, self.actives, length*self.ONE_DAY, time_start*self.HOUR_LENGTH, time_end*self.HOUR_LENGTH, density)
        g = graphing(self.Queue, self.mode)
        g.graph_age(self.manager.expelledParticleData, self.counter, pathname)
        self.write_output(pathname + "\expelled.csv", self.manager.expendedParticles)
        self.write_output(pathname + "\pipe_contents.csv", self.manager.particleIndex)
        self.write_age_and_FreeChlorine_data(pathname + "\expelled_particle_ages.csv", self.manager.expelledParticleData)
        if self.manager.diffusionActive:
            g.write_bins(pathname + "\inputbin", self.manager.bins)
        # self.controller.event_generate("<<sim_finished>>", when = "tail")
        send = ("status_completed", "Simulation complete.")
        self.Queue.put(send)

    #this function executes the simulation in preset mode. This changes how pipes are activated and enables different
    # flow rates for each activation.
    def exec_preset(self, arguments: execution_arguments):
        try:
            modelfile = arguments.modelfile
            presetsfile = arguments.presetsfile
            density = arguments.density
            pathname = arguments.pathname
            self.manager.molecularDiffusionCoefficient = arguments.molecularDiffusionCoefficient
            self.manager.diffusionActive = arguments.diffuse
            # self.controller.event_generate("<<sim_started>>", when = "tail")
            send = ("status_started", "Simulation started.")
            self.Queue.put(send)

            try:
                self.root, self.endpoints = builder.build(modelfile, self.manager)
            except Exception as e:
                raise Exception("Error building model. Check model file for errors. [" + str(e) + "]")
            
            self.manager.setTimeStep(self.TIME_STEP)
            self.Queue.put(send)
            
            #self.controller.preview_manager.start(self.root, self.manager)
            # send = ("start_preview", tree_model)
            # self.Queue.put(send)
            try:
                maxTime, instructions = builder.load_sim_preset(presetsfile)
                maxTime, instructions = self.parse_instructions(maxTime, instructions)
            except Exception as e:
                raise Exception("Error loading preset file. Check preset file for errors. [" + str(e) + "]")
            
            try:
                self.sim_preset(self.root, self.endpoints, instructions, maxTime, density)
            except Exception as e:
                raise Exception("Error running simulation. Check uploaded files for errors. [" + str(e) + "]" )
            
            try:
                if not os.path.isdir(pathname):
                    os.mkdir(pathname)
                g = graphing(self.Queue, self.mode)
                g.graph_age(self.manager.expelledParticleData, self.counter, pathname)
            except Exception as e:
                raise Exception("Error generating graphs. [" + str(e) + "]") 

            try:            
                self.write_output(pathname+"\expelled.csv", self.manager.expendedParticles)
                self.write_output(pathname+"\pipe_contents.csv", self.manager.particleIndex)
                self.write_age_and_FreeChlorine_data(pathname+"\expelled_particle_ages.csv", self.manager.expelledParticleData)
                if self.manager.diffusionActive:
                    g.write_bins(".\static\plots\histogram", self.manager.bins)
                ageDict = self.write_pipe_ages(self.manager.expendedParticles, pathname+"\pipe_ages.csv")
                self.root.generate_tree()
                self.root.show_tree(pathname + "/tree_graph.png", ageDict)
            except Exception as e:
                raise Exception("Error writing output files. Check uploaded files for errors and ensure that the output directory is not open in another program. [" + str(e) + "]" )
            # tree_model.render(".\static\plots\pipe_tree.png")
            # self.controller.event_generate("<<sim_finished>>", when = "tail")
            send = ("status_completed", "Simulation complete.")
            self.Queue.put(send)
        except Exception as e:
            raise Exception(e)
        

    # this function translates the instructions from the instructions file (recorded as minutes)
    # into the appropriate time scale (seconds, minutes, or hours) as selected.
    def parse_instructions(self, maxTime, instructions):
        maxTime = int(maxTime * self.ONE_DAY)
        for key in instructions.keys():
            val = instructions.get(key)
            newVal = []
            for each in val:
                newVal.append((int((each[0]*self.TIME_STEP)), int(each[1]*self.TIME_STEP), each[2]))
            instructions[key] = newVal
        return maxTime, instructions
