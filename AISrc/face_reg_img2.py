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

class FaceRecog:
    def __init__(self):
        self.cropped = np.zeros((2, 2))
            
    def main(self, cropped):
        
        # Cai dat cac tham so can thiet
        INPUT_IMAGE_SIZE = 160
        current_path = str(os.path.abspath(os.getcwd())) # .../AISrc
        length = len(current_path)
        current_path = current_path[:length-6] # ... /MiAI_Facerecog_2
        FACENET_MODEL_PATH = current_path + '\Models\\20180402-114759.pb'

        with tf.Graph().as_default():

            # Cai dat GPU neu co
            gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.6)
            sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))

            with sess.as_default():

                facenet.load_model(FACENET_MODEL_PATH)
                # Lay tensor input va output
                images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
                embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
                phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")

                paths =  np.load(current_path + '\\paths.npy')
                labels = np.load(current_path + '\\labels.npy')
                emb_arrays = np.load(current_path + '\\data.npy')

                recoged_name = ""
                while (True):
                    try:
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
                        processed_path = current_path + "\Dataset\\FaceData\\processed\\"
                        p = p[len(processed_path):]
                        print(p)

                        strArr = p.split('\\')
                        personName = strArr[0]

                        dis = converter.Converter()
                        probability = dis.convert_dis2sim(min(sim))
                        print("Name: {}, Probability: {}".format(personName, probability))

                        if probability > 70:
                            recoged_name = personName
                        # # Neu ty le nhan dang > 0.5 thi hien thi ten
                        # if probability > 70:
                        #     name = personName
                        # else:
                        #     # Con neu <=0.5 thi hien thi Unknow
                        #     name = "Unknown"
                    except Exception as e:
                        print(e)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                    break

                return recoged_name
                cv2.destroyAllWindows()


#test = FaceRecog()
