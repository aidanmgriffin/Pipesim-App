import driver
import builder
import preview
import showimage
import numpy as np
from functools import partial
import threading
from multiprocessing import Queue, Process, Pool
import os
import datetime
import csv


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
        particlelogfile = "SingleParticle.csv"
        particlelogfile = open(particlelogfile, 'w')

        self.options = {"Seconds":1, "Minutes":2, "Hours":3}
        self.step_size = 1
        self.step_var = 1

        
    def setDiffusionStatus(self):
        if self.diffusion_check_internal.get() == 0:
            self.diffusion_status = False
        if self.diffusion_check_internal.get() == 1:
            self.diffusion_status = True

    # this loop runs the graphical interface once it has been configured as above
    def start(self):
        pass
        #self.window.after(500, self.check_queue)
        #self.window.mainloop()

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
    #def check_queue(self):
    #    ending = False
    #    item = self.queue_get_next()
    #    while item != None:
    #        if item[0] == "status_completed":
    #            self.status_update_handler(item[1])
    #            self.enable()
    #            ending = True
    #        elif item[0] == "status_started":
    #            self.disable()
    #        elif item[0] == "graph_completed":
    #            self.display_graph(item[1])
    #            pass
    #        elif item[0] == "progress_update":
    #            self.status_update_handler(item[1])
    #        elif item[0] == "start_preview":
    #            model = item[1]
    #            self.preview_manager.start(model)
    #        elif item[0] == "status_update":
    #            self.preview_manager.updater(item[1], self.outputLocation)
    #        elif item[0] == "random_sim_configuration":
    #            self.random_simulation_handler(item[1])
    #        item = self.queue_get_next()
    #    if ending:
    #        return
    #    else:
    #        self.after(500, func=self.check_queue)
    #        return

    # gets the next item from the message queue if it exists or returns None if empty.
    def queue_get_next(self):
        try:
            item = self.Queue.get(block=False, timeout=0)
        except:
            item = None
        return item

    # updates step size as indicated by the step size variable (used by radio buttons). This function is called
    # when the radio button selection changes.
    def set_step_time(self):
        #self.step_size = self.step_var.get()
        self.step_size = self.step_var
        # print(self.step_size)
    
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

    def settings_preset_simulation_button_handler(self, filename):
        print("valid")
        density = None
        valid = True
        f0 = None

        try:
            #f0 = open(self.file0.get())
            f0 = open(filename)
            f0.close()
        except:
            # tm.showerror(title = "Error", message = "invalid filename: settings file")
            valid = False
        
        if valid:
            #contents = self.load_settings_csv(self.file0.get())
            contents = self.load_settings_csv(filename)

            # print(contents, contents[0][3])
            if contents[0][3] == 'Yes' or contents[0][3] == 'yes':
                self.diffusion_status = True 
            else:
                self.diffusion_status = False
                
            self.options = {"Seconds":1, "Minutes":2, "Hours":3}
            #self.step_var.set(self.options[contents[0][5]])
            self.step_var = self.options[contents[0][5]]
            self.set_step_time()

            self.generate_path()
            simulator = driver.Driver(self.Queue, step = self.step_size)

            print(" pathname : ", self.outputLocation)
            #arguments = driver.execution_arguments(settingsfile = self.file0.get(), modelfile=contents[0][0], presetsfile=contents[0][1],
            #                                       density= float(contents[0][2]), pathname=self.outputLocation,
            #                                       diffuse=self.diffusion_status, diffusionCoefficient= float(contents[0][4]))
            arguments = driver.execution_arguments(settingsfile = filename, modelfile=contents[0][0], presetsfile=contents[0][1],
                                                   density= float(contents[0][2]), pathname=self.outputLocation,
                                                   diffuse=self.diffusion_status, diffusionCoefficient= float(contents[0][4]))
            
            sim = Process(target = simulator.exec_preset, args = (arguments,))
            
            # sim = threading.Thread(target = simulator.exec_preset, args = arguments)
            sim.start()
            sim.join()

            return(1)


    # function validates file name input for the two preset configuration files and (if valid)
    # launches the simulation in preset mode.
    def preset_simulation_button_handler(self, file1, file2, density1, diffusion_status, diffusion_coefficient, granularity):
        density = None
        valid = True
        f1 = None
        f2 = None
       
        try:
            f1 = open(file1)
            print(file1)
            f1.close()
        except:
            # tm.showerror(title = "Error", message = "invalid filename: pipes model")
            valid = False
        try:
            f2 = open(file2)
            f2.close()
        except:
            # tm.showerror(title = "Error", message = "Invalid filename: test procedure")
            valid = False
        try:
            #density = self.density1.get()
            density = float(density1)
        except:
            # tm.showerror(title = "Error", message = "Invalid argument: non-numeric density")
            valid = False
        self.step_var = self.options[granularity]
        self.set_step_time()

        if valid:
            self.generate_path()
            simulator = driver.Driver(self.Queue, step = self.step_size)
            arguments = driver.execution_arguments(settingsfile = None, modelfile=file1, presetsfile=file2,
                                                   density=density, pathname=self.outputLocation,
                                                   diffuse=diffusion_status, diffusionCoefficient=diffusion_coefficient)
            sim = Process(target = simulator.exec_preset, args = (arguments,))
            # sim = threading.Thread(target = simulator.exec_preset, args = arguments)
            sim.start()
            sim.join()

            return(1)

    # this function validates all the inputs int he window to ensure they are valid and will result in a successful
    # simulation. The function will raise an error describing the problem if there is one, allowing the user
    # to correct their input. If the input validates successfully, then this function will close the configurator
    # window and call another function that begins the simulation in random mode.
    # def validate_configuration(self):
    #     valid = True
    #     for element in self.frequencies:
    #         val = element.get()
    #         try:
    #             val = float(val)
    #             if val < 0 or val > 1:
    #               raise Exception
    #         except:
    #             tm.showerror("A frequency input is non-numeric or out of range [0,1]")
    #             valid = False
    #     for element in self.flowrates:
    #         flow = element.get()
    #         try:
    #             flow = float(flow)
    #             if flow < 0:
    #                 raise Exception
    #         except:
    #             tm.showerror("A flowrate input is non-numeric or out of range [0,infinity)")
    #             valid = False
    #     start_time = None
    #     end_time = None
    #     try:
    #         start_time = float(self.active_start.get())
    #         if start_time < 0.0 or start_time > 24.0:
    #             raise Exception
    #     except:
    #         tm.showerror("Start time is non-numeric or out of range")
    #         valid = False
    #     try:
    #         end_time = float(self.active_end.get())
    #         if end_time < 0.0 or end_time > 24.0:
    #             raise Exception
    #     except:
    #         tm.showerror("end time is non-numeric or out of range")
    #         valid = False
    #     duration = None
    #     try:
    #         duration = int(self.runtime.get())
    #         if duration < 1:
    #             raise Exception
    #     except:
    #         tm.showerror("simulation duration is not an integer or less than one.")
    #         valid = False
    #     density = None
    #     try:
    #         density = float(self.densityEntry.get())
    #         if density <= 0.0:
    #             raise Exception
    #     except:
    #         tm.showerror("density is nonpositive or nonnumeric")
    #         valid = False
    #     randLow = None
    #     randHigh = None
    #     try:
    #         randLow = int(self.lowDuration.get())
    #         randHigh = int(self.highDuration.get())
    #         if randLow < 1 or randHigh < 0:
    #             raise Exception
    #         elif randLow > randHigh:
    #             raise Exception
    #     except:
    #         tm.showerror("nonnumeric entry or invalid range: a > b or a,b < 1.")
    #         valid = False
    #     if valid:
    #         for i in range(len(self.checks)):
    #             checkval = self.checks[i].cget("text")
    #             if checkval == 1:
    #                 instruction = (self.endpointNames[i], float(self.frequencies[i].get()), float(self.flowrates[i].get()))
    #                 self.activation_instructions.append(instruction)
    #                 #print(instruction)
    #         #update the configuration object so that it does not contain the model anymore, only needs the filename
    #         #self.root, self.endpoints, self.manager, self.timer
    #         configuration = (self.fname, (start_time, end_time), (randLow, randHigh), duration, density, self.activation_instructions)
    #         self.parent.Queue.put(("random_sim_configuration", configuration))
    #         self.configurator.destroy()

            #self.parent.random_simulation_handler(configuration)

# starts main window thread
def main():
    sim = simulation_window()
    sim.start()

# executes when python is run from the command line or executed.
if __name__ == "__main__":
    main()


