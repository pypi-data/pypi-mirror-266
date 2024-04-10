import webbrowser
import os, argparse, re

class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   GRAY_DARK = '\033[38;5;232m'
   GRAY_MEDIUM = '\033[38;5;244m'
   GRAY_LIGHT = '\033[38;5;250m'
   GRAY_VERY_LIGHT = '\033[38;5;254m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'

def say(who, message,
        who_color = color.PURPLE,
        message_color = color.CYAN):
   print("\n" + color.BLUE + "> " + color.BOLD + who_color + color.UNDERLINE + who + color.END + ": ", end="")
   print(message_color + message)

def read_file(path):
    with open(path, 'r') as file:
        data = file.read()
    return data

def open_local_browser(dir_path):
   current_dir = os.getcwd()
   try:
      # Get the absolute path of the file
      abs_path = os.path.abspath(dir_path)

      # Check if the file exists
      if os.path.exists(abs_path):
         # Open the file in the default web browser
          webbrowser.open(f"file://{abs_path}/index.html")
          print(f"opened {dir_path} in the web browser")
      else:
         print(f"can't find a file system path to open in the browser: {file_path}")
   finally:
      os.chdir(current_dir)

def parse_cli_arguments():

    parser = argparse.ArgumentParser(description='thoughts in, software out')

    parser.add_argument('--requirements', type=str, help='path to the requirements file')
    parser.add_argument('--prompt', type=str, help='short idea to convert to creation')


    parser.add_argument('--user-stories', action='store_true', help='create and refine user stories')
    parser.add_argument('--build-user-stories', action='store_true', help='build prototype on combined (non refined) user stories')

    parser.add_argument('--build-prototype', action='store_true', help='build prototype')
    parser.add_argument('--test-prototype', action='store_true', help='test prototype')

    parser.add_argument('--claude', nargs='?', const=True, default=None,
                        help='choose a claude model (optional, can be provided without a value)')
    parser.add_argument('--openai', nargs='?', const=True, default=None,
                        help='choose an open ai model (optional, can be provided without a value)')
    parser.add_argument('--ollama', nargs='?', const=True, default=None,
                        help='choose an ollama model (optional, can be provided without a value)')
    parser.add_argument('--replicate', nargs='?', const=True, default=None,
                        help='choose a model from Replicate (optional, can be provided without a value)')

    args = parser.parse_args()

    return args
