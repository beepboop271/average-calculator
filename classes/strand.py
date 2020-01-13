class Strand():
    def __init__(self, strand_str, course_weight):
        self.name = strand_str
        self.weight = course_weight
        self.marks = []
        self.mark = 1.0
        self.is_valid = False

    def __eq__(self, other):
        if(other is None
           or type(other) != type(self)
           or self.name != other.name
           or self.mark != other.mark
           or len(self.marks) != len(other.marks)
           or self.weight != other.weight):
            return False
        for mark in self.marks:
            if not other.has_mark(mark):
                return False
        return True

    def __ne__(self, other):
        return not(self == other)

    # def __str__(self):
    #     s = "("+self.name+" cw"+str(self.weight)+" [ "
    #     for mark in self.marks:
    #         s += str(mark)+" "
    #     s += "])"
    #     return s

    def add_mark_obj(self, mark_obj):
        self.marks.append(mark_obj)
        # self.calculate_strand_mark()

    def has_mark(self, mark_obj):
        for own_mark in self.marks:
            if mark_obj == own_mark:
                return True
        return False

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
