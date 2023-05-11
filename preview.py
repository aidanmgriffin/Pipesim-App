# # import tkinter as tk
# import particles
# import builder
# import scrollframe
# from functools import partial
# import ete3
# from ete3 import NodeStyle, AttrFace
# import PyQt5
# from multiprocessing import Process
# from PIL import ImageTk, Image
# from matplotlib import colors
# import os
# import shutil

# # this is a helper function that applies a visual design (layout) to an existing node. The node in question is not
# # a part of the pipe network, it is a representation of a pipe in the network. The node (pipe) background color defaults
# # to 100% green and gradually changes from green to red as the stagnation time increases. Note that the value used
# # for comparison is the active variable, which means that it will use the max_age, avg_age, or min_age value as set in
# # the user interface. It is recommended to set this value before running the simulation to get consistent visual output
# # throughout the simulation run.
# # This function is not aware of different time scales that can be used in the simulation, so stagnation times longer
# # than 1 day will appear as maximum stagnation (red). However, this will change if time steps are altered to use minutes
# # or hours instead of seconds. In other words, the output of the real-time graph visual should not be viewed as absolute
# # but rather as relative.
# def layout(node):
#     max_age = 86400
#     default_green = [0,255,50]
#     value = node.active
#     if value >= max_age:
#         value = max_age
#     scale = value / max_age
#     default_green[0] += 255 * scale
#     default_green[1] -= 255 * scale
#     default_green = [i/255 for i in default_green]
#     hex = colors.to_hex(default_green)
#     if not node.is_leaf():
#         style = NodeStyle()
#         style['bgcolor'] = hex
#         node.set_style(style)
#     return node

# # this class controls the live preview of the simulation state (pipes and particle ages)
# # it creates a scrollable frame within the window of the parent (or if no parent window is supplied, it creates it's
# # own window to run inside of. It parses the pipe model file and lays out all the pipes on a grid, the size of which
# # is determined by the size of the pipe network being modeled.
# # The layout of the grid puts the root pipe at the left, and each column to the right contains children of the column
# # to the left of it. Children should appear in the same row as the parent, or if there are more than one, should appear
# # on adjacent rows (above and below). the grid height is determined by the highest number of children on the same level
# # which is intended to minimize the number of times children are displaced from being adjacent to the parent.
# # This implementation was the easiest to do, but the drawback is that it is sometimes difficult to see which child pipes
# # belong to which parent pipes.
# class live_preview():

#     # this constructor initiates the live preview and attaches the scrollable frame to the master widget.
#     # also needs a reference to the parent window to enable registering events with the main window.
#     def __init__(self,window = None, master = None):
#         self.root = None # root pipe node of pipes tree
#         self.manager = None # particle manager
#         # # self.active = tk.IntVar()
#         # # self.active.set(0)
#         # self.graph_counter = 0
#         # if master == None or window == None:
#         #     self.independent = True
#         #     self.master = tk.Tk()
#         #     self.master.geometry("640x400")
#         #     self.window = self.master
#         # else:
#         #     self.independent = False
#         #     self.master = master
#         #     self.window = window
#         # self.container = scrollframe.Scrolling_Area(master = self.master, width = 1000, height = 600)
#         # self.displaySelectLabel = tk.Label(master = self.container, text = "Detail Display Select")
#         # self.displaySelectFrame = tk.Frame(master = self.container, borderwidth = 1)
#         # label_names = ["Minimum age", "Maximum age", "Average age", "Number of particles"]
#         # for i in range (0, 4):
#         #     button = tk.Radiobutton(self.displaySelectFrame, text = label_names[i], padx = 20, variable = self.active, value = i) # command = partial(self.updater, None)
#         #     button.grid(row = 0, column = i)

#         # if self.independent:
#         #     self.displaySelectLabel.pack(side = "top", expand = 0, fill = "both")
#         #     self.displaySelectFrame.pack(side= "top", expand = 0, fill = "both")
#         #     self.container.pack(side = "top", expand = 1, fill = "both")
#         # else:
#         #     self.displaySelectLabel.grid(row = 2, column = 0)
#         #     self.displaySelectFrame.grid(row = 3, column = 0)
#         #     self.container.grid(row = 0, column = 0)
#         # self.envelope = self.container.innerframe
#         self.vars = {}
#         self.pipeData = {}
#         # self.canvas = tk.Canvas(master=self.envelope, width=1500, height=1000)
#         # self.canvas.grid(row=0, column=0)
#         self.tree = None
#         self.graph = None

#     # the constructor does not need a reference to the root node of the model, because the frame may be created at
#     # application launch, while the model will not be available until later. Therefore, this function builds
#     # the contents of the frame and (if independent of a parent window) begins the window's main loop which makes it
#     # active.
#     def start(self, model):
#         self.tree = model
#         # if self.independent:
#         #     self.master.mainloop()

#     # this helper function allows other functions or classes to get access to the scrollable frame the preview class
#     # generates. Display calls this function to place the scrollable frame in the main application window.
#     def get_frame(self):
#         return self.container

#     # this function is called by display when the simulation is started to disable input to the radio buttons once
#     # the simulation is started.
#     # def disable(self):
#     #     self.disable_helper(self.container)

#     # this helper function disables the radio buttons in the preview pane
#     # def disable_helper(self, widget):
#     #     for item in widget.winfo_children():
#     #         try:
#     #             item['state'] = tk.DISABLED
#     #         except:
#     #             pass
#     #         self.disable_helper(item)

#     # this function is called by display when the simulation is completed. It re-enables input to the radio buttons.
#     def enable(self):
#         self.enable_helper(self.container)

#     # this function performs the re-enabling of the radio buttons.
#     # def enable_helper(self, widget):
#     #     for item in widget.winfo_children():
#     #         try:
#     #             item['state'] = tk.NORMAL
#     #         except:
#     #             pass
#     #         self.enable_helper(item)

#     # the updater handles the event call that has been registered with the window. This event queries all the pipes
#     # in the model and updates the display label with the aggregate data about the particles in that pipe.
#     def updater(self, particleData, output_path):
#         self.pipeData = particleData
#         self.TreeUpdater()
#         foldername = output_path
#         if self.graph_counter == 0:
#             if os.path.isdir(foldername):
#                 shutil.rmtree(foldername)
#                 os.mkdir(foldername)
#             else:
#                 os.mkdir(foldername)
#         filename = "/tree_graph-{}.png"
#         filename = foldername + filename
#         generate = filename.format(self.graph_counter)
#         self.graph_counter += 1
#         #self.generate_image(self.tree, filename)
#         p = Process(target=self.generate_image, args=(self.tree, generate))
#         p.start()
#         index = self.graph_counter
#         while index >= 0:
#             try:
#                 openfile = filename.format(index)
#                 #print(openfile)
#                 image = Image.open(openfile)
#                 # image = ImageTk.PhotoImage(image)
#                 self.graph = image
#                 # self.canvas.create_image(10, 10, anchor="nw", image=self.graph)
#                 break
#             except:
#                 #print("missed file", index)
#                 index -= 1

#     # this static function is used to create an image and save it, when passed and ete3 tree object. This function
#     # is called by updater and runs in it's own process so it does not hold up the rest of the program, though the
#     # function itself does not start a new process.
#     @staticmethod
#     def generate_image(tree, filename):
#         if tree != None:
#             ts = ete3.TreeStyle()
#             ts.show_leaf_name=False
#             ts.mode="r"
#             for node in tree.traverse():
#                layout(node)
#             #ts.layout_fn = layout
#             tree.render(filename, w=400, units='mm', tree_style=ts)
#             return filename

#     # this function extracts pertinent data from the pipedata that is passed into the class and updates the ete3 tree
#     # which is used to visually represent the data in the 'real-time' graph.
#     def TreeUpdater(self):
#         if self.tree is None:
#             return
#         else:
#             if self.pipeData is not None:
#                 for node in self.tree.traverse():
#                     key = node.name
#                     if node.name in self.pipeData.keys():
#                         data = self.pipeData[key]
#                         node.num_particles=data[3]
#                         node.avg_age=data[2]
#                         node.max_age=data[1]
#                         node.min_age=data[0]
#                         node.active=data[self.active.get()]
#                     else:
#                         pass
#                         #print("unknown key: ", key)
#                         #print(self.pipeData)

# # debugging function used in early development. Probably doesn't still work. not recently tested.
# if __name__ == '__main__':
#     partman = particles.ParticleManager()

#     root, endpoints = builder.build("PACCAR-kitchens.csv", partman)
#     obj = live_preview()
#     obj.start(root)
#     #preview = obj.get_frame()
#     #preview.grid(row = 0, column = 0)
