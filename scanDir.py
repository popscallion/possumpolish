import os
import re
        
def scanDir(directory, extension='avi', filter_string=None, verbose=False):
    file_list=[]
    for root, dirs, files in os.walk(directory):
        for name in files:
            if name.lower().endswith(extension):
                filename = os.path.join(root, name)
                if verbose == True:
                    print("Found file with extension ."+ extension + ": " + filename)
                file_list.append(filename)
                continue
            else:
                continue
    if filter_string != None:
        file_list = [file for file in file_list if not re.search(filter_string, file)]
    return(file_list)