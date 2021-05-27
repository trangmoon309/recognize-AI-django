import detect
import face_reg_img2
import numpy as np

class Recog_Module:
    def __init__(self):
        self.cropped = r"test\\imgTest.jpg"

    def Recog_Process(self, img_path):
        mtcnn_detect = detect.MTCNN_Detect()
        recog = face_reg_img2.FaceRecog()

        cropped_face_list = mtcnn_detect.main(img_path)
        recog_faces = []
        for cropped_item in cropped_face_list:
            person_name = recog.main(cropped_item)
            if person_name != "":
                recog_faces.append(person_name)
        return recog_faces
            
#r = Recog_Module()
#r.Recog_Process( r"test\\jennie.jpg")
