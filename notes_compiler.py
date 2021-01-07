import os, glob
import re

MARK_LINK = 0

MARKER_TARGET_BASIC = "(@){}"
MARKER_LINK_BASIC = "(&){}"
MARKER_TARGET_PATTERN = "\(@\w+\){"
MARKER_LINK_PATTERN = "\(&\w+\){"
MARKER_ENDING = ".*?}"

def compile_all_notes(directory):
  markers = {}
  paths = [f.replace("\\", "/") for f in glob.glob(directory+"/**", recursive=True) if f.endswith(".txt") or f.endswith(".rpg")]
  for path in paths:
    with open(path, "r", encoding="UTF-8") as file:
      data = file.read()
      mark_points = [(m.group(0), m.start()) for m in re.finditer(MARKER_TARGET_PATTERN + MARKER_ENDING, data)]
      for (mark, point) in mark_points:
        id_group = re.match(MARKER_TARGET_PATTERN, mark).group(0)
        id = id_group[2:-2]
        content = mark[len(id_group):-1]
        markers[id] = (path, content)

  return markers

def format_file(text, markers, target_ID = None):
  to_mark = []
  pointers = {}
  target_pointer = None
  
  links = [(m.group(0), m.start(), False) for m in re.finditer(MARKER_LINK_PATTERN + MARKER_ENDING, text)]
  targets = [(m.group(0), m.start(), True) for m in re.finditer(MARKER_TARGET_PATTERN + MARKER_ENDING, text)]
  
  marks = (links + targets)
  marks.sort(key=lambda a:a[1])

  div = 0
  for mark, start, is_target in marks:
    if is_target:
      id_group = re.match(MARKER_TARGET_PATTERN, mark).group(0)
      id = id_group[2:-2]
      if id == target_ID:
        target_pointer = start - div
      content = mark[len(id_group):-1]
      text = text.replace(mark, content)
      pointers[id] = start - div
      div += len(mark) - len(content)
    else:
      id_group = re.match(MARKER_LINK_PATTERN, mark).group(0)
      id = id_group[2:-2]
      if id in markers:
        content = mark[len(id_group):-1]
        to_mark.append(
          (start - div, start - div + len(content), MARK_LINK, markers[id][0], id)
        )
        text = text.replace(mark, content)
        div += len(mark) - len(content)
      
  (to_mark, pointers, target_pointer) = convert_indexes_of_markers(text, to_mark, pointers, target_pointer)
  return (text, to_mark, pointers, target_pointer)

def extract_filename(path):
  splitted = path.split('/')
  file = os.path.splitext(splitted[len(splitted) - 1])[0]
  return file

def convert_indexes_of_markers(text, to_mark, targets_pointer, target=None):
  pointers_list = [x for f in to_mark for x in (f[0], f[1])]
  if target != None:
    pointers_list.append(target)
  to_remove = len(pointers_list) + len(targets_pointer.keys())

  count = 0
  for line in text.split('\n'):
    count += 1
    for i, pointers in enumerate(pointers_list, start=0):
      if type(pointers) == int:
        if pointers <= len(line):
          pointers_list[i] = str(count) + "." + str(pointers)
          to_remove -= 1
        else:
          pointers_list[i] -= len(line) + 1
       
    for k, value in targets_pointer.items():
      if type(value) == int:
        if value <= len(line):
          targets_pointer[k] = str(count) + "." + str(value)
          to_remove -= 1
        else:
          targets_pointer[k] -= len(line) + 1


    if to_remove == 0:
      break
    
  new_to_mark = []
  for i in range(len(to_mark)):
    new_to_mark.append((
      pointers_list[i*2], 
      pointers_list[i*2+1], 
      to_mark[i][2],
      to_mark[i][3],
      to_mark[i][4]
    ))
  if target != None:
    target = pointers_list[-1]

  return (new_to_mark, targets_pointer, target)
