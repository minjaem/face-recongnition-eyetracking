import face_recognition
import cv2
import numpy as np
import os.path
import copy
import pymysql.cursors

video_capture = cv2.VideoCapture(0)




path = "./known"
file_list = os.listdir(path)


name_lst= []
known_face_names = []
known_face_encodings = []


for i in file_list:
    name_lst.append(i.replace(".jpg",""))

for i in name_lst:
    known_face_names.append(i)

temp_lst = copy.deepcopy(name_lst)

for idx,i in enumerate(name_lst):
    name_lst[idx] = name_lst[idx] + '_face_encoding'
    known_face_encodings.append(name_lst[idx])



for i in range(len(temp_lst)):
    temp = "known/" + temp_lst[i] + '.jpg'
    temp_image = face_recognition.load_image_file(temp)
    temp_face_encoding = face_recognition.face_encodings(temp_image)[0]
    known_face_encodings[i] = temp_face_encoding


# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

while True:
    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)

            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            min_value = min(face_distances)
            name = "unknown"
            best_match_index = np.argmin(face_distances)
            if min_value < 0.4 and matches[best_match_index]:
                name = known_face_names[best_match_index]

            face_names.append(name)

            # if Counter <= 15:
            connection = pymysql.connect(user="root", password="dgu1234!", host="localhost", port=3309,
                                         charset="utf8mb4")

            try:
                with connection.cursor() as cursor:
                    sql = 'USE kiosk'
                    cursor.execute(sql)
                    if (Counter2 == 0):
                        sql = 'Drop TABLE customer'
                        cursor.execute(sql)
                        sql = 'CREATE TABLE customer (name varchar(10))'
                        cursor.execute(sql)
                        cursor.execute(sql)
                        sql = 'INSERT INTO customer values(%s)'
                        cursor.execute(sql, ('boyoung'))
                        cursor.execute(sql, ('minho'))
                        cursor.execute(sql, (name))

                    connection.commit()
                    result2 = cursor.fetchall()
                    print(result2)
            finally:
                connection.close()
                Counter2 = 1
                print(name, face_names, face_distances)

    process_this_frame = not process_this_frame


    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()