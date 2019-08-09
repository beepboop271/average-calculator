class Strand():
    def __init__(self, strand, course_weight):
        self.strand = strand
        self.weight = course_weight
        self.marks = []
        self.mark = 1.0
        self.is_valid = False

    # def __str__(self):
    #     s = "("+self.strand+" cw"+str(self.weight)+" [ "
    #     for mark in self.marks:
    #         s += str(mark)+" "
    #     s += "])"
    #     return s

    def add_mark_obj(self, mark_obj):
        self.marks.append(mark_obj)

    def calculate_strand_mark(self):
        total_weights = 0
        weighted_sum = 0
        for mark in self.marks:
            total_weights += mark.weight
            weighted_sum += (float(mark.numerator)/mark.denominator
                             * mark.weight)
        if total_weights == 0:
            self.is_valid = False
            self.mark = 1.0
        else:
            self.is_valid = True
            self.mark = float(weighted_sum)/total_weights
