from adafruit_servokit import ServoKit
import cv2
import jetson.inference
import jetson.utils
import time
import numpy as np
import threading

item = ""
top = 0
bottom = 0
left = 0
right = 0


def object_detection():

    global item
    global top
    global bottom
    global left
    global right
    timeStamp=time.time()
    fpsFiltered=0

    net=jetson.inference.detectNet(argv=["--model=/home/jetbot/Downloads/jetson-inference/python/training/detection/ssd/models/myModel/ssd-mobilenet.onnx", "--labels=/home/jetbot/Downloads/jetson-inference/python/training/detection/ssd/models/myModel/labels.txt", "--input-blob=input_0", "--output-cvg=scores", "--output-bbox=boxes"], threshold=0.5)
    dispW=1280
    dispH=720
    flip=2

    font=cv2.FONT_HERSHEY_SIMPLEX
    #cam=jetson.utils.gstCamera(dispW,dispH,'/dev/video0')
    #display=jetson.utils.glDisplay()

    cam=cv2.VideoCapture('/dev/video0')
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, dispW)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, dispH)
    #while display.IsOpen():
        #img,width,height=cam.CaptureRGBA()
    while True:
        _,img = cam.read()
        height=img.shape[0]
        width=img.shape[1]

        frame=cv2.cvtColor(img,cv2.COLOR_BGR2RGBA).astype(np.float32)
        frame=jetson.utils.cudaFromNumpy(frame)

        detections=net.Detect(frame,width,height)
        for detect in detections:
            #print(detect)
            ID=detect.ClassID
            top=int(detect.Top)
            left=int(detect.Left)
            bottom=int(detect.Bottom)
            right=int(detect.Right)
            item=net.GetClassDesc(ID)
            print(item,top,left,bottom,right)
            #time.sleep(1)
            cv2.rectangle(img,(left,top),(right,bottom),(255,0,0),2)
            cv2.putText(img,item,(left,top+20),font,.75,(0,0,255),2)
        #display.RenderOnce(frame,width,height)
        dt=time.time()-timeStamp
        timeStamp=time.time()
        fps=1/dt
        fpsFiltered=0.9*fpsFiltered+.1*fps
        print(str(round(fps,1))+' fps')

        cv2.putText(img,str(round(fpsFiltered,1))+' fps',(0,30),font,1,(0,0,255),2)
        cv2.imshow('detCam',img)
        cv2.moveWindow('detCam',0,0)
        if cv2.waitKey(1)==ord('q'):
            break
    cam.release()
    cv2.destroyAllWindows()

def servo_run():
    myKit=ServoKit(channels=16)

    for i in range(0,50,1):
        myKit.servo[1].angle=i
        print("clockwise 1")
        print(i)
        time.sleep(0.05)
            
    for i in range(90,70,-1):
        myKit.servo[2].angle=i
        print("clockwise 2")
        print(i)
        time.sleep(0.05)

def servo_pick():
    myKit=ServoKit(channels=16)

    for i in range(0,30,1):
        myKit.servo[0].angle=i
        print("clockwise 0")
        print(i)
        time.sleep(0.05)

    for i in range(50,70,1):
        myKit.servo[1].angle=i
        print("clockwise 1")
        print(i)
        time.sleep(0.05)

    for i in range(70,30,-1):   
        myKit.servo[2].angle=i
        print("clockwise 2")
        print(i)
        time.sleep(0.05)


    for i in range(30,0,-1):
        myKit.servo[0].angle=i
        print("anticlockwise 0")
        print(i)
        time.sleep(0.05)

    for i in range(30,70,1):  
        myKit.servo[2].angle=i
        print("clockwise 2")
        print(i)
        time.sleep(0.05)

    for i in range(70,50,-1):
        myKit.servo[1].angle=i
        print("clockwise 1")
        print(i)
        time.sleep(0.05)

def servo_place():
    myKit=ServoKit(channels=16)

    for i in range(50,70,1):
        myKit.servo[1].angle=i
        print("clockwise 1")
        print(i)
        time.sleep(0.05)

    for i in range(70,68,-1):   
        myKit.servo[2].angle=i
        print("clockwise 2")
        print(i)
        time.sleep(0.05)

    for i in range(0,30,1):
        myKit.servo[0].angle=i
        print("clockwise 0")
        print(i)
        time.sleep(0.05)


    for i in range(30,0,-1):
        myKit.servo[0].angle=i
        print("anticlockwise 0")
        print(i)
        time.sleep(0.05)

    for i in range(68,70,1):  
        myKit.servo[2].angle=i
        print("clockwise 2")
        print(i)
        time.sleep(0.05)

    for i in range(70,50,-1):
        myKit.servo[1].angle=i
        print("clockwise 1")
        print(i)
        time.sleep(0.05)
     


if __name__=="__main__":
    time.sleep(1)
    picked = 0
    thread1 = threading.Thread(target=object_detection)
    #thread2 = threading.Thread(target=servo_run)
    thread1.start()
    #thread2.start()
    servo_run()
    while True:
        if (item == "Redbox" and picked == 0):
            servo_pick()
            item = ""
            picked = 1
        elif (item == "Basket" and picked == 1):
            servo_place()
            item = ""
            picked = 0

    thread1.join()