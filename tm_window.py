import tkinter as tk
from tkinter import messagebox
from enum import Enum
from tm_data import TM_data, TM_remove_mode, TM_effect

EFFECT_ROW_WIDTH = 60
ORDER_LIST_NAME = 'order_list'
LEFT_EFFECT_LIST_NAME = 'left_effect_list'
LEFT_TOP_NAME = 'Current object:'
RIGHT_EFFECT_LIST_NAME = 'right_effect_list'
RIGHT_TOP_NAME = 'Selected object:'

#dialog_constants
EFFECT_DESCRIPTION_WIDTH = 50
TEXT_LINE_WIDTH = 200
ROUNDS_STATS_DELTA_ENTRY_WIDTH = 5

class TM_window(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master=master)
        
        self.__data = TM_data()
        
        self.__order_list = []
        self.__order_list_box = tk.Listbox(self, selectmode="SINGLE", name=ORDER_LIST_NAME, exportselection=False)
        self.__left_character = TM_object_Frame(self, self.__data, True)
        self.__right_character = TM_object_Frame(self, self.__data, False)

        self.__create_GUI()
        self._read_to_list()
        self.lift()

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
            self.__left_character._show_object(next_id)
            if self.__right_character._id == next_id:
                self.__right_character._hide()

    def __add_object(self):
        self._open_dialog(Dialog_type.DIALOG_OBJECT)

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
                self.__left_character._show_object(id)
                self.update_idletasks()
            if mode == TM_remove_mode.ROUND_END_COUNT_BUT_TEST:
                self._open_dialog(Dialog_type.DIALOG_END_TEST, (id, index, mode, text))
            elif mode == TM_remove_mode.ROUND_END_MESSAGE_ON_EXPIRE:
                self._open_dialog(Dialog_type.DIALOG_END_MESSAGE, (id, index, mode, text))
            elif mode == TM_remove_mode.ROUND_END_TEST_STACK or \
                 mode == TM_remove_mode.TURN_CAN_TEST_STACK:
                self._open_dialog(Dialog_type.DIALOG_STACK_TEST, (id, index, mode, text))   
    
    def __on_list_element_selected(self, event):
        index = self.__order_list_box.curselection()[0]
        if index != 0 and self.__order_list[index][0] != 0: #not current and not ROUND END
            self.__right_character._show_object(self.__order_list[index][0])

    #dialogs
    def _open_dialog(self, dialog_type, params=None):
        dialog = TM_dialog(self, dialog_type, params)     
        self.wm_attributes("-disabled", True)
        dialog.protocol("WM_DELETE_WINDOW", lambda : self._close_dialog(dialog_type, dialog, params==None))
        self.wait_window(dialog)

    def _close_dialog(self, dialog_type, dialog, is_new):
        if not dialog.canceled:
            if dialog_type == Dialog_type.DIALOG_OBJECT:
                if is_new:
                    self._read_to_list(self.__data.add_object(dialog.data[1], dialog.data[2], dialog.data[3]))
                else:
                    self._read_to_list(self.__data.edit_object(dialog.data[0], dialog.data[1], dialog.data[2], dialog.data[3]))
                    self.__get_object_frame_by_id(dialog.data[0])._show_object()
            elif dialog_type == Dialog_type.DIALOG_EFFECT:
                if is_new:
                    self.__data.add_effect(dialog.data[0], dialog.data[2], dialog.data[3], dialog.data[4], dialog.data[5], dialog.data[6], dialog.data[7])
                else:
                    self.__data.edit_effect(dialog.data[0], dialog.data[1], dialog.data[2], dialog.data[3], dialog.data[4], dialog.data[5], dialog.data[6], dialog.data[7])
                self.__get_object_frame_by_id(dialog.data[0])._show_effects()
            elif dialog_type == Dialog_type.DIALOG_STACK_TEST or \
                 dialog_type == Dialog_type.DIALOG_END_TEST:
                self.__data.effect_update_reaction(dialog.data[0], dialog.data[1], dialog.data[2], dialog.data[3])
                self.__get_object_frame_by_id(dialog.data[0])._show_effects()
   
        dialog.destroy()
        self.wm_attributes("-disabled", False)
        self.lift()
    
    def __get_object_frame_by_id(self, id):
        if self.__left_character._id == id:
            return self.__left_character
        elif self.__right_character._id == id:
            return self.__right_character


class TM_object_Frame(tk.Frame):
    def __init__(self, parent, data, is_left):
        super().__init__(parent)
        self.__data = data

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

    def _show_object(self, id=None):
        if id:
            self.grid()
            self._id = id
        (
            name,
            initiative,
            self.__advantage,
            self.__advantage_max,
            effects
        ) = self.__data.get_object(self._id)
    
        self.__name.set(name)
        self.__initiative.set(initiative)
        self.__create_advantage_text()
        self.__update_buttons_status()
        self._show_effects(effects)
        
    def _show_effects(self, effects=None):
        if not effects:
            self.__effects = self.__data.get_effects(self._id)
        else:
            self.__effects = effects
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

        self.__effects_list = tk.Listbox(content, width=EFFECT_ROW_WIDTH, name=LEFT_EFFECT_LIST_NAME if is_left else RIGHT_EFFECT_LIST_NAME)
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
        self.master._open_dialog(Dialog_type.DIALOG_OBJECT,  (self._id, self.__name.get(), self.__initiative.get(), self.__advantage_max))

    def __remove(self):
        if messagebox.askokcancel("delete", "Are you sure to delete it?", icon='warning'):
            self.master._read_to_list(self.__data.remove_object(self._id))
            self._hide()

    def __add_effect(self):
        self.master._open_dialog(Dialog_type.DIALOG_EFFECT, self._id)

    def __edit_effect(self):
        if self.__effects_list.curselection():
            index = self.__effects_list.curselection()[0]
            current_data = self.__data.get_effect(self._id, index)
            edit_data = (self._id, index, current_data[0], current_data[1], current_data[2], current_data[3], current_data[4], current_data[5])
            self.master._open_dialog(Dialog_type.DIALOG_EFFECT, edit_data)

    def __remove_effect(self):
        if self.__effects_list.curselection():
            if messagebox.askokcancel("delete", "Are you sure to delete it?", icon='warning'):
                index = self.__effects_list.curselection()[0]
                self.__effects_list.delete(index)
                self.__data.remove_effect(self._id, index)          

    def __increase_advances(self):
        if self.__data.change_advantage(self._id, self.__advantage+1):
            self.__advantage += 1
            self.__create_advantage_text()
            self.__update_buttons_status()

    def __decrease_advances(self):
        if self.__data.change_advantage(self._id, self.__advantage-1):
            self.__advantage -= 1
            self.__create_advantage_text()
            self.__update_buttons_status()

    def __update_buttons_status(self):
        if self.__advantage == 0: 
            self.__addvanate_remove_button.config(state=tk.DISABLED)
        else:
            self.__addvanate_remove_button.config(state=tk.NORMAL)
        if self.__advantage == self.__advantage_max: 
            self.__addvanate_add_button.config(state=tk.DISABLED)
        else:
            self.__addvanate_add_button.config(state=tk.NORMAL)
        

    #private
    def __create_advantage_text(self):
        self.__advantage_text.set(f"{self.__advantage} / {self.__advantage_max}")

    def __format_effect(self, effect):
        formated = effect[0] + ': ' 
        if effect[1] != -1:
            formated += "Rounds: " + str(effect[1]) + "; "
        if effect[2] != -1:
            formated += "Stacks: " + str(effect[2]) + "; "
        formated += effect[3]
        return formated


class TM_dialog(tk.Toplevel):
    def __init__(self, master, dialog_type, params):
        super().__init__(master=master)
        self.data = params
        self.is_new = params == None
        self.canceled = True
        self.dialog_type = dialog_type

        if dialog_type == Dialog_type.DIALOG_OBJECT:
            self.__object_dialog()
        elif dialog_type == Dialog_type.DIALOG_EFFECT:
            self.__effect_dialog()
        elif dialog_type == Dialog_type.DIALOG_STACK_TEST:
            self.__stack_dialog()
        elif dialog_type == Dialog_type.DIALOG_END_TEST:
            self.__end_test_dialog()
        elif dialog_type == Dialog_type.DIALOG_END_MESSAGE:
            self.__end_message_dialog()

    #build
    def __object_dialog(self):
        #params: id, name, ini, adv_max
        if not self.data:
            self.data = (-1, "", 0, 0)

        def save():
            if name.get() and initiative.get() >= 0 and advantage_max.get() >= 0:
                self.__accept_dialog(
                    (self.data[0], name.get(), initiative.get(), advantage_max.get())
                )

        name = tk.StringVar(value=self.data[1])
        initiative = tk.IntVar(value=self.data[2])
        advantage_max = tk.IntVar(value=self.data[3])

        self.geometry("240x140")
        tk.Label(self, text = "Name").place(x = 10, y = 10)
        tk.Entry(self, textvariable=name).place(x = 100, y = 10)
        tk.Label(self, text = "Initiative").place(x = 10, y = 40)
        tk.Entry(self, textvariable=initiative).place(x = 100, y = 40)
        tk.Label(self, text = "Max advantage").place(x = 10, y = 70)
        tk.Entry(self, textvariable=advantage_max).place(x = 100, y = 70)
        tk.Button(self, text = "Save", command=save).place(x = 60, y = 100)
        tk.Button(self, text = "Cancel", command=self.__reject_dialog).place(x = 120, y = 100)

    def __effect_dialog(self):
        #params: id, index, name, r, s, eff, mode, text
        if isinstance(self.data, int):
            self.is_new = True
            self.data = (self.data, -1, "", 0, 0, "", TM_remove_mode.get_default(), "")
        else:
            self.data = (self.data[0], self.data[1], self.data[2], self.data[3], self.data[4],
                         self.data[5], TM_remove_mode.get_options()[self.data[6].value], self.data[7])


        def block_entries(event=None):
            if TM_remove_mode.needs_rounds(mode.get()):
                rounds_entry.config(state=tk.NORMAL)
            else: 
                rounds_entry.config(state=tk.DISABLED)
            
            if TM_remove_mode.needs_stacks(mode.get()):
                stacks_entry.config(state=tk.NORMAL)
            else: 
                stacks_entry.config(state=tk.DISABLED)

            if TM_remove_mode.needs_dialog(mode.get()):
                dialog_entry.config(state=tk.NORMAL)
            else: 
                dialog_entry.config(state=tk.DISABLED)

        def save():
            if name.get() and mode.get() and effects.get():
                if (not TM_remove_mode.needs_rounds(mode.get()) or rounds.get() > 0) and \
                   (not TM_remove_mode.needs_stacks(mode.get()) or stacks.get() > 0) and \
                   (not TM_remove_mode.needs_dialog(mode.get()) or dialog_text.get()):
                    if not TM_remove_mode.needs_rounds(mode.get()):
                        rounds.set(-1)
                    if not TM_remove_mode.needs_stacks(mode.get()):
                        stacks.set(-1)
                    if not TM_remove_mode.needs_dialog(mode.get()):
                        dialog_text.set("")
                    self.__accept_dialog((
                        self.data[0], self.data[1], name.get(), rounds.get(), stacks.get(),
                        effects.get(), TM_remove_mode.parse(mode.get()), dialog_text.get() 
                    ))

        name = tk.StringVar(value=self.data[2])
        mode = tk.StringVar(value=self.data[6])
        rounds = tk.IntVar(value=self.data[3])
        stacks = tk.IntVar(value=self.data[4])
        effects = tk.StringVar(value=self.data[5])
        dialog_text = tk.StringVar(value=self.data[7])

        self.geometry("450x230")
        rounds_entry = tk.Entry(self, textvariable=rounds, width=ROUNDS_STATS_DELTA_ENTRY_WIDTH)
        stacks_entry = tk.Entry(self, textvariable=stacks, width=ROUNDS_STATS_DELTA_ENTRY_WIDTH)
        dialog_entry = tk.Entry(self, textvariable=dialog_text, width=EFFECT_DESCRIPTION_WIDTH)
        block_entries()

        tk.Label(self, text = "Name").place(x = 10, y = 10)
        tk.Entry(self, textvariable=name).place(x = 100, y = 10)    
        tk.Label(self, text = "Mode").place(x = 10, y = 40)
        tk.OptionMenu(self, mode, *(TM_remove_mode.get_options()), command=block_entries).place(x = 100, y = 35)
        tk.Label(self, text = "Rounds").place(x = 10, y = 70)
        rounds_entry.place(x = 60, y = 70)
        tk.Label(self, text = "Stacks").place(x = 100, y = 70)
        stacks_entry.place(x = 150, y = 70)
        tk.Label(self, text = "Effect").place(x = 10, y = 100)
        tk.Entry(self, textvariable=effects, width=EFFECT_DESCRIPTION_WIDTH).place(x = 100, y = 100)
        tk.Label(self, text = "Dialog text").place(x = 10, y = 130)
        dialog_entry.place(x = 100, y = 130)
        tk.Label(self, 
            text = "Hint: to instert current rounds/stack number in effect or dialog use character " + 
            TM_effect.DESCRIPTION_REPLACE_WITH_ROUNDS_SIGN + '/' + TM_effect.DESCRIPTION_REPLACE_WITH_STACK_SIGN
        ).place(x = 10, y = 160)
        tk.Button(self, text = "Save", command=save).place(x = 250, y = 190)
        tk.Button(self, text = "Cancel", command=self.__reject_dialog).place(x = 300, y = 190)

    def __stack_dialog(self):
        #params: id, index, mode, text->returned
        delta = tk.IntVar(value = 0)

        def save():
            self.__accept_dialog((self.data[0], self.data[1], self.data[2], delta.get()))

        self.geometry("220x180")
        tk.Label(self, text=self.data[3], wraplength=TEXT_LINE_WIDTH, justify=tk.LEFT).place(x = 5, y = 5)
        tk.Label(self, text = "Change stacks value by:").place(x=10, y=100)
        tk.Label(self, text = "(\"-1\" means remove 1 stack)").place(x=10, y=120)
        tk.Entry(self, textvariable=delta, width=ROUNDS_STATS_DELTA_ENTRY_WIDTH).place(x=150, y = 100)
        tk.Button(self, text = "Save", command=save).place(x = 90, y = 140)
        
    def __end_test_dialog(self):
        #params: id, index, mode, text->returned

        def lose():
            self.__accept_dialog((self.data[0], self.data[1], self.data[2], False))

        self.geometry("220x130")
        tk.Label(self, text=self.data[3], wraplength=TEXT_LINE_WIDTH, justify=tk.LEFT).place(x = 5, y = 5)
        tk.Button(self, text = "Keep", command=self.__reject_dialog).place(x = 100, y = 100)
        tk.Button(self, text = "Lose", command=lose).place(x = 150, y = 100)

    def __end_message_dialog(self):
        #params: id, index, mode, text->returned

        self.geometry("220x130")
        tk.Label(self, text=self.data[3], wraplength=TEXT_LINE_WIDTH, justify=tk.LEFT).place(x = 5, y = 5)
        tk.Button(self, text = "Close", command=self.__reject_dialog).place(x = 150, y = 100)


    #result
    def __accept_dialog(self, new_data):
        self.data = new_data
        self.canceled = False
        self.master._close_dialog(self.dialog_type, self, self.is_new)

    def __reject_dialog(self):
        self.master._close_dialog(self.dialog_type, self, self.is_new)


class Dialog_type(Enum):
    DIALOG_OBJECT = 0
    DIALOG_EFFECT = 1
    DIALOG_STACK_TEST = 2
    DIALOG_END_TEST = 3
    DIALOG_END_MESSAGE = 4


if __name__ == "__main__":
    root = tk.Tk()
    root.wm_state('iconic')
    TM_window(root).mainloop()