# from tkinter import Tk
# from tkinter import Label
# from tkinter import StringVar
# from tkinter import Canvas
# from PIL import Image
# from PIL import ImageTk
# from tkinter import PhotoImage
# from tkinter import Button
# from multiprocessing import Process

# # this class displays the results graph when the simulation is completed. This was moved to its own window to
# # save real-estate in the main application window for more interactive content.
# class ShowImageDialogHelper:
#     def __init__(self, title="", message="", image=None):
#         self.window = Tk()
#         self.window.title(title)
#         self.window.msg = StringVar()
#         self.window.msg.set(message)
#         image=PhotoImage(file=image)
#         self.window.geometry("800x680")
#         if image is not None:
#             canvas = Label(master=self.window, image=image)
#             canvas.pack()
#         dmesg = Label(master=self.window, width=600, textvariable=self.window.msg)
#         dmesg.pack()
#         button = Button(master=self.window, text="OK", command=self.window.destroy)
#         button.pack()
#         self.window.mainloop()

# # this is the class that is called from outside. it starts a new window it its own process to avoid conflicting
# # with the main window.
# class ShowImageDialog:
#     def __init__(self, title="", message="", image=None):
#         p = Process(target=ShowImageDialogHelper, args=(title, message, image))
#         p.start()

# # this function is used for testing. note that it may not work if there is no file that matches the filename variable
# # requested in the first line of the function.
# if __name__ == '__main__':
#     filename='age_graph.png'
#     #image = Image.open(filename)
#     #image = image.resize(size = (600,400))
#     s = ShowImageDialog("test","test",image=filename)