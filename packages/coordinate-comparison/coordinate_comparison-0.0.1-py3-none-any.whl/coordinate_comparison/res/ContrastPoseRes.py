class ContrastPoseRes:
    """
    isMate 是否匹配上
    average 所有关键点匹配平均值
    """

    def __init__(self, is_mate, average, similarity_matrix):
        self.is_mate = is_mate
        self.average = average
        self.similarity_matrix = similarity_matrix

    def to_string(self):
        return f"是否匹配：[{self.is_mate}], 平均值: [{self.average}]"