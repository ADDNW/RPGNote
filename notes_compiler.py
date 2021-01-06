import os, glob
import re

MARK_LINK = 0

MARKER_TARGET_PATTERN = "\(@\d+\){"
MARKER_LINK_PATTERN = "\(&\d+\){"
MARKER_ENDING = ".*}"

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
  div = 0

  targets = [(m.group(0), m.start()) for m in re.finditer(MARKER_TARGET_PATTERN + MARKER_ENDING, text)]
  for target, start in targets:
    id_group = re.match(MARKER_TARGET_PATTERN, target).group(0)
    id = id_group[2:-2]
    if id == target_ID:
      target_pointer = start - div
    content = target[len(id_group):-1]
    text = text.replace(target, content)
    pointers[id] = start - div
    div += len(target) - len(content)

  div = 0
  links = [(m.group(0), m.start()) for m in re.finditer(MARKER_LINK_PATTERN + MARKER_ENDING, text)]
  for link, start in links:
    id_group = re.match(MARKER_LINK_PATTERN, link).group(0)
    id = id_group[2:-2]
    if id in markers:
      content = link[len(id_group):-1]
      to_mark.append(
        (start - div, start - div + len(content), MARK_LINK, markers[id][0], id)
      )
      text = text.replace(link, content)
      div += len(link) - len(content)

  if target_pointer:
    target_pointer -= div

  (to_mark, target_pointer) = convert_indexes_of_markers(to_mark, text, target_pointer)
  return (text, to_mark, pointers, target_pointer)

def extract_filename(path):
  splitted = path.split('/')
  file = os.path.splitext(splitted[len(splitted) - 1])[0]
  return file

def convert_indexes_of_markers(to_mark, text, target_pointer=None):
  pointers_list = [x for f in to_mark for x in (f[0], f[1])]
  if target_pointer != None:
    pointers_list.append(target_pointer)
  pointers_translated = [-1 for x in pointers_list]
  to_remove = len(pointers_list)

  count = 0
  for line in text.split('\n'):
    count += 1
    for i, pointers in enumerate(pointers_list, start=0):
      if pointers < 0:
        pass
      elif pointers <= len(line):
        pointers_translated[i] = str(count) + "." + str(pointers)
        pointers_list[i] = -1
        to_remove -= 1
      else:
        pointers_list[i] -= len(line) + 1
      
    if to_remove == 0:
      break
    
  new_to_mark = []
  for i in range(len(to_mark)):
    new_to_mark.append((
      pointers_translated[i*2], 
      pointers_translated[i*2+1], 
      to_mark[i][2],
      to_mark[i][3],
      to_mark[i][4]
    ))
  if target_pointer != None:
    target_pointer = pointers_translated[-1]

  return (new_to_mark, target_pointer)