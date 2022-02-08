import cv2
import face_recognition as fr
import numpy as np
import os
from datetime import datetime, date
import sqlite3

path = "training"
todayDate = date.today()
todayDate = str(todayDate)

knownEncodings = []
empid = []
names = []
conn = sqlite3.connect('attendance.db')
c = conn.cursor()

def find_encoding(im):
    imColor = cv2.cvtColor(im, cv2.COLOR_BGR2RGB)
    face_encodings = fr.face_encodings(imColor)[0]
    knownEncodings.append(face_encodings)


m = c.execute("SELECT * FROM users")
for i in m:
    with open("image.jpg", "wb") as f:
        f.write(i[5])
    img = cv2.imread('image.jpg')

    if os.path.exists('image.jpg'):
        os.remove('image.jpg')

    find_encoding(img)
    names.append(i[0])
    empid.append(i[1])

c.execute(f"CREATE TABLE IF NOT EXISTS '{todayDate}' (name TEXT, empId TEXT REFERENCES users(empId) PRIMARY KEY, attend TEXT, time TEXT)")
conn.commit()

for i, j in zip(names, empid):
    try:
        c.execute(f"INSERT INTO '{todayDate}' (name, empId) values(?, ?)", (i, j))
        conn.commit()
    except sqlite3.IntegrityError:
        continue


alreadyPresent = []


def markattendance(empid):
    if empid not in alreadyPresent:
        alreadyPresent.append(empid)
        now = datetime.now()
        dtString = now.strftime('%H:%M:%S')

        c.execute(f"UPDATE '{todayDate}' SET time='{dtString}'  WHERE empId = '{empid}' AND time IS NULL")
        c.execute(f"UPDATE '{todayDate}' SET attend='YES'  WHERE empId = '{empid}' AND time IS NOT NULL ")
        conn.commit()



print("Encoding Complete : " + str(len(knownEncodings)))

feed = cv2.VideoCapture(0)
while True:
    success, img = feed.read()

    imgSmall = cv2.resize(img, (0, 0), None, 0.25, 0.25)
    imgSmall = cv2.cvtColor(imgSmall, cv2.COLOR_BGR2RGB)

    frameFaceLocation = fr.face_locations(imgSmall)
    frameFaceEncoding = fr.face_encodings(imgSmall, frameFaceLocation)

    for encode, location in zip(frameFaceEncoding, frameFaceLocation):
        match = fr.compare_faces(knownEncodings, encode)
        distance = fr.face_distance(knownEncodings, encode)

        # print(distance)
        matchIndex = np.argmin(distance)

        if match[matchIndex]:
            name = names[matchIndex].upper()
            emp = empid[matchIndex]
            # print(name)

            y1 = location[0]*4
            x1 = location[3]*4
            x2 = location[1]*4
            y2 = location[2]*4

            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.rectangle(img, (x1, y2-35), (x2, y2), (0, 255, 0), cv2.FILLED)
            cv2.putText(img, name, (x1+6, y2-6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 2)
            markattendance(emp)

    cv2.imshow('webcam', img)
    key = cv2.waitKey(1)
    if key == ord('q'):
        feed.release()
        cv2.destroyWindow('webcam')
        conn.commit()
        c.close()
        conn.close()
