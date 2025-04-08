import cv2
import numpy as np
from ultralytics import YOLO
from panel import create_text_panel
from letters import class_names

model = YOLO('best.pt')
cap = cv2.VideoCapture(0)

prev_letter_class_id = -1
counter = 0
accumulated_text = ""
SPACE_CLASS = class_names.index('ض')
DELETE_CLASS = class_names.index('خ')
message = ["everything is good"]


while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 640))
    results = model(frame, conf=0.85)
    
    result = results[0]

    detections = []
    for box in result.boxes:
        if box.conf >= 0.85:
                cls_id = int(box.cls.item())
                print(cls_id)
                detections.append(cls_id)
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            
    
    if len(detections) > 2: 
        message = ["Maximum hands in one frame is 2"]
    else:  
        if len(detections) == 2 and detections[0]==detections[1]:
            if detections[0]== SPACE_CLASS and prev_letter_class_id == 50: 
                counter = counter + 1
            elif detections[0]==DELETE_CLASS and prev_letter_class_id == 51:
                counter = counter + 1
            else:
                if detections[0]== SPACE_CLASS :
                    prev_letter_class_id = 50
                    counter = 1
                elif detections[0]==DELETE_CLASS:
                    prev_letter_class_id = 51
                    counter = 1
                else:
                    counter = 0
                    prev_letter_class_id = -1                 
        elif len(detections)==1:
            if detections[0] == prev_letter_class_id:
                counter = counter + 1
            else:
                counter = 1
                prev_letter_class_id = detections[0]
        else:
            counter = 0
            prev_letter_class_id = -1          
    
    if counter>=5:
        for box in result.boxes:
            if box.conf >= 0.85:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 0), -1)  
        if prev_letter_class_id==50:
            accumulated_text = accumulated_text + " "
            counter = 0
        elif prev_letter_class_id==51:
            accumulated_text = ""
            counter = 0
        else:
            accumulated_text = accumulated_text + class_names[prev_letter_class_id]
            counter = 0
           
                                                        

    text_panel = create_text_panel(accumulated_text , messages=message)
    print(accumulated_text)
    message = ["evrything is good"]
    combined = np.hstack((frame, text_panel))
    cv2.imshow('Sign Language Detection', combined)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()