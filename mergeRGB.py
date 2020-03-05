import numpy as np
import cv2
import os
import blend_modes
        
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
