import tensorflow.compat.v1 as tf
import argparse
import facenet
import os
import sys
import math
import pickle
import numpy as np
import cv2
import collections
from sklearn.svm import SVC
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
import converter
from mtcnn import MTCNN

class FaceRecog:
    def __init__(self):
        self.image_path = r"test\\imgTest.jpg"
            
    def main(self, image_path):
        
        # Cai dat cac tham so can thiet
        MINSIZE = 20
        THRESHOLD = [0.6, 0.7, 0.7]
        FACTOR = 0.709
        IMAGE_SIZE = 182
        INPUT_IMAGE_SIZE = 160
        CLASSIFIER_PATH = 'Models/facemodel.pkl'
        #IMAGE_PATH = r"test\\imgTest.jpg"
        IMAGE_PATH = image_path
        FACENET_MODEL_PATH = 'Models/20180402-114759.pb'

        # Load model da train de nhan dien khuon mat - thuc chat la classifier
        with open(CLASSIFIER_PATH, 'rb') as file:
            model, class_names = pickle.load(file)
        print("Custom Classifier, Successfully loaded")

        with tf.Graph().as_default():

            # Cai dat GPU neu co
            gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.6)
            sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))

            with sess.as_default():

                # Load model MTCNN phat hien khuon mat
                print('Loading feature extraction model')
                facenet.load_model(FACENET_MODEL_PATH)

                # Lay tensor input va output
                images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
                embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
                phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
                embedding_size = embeddings.get_shape()[1]

                # Doc hinh anh
                cap = cv2.imread(IMAGE_PATH)

                # Chuẩn bị dữ liệu về các vectors về hình ảnh có sẵn đã được embeedings = facenet
                print('Calculating features for images')
                dataset = facenet.get_dataset("Dataset/FaceData/processed")
                paths, labels = facenet.get_image_paths_and_labels(dataset)
                nrof_images = len(paths)
                nrof_batches_per_epoch = int(math.ceil(1.0*nrof_images / 1000))
                emb_arrays = np.zeros((nrof_images, embedding_size))
                for i in range(nrof_batches_per_epoch):
                    start_index = i*1000
                    end_index = min((i+1)*1000, nrof_images)
                    paths_batch = paths[start_index:end_index]
                    images = facenet.load_data(paths_batch, False, False, 160)
                    feed_dict = { images_placeholder:images, phase_train_placeholder:False }
                    # trả về danh sách embedded vectors
                    emb_arrays[start_index:end_index,:] = sess.run(embeddings, feed_dict=feed_dict)

                # emb_arrays sẽ lưu vectors của tất cả các hình
                # emb_array sẽ lưu vector của hình ảnh người được nhận được từ camera     
                detector = MTCNN()
                image = cv2.cvtColor(cv2.imread(image_path), cv2.COLOR_BGR2RGB)
                result = detector.detect_faces(image)   
                
                while (True):

                    # Phat hien khuon mat, tra ve vi tri trong bounding_boxes
                    bounding_boxes_list = []
                    for i in result:
                        bounding_boxes_list.append(i["box"])

                    bounding_boxes = np.asfarray(bounding_boxes_list)

                    faces_found = bounding_boxes.shape[0]
                    try:
                        # Neu co it nhat 1 khuon mat trong cap
                        if faces_found > 0:
                            det = bounding_boxes[:, 0:4]
                            bb = np.zeros((faces_found, 4), dtype=np.int32)
                            for i in range(faces_found):
                                bb[i][0] = det[i][0]
                                bb[i][1] = det[i][1]
                                bb[i][2] = det[i][2]
                                bb[i][3] = det[i][3]

                                x = bb[i][0]
                                y = bb[i][1]
                                w = bb[i][2]
                                h = bb[i][3]

                                # Cat phan khuon mat tim duoc
                                cropped = cap[y:y+h, x:x+w]
                                scaled = cv2.resize(cropped, (INPUT_IMAGE_SIZE, INPUT_IMAGE_SIZE),interpolation=cv2.INTER_CUBIC)
                                scaled = facenet.prewhiten(scaled)
                                scaled_reshape = scaled.reshape(-1, INPUT_IMAGE_SIZE, INPUT_IMAGE_SIZE, 3)
                                feed_dict = {images_placeholder: scaled_reshape, phase_train_placeholder: False}
                                emb_array = sess.run(embeddings, feed_dict=feed_dict)
                                
                                # dùng L2 distance để đo khoảng cách L2 giữa 2 véctor
                                # [-1,1]
                                sim = euclidean_distances(emb_arrays, emb_array)
                                sim = np.squeeze(sim, axis = 1)
                                argmin = np.argsort(sim)[::1][:1]
                                label = [labels[idx] for idx in argmin][0]

                                p = paths[label*10]

                                p = p[27:]
                                strArr = p.split('\\')
                                personName = strArr[0]

                                dis = converter.Converter()
                                probability = dis.convert_dis2sim(min(sim))
                                print("Name: {}, Probability: {}".format(personName, probability))

                                # Neu ty le nhan dang > 0.5 thi hien thi ten
                                if probability > 70:
                                    name = personName
                                else:
                                    # Con neu <=0.5 thi hien thi Unknow
                                    name = "Unknown"
                    except Exception as e:
                        print(e)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    break
                cap.release()
                cv2.destroyAllWindows()


#test = FaceRecog()
#test.main(r"test\\imgTest.jpg")