import tkinter as tk
from tkinter import messagebox
from tm_data import TM_data, TM_remove_mode

EFFECT_WIDTH = 60
ORDER_LIST_NAME = 'order_list'
LEFT_EFFECT_LIST_NAME = 'left_effect_list'
LEFT_TOP_NAME = 'Current object:'
RIGHT_EFFECT_LIST_NAME = 'right_effect_list'
RIGHT_TOP_NAME = 'Selected object:'

class TM_window(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.__data = TM_data()
        
        self.__order_list = []
        self.__order_list_box = tk.Listbox(self, selectmode="SINGLE", name=ORDER_LIST_NAME, exportselection=False)
        self.__left_character = TM_object_Frame(self, self.__data, True)
        self.__right_character = TM_object_Frame(self, self.__data, False)

        self.__create_GUI()
        self._read_to_list()

    def __create_GUI(self):
        self.minsize(800,600)

        self.__order_list_box.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)
        self.__order_list_box.bind('<<ListboxSelect>>', self.__on_list_element_selected)

        tk.Button(self, command = self.__add_object, text = "ADD").grid(
            row=1, column=0, sticky=tk.NSEW
        )
        tk.Button(self, command = self.__next, text = "NEXT").grid(
            row=1, column=1, sticky=tk.NSEW
        )

        self.__left_character.grid(row=0, rowspan=2, column=2, sticky=tk.NSEW)
        self.__left_character._hide()
        self.__right_character.grid(row=0, rowspan=2, column=3, sticky=tk.NSEW)
        self.__right_character._hide()

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=3)
        self.columnconfigure(3, weight=3)
        self.rowconfigure(0, weight=36)
        self.rowconfigure(1, weight=1)

    def __next(self):
        if self.__order_list[0][0] != 0: #if current is not ROUND END
            self.__execute__effects(self.__data.get_current_effects_to_execute())

        self.__data.next()
        
        current = self.__order_list[0]
        self.__order_list_box.delete(0)
        self.__order_list_box.insert(tk.END, current[1])
        self.__order_list = (self.__order_list[1:]) + [current]
        next_id = self.__order_list[0][0]
        if next_id == 0: #if next is ROUND END
            self.__execute__effects(self.__data.get_current_effects_to_execute())
            self.__left_character._hide()
        else:
            self.__left_character._new_object(next_id, self.__data.get_object(next_id))
            if self.__right_character._id == next_id:
                self.__right_character._hide()

    def __add_object(self):
        pass #TODO

    def _read_to_list(self, new_list=None):
        if not new_list:
            new_list = self.__data.tm_list
        self.__order_list = new_list
        self.__order_list_box.delete(0, tk.END)
        for el in self.__order_list:
            self.__order_list_box.insert(tk.END, el[1])

    def __execute__effects(self, effects):
        for id, index, mode, text in effects:
            if id != self.__left_character._id:
                self.__left_character._new_object(id, self.__data.get_object(id))
            #TODO dialogs
            if mode == TM_remove_mode.ROUND_END_COUNT_BUT_TEST:
                result = True #or False
            elif mode == TM_remove_mode.ROUND_END_MESSAGE_ON_EXPIRE:
                result = None
            elif mode == TM_remove_mode.ROUND_END_TEST_STACK or \
                 mode == TM_remove_mode.TURN_CAN_TEST_STACK:
                result = -1
            self.__data.effect_update_reaction(id, index, mode, result)
    
    def __on_list_element_selected(self, event):
        w = event.widget
        if w._name == ORDER_LIST_NAME:
            index = self.__order_list_box.curselection()[0]
            if index != 0 and self.__order_list[index][0] != 0: #not current and not ROUND END
                self.__right_character._new_object(
                    self.__order_list[index][0], self.__data.get_object(self.__order_list[index][0])
                )


class TM_object_Frame(tk.Frame):
    def __init__(self, parent, data, is_left):
        super().__init__(parent)
        self.__data = data
        self.__parent = parent

        self._id = 0

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

        self.__create_GUI(is_left)

    def _new_object(self, id, character_data):
        self.grid()
        self._id = id
        (
            name,
            initiative,
            self.__advantage,
            self.__advantage_max,
            self.__effects
        ) = character_data
    
        self.__name.set(name)
        self.__initiative.set(initiative)
        self.__create_advantage_text()
        self.__effects_list.delete(0, tk.END)
        for effect in self.__effects:
            self.__effects_list.insert(tk.END, self.__format_effect(effect))

    def _hide(self):
        self.id = 0
        self.grid_remove()

    #gui
    def __create_GUI(self, is_left):
        self.__create_top_panel(is_left)
        self.__create_bottom_panel()
        self.__create_object_placeholder(is_left)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=2)
        self.rowconfigure(1, weight=51)
        self.rowconfigure(2, weight=2)

    def __create_top_panel(self, is_left):
        top = tk.Frame(self)
        top.grid(row = 0, column = 0, sticky=tk.NSEW)

        tk.Label(
            top, text = LEFT_TOP_NAME if is_left else RIGHT_TOP_NAME 
        ).grid(row=0, column=0, sticky=tk.NSEW)
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
    
    def __create_object_placeholder(self, is_left):
        content = tk.Frame(self)
        content.grid(row = 1, column = 0, sticky=tk.NSEW)

        tk.Label(content, textvariable=self.__name).grid(row = 0, column = 0, columnspan = 3, sticky=tk.NSEW)
        tk.Label(content, text="Initiative").grid(row = 1, column = 0, sticky=tk.NSEW)
        tk.Label(content, text="Advances").grid(row = 1, column = 1, columnspan = 2, sticky=tk.NSEW)
        tk.Label(content, textvariable=self.__initiative).grid(row = 2, column = 0, rowspan = 2, sticky=tk.NSEW)
        
        self.__addvanate_add_button = tk.Button(content, text = "+", command=self.__increase_advances)
        self.__addvanate_add_button.grid(row = 2, column = 1, sticky=tk.NSEW)
        self.__addvanate_remove_button = tk.Button(
            content, text = "-", command=self.__decrease_advances, state=tk.DISABLED
        )
        self.__addvanate_remove_button.grid(row = 3, column = 1, sticky=tk.NSEW)

        tk.Label(content, textvariable=self.__advantage_text).grid(row = 2, column = 2, rowspan = 2, sticky=tk.NSEW)

        self.__effects_list = tk.Listbox(content, width=EFFECT_WIDTH, name= LEFT_EFFECT_LIST_NAME if is_left else RIGHT_EFFECT_LIST_NAME)
        self.__effects_list.grid(row = 4, column = 0, columnspan = 3, sticky=tk.NSEW)

        content.rowconfigure(0, weight=3)
        content.rowconfigure(1, weight=3)
        content.rowconfigure(2, weight=1)
        content.rowconfigure(3, weight=1)
        content.rowconfigure(4, weight=48)
        content.columnconfigure(0, weight=4)
        content.columnconfigure(1, weight=1)
        content.columnconfigure(2, weight=3)
        
    def __create_bottom_panel(self):
        bottom = tk.Frame(self)
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
        pass #TODO

    def __remove(self):
        if messagebox.askokcancel("delete", "Are you sure to delete it?", icon='warning'):
            self.__parent._read_to_list(self.__data.remove_object(self._id))
            self._hide()

    
    def __add_effect(self):
        pass #TODO

    def __edit_effect(self):
        pass #TODO

    def __remove_effect(self):
        if self.__effects_list.curselection():
            if messagebox.askokcancel("delete", "Are you sure to delete it?", icon='warning'):
                index = self.__effects_list.curselection()[0]
                self.__effects_list.delete(index)
                self.__data.remove_effect(self._id, index)
                

    def __increase_advances(self):
        if self.__advantage == 0:
            self.__addvanate_remove_button.config(state=tk.NORMAL)
        if self.__data.change_advantage(self._id, self.__advantage+1):
            self.__advantage += 1
            self.__create_advantage_text()
            if self.__advantage == self.__advantage_max:
                self.__addvanate_add_button.config(state=tk.DISABLED)

    def __decrease_advances(self):
        if self.__advantage == self.__advantage_max:
            self.__addvanate_add_button.config(state=tk.NORMAL)
        if self.__data.change_advantage(self._id, self.__advantage-1):
            self.__advantage -= 1
            self.__create_advantage_text()
            if self.__advantage == 0:
                self.__addvanate_remove_button.config(state=tk.DISABLED)

    def __create_advantage_text(self):
        self.__advantage_text.set(f"{self.__advantage} / {self.__advantage_max}")

    def __format_effect(self, effect):
        formated = effect[0] + ': ' 
        if effect[1]:
            formated += "Rounds: " + str(effect[1]) + "; "
        if effect[2]:
            formated += "Stacks: " + str(effect[2]) + "; "
        formated += effect[3]
        return formated

if __name__ == "__main__":
    TM_window().mainloop()