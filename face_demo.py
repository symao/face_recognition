import face_recognition
import cv2
import os

def demo_detection(img_file = 'data/got0.jpg'):
    # load image
    img = cv2.imread(img_file)
    # detect face
    face_locations = face_recognition.face_locations(img)
    # draw
    for top,right,bottom,left in face_locations:
        cv2.rectangle(img, (left,top), (right,bottom), (55,255,155), 2)
    cv2.imshow('detection result',img)
    cv2.waitKey()

def demo_keypoint(img_file = 'data/got0.jpg'):
    # load image
    img = cv2.imread(img_file)
    # detect keypoints
    face_landmarks_list = face_recognition.face_landmarks(img)
    # draw
    color_dict = {'nose_tip':(0,255,125),
                  'right_eye':(100,110,120),
                  'left_eye':(100,110,120),
                  'bottom_lip':(0,0,250),
                  'top_lip':(0,0,250),
                  'right_eyebrow':(100,100,10),
                  'left_eyebrow':(100,100,10),
                  'nose_bridge':(0,120,0),
                  'chin':(250,0,0)}
    for landmark in face_landmarks_list:
        for part_name, pts in landmark.items():
            for pt in pts:
                cv2.circle(img, pt, 2, color_dict[part_name], -1)
    cv2.imshow('keypoints result',img)
    cv2.waitKey()

def demo_recognition(img_file = 'data/got0.jpg', dataset=['data/JohnSnow.jpg','data/DaenerysTargaryen.jpg', 'data/symao.jpg']):
    # load face image in dataset and encode
    face_list = [face_recognition.face_encodings(cv2.imread(x))[0] for x in dataset]
    name_list = [os.path.splitext(os.path.basename(x))[0] for x in dataset]
    # load test image
    img = cv2.imread(img_file)
    # detect faces in test image
    face_locations = face_recognition.face_locations(img)
    # encode faces
    face_encodings = face_recognition.face_encodings(img, face_locations)
    # for each face, compare to face dataset to find similar face(recognition)
    face_names = []
    for en in face_encodings:
        match = face_recognition.compare_faces(face_list, en)
        name = 'Unknown' if True not in match else name_list[match.index(True)]
        face_names.append(name)
    # draw
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        cv2.rectangle(img, (left, top), (right, bottom), (55,255,155), 2)
        cv2.putText(img, name, (left, top - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 0, 255), 1)
    cv2.imshow('recognition result', img)
    cv2.waitKey()

def demo_recognition_live(dataset=['data/JohnSnow.jpg','data/DaenerysTargaryen.jpg','data/symao.jpg']):
    # load face image in dataset and encode
    face_list = [face_recognition.face_encodings(cv2.imread(x))[0] for x in dataset]
    name_list = [os.path.splitext(os.path.basename(x))[0] for x in dataset]
    cap = cv2.VideoCapture(0)

    if cap.isOpened():
        ret,img = cap.read()
        while ret:
            small_img = cv2.resize(img, None, fx=0.5,fy=0.5)
            face_locations = face_recognition.face_locations(small_img, model="cnn")
            face_encodings = face_recognition.face_encodings(small_img, face_locations)
            face_names = []
            for en in face_encodings:
                    match = face_recognition.compare_faces(face_list, en)
                    name = 'Unknown' if True not in match else name_list[match.index(True)]
                    face_names.append(name)
            for (top, right, bottom, left), name in zip(face_locations, face_names):
                cv2.rectangle(img, (left*2, top*2), (right*2, bottom*2), (55,255,155), 2)
                cv2.putText(img, name, (left*2, top*2 - 6), cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 0, 255), 1)
            cv2.imshow('recognition result', img)
            key = cv2.waitKey(10)
            if key == 27:
                break
            ret,img = cap.read()

if __name__ == '__main__':
    demo_detection()
    demo_keypoint()
    demo_recognition()
    # demo_recognition_live()

    # for f in ['data/got0.jpg','data/got2.jpg','data/got1.jpg']:
    #     demo_recognition(f)

    # for i in os.listdir('data'):
    #     demo_detection(os.path.join('data',i))
    
    
