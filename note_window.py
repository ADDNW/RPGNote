import tkinter as tk
from tkinter import filedialog

class Note_window(tk.Tk):
  def __init__(self):
    super().__init__()
    
    #mode
    self.write_mode = False
    
    #filedata
    self.working_directory = ''
    self.current_file = ''
    self.marked_files = []
    
    #pointers
    self.markers = {}
    self.NPCs = {}

    #GUI objects - created in createGUI method
    self.note_area = None
    self.marked_files_area = None
    self.top_panel_area = None

    self.__create_GUI()
  
  #init
  def __create_GUI(self):
    self.__create_menu()
    self.__create_top_panels()
    self.__create_marked_area()
    self.__create_content()

  def __create_menu(self):
    menubar = tk.Menu(self)
    filemenu = tk.Menu(menubar, tearoff = 0)
    filemenu.add_command(label = "New working directory", command = self.__read_working_directory)
    self.bind("<Control-o>", self.__read_working_directory)
    filemenu.add_command(label = "Save", command = self.__save_file)
    self.bind("<Control-s>", self.__save_file)

    menubar.add_cascade(label = "File", menu = filemenu)
    self.config(menu = menubar)

  def __create_top_panels(self):
    pass

  def __create_marked_area(self):
    pass

  def __create_content(self):
    pass

  #file working
  def __read_working_directory(self):
    return ''

  def mark_files(self):
    return []

  def open_file(self):
    path = filedialog.askopenfilename()
    if not path.startswith(self.working_directory):
      #TODO warning about file is not part of this workspace
      return None
    with open(path, "r") as new_file:
      self.note_area #TODO add line by line text to note_area

  def __save_file(self):
    pass

  #markers insert
  def add_target_marker(self):
    pass

  def add_link_marker(self):
    pass


if __name__ == "__main__":
  Note_window().mainloop()