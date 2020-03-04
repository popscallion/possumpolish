import os
import re
        
def scanDir(directory, extension='avi'):
    vid_list=[]
    for root, dirs, files in os.walk(directory):
        for name in files:
            if name.lower().endswith(extension):
                filename = os.path.join(root, name)
                print("Found file with extension ."+ extension + ": " + filename)
                vid_list.append(filename)
                continue
            else:
                continue
    return(vid_list)
