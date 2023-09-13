#!/usr/bin/env python3
import os
import token
import tokenize
import itertools
import sys
import glob
from tabulate import tabulate

TOKEN_WHITELIST = [token.OP, token.NAME, token.NUMBER, token.STRING]

if __name__ == "__main__":  
    if len(sys.argv) < 2:
        print("Usage: sz.py <directory_path>")
        sys.exit(1)

    # create the header names for the output
    headers = ["Name", "Directory","Lines", "Tokens/Line"]
    # create a blank table to store the data into
    table = []
    #create a simple variable containing the path to the folder to be monitored. In turn, if a different folder path is needed, you can modify this variable in one place instead of having todo so in multiple places. 
    project_folder_path = os.path.expanduser(sys.argv[1])
    
    # create dictionary of file types to be checked. If a file type in a directory is not in this list, the file type will be ignored. 
    valid_file_types = {'.py': True, '.ipynb': True,'.txt': True, '.c': True, '.cpp': True, '.java': True, '.js': True, '.git': True}

    for path, subdirs, files in os.walk(project_folder_path):
        for name in files:
            
            # checking if files in directory match name, if so, skips as these are hidden System Files and should not be reported on. 
            #Additionally, checks all file in directories and sub directorys to see which file types match file types in dictionary
            if name == '.DS_Store' or not any(name.endswith(ext) for ext in valid_file_types):
                continue
            filepath = os.path.join(path, name)
            dirName = os.path.dirname(filepath).rsplit('/', 1)[-1]
            try:
                with tokenize.open(filepath) as file_:
                    tokens = [t for t in tokenize.generate_tokens(file_.readline) if t.type in TOKEN_WHITELIST]
                    token_count, line_count = len(tokens), len(set([t.start[0] for t in tokens]))
                    if line_count == 0:
                        table.append([name, dirName, "File is blank"])
                        continue
                    else:
                        table.append([name, dirName, line_count,  token_count/line_count]) 

            except Exception as e:
                print(f"Could not read the file: {name} in directory: {dirName} : {e}")

    print(tabulate([headers] + sorted(table, key=lambda x: -x[1] if isinstance(x[1], int) else x[1]), headers="firstrow", floatfmt=".1f")+"\n")
  
    for dir_name, group in itertools.groupby(sorted(table, key=lambda x: x[1]), key=lambda x: x[1]):
        print(f"{dir_name:30s} : {sum([x[2] for x in group if isinstance(x[2], int)]):6d}")


    #print(f"\ntotal line count: {sum([x[1] for x in table])}")
    #print(f"{dir_name:30s} : {sum([x[1] for x in group if isinstance(x[1], int)]):6d}")
