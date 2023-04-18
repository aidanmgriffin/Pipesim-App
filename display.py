import driver
import builder
import preview
import showimage
# import tkinter as tk
# from PIL import ImageTk, Image
# from tkinter import filedialog
# from tkinter import StringVar
# from tkinter import IntVar
# from tkinter import DISABLED
# from tkinter import LEFT
# import tkinter.messagebox as tm
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
        #self.file0 = StringVar()
        #self.file1 = StringVar()
        #self.file2 = StringVar()
        #self.file3 = StringVar()
        self.Queue = Queue(maxsize=1000)
        #message = StringVar(self.window, name="message")
        #self.density1 = StringVar()
        self.graph = None
        self.diffusion_status = False
        #self.density1.set('0.5')
        #self.window.title("Water Simulation")
        #self.window.columnconfigure(0, weight = 1, minsize = 10)
        #self.window.rowconfigure(0, weight = 1, minsize = 10)
        #self.window.columnconfigure(1, weight = 1, minsize = 0)
        #self.window.rowconfigure(1, weight = 1, minsize = 0)
        #self.frame0 = tk.Frame(master=self.window, borderwidth = 1)
        #self.frame1 = tk.Frame(master=self.window, borderwidth=1)
        #self.frame2 = tk.Frame(master=self.window, borderwidth=1)
        #self.frame3 = tk.Frame(master=self.window, borderwidth=1)
        ##self.frame4 = tk.Frame(master = self.frame2, borderwidth = 1)
        #self.frame0.grid(row = 0, column = 0, padx = 10, pady = 10, sticky = "nw")
        #self.frame1.grid(row = 0, column = 1, padx = 10, pady = 10, sticky = "nw")
        #self.frame2.grid(row = 1, column = 0, padx = 10, pady = 10, sticky = "nw")
        #self.frame3.grid(row = 1, column = 1, padx = 10, pady = 10, sticky = "nw")
        ##self.frame4.grid(row = 4, column = 0, padx = 10, pady=10 sticky = "sw")
        ##self.canvas = tk.Canvas(master=self.frame1, width=600, height=600)
        ##self.canvas.grid(row=0, column=0)

        #self.left_column_top = tk.Frame(master=self.frame0, borderwidth=1)
        #self.left_column_top.grid(row = 0, column = 0, padx = 0, pady = 10, sticky = "nw")
        #self.left_column_middle = tk.Frame(master=self.frame0, borderwidth=1)
        #self.left_column_middle.grid(row=1, column=0, padx=0,pady=10, sticky="nw")
        #self.left_column_bottom = tk.Frame(master=self.frame0, borderwidth=1)
        #self.left_column_bottom.grid(row=2, column=0, padx=0, pady=10, sticky="nw")

        ##add warnings
        #self.warning_label1 = tk.Label(master=self.left_column_bottom, text="Remember to set your preferred graph visualization\noption before starting the simulation.", justify=LEFT)
        #self.warning_label1.grid(row = 4, column = 0, sticky = "sw")
        #self.warning_label2 = tk.Label(master=self.left_column_bottom, text="Please close and re-open the application before\nrunning a second simulation.", justify=LEFT)
        #self.warning_label2.grid(row = 5, column = 0, sticky = "sw")
        #self.warning_label2.config(fg='darkred')
        #self.warning_label1.config(fg='darkred')

        ##setting presets configuration block
        #self.frame0_label = tk.Label( 
        #    master = self.left_column_top, text = "Import Settings Preset",
        #    font = "Helvetica 10 bold",
        #    )
        #self.frame0_label.grid(row = 0, column = 0, sticky = "nw")
        #self.file0_label = tk.Label(master = self.left_column_top, text="Select settings preset")
        #self.file0_label.grid(row = 1, column = 0, sticky = "nw")
        #self.mode_0_button = tk.Button(master = self.left_column_top, text = "Run Simulation", command = self.settings_preset_simulation_button_handler)
        #self.mode_0_button.grid(row=4, column = 0, sticky = "s")


        ##presets functionality configuration block
        #self.frame1_label = tk.Label(
        #    master = self.left_column_top, text = "Deterministic / Predefined Test Setup",
        #    font = "Helvetica 10 bold",
        #    )
        #self.frame1_label.grid(row = 6, column = 0, sticky = "nw")
        #self.file1_label = tk.Label(master = self.left_column_top, text="Select pipes model (file)")
        #self.file2_label = tk.Label(master = self.left_column_top, text = "Select test procedure (file)")
        #self.file1_label.grid(row = 7, column = 0, sticky = "nw")
        #self.file2_label.grid(row = 9, column = 0, sticky = "nw")
        #self.file0_button = tk.Button(master = self.left_column_top, text = "Open", command = self.button_handler_0)
        #self.file0_button.grid(row = 2, column = 1, sticky = "nw")
        #self.file1_button = tk.Button(master = self.left_column_top, text = "Open", command = self.button_handler_1)
        #self.file1_button.grid(row = 8, column = 1, sticky = "nw")
        #self.file2_button = tk.Button(master = self.left_column_top, text = "Open", command = self.button_handler_2)
        #self.file2_button.grid(row = 10, column = 1, sticky = "nw")
        #self.file0_textBox = tk.Entry(master = self.left_column_top, width = 33, textvariable = self.file0)
        #self.file0_textBox.grid(row=2, column = 0, sticky = "nw")
        #self.file1_textBox = tk.Entry(master = self.left_column_top, width = 33, textvariable = self.file1)
        #self.file1_textBox.grid(row=8, column = 0, sticky = "nw")
        #self.file2_textBox = tk.Entry(master = self.left_column_top, width = 33, textvariable = self.file2)
        #self.file2_textBox.grid(row=10, column = 0, sticky = "nw")
        #self.density_label = tk.Label(master = self.left_column_top, text = "Select particle density.\nRecommended interval (0,1]", justify = LEFT)
        #self.density_label.grid(row = 11, column = 0, sticky = "nw")
        #self.density_textBox = tk.Entry(master = self.left_column_top, width = 4, textvariable = self.density1)
        #self.density_textBox.grid(row = 12, column = 0, sticky = "nw")
        #self.mode_1_button = tk.Button(master = self.left_column_top, text = "Run Simulation", command = self.preset_simulation_button_handler)
        #self.mode_1_button.grid(row=13, column = 0, sticky = "s")

        ## probabalistic simulation mode
        #self.frame2_label = tk.Label(
        #    master = self.left_column_middle, text = "Probabalistic / Random Test Setup",
        #    font = "Helvetica 10 bold"
        #)
        #self.frame2_label.grid(row = 0, column = 0, sticky = "nw")
        #self.file3_label = tk.Label(master = self.left_column_middle, text = "select pipes model (file)")
        #self.file3_label.grid(row = 1, column = 0, sticky = "nw")
        #self.file3_textBox = tk.Entry(master = self.left_column_middle, width = 33, textvariable = self.file3)
        #self.file3_textBox.grid(row = 2, column = 0, sticky = "nw")
        #self.file3_button = tk.Button(master = self.left_column_middle, text = "Open", command = self.button_handler_3)
        #self.file3_button.grid(row = 2, column = 1, sticky = "nw")
        #self.configurator_button = tk.Button(master = self.left_column_middle, text = "Configure", command = partial(random_configurator, self.file3, self))
        #self.configurator_button.grid(row = 3, column = 0, sticky = "n")

        ##progress information display
        #self.preview_manager = preview.live_preview(window = self.window, master = self.frame1)
        #self.preview = self.preview_manager.get_frame()
        #self.preview.grid(row = 0, column = 0)
        #self.statusLabel = tk.Label(master = self.frame1, text = "Simulation not started.", width = 100, height = 2)
        #self.statusLabel.grid(row = 1, column = 0, sticky = "s", pady = (30,20))

        ##diffusion selection switch
        #self.diffusion_check_internal = tk.IntVar()

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
        #self.diffusion_options_frame = tk.Frame(master=self.left_column_bottom)
        #self.diffusion_options_frame.grid(row=0, column=0, sticky="nw")
        #self.diffusion_label = tk.Label(master=self.diffusion_options_frame, text="Diffusion Options", font="Helvetica 10 bold")
        #self.diffusion_label.grid(row=0, column=0, sticky="nw")

        #self.diffusion_enable = tk.Checkbutton(master=self.diffusion_options_frame, text="Enable", variable=self.diffusion_check_internal, offvalue=0, onvalue=1, command=setDiffusionStatus)
        #self.diffusion_enable.grid(row=1, column=0, sticky="nw")

        # time granularity control
        #self.time_granularity_frame = tk.Frame(master=self.left_column_bottom)
        #self.time_granularity_frame.grid(row=1, column=0, sticky="nw")
        #self.time_label = tk.Label(master = self.time_granularity_frame, text = "Time Granularity Options", font = "Helvetica 10 bold")
        #self.time_label.grid(row = 0, column = 0, sticky = "nw")
        
        #self.step_var = tk.IntVar()
        #self.step_var.set(1)
        #self.radio_grid = tk.Frame(master = self.time_granularity_frame, borderwidth = 1)
        #self.radio_grid.grid(row = 1, column = 0, sticky = "nw")
        #for key in self.options:
        #    value = self.options.get(key)
        #    tk.Radiobutton(self.radio_grid, text = key, value = value, padx = 20, variable = self.step_var, command = self.set_step_time).grid(row = 1, column = value-1, sticky = "nw")

        ##initialize output location based on current date and time
        #self.generate_path()

    # this loop runs the graphical interface once it has been configured as above
    def start(self):
        pass
        #self.window.after(500, self.check_queue)
        #self.window.mainloop()

    # in order to preserve data from subsequent executions of the simulator, a new save path is generated on each
    # simulation run. the save path is in the format $currentFolder/logs/$currentTime/.
    def generate_path(self):
        path = "/logs/" + str(datetime.datetime.now())
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

    ## opens the file picker and returns the name of the opened file
    #def open_file_name(self):
    #    filename = filedialog.askopenfilename(
    #        initialdir = ".", title = "Select File",
    #        filetypes = (("CSV files","*.csv"),("All Files","*.*"))
    #    )
    #    return filename

    #def button_handler_0(self):
    #    #self.window.update()
    #    filename = self.open_file_name()
    #    self.file0_textBox.delete(0, tk.END)
    #    self.file0_textBox.insert(0, filename)
    #    self.file0.set(filename)

    ## button function for opening model file in preset mode
    #def button_handler_1(self):
    #    #self.window.update()
    #    filename = self.open_file_name()
    #    self.file1_textBox.delete(0, tk.END)
    #    self.file1_textBox.insert(0, filename)
    #    self.file1.set(filename)

    ## button function for opening preset file (preset mode)
    #def button_handler_2(self):
    #    #self.window.update()
    #    filename = self.open_file_name()
    #    self.file2_textBox.delete(0, tk.END)
    #    self.file2_textBox.insert(0, filename)
    #    self.file2.set(filename)

    ## button function for opening model file in random mode
    #def button_handler_3(self):
    #    #self.window.update()
    #    filename = self.open_file_name()
    #    self.file3_textBox.delete(0, tk.END)
    #    self.file3_textBox.insert(0, filename)
    #    self.file3.set(filename)

    #def display_graph(self, filename):
    #    filepath = os.path.abspath(filename)
    #    #filepath = path + '\\' + filename
    #    #print("filepath= {}".format(filepath))
    #    self.graph = filepath
    
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

    # this function is triggered to update the status label in the view window according to the "message" parameter.
    #def status_update_handler(self, message):
    #    self.statusLabel.config(text = message)

    ## this function takes input from the random configurator and launches the simulation in random mode.
    #def random_simulation_handler(self, configuration_options):
    #    filename, active_hours, activation_range, duration, density, instructions = configuration_options
    #    simulator = driver.Driver(queue=self.Queue, timer=None, step=self.step_size)
    #    output = self.generate_path()
    #    arguments = driver.execution_arguments(modelfile=filename, pathname=output, active_hours=active_hours,
    #                                           activation_range=activation_range, length=duration,density=density,
    #                                           instructions=instructions, diffuse=self.diffusion_status)
    #    x = Process(target=simulator.exec_randomized, args=(arguments,))
    #    # x = threading.Thread(target=simulator.exec_randomized, args=(root, endpoints, manager, active_hours, activation_range, duration, density, instructions))
    #    x.start()

    ## disables interactive elements in the display window when called. Called upon simulation starting.
    #def disable(self):
    #    self.disable_helper(self.window)
    #    self.preview_manager.disable()

    ## this function disables all the widgets in the main window. To be used to prevent input while the simulation is running.
    #def disable_helper(self, widget):
    #    for item in widget.winfo_children():
    #        if item is not self.frame1:
    #            try:
    #                item['state'] = tk.DISABLED
    #            except:
    #                pass
    #            self.disable_helper(item)

    ## re-enables interactive elements in the display window when called. Called upon simulation completion (as received
    ## in the message queue)
    #def enable(self):
    #    showimage.ShowImageDialog(title="Simulation Complete",
    #        message="Simulation completed. Results have been written to files.\nexpelled.csv: expelled particle details\nexpelled_particle_ages.csv: time, age, and ID of expelled particles\npipe_contents.csv: details on particles in pipes\nage_graph.png: graph of expelled particle ages",
    #        image=self.graph)
    #    self.enable_helper(self.window)
    #    self.preview_manager.enable()

    ## this function re-enables all the widgets in the main window. to be used when the simulation has been completed.
    #def enable_helper(self, widget):
    #    for item in widget.winfo_children():
    #        try:
    #            item['state'] = tk.NORMAL
    #        except:
    #            pass
    #        self.enable_helper(item)

# this class controls a sub-window that collects all the options for the probabalistic simulation and passes them to
# another function that starts the simulation.
# class random_configurator:
#     # This function builds the configurator window
#     def __init__(self,fileVar, parent):
#         self.parent = parent
#         self.fname = fileVar.get()
#         self.valid = True
#         self.density = StringVar()
#         self.root = None
#         self.endpoints = []
#         self.endpointNames = []
#         self.windowItems = []
#         self.checks = []
#         self.frequencies = []
#         self.flowrates = []
#         self.activation_instructions = []
#         self.timer = None
#         try:
#             f1 = open(self.fname)
#             f1.close()
#         except:
#             tm.showerror(title = "Error", message = "invalid filename: pipes model")
#             self.valid = False
#         if not self.valid:
#             return
#         self.options = None
#         self.configurator = tk.Tk()
#         self.frame = tk.Frame(master= self.configurator, borderwidth = 1)
#         self.frame.grid(row = 0, column = 0, pady = 10, padx = 10)
#         self.subframe = tk.Frame(master = self.frame, borderwidth = 0)
#         self.subframe2 = tk.Frame(master = self.frame, borderwidth = 0)
#         self.subframe3 = tk.Frame(master = self.frame, borderwidth = 0)
#         self.configurator.title('Configuration Options')
#         # I think I have now done the work to break dependence of the preview window upon having direct access to the
#         # particle manager object. However, the configurator is still dependent upon having an idea of what the model
#         # is so that it can display user options.
#         self.root, self.endpoints, self.manager, self.timer = builder.build(self.fname)
#         for end in self.endpoints:
#             self.endpointNames.append(end.name)
#         header0 = tk.Label(master = self.frame, text = "Activate Endpoint")
#         header0.grid(row = 0, column = 0, sticky = "nw")
#         header2 = tk.Label(master = self.frame, text = "Probability")
#         header2.grid(row = 0, column = 1, sticky = "nw")
#         header3 = tk.Label(master = self.frame, text = "Flow")
#         header3.grid(row = 0, column = 2, sticky = "nw")
#         i = 0
#         for name in self.endpointNames:
#             selection = IntVar()
#             line = i+1
#             check = tk. Checkbutton(master = self.frame, text = name, variable = selection, onvalue=1, offvalue=0)
#             check.grid(row = line, column = 0, sticky = "nw")
#             check.var = selection
#             check.var.set(0)
#             activation = tk.Entry(master = self.frame, width = 4)
#             activation.grid(row = line, column = 1, sticky = 'nw')
#             activation.insert(0, "0")
#             self.frequencies.append(activation)
#             velocity = tk.Entry(master = self.frame, width = 4)
#             velocity.grid(row = line, column = 2, sticky = "nw")
#             velocity.insert(0, "0")
#             self.flowrates.append(velocity)
#             ## weird hack to make check buttons divulge useful information
#             checkLabel = tk.Label(master=self.frame, state = DISABLED, textvariable = check.var)
#             checkLabel.pack_forget()
#             self.checks.append(checkLabel)
#             i += 1

#         self.subframe.grid(row = i+2, column = 0, sticky = "nw")
#         active_hours = tk.Label(master = self.subframe, text = "Set active hours")
#         active_hours.grid(row = 0, column = 0, sticky = "nw")
#         activeWarning = tk.Label(master = self.subframe, text = "Range [0,24)")
#         activeWarning.grid(row = 0, column = 4, sticky = "nw")
#         self.active_start = tk.Entry(master = self.subframe, width = 4)
#         self.active_start.grid(row = 0, column = 1, sticky = "ne")
#         divider = tk.Label(master = self.subframe, text = "-")
#         divider.grid(row = 0, column = 2, sticky = "ne")
#         self.active_end = tk.Entry(master = self.subframe, width = 4)
#         self.active_end.grid(row = 0, column = 3, sticky = "ne")
#         self.active_start.insert(0, "0")
#         self.active_end.insert(0, "24")
#         self.subframe2.grid(row = i+3, column = 0, sticky = "nw")
#         lengthLabel = tk.Label(master = self.subframe2, text = "Simulation time")
#         lengthLabel.grid(row = 0, column = 0, sticky = "nw")
#         self.runtime = tk.Entry(master = self.subframe2, width = 4)
#         self.runtime.grid(row = 0, column = 1, sticky = "nw")
#         lengthWarning = tk.Label(master = self.subframe2, text = "In days")
#         lengthWarning.grid(row = 0, column = 2, sticky = "nw")
#         densityLabel = tk.Label(master = self.subframe2, text = "Particle density")
#         densityLabel.grid(row = 1, column = 0, sticky = "nw")
#         self.densityEntry = tk.Entry(master = self.subframe2, width = 4)
#         self.densityEntry.grid(row = 1, column = 1, sticky = "nw")
#         densityWarning = tk.Label(master = self.subframe2, text = "Recommended range [0.1, 1]")
#         densityWarning.grid(row = 1, column = 2, sticky = "nw")
#         self.subframe3.grid(row = i+4, column = 0, sticky = "nw")

#         durationLabel = tk.Label(master = self.subframe3, text = "Activation duration range")
#         durationLabel.grid(row = 0, column = 0, sticky = "nw")
#         self.lowDuration = tk.Entry(master = self.subframe3, width = 4)
#         self.lowDuration.grid(row = 0, column = 1, sticky = "nw")
#         divider2 = tk.Label(master=self.subframe3, text="-")
#         divider2.grid(row=0, column=2, sticky="ne")
#         self.highDuration = tk.Entry(master = self.subframe3, width = 4)
#         self.highDuration.grid(row = 0, column = 3, sticky = "nw")
#         durationWarning = tk.Label(master = self.subframe3, text = "Positive integers required, a < b")
#         durationWarning.grid(row = 0, column = 4, sticky = "nw")

#         confirm = tk.Button(master = self.frame, text = "Run Simulation", command = self.validate_configuration)
#         confirm.grid(row = i+5, column = 0, sticky = "s")
#         self.configurator.mainloop()

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


