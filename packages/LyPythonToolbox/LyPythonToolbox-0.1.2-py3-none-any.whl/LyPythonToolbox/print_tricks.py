import os

def print_separator(separator="="):
    size = os.get_terminal_size()
    width = size.columns
    print(separator * width)