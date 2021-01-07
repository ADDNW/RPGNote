import tkinter as tk
from tkinter import filedialog, ttk
from notes_compiler import format_file, extract_filename, compile_all_notes, \
  MARKER_TARGET_PATTERN, MARKER_ENDING, MARKER_LINK_PATTERN, MARK_LINK, MARKER_LINK_BASIC, MARKER_TARGET_BASIC


class Note_window(tk.Tk):
  def __init__(self):
    super().__init__()
    
    #mode
    self.write_mode = False
    
    #filedata
    self.working_directory = ''
    self.current_file = ''
    self.marked_files = []
    self.current_file_content = ''
    
    #pointers
    self.markers = None
    self.current_file_pointers = None

    #GUI objects - created in createGUI method
    self.note_area = None
    self.marked_files_area = None
    self.write_panel_area = None

    self.__create_GUI()
  
  #init
  def __create_GUI(self):
    self.minsize(800,600)
    self.__create_menu()
    self.__create_top_panels()
    self.__create_marked_area()
    self.__create_content()

    self.columnconfigure(0, weight=1)
    self.columnconfigure(1, weight=9)
    self.rowconfigure(0, weight=1)
    self.rowconfigure(1, weight=1)
    self.rowconfigure(2, weight=98)

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
    self.write_panel_area = tk.Frame(self, bg="white")
    main_panel_area = tk.Frame(self, bg="white")

    for command, label in [
      (self.__open_file, "Open file"),
      (self.__mark_files, "Mark files"),
      (self.__mark_current_file, "Mark current"),
      (self.__unmark_current_file, "Unmark current"),
      (None,None),
      (self.__switch_mode, "Switch Mode"),
      (self.__open_TM_window, "Start TM")
    ]:
      if label:
        tk.Button(main_panel_area, command = command, text = label).pack(side="left")
      else:
         tk.ttk.Separator(main_panel_area, orient='vertical').pack(side="left", padx=(7,5), fill='y')

    tk.Button(self.write_panel_area, command = self.__add_link_marker, text = "Create link here").pack(side="left")
    tk.Button(self.write_panel_area, command = self.__add_target_marker, text = "Create mark here").pack(side="left")

    main_panel_area.grid(row = 0, column = 1, sticky = tk.NSEW)

  def __create_marked_area(self):
    self.marked_files_area = tk.Listbox(self, selectmode="SINGLE")
    self.marked_files_area.bind('<<ListboxSelect>>', self.__open_marked_file)
    self.marked_files_area.grid(row = 0, column = 0, rowspan = 3, sticky = tk.NSEW)

  def __create_content(self):
    note = tk.Frame(self)
    self.note_area = tk.Text(note)
    scroll = tk.Scrollbar(note, orient="vertical", command=self.note_area.yview)
    self.note_area.configure(yscrollcommand=scroll.set)

    self.note_area.grid(row=0, column = 0, sticky = tk.NSEW)
    scroll.grid(row=0, column = 1, sticky = tk.NS)

    note.rowconfigure(0, weight=1)
    note.columnconfigure(0, weight=999)
    note.columnconfigure(1, weight=1)
    note.grid(row = 2, column = 1, sticky = tk.NSEW)

  #file working
  def __read_working_directory(self):
    path = filedialog.askdirectory()
    if path:
      self.working_directory = path
      if not self.write_mode:
        self.markers = compile_all_notes(path)
        self.current_file = None
        self.marked_files = []
        self.current_file_pointers = None
        self.note_area.delete('1.0', tk.END)

  def __mark_files(self):
    if self.working_directory:
      for file in filedialog.askopenfilenames():
        if file.startswith(self.working_directory):
          self.marked_files.append(file)
          self.marked_files_area.insert(tk.END, extract_filename(file))

  def __open_file(self):
    path = filedialog.askopenfilename()
    if self.working_directory and path.startswith(self.working_directory):
      self.__read_file(path)
      
  def __save_file(self, event=None):
    self.current_file_content = self.note_area.get(1.0, tk.END)[0:-1]
    with open(self.current_file, "w+",  encoding="UTF-8") as file:
      file.write(self.current_file_content)

  #marking files
  def __mark_current_file(self):
    if self.current_file and not self.current_file in self.marked_files:
      self.marked_files.append(self.current_file)
      self.marked_files_area.insert(tk.END, extract_filename(self.current_file) )

  def __unmark_current_file(self):
    if self.current_file in self.marked_files:
      self.marked_files_area.delete(self.marked_files.index(self.current_file))
      self.marked_files.remove(self.current_file)

  #markers insert
  def __add_target_marker(self):
    self.note_area.insert(tk.INSERT, MARKER_TARGET_BASIC)

  def __add_link_marker(self):
    self.note_area.insert(tk.INSERT, MARKER_LINK_BASIC)

  #appflow
  def __switch_mode(self):
    if self.write_mode:
      #change to readonly
      self.__save_file()
      self.write_mode = False
      self.write_panel_area.grid_remove()

      self.markers = compile_all_notes(self.working_directory)
      (text, to_mark, self.current_file_pointers, _) = format_file(self.current_file_content, self.markers)
      self.__fill_note_area(text, to_mark)
      
    else:
      #change to editable
      self.write_mode = True
      self.write_panel_area.grid(row = 1, column = 1, sticky = tk.NSEW)
      self.__fill_note_area(self.current_file_content)

  def __open_marked_file(self, event):
    w = event.widget
    if len(w.curselection()) == 1:
      self.__read_file( self.marked_files[int(w.curselection()[0])] )

  def __read_file(self, file, target_ID = None):
    self.current_file = file
    for tag in self.note_area.tag_names():
      self.note_area.tag_delete(tag)

    with open(file, "r", encoding="UTF-8") as file:
      self.current_file_content = file.read()
      if self.write_mode:
        text = self.current_file_content
        to_mark = None
        target = None
      else:
        (text, to_mark, self.current_file_pointers, target) = format_file(self.current_file_content, self.markers, target_ID)
      self.__fill_note_area(text, to_mark, target)
      
  def __mark_text_parts(self, to_mark):
    counter = 0
    for start, end, mode, file, id in to_mark:
      tag = "link_"+str(counter)
      self.note_area.tag_add(tag, start, end)
      self.note_area.tag_configure(tag, foreground="blue")
      self.note_area.tag_bind(tag, "<ButtonRelease-1>", 
        lambda e, i=id, f=file: self.__follow_link(e, i, f)
      )
      
      counter += 1

  def __open_TM_window(self):
    pass

  def __follow_link(self, event, target_ID, target_file):
    if target_file == self.current_file:
      self.note_area.mark_set(tk.INSERT, self.current_file_pointers[target_ID])
      self.note_area.see(tk.INSERT)
    else:
      self.__read_file(target_file, target_ID)

  def __fill_note_area(self, text, to_mark=None, target=None):
    self.note_area.config(state= tk.NORMAL)
    self.note_area.delete(1.0, tk.END)
    self.note_area.insert(1.0, text)
    if target:
      self.note_area.mark_set(tk.INSERT, target)
      self.note_area.see(tk.INSERT)
    if to_mark:
      self.__mark_text_parts(to_mark)
    
    if not self.write_mode:
      self.note_area.config(state= tk.DISABLED)

  #Note_window END

if __name__ == "__main__":
  Note_window().mainloop()
  