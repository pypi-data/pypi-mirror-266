from coordinate_comparison.res.ContrastPoseRes import ContrastPoseRes
from coordinate_comparison.utils.comparison_tools import ComparisonTools


def contrast(vectors_a, vectors_b, threshold: float, point_arr):
    is_mate = True
    similarity_matrix = []
    average = 0
    len_a = len(vectors_a)
    len_b = len(vectors_b)
    if len(point_arr) == 0:
        average_num = len_a
    else:
        average_num = len(point_arr)
    if len_a > 0 and len_a == len_b:
        sum_val = 0
        for index, vector_a in enumerate(vectors_a):
            if index in point_arr or len(point_arr) == 0:
                val = ComparisonTools.cosine_similarity(vector_a, vectors_b[index])
                if is_mate and val < threshold:
                    is_mate = False
                similarity_matrix.append(val)
                sum_val += val
        if sum_val > 0:
            average = sum_val / average_num
    else:
        is_mate = False
    return ContrastPoseRes(is_mate, average, similarity_matrix)
