import os
import re
        
def scanDir(directory, extension='avi', verbose=False):
    vid_list=[]
    for root, dirs, files in os.walk(directory):
        for name in files:
            if name.lower().endswith(extension):
                filename = os.path.join(root, name)
                if verbose == True:
                    print("Found file with extension ."+ extension + ": " + filename)
                vid_list.append(filename)
                continue
            else:
                continue
    return(vid_list)
