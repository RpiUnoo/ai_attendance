import cv2
import face_recognition
import os
import pickle
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL':"https://attendaceface-b73be-default-rtdb.firebaseio.com/",
    'storageBucket':"attendaceface-b73be.appspot.com"
})

# Importing images to a list
folderPath = 'Images'
ImagePath = os.listdir(folderPath)
img_list = []
student_ids = []
for path in ImagePath:
    img_list.append(cv2.imread(os.path.join(folderPath,path)))
    student_ids.append(os.path.splitext(path)[0])

    filename = f'{folderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)
#print(len(img_list))
print(student_ids)

def encodings(imagesList):
    encode_list = []
    for img in imagesList:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encode_list.append(encode)

    return encode_list

print("encoding started.....")
encode_list = encodings(img_list)
encode_list_ids = [encode_list,student_ids]
print("encoding completed")

file = open('encode_file.p','wb')
pickle.dump(encode_list_ids,file)
file.close()