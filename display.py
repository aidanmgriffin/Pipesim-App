"""
This file contains the SimulationWindow class which is responsible for the graphical user interface of the application.
"""

import os
import csv
import driver
import traceback
import multiprocessing #, Manager
from multiprocessing import Queue, Process


class SimulationWindow():
    """
    This class represents the view or graphical user interface of this simulation application. It allows for
    test setup and provided feedback on results.
    """

    def __init__(self):
        """
        Establish initial window state including text, buttons, and data entry boxes.
        """

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
        """
        Sets the diffusion status to true or false based on the value of the diffusion check box.
        """

        if self.diffusion_check_internal.get() == 0:
            self.diffusion_status = False
        if self.diffusion_check_internal.get() == 1:
            self.diffusion_status = True


    def generate_path(self):
        """
        In order to preserve data from subsequent executions of the simulator, a new save path is generated on each
        simulation run. the save path is in the format $currentFolder/logs/$currentTime/.

        :return: the path to the save location
        """

        path = "/logs/output_batch"
        path = path.replace(" ", "-")
        path = path.replace(":", "-")
        path = path.replace(".", "-")
        path = "." + path
        if not os.path.isdir("./logs"):
            os.mkdir("./logs")
        self.outputLocation = path
        return path

    def check_queue(self):
       """
       The application runs across several different processes which are not synchronized with each other.
       as a consequence, processes must communicate across a messaging pipeline to update the user and the rest of the
       application. This function receives messages (usually sent by the simulation) and updates the display or preview
       accordingly.
       """

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

    def queue_get_next(self):
        """
        Gets the next item from the message queue if it exists or returns None if empty.

        :return: the next item in the queue or None if empty
        """

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
        """
        This function is used to catch exceptions that occur in the simulation process and pass them back to the main

        :param func: the function to be executed
        :param exception_holder: a namespace object used to store the exception
        :param args: arguments to be passed to the function
        :return: the return value of the function
        """

        try:
            return func(*args)
        except Exception as e:
            traceback.print_exc()
            exception_holder.exception = e

    def preset_simulation_button_handler(   self, 
                                            file1, 
                                            file2, 
                                            density1, 
                                            # vol_density,
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
        """
        Function validates file name input for the two preset configuration files and (if valid) launches the simulation in preset mode.
        Takes parameters from the settings preset file and passes them to the simulation.

        :param file1: the name of the model file
        :param file2: the name of the preset file
        :param density1: the density of the particles in the pipe network i.e. length between particles.
        :param diffusion_status: the status of diffusion
        :param stagnant_diffusion_status: the status of stagnant diffusion
        :param advective_diffusion_status: the status of advective diffusion
        :param molecular_diffusion_coefficient: the molecular diffusion coefficient
        :param granularity: the granularity of the simulation
        :param decay_free_chlorine_status: the status of free chlorine decay
        :param decay_monochloramine_status: the status of monochloramine decay
        :param starting_particles_free_chlorine_concentration: the starting concentration of free chlorine
        :param injected_particles_free_chlorine_concentration: the injected concentration of free chlorine
        :param decay_monochloramine_dict: the dictionary of monochloramine decay
        :param groupby_status: the status of groupby
        :param timestep_group_size: the size of the timestep group
        :return: 1 if the simulation was successful and 0 otherwise
        """

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
            density = float(density1)
        except:
            valid = False
        # try:
        #     vol_density = float(vol_density)
        # except:
        #     valid = False

        self.step_size = granularity

        manager = multiprocessing.Manager()
        exception_holder = manager.Namespace()

        if valid:
            self.generate_path()
            simulator = driver.Driver(self.Queue, step = self.step_size)
            arguments = driver.ExecutionArguments(
                modelfile=file1,
                presetsfile=file2,
                density=density,
                # vol_density=vol_density,
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
            
            if sim.exitcode == 0:
                return(1)
            else:
                return(0)
        else:
            return(0)
            

  