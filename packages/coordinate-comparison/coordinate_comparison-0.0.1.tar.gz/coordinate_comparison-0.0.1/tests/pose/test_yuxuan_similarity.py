from coordinate_comparison.pose import yuxuan_similarity
from coordinate_comparison.utils.comparison_tools import ComparisonTools
import os


def test_contrast():
    result1 = ComparisonTools.image_recognition('E:/workspace_work/workspace_python/hagrid/dataset/call/000fa617-c7ba-47f9-9860-4971d78abc41.jpg')
    if result1.pose_landmarks:
        landmarks1 = ComparisonTools.landmarks_to_arr(result1.pose_landmarks.landmark)

    result2 = ComparisonTools.image_recognition('E:/workspace_work/workspace_python/hagrid/dataset/call/000fa617-c7ba-47f9-9860-4971d78abc41.jpg')
    if result2.pose_landmarks:
        landmark2 = ComparisonTools.landmarks_to_arr(result2.pose_landmarks.landmark)

    print(yuxuan_similarity.contrast(landmarks1, landmark2, 0.9, []).to_string())

    # if result.pose_landmarks:
    #     print(ComparisonTools.landmarks_to_arr(result.pose_landmarks.landmark))
    # if result.left_hand_landmarks:
    #     print(ComparisonTools.landmarks_to_arr(result.left_hand_landmarks.landmark))
    # if result.right_hand_landmarks:
    #     print(ComparisonTools.landmarks_to_arr(result.right_hand_landmarks.landmark))
    # if result.face_landmarks:
    #     print(ComparisonTools.landmarks_to_arr(result.face_landmarks.landmark))
