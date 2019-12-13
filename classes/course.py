from .strand import Strand
STRAND_STRINGS = ["k", "t", "c", "a", "f"]


class Course():
    def __init__(self, name,
                 weights=[],
                 assessment_list=None):
        self.name = name
        self.assessments = []
        self.mark = 1.0
        self.is_valid = False
        self.strands = {"k": None,
                        "t": None,
                        "c": None,
                        "a": None,
                        "f": None}
        if len(weights) == len(self.strands):
            for i in range(len(self.strands)):
                self.add_strand_tuple(STRAND_STRINGS[i], weights[i])
            if assessment_list is not None:
                for assessment_obj in assessment_list:
                    self.add_assessment_obj(assessment_obj)

    def __eq__(self, other):
        if self.mark != other.mark:
            return False
        for strand_str in STRAND_STRINGS:
            if self.strands.get(strand_str) != other.strands.get(strand_str):
                return False
        return True

    def __ne__(self, other):
        return not(self == other)

    def get_report_str(self, strand_precision=3, course_precision=4):
        s = self.name+"\n\t"
        for strand_str in STRAND_STRINGS:
            strand_obj = self.strands[strand_str]
            s += strand_obj.name+" "
            if strand_obj.is_valid:
                s += str(round(strand_obj.mark*100, strand_precision))+" \t"
            else:
                s += "None\t"
        if self.is_valid:
            s += "\n\tavg "+str(round(self.mark*100, course_precision))
            s += "\n\tta shows "+str(round(self.mark*100, 1))+"\n"
        else:
            s += "\n\tavg None\n\tta shows None"
        return s

    def add_strand_tuple(self, strand_str, course_weight):
        self.strands[strand_str] = Strand(strand_str, course_weight)
        # self.calculate_course_mark()

    def add_assessment_obj(self, assessment_obj):
        self.assessments.append(assessment_obj)
        for strand_str in assessment_obj.marks.keys():
            if assessment_obj.marks[strand_str] is not None:
                self.strands[strand_str] \
                        .add_mark_obj(assessment_obj.marks[strand_str])
        self.calculate_course_mark()

    def calculate_course_mark(self):
        total_weights = 0
        weighted_sum = 0
        for strand_obj in self.strands.values():
            strand_obj.calculate_strand_mark()
            if strand_obj.is_valid:
                total_weights += strand_obj.weight
                weighted_sum += strand_obj.mark*strand_obj.weight
        if total_weights == 0:
            self.is_valid = False
            self.mark = 1.0
        else:
            self.is_valid = True
            self.mark = float(weighted_sum)/total_weights
