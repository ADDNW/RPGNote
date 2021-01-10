import tkinter as tk
from tm_data import TM_data

TOP_ROW_HEIGHT = 10
BOTTOM_ROW_HEIGHT = 10
BUTTON_PADDING_Y = -1
OBJECT_LABELS_HEIGHT = 20


class TM_window(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.data = TM_data()
        
        self.__order_list = tk.Listbox(self, selectmode="SINGLE")
        self.__left_character = TM_object_Frame(self.data, "Current object:")
        self.__right_character = TM_object_Frame(self.data, "Selected object:")

        self.__create_GUI()

    def __create_GUI(self):
        self.minsize(800,600)

        self.__order_list.grid(row=0, column=0, sticky=tk.NSEW)
        
        list_button_frame = tk.Frame(self, height=BOTTOM_ROW_HEIGHT)
        list_button_frame.grid(row=1, column=0, sticky=tk.NSEW)
        list_button_frame.columnconfigure(0, weight=1)
        list_button_frame.columnconfigure(1, weight=1)
        list_button_frame.rowconfigure(0, weight=1)
        
        tk.Button(list_button_frame, command = self.__add_object, text = "ADD").grid(
            row=0, column=0, sticky=tk.NSEW
        )
        tk.Button(list_button_frame, command = self.__next, text = "NEXT").grid(
            row=0, column=1, sticky=tk.NSEW
        )

        self.__left_character.grid(row=0, rowspan=2, column=1, sticky=tk.NSEW)
        self.__right_character.grid(row=0, rowspan=2, column=2, sticky=tk.NSEW)

        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=3)
        self.columnconfigure(2, weight=3)
        self.rowconfigure(0, weight=24)
        self.rowconfigure(1, weight=1)

    def __next(self):
        pass

    def __add_object(self):
        pass

class TM_object_Frame(tk.Frame):
    def __init__(self, data, top_name):
        super().__init__()
        self.__data = data
        
        self.__id = 0

        #character data
        self.__name = tk.StringVar()
        self.__initiative = tk.IntVar()
        self.__advantage = 0
        self.__advantage_max = 0
        self.__advantage_text = tk.StringVar()
        self.__effects = [] #(self._name, self._rounds_to_end, self._stacks, self.__insert_counters(self._effect), self._remove_mode)

        #GUI elements
        self.__effect_edit_button = None
        self.__effect_remove_button = None
        self.__addvanate_add_button = None
        self.__addvanate_remove_button = None
        self.__effects_list = None

        #TEMP:
        self.__name.set("Krwawienie")
        self.__initiative.set(35)
        self.__advantage_text.set("3 / 5")

        self.__create_GUI(top_name)

    def _new_object(self, id, character_data):
        self.grid()
        self.__id = id
        (
            name,
            initiative,
            self.__advantage,
            self.__advantage_max,
            self.__effects
        ) = character_data

        self.__name.set(name)
        self.__initiative.set(initiative)
        self.__advantage_text.set("{self.__advantage} / {self.__advantage_max}")

    def _hide(self):
        self.id = 0
        self.grid_remove()

    #gui
    def __create_GUI(self, top_name):
        self.__create_top_panel(top_name)
        self.__create_bottom_panel()
        self.__create_object_placeholder()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=18)
        self.rowconfigure(2, weight=1)

    def __create_top_panel(self, top_name):
        top = tk.Frame(self, height = TOP_ROW_HEIGHT)
        top.grid(row = 0, column = 0, sticky=tk.NSEW)

        tk.Label(top, text= top_name).grid(row=0, column=0, sticky=tk.NSEW)
        tk.Button(top, command = self.__edit, text = "EDIT").grid(
            row=0, column=1, sticky=tk.NSEW
        )
        tk.Button(top, command = self.__remove, text = "REMOVE").grid(
            row=0, column=2, sticky=tk.NSEW
        )
        top.rowconfigure(0, weight=1)
        top.columnconfigure(0, weight=1)
        top.columnconfigure(1, weight=1)
        top.columnconfigure(2, weight=1)
    
    def __create_object_placeholder(self):
        content = tk.Frame(self, height=TOP_ROW_HEIGHT)
        content.grid(row = 1, column = 0, sticky=tk.NSEW)

        tk.Label(content, textvariable=self.__name).grid(row = 0, column = 0, columnspan = 3, sticky=tk.NSEW)
        tk.Label(content, text="Initiative").grid(row = 1, column = 0, sticky=tk.NSEW)
        tk.Label(content, text="Advances").grid(row = 1, column = 1, columnspan = 2, sticky=tk.NSEW)
        tk.Label(content, textvariable=self.__initiative).grid(row = 2, column = 0, rowspan = 2, sticky=tk.NSEW)
        
        self.__addvanate_add_button = tk.Button(content, text = "+", command=self.__increase_advances)
        self.__addvanate_add_button.grid(row = 2, column = 1, sticky=tk.NSEW)
        self.__addvanate_remove_button = tk.Button(
            content, text = "-", command=self.__increase_advances, state=tk.DISABLED
        )
        self.__addvanate_remove_button.grid(row = 3, column = 1, sticky=tk.NSEW)

        tk.Label(content, textvariable=self.__advantage_text).grid(row = 2, column = 2, rowspan = 2, sticky=tk.NSEW)

        self.__effects_list = tk.Listbox(content)
        self.__effects_list.grid(row = 4, column = 0, columnspan = 3, sticky=tk.NSEW)

        content.rowconfigure(0, weight=2)
        content.rowconfigure(1, weight=2)
        content.rowconfigure(2, weight=1)
        content.rowconfigure(3, weight=1)
        content.rowconfigure(4, weight=16)
        content.columnconfigure(0, weight=4)
        content.columnconfigure(1, weight=1)
        content.columnconfigure(2, weight=3)
        
    def __create_bottom_panel(self):
        bottom = tk.Frame(self, height=BOTTOM_ROW_HEIGHT)
        bottom.grid(row = 2, column = 0, sticky=tk.NSEW)

        tk.Label(bottom, text= "Effect: ").grid(row=0, column=0, sticky=tk.NSEW)
        tk.Button(bottom, command = self.__add_effect, text = "ADD").grid(
            row=0, column=1, sticky=tk.NSEW
        )
        self.__effect_edit_button = tk.Button(bottom, command = self.__edit_effect, text = "EDIT")
        self.__effect_edit_button.grid(row=0, column=2, sticky=tk.NSEW)
        self.__effect_remove_button = tk.Button(bottom, command = self.__remove_effect, text = "REMOVE")
        self.__effect_remove_button.grid(row=0, column=3, sticky=tk.NSEW)

        bottom.rowconfigure(0, weight=1)
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=1)
        bottom.columnconfigure(2, weight=1)
        bottom.columnconfigure(3, weight=1)

    #buttons
    def __edit(self):
        pass

    def __remove(self):
        pass
    
    def __add_effect(self):
        pass

    def __edit_effect(self):
        pass

    def __remove_effect(self):
        pass

    def __increase_advances(self):
        pass

    def __decrease_advances(self):
        pass

if __name__ == "__main__":
    TM_window().mainloop()