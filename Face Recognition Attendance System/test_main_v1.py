import cv2
import numpy as np
import pandas as pd
import face_recognition
import os
from datetime import datetime
import datetime as dt
import cvzone
from csv import DictWriter


from datetime import timedelta

# from PIL import ImageGrab

path = 'Training_images'
images = []
classNames = []
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)


def findEncodings(images):
    encodeList = []

    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


def markAttendance(name):

    with open('datasets/Attendance_test.csv', 'r+') as f:
        myDataList = f.readlines()

        nameList = []

        for line in myDataList:
            entry = line.split(',')
            nameList.append(entry[0])

            now = datetime.now()

            if name not in nameList:
                In_Time = now.strftime('%H:%M:%S')
                Date = now.date()  # convert to date from datetime
                
                # time_change = dt.timedelta(minutes=2)  # to add time
                # new_time = now + time_change  # added time in new var

                f.writelines(f'\n{name}, {Date}, {In_Time}')

    df = pd.read_csv('datasets/Attendance_test.csv', index_col = False)

    # Grouping our dataset so that we can get min and max time
    df_dd = df.groupby(['Name', 'Date'], as_index=False)

    min_att = df_dd.min()   # min time
    max_att = df_dd.max()   # max time

    new_df = pd.merge(min_att, max_att, how='inner', left_on=['Name', 'Date'], right_on=['Name', 'Date'])
    new_df.rename(columns={"In_Time_x":"In_Time" , "In_Time_y": "Out_Time"}, inplace=True)
    print(new_df)
    new_df.to_csv('datasets/Attendance.csv', index = False)


## FOR CAPTURING SCREEN RATHER THAN WEBCAM
# def captureScreen(bbox=(300,300,690+300,530+300)):
#     capScr = np.array(ImageGrab.grab(bbox))
#     capScr = cv2.cvtColor(capScr, cv2.COLOR_RGB2BGR)
#     return capScr


encodeListKnown = findEncodings(images)
print('Encoding Complete')

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    # img = captureScreen()
    imgS = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        # print(faceDis)
        matchIndex = np.argmin(faceDis)

        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            # print(name)
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2 - 25), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1 + 8, y2 - 7), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 2)
            markAttendance(name)

    cv2.imshow('Webcam', img)

# if we press "a" key from keyboard camera will close
    if cv2.waitKey(10) == ord("a"):
        break

cap.release()

