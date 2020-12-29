import tkinter as tk

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

    #GUI objects
    (
      self.note_area,
      self.marked_files_area,
      self.marked_files_buttons,
      self.top_panel_area,
      self.write_top_panel,
      self.read_top_panel
    ) = self.createGUI()
  
  #init
  def createGUI(self):
    return (None, None, None, None, None, None)

  #file working
  def read_working_directory(self):
    return ''

  def mark_files(self):
    return []

  def open_file(self, name):
    pass
  
  def save_file(self, name):
    pass

  #markers insert
  def add_target_marker(self):
    pass

  def add_link_marker(self):
    pass


if __name__ == "__main__":
  Note_window().mainloop()