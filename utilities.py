import numpy as np
import cv2
import os
import imutils
import math
import re
import blend_modes
        
def scanDir(directory, extension='avi', filter_string=None, filter_out=False, verbose=False):
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
        if filter_out:
            file_list = [file for file in file_list if not re.search(filter_string, file)]
        else:
            file_list = [file for file in file_list if re.search(filter_string, file)]
    return(file_list)
        
def tandemPreviews(video_dict):
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    capA = cv2.VideoCapture(os.path.join(video_dict['path'],video_dict['c1'][0]))
    capB = cv2.VideoCapture(os.path.join(video_dict['path'],video_dict['c2'][0]))
    frame_index = 0
    frame_width = int(capA.get(3))
    frame_height = int(capA.get(4))
    frame_rate = round(capA.get(5),2)
    input_name =os.path.splitext(video_dict['c1'][0])
    output_name = os.path.join(video_dict['path'],(input_name[0][:-1]+'_tandem'+'.mp4'))
    
    frameA_yStart = math.floor(frame_height*.1)
    frameA_yEnd = math.floor(frame_height*.8)
    frameB_yStart = math.floor(frame_height*.3)
    frameB_yEnd = math.floor(frame_height)
    
    output_dims = [frame_width, frameA_yEnd-frameA_yStart+frameB_yEnd-frameB_yStart]
    out = cv2.VideoWriter(output_name,
                         fourcc,
                         frame_rate,(output_dims[0], output_dims[1]))
    while(capA.isOpened()):
        retA, frameA = capA.read()
        retB, frameB = capB.read()
        frame_index += 1
        if retA == True:
            frameArotate = imutils.rotate(frameA, 128)
            frameAcrop = frameArotate[frameA_yStart:frameA_yEnd,:]
            frameBcrop = frameB[frameB_yStart:frameB_yEnd,:]
            concatenated = cv2.vconcat([frameAcrop, frameBcrop])
            preview = cv2.resize(concatenated, (output_dims[0], output_dims[1]))
            labeled = cv2.putText(preview, video_dict['path'], (20,20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
            labeled = cv2.putText(preview, 'FRAME '+str(frame_index), (20,40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
            labeled = cv2.putText(preview, 'DIMS '+str(preview.shape), (20,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255))
            cv2.cvtColor(labeled, cv2.COLOR_BGR2GRAY)  
            cv2.imshow('test',labeled)
            out.write(labeled)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                frame_index = 0
                break
        else:
            frame_index = 0
            break
    capA.release()
    capB.release()
    out.release()
    cv2.destroyAllWindows()


        
def mergeRGB(video_dict, codec, mode):
    capA = cv2.VideoCapture(video_dict['A'])
    capB = cv2.VideoCapture(video_dict['B'])
    frame_width = int(capA.get(3))
    frame_height = int(capA.get(4))
    frame_rate = round(capA.get(5),2)
    input_name =os.path.splitext(os.path.basename(video_dict['A']))
    output_name = mode+"_RGBMerge_"+input_name[0][:-4]+input_name[1]
    out = cv2.VideoWriter(output_name,
                         codec,
                         frame_rate,(frame_width, frame_height))
    while(capA.isOpened()):
        retA, frameA = capA.read()
        retB, frameB = capB.read()
        if retA == True:
            ## give frames an alpha channel to prepare for blending; blend_modes requires 32bit
            frameA = cv2.cvtColor(frameA, cv2.COLOR_BGR2BGRA,4).astype(np.float32)
            frameB = cv2.cvtColor(frameB, cv2.COLOR_BGR2BGRA,4).astype(np.float32)
            if mode == "difference":
                extraChannel = blend_modes.difference(frameA,frameB,1)
            elif mode == "multiply":
                extraChannel = blend_modes.multiply(frameA,frameB,1)
            else:
                extraChannel = np.zeros((frame_width, frame_height,3),np.uint8)
                extraChannel = cv2.cvtColor(extraChannel, cv2.COLOR_BGR2BGRA,4).astype(np.float32)

            ## get rid of alpha channel in preparation for converting back to grayscale; opencv prefers 8bit
            frameA = cv2.cvtColor(frameA, cv2.COLOR_BGRA2BGR).astype(np.uint8)  
            frameB = cv2.cvtColor(frameB, cv2.COLOR_BGRA2BGR).astype(np.uint8)  
            extraChannel = cv2.cvtColor(extraChannel, cv2.COLOR_BGRA2BGR).astype(np.uint8)  

            ## convert to grayscale so we can merge into 3-channel image
            frameA = cv2.cvtColor(frameA, cv2.COLOR_BGR2GRAY)  
            frameB = cv2.cvtColor(frameB, cv2.COLOR_BGR2GRAY)  
            extraChannel = cv2.cvtColor(extraChannel, cv2.COLOR_BGR2GRAY)  

            ## merge, show and write                  
            merged = cv2.merge((extraChannel, frameB, frameA))
            cv2.imshow('merged',merged)
            out.write(merged)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break
    capA.release()
    capB.release()
    out.release()
    cv2.destroyAllWindows()
    print("done!")

    
def concatenateVideos(video_files, codec, interval=1):
    frame_index = 0
    video_index = 0
    cap = cv2.VideoCapture(video_files[0])
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    frame_rate = round(cap.get(5),2)
    output_name = "concatenated_1in"+str(interval)+".avi"
    out = cv2.VideoWriter(output_name, 
                          cv2.VideoWriter_fourcc(*codec), 
                          frame_rate,(frame_width, frame_height))
    while(cap.isOpened()):
        ret, frame = cap.read()
        frame_index += 1
        if frame is None:
            print("end of video " + str(video_index) + " ... next one now")
            video_index += 1
            if video_index >= len(video_files):
                break
            cap = cv2.VideoCapture(video_files[ video_index ])
            ret, frame = cap.read()
            frame_index = 0
        elif frame_index == interval:
            frame = frame.astype(np.uint8)
            cv2.imshow('frame',frame)
            out.write(frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            frame_index = 0         
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("done!")