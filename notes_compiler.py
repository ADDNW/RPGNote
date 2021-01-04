import os

def compile_all_notes(directory):
  return {}

def format_file(text, markers):
  return (text, [])

def extract_filename(path):
  splitted = path.split('/')
  file = os.path.splitext(splitted[len(splitted) - 1])[0]
  return file