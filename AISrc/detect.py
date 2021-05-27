from os import read
import numpy as np
import cv2
from mtcnn import MTCNN
import os
from PIL import Image

class MTCNN_Detect:
    def __init__(self):
        self.image_path = r"test\\imgTest.jpg"

    def main(self, image_path):
        detector = MTCNN()
        image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
        result = detector.detect_faces(image)  
        cap = cv2.imread(image_path)


        bounding_boxes_list = []

        for i in result:
            bounding_boxes_list.append(i["box"])
            
        bounding_boxes = np.asfarray(bounding_boxes_list)
        faces_found = bounding_boxes.shape[0]
        det = bounding_boxes[:, 0:4]
        bb = np.zeros((faces_found, 4), dtype=np.int32)

        cropped_list = []

        for i in range(faces_found):    
            bb[i][0] = det[i][0]
            bb[i][1] = det[i][1]
            bb[i][2] = det[i][2]
            bb[i][3] = det[i][3]

            x = bb[i][0]
            y = bb[i][1]
            w = bb[i][2]
            h = bb[i][3]
            cropped = cap[y:y+h, x:x+w]
            cropped_list.append(cropped)

        return cropped_list

    def crop_and_save(self, raw_path, name):
        images = []
        dem = 0
        current_path = str(os.path.abspath(os.getcwd())) # .../AISrc
        length = len(current_path)
        current_path = current_path[:length-6] # ... /MiAI_Facerecog_2
        newpath = current_path + "\Dataset\\FaceData\\processed\\" + name
        if not os.path.exists(newpath):
            os.makedirs(newpath)

        for filename in os.listdir(raw_path):
            img = cv2.imread(os.path.join(raw_path,filename))
            if img is not None:
                images.append(img)
                detector = MTCNN()
                result = detector.detect_faces(img)
                for item in result:
                    x = item['box'][0]
                    y = item['box'][1]
                    w = item['box'][2]
                    h = item['box'][3]
                    crop_img = img[y:y+h, x:x+w]
                    crop_img2 = cv2.resize(crop_img,(160, 160))
                    img_name = str(dem+1) + ".jpg"
                    cv2.imwrite(os.path.join(newpath , img_name), crop_img2)
                    cv2.waitKey(0)
                    dem = dem +1
            
#test = MTCNN_Detect()
#test.crop_and_save(r"test\\imgTest.jpg")