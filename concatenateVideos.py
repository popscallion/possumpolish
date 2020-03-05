import numpy as np
import cv2
        
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
