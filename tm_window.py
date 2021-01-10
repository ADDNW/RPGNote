import tkinter as tk

class TM_window(tk.Tk):
    def __init__(self):
        super().__init__()



        self.__create_GUI()

    def __create_GUI(self):
        self.minsize(800,600)
        