import cv2
import dlib
import face_recognition

# Initialize dlib's face detector and facial landmarks predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Load reference images and create face encodings
known_face_encodings = []
known_face_names = []

known_face_encodings.append(face_recognition.face_encodings(face_recognition.load_image_file("dad.jpg"))[0])
known_face_names.append("Dad")
known_face_encodings.append(face_recognition.face_encodings(face_recognition.load_image_file("ashley.jpg"))[0])
known_face_names.append("ashley")
known_face_encodings.append(face_recognition.face_encodings(face_recognition.load_image_file("Damian.jpg"))[0])
known_face_names.append("Damian")
known_face_encodings.append(face_recognition.face_encodings(face_recognition.load_image_file("Raven.jpg"))[0])
known_face_names.append("Raven")



cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

scale_factor = 0.5
frame_counter = 0

def landmarks_to_points(landmarks):
    points = []
    for feature_name in landmarks:
        points.extend(landmarks[feature_name])
    return points

def list_to_dlib_points(points):
    return [dlib.point(x, y) for (x, y) in points]

while cap.isOpened():
    frame_counter += 1
    ret, frame = cap.read()
    if not ret:
        break

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_frame = frame[:, :, ::-1]

    #flipping the frame
    flipped = cv2.flip(frame, 1)

    if frame_counter % 2 == 0:
        small_frame = cv2.resize(flipped, (0, 0), fx=scale_factor, fy=scale_factor)
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        rgb_small_frame = small_frame[:, :, ::-1]
        
        # face locations
        faces = detector(gray)
        face_locations = face_recognition.face_locations(rgb_frame)#[(face.top(), face.right(), face.bottom(), face.left()) for face in faces]
        
        #face landmarks
        face_landmarks = face_recognition.face_landmarks(rgb_frame, face_locations)
        face_landmarks_as_points = [landmarks_to_points(landmark) for landmark in face_landmarks]
        
        # Convert face_landmarks to dlib full_object_detections
        face_landmarks_as_dlib = [dlib.full_object_detection(dlib.rectangle(face_location[3], face_location[0], face_location[1], face_location[2]), list_to_dlib_points(face_landmark)) for face_location, face_landmark in zip(face_locations, face_landmarks_as_points)]

        # Face Encodings 
        face_encodings = face_recognition.face_encodings(rgb_frame, face_landmarks_as_dlib)

        for (i, face) in enumerate(faces):
            landmarks = predictor(gray, face)

            for n in range(0, 68):
                x = int(landmarks.part(n).x / scale_factor)
                y = int(landmarks.part(n).y / scale_factor)
                cv2.circle(flipped, (x, y), 2, (0, 255, 0), -1)

            # See if the face is a match for the known face(s)
            if i < len(face_encodings):
                matches = face_recognition.compare_faces(known_face_encodings, face_encodings[i])
                name = "Unknown"

                # Find the best match
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]

                # Draw a rectangle around the face and label the face
                top = int(face.top() / scale_factor)
                right = int(face.right() / scale_factor)
                bottom = int(face.bottom() / scale_factor)
                left = int(face.left() / scale_factor)
                cv2.rectangle(flipped, (left, top), (right, bottom), (0, 0, 255), 2)
                cv2.putText(flipped, name, (left + 6, bottom - 6), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 255, 255), 1)

    cv2.imshow('camera', flipped)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

