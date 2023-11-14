import driver
# import builder
# import preview
# import showimage
# import numpy as np
# from functools import partial
# import threading
from multiprocessing import Queue, Process
import multiprocessing #, Manager
import os
# import datetime
import csv
import traceback
import sys


# this function takes in a dictionary containing one or more lists. each list contains the age of particles
# that left the pipe network from a specific endpoint, along with the exit time. This function graphs these
# on an age vs time graph for each endpoint.

# This class represents the view or graphical user interface of this simulation application. It allows for
# test setup and provided feedback on results.
class simulation_window():

    # establish initial window state including text, buttons, and data entry boxes.
    def __init__(self):
        #window initialization
        super().__init__()
        self.window = self
        self.outputLocation = None
        self.Queue = Queue(maxsize=1000)
        self.graph = None
        self.diffusion_status = False
        logfile = "ParticleDiffusion.log"
        logfile = open(logfile, 'w')
        self.options = {"Seconds":1, "Minutes":2, "Hours":3, "Custom":4}
        self.step_size = 1
        self.step_var = 1

    def setDiffusionStatus(self):
        if self.diffusion_check_internal.get() == 0:
            self.diffusion_status = False
        if self.diffusion_check_internal.get() == 1:
            self.diffusion_status = True


    # in order to preserve data from subsequent executions of the simulator, a new save path is generated on each
    # simulation run. the save path is in the format $currentFolder/logs/$currentTime/.
    def generate_path(self):
        # path = "/logs/" + str(datetime.datetime.now())
        path = "/logs/output_batch"
        path = path.replace(" ", "-")
        path = path.replace(":", "-")
        path = path.replace(".", "-")
        path = "." + path
        if not os.path.isdir("./logs"):
            os.mkdir("./logs")
        self.outputLocation = path
        #self.preview_manager.graph_counter = 0
        return path

    # The application runs across several different processes which are not synchronized with each other.
    # as a consequence, processes must communicate across a messaging pipeline to update the user and the rest of the
    # application. This function receives messages (usually sent by the simulation) and updates the display or preview
    # accordingly.
    def check_queue(self):
       ending = False
       item = self.queue_get_next()
       while item != None:
           if item[0] == "status_completed":
               self.status_update_handler(item[1])
               self.enable()
               ending = True
           elif item[0] == "status_started":
               self.disable()
           elif item[0] == "graph_completed":
               self.display_graph(item[1])
               pass
           elif item[0] == "progress_update":
               self.status_update_handler(item[1])
           elif item[0] == "start_preview":
               model = item[1]
               self.preview_manager.start(model)
           elif item[0] == "status_update":
               self.preview_manager.updater(item[1], self.outputLocation)
           elif item[0] == "random_sim_configuration":
               self.random_simulation_handler(item[1])
           item = self.queue_get_next()
       if ending:
           return
       else:
           self.after(500, func=self.check_queue)
           return

    # gets the next item from the message queue if it exists or returns None if empty.
    def queue_get_next(self):
        try:
            item = self.Queue.get(block=False, timeout=0)
        except:
            item = None
        return item

    def load_settings_csv(self, filename):
        file = open(filename,"r")
        csvfile = csv.reader(file,dialect="excel")
        
        start = 0
        rval = []
        for line in csvfile:
            if start == 0:
                start = 1
                continue
        rval.append(line)

        return rval

    def exception_wrapper(self, func, exception_holder, *args):
        try:
            return func(*args)
        except Exception as e:
            traceback.print_exc()
            exception_holder.exception = e

    #Takes parameters from the settings preset file and passes them to the simulation.
    def settings_preset_simulation_button_handler(self, filename):
        density = None
        valid = True
        f0 = None

        try:
            f0 = open(filename)
            f0.close()
        except:
            valid = False
        
        if valid:
            contents = self.load_settings_csv(filename)

            if contents[0][3] == 'Yes' or contents[0][2] == 'yes':
                self.diffusion_stagnant_status = True 
            else:
                self.diffusion_stagnant_status = False
            
            if contents[0][4] == 'Yes' or contents[0][3] == 'yes':
                self.diffusion_advective_status = True 
            else:
                self.diffusion_advective_status = False

            if self.diffusion_advective_status == True or self.diffusion_stagnant_status == True:
                self.diffusion_status = True
            else:
                self.diffusion_status = False

            self.step_size = float(contents[0][6]) / 60
            self.generate_path()

            manager = multiprocessing.Manager()
            exception_holder = manager.Namespace()
            
            simulator = driver.Driver(self.Queue, step = self.step_size)
            arguments = driver.execution_arguments(settingsfile = filename, modelfile=contents[0][0], presetsfile=contents[0][1],
                                                   density= float(contents[0][5]), pathname=self.outputLocation,
                                                   diffuse=self.diffusion_status, diffuse_stagnant= self.diffusion_stagnant_status, diffuse_advective=self.diffusion_advective_status, molecular_diffusion_coefficient = float(contents[0][4]))
            
            sim = Process(target = self.exception_wrapper, args = (simulator.exec_preset, exception_holder, arguments))
            sim.start()
            sim.join()

            if sim.exitcode == 0:
                return([1, self.diffusion_status])
            else:
                return(0)
            
        
    # function validates file name input for the two preset configuration files and (if valid) launches the simulation in preset mode.
    def preset_simulation_button_handler(   self, 
                                            file1, 
                                            file2, 
                                            density1, 
                                            diffusion_status, 
                                            stagnant_diffusion_status, 
                                            advective_diffusion_status, 
                                            molecular_diffusion_coefficient, 
                                            granularity, 
                                            decay_free_chlorine_status, 
                                            decay_monochloramine_status, 
                                            starting_particles_free_chlorine_concentration, 
                                            injected_particles_free_chlorine_concentration,
                                            decay_monochloramine_dict,
                                            groupby_status,
                                            timestep_group_size,
                                         ):
        # print("display.py")
        # return 1
        density = None
        valid = True
        f1 = None
        f2 = None
        try:
            f1 = open(file1)
            f1.close()
        except:
            valid = False
        try:
            f2 = open(file2)
            f2.close()
        except:
            valid = False
        try:
            #density = self.density1.get()
            density = float(density1)
        except:
            valid = False

        # print("granularity: ", granularity , "dcfs", decay_free_chlorine_status, "dcms", decay_monochloramine_status)
        self.step_size = granularity

        manager = multiprocessing.Manager()
        exception_holder = manager.Namespace()

        # print("prevalid")
        if valid:
            # print("valid")
            self.generate_path()
            simulator = driver.Driver(self.Queue, step = self.step_size)
            arguments = driver.execution_arguments(
                settingsfile = None, 
                modelfile=file1,
                presetsfile=file2,
                density=density,
                pathname=self.outputLocation,
                diffuse=diffusion_status,
                diffuse_stagnant =stagnant_diffusion_status,
                diffuse_advective = advective_diffusion_status,
                molecular_diffusion_coefficient=molecular_diffusion_coefficient,
                decay_free_chlorine_status=decay_free_chlorine_status,
                decay_monochloramine_status=decay_monochloramine_status,
                starting_particles_free_chlorine_concentration=starting_particles_free_chlorine_concentration,
                injected_particles_free_chlorine_concentration=injected_particles_free_chlorine_concentration,
                decay_monochloramine_dict=decay_monochloramine_dict,
                groupby_status=groupby_status,
                timestep_group_size=timestep_group_size,
                )
            
            sim = Process(target = self.exception_wrapper, args = (simulator.exec_preset,exception_holder, arguments))

            sim.start()
            sim.join()

            if hasattr(exception_holder, 'exception'):
                print("exception holder")
                raise exception_holder.exception
            
            # print("sim exit code: ", sim.exitcode)
            
            if sim.exitcode == 0:
                return(1)
            else:
                return(0)
        else:
            # print("returning 0 from display")
            return(0)
            

  