import cv2
import os
import pickle
import face_recognition
import numpy as np
import cvzone
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage
from datetime import datetime

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://attendaceface-b73be-default-rtdb.firebaseio.com/",
    'storageBucket':"attendaceface-b73be.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3,640)
cap.set(4,480)

imgBackground = cv2.imread('Resources/background.png')


# Importing mode images to a list
folderModePath = 'Resources/Modes'
modeImagePath = os.listdir(folderModePath)
imgMode_list = []
for path in modeImagePath:
    imgMode_list.append(cv2.imread(os.path.join(folderModePath,path)))
#print(len(imgMode_list))


# Loading encodings
print("loading encode file....")
file = open('encode_file.p','rb')
encodelist_ids = pickle.load(file)
file.close()
encode_list,student_ids = encodelist_ids
#print(student_ids)
print('encode file loaded')


modeType =0
counter = 0

while True:
    success,img = cap.read()
    imgs = cv2.resize(img,(0,0),None,0.25,0.25)
    imgs = cv2.cvtColor(imgs,cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgs)
    encodedCurFrame = face_recognition.face_encodings(imgs,faceCurFrame)

    imgBackground[162:162+480,55:55+640] = img
    imgBackground[44:44+633,808:808+414] = imgMode_list[modeType]

    
    if faceCurFrame:
        for encodeFace,faceLoc in zip(encodedCurFrame,faceCurFrame):
            matches = face_recognition.compare_faces(encode_list,encodeFace)
            faceDis = face_recognition.face_distance(encode_list,encodeFace)
            #print(matches)
            #print(faceDis)

            idx = np.argmin(faceDis)
            if matches[idx]:
                #print("known face detected")
                y1,x2,y2,x1 = faceLoc
                y1,x2,y2,x1 =  y1*4,x2*4,y2*4,x1*4
                bbox = 55+x1,162+y1,x2-x1,y2-y1
                id = student_ids[idx]
                imgBackground = cvzone.cornerRect(imgBackground,bbox,rt=0) 

            if counter == 0:
                cvzone.putTextRect(imgBackground,'Loading...',(200,330))
                cv2.imshow('Attendance',imgBackground)
                cv2.waitKey(1)
                counter = 1
                modeType = 1
        
        if counter!=0:

            if counter==1:
                # fetching data
                studentInfo = db.reference(f'Students/{id}').get()
                #print(studentInfo)

                # fetching image
                blob = bucket.get_blob(f'Images/{id}.png')
                #print(blob)
                #print(f'Images/{id}.png')
                array = np.frombuffer(blob.download_as_string(),np.uint8)
                imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)

                # update attendace
                datetimeObject = datetime.strptime(studentInfo['last_attendance_time'],
                                                "%Y-%m-%d %H:%M:%S")
                
                secondsElapsed = (datetime.now()-datetimeObject).total_seconds()
                #print(secondsElapsed)
                
                if secondsElapsed>30:
                    ref = db.reference(f'Students/{id}')
                    studentInfo['total_attendance'] += 1
                    ref.child('total_attendance').set(studentInfo['total_attendance'])
                    ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                
                else:
                    counter = 0
                    modeType = 3
                    imgBackground[44:44+633,808:808+414] = imgMode_list[modeType]

            if modeType!=3:


                if 15<counter<25:
                    modeType=2
                imgBackground[44:44+633,808:808+414] = imgMode_list[modeType]

                if counter<=15:
                    cv2.putText(imgBackground,str(studentInfo['total_attendance']),(861,125),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                    cv2.putText(imgBackground,str(studentInfo['major']),(1006,550),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                    cv2.putText(imgBackground,str(id),(1006,493),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                    cv2.putText(imgBackground,str(studentInfo['standing']),(910,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                    cv2.putText(imgBackground,str(studentInfo['year']),(1025,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                    cv2.putText(imgBackground,str(studentInfo['starting_year']),(1125,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                    
                    (w,h),_ = cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                    offset = (414-w)//2
                    cv2.putText(imgBackground,str(studentInfo['name']),(808+offset,445),cv2.FONT_HERSHEY_COMPLEX,1,(50,50,50),1)    

                    imgBackground[175:175+216,909:909+216] = imgStudent

            
                counter+=1

                if counter>=25:
                    modeType = 0
                    counter = 0
                    studentInfo = []
                    imgStudent = []
                    imgBackground[44:44+633,808:808+414] = imgMode_list[modeType]

    else:
        modeType = 0
        counter = 0
    
    cv2.imshow('Attendance',imgBackground)
    cv2.waitKey(1)