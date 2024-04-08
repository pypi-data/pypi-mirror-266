import cv2
import mediapipe as mp
import numpy as np


class ComparisonTools:

    # 获取指图片的姿态关键点
    @staticmethod
    def image_recognition(path):
        mp_holistic = mp.solutions.holistic
        with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
            # 进行姿态估计的操作
            image = cv2.imread(path)
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = holistic.process(image_rgb)
            cv2.destroyAllWindows()
            return results

    # 两个向量计算余弦相似度
    @staticmethod
    def cosine_similarity(vector_a, vector_b):
        dot_product = np.dot(vector_a, vector_b)
        norm_a = np.linalg.norm(vector_a)
        norm_b = np.linalg.norm(vector_b)
        similarity = dot_product / (norm_a * norm_b)
        return similarity

    @staticmethod
    def landmarks_to_arr(landmarks):
        landmark_arr = []
        for index, landmark in enumerate(landmarks):
            landmark_arr.append([landmark.x, landmark.y, landmark.z if landmark.HasField('z') else None, landmark.visibility if landmark.HasField('visibility') else None])
        return landmark_arr
