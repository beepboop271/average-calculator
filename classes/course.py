from strand import Strand
STRANDS = ["k", "t", "c", "a", "f"]


class Course():
    def __init__(self, course, weights=[],
                 knowledge=None, thinking=None, communication=None,
                 application=None, final=None):
        self.course = course
        self.strands = {"k": knowledge,
                        "t": thinking,
                        "c": communication,
                        "a": application,
                        "f": final}
        self.assessments = []
        self.mark = 1.0
        self.is_valid = False
        if len(weights) == len(self.strands):
            for i in range(len(self.strands)):
                self.add_strand_tuple(STRANDS[i], weights[i])

    def get_report_str(self, strand_precision=3, course_precision=4):
        s = self.course+"\n\t"
        for strand in STRANDS:
            strand = self.strands[strand]
            s += strand.strand+" "
            if strand.is_valid:
                s += str(round(strand.mark*100, strand_precision))+" \t"
            else:
                s += "None\t"
        if self.is_valid:
            s += "\n\tavg "+str(round(self.mark*100, course_precision))
            s += "\n\tta shows "+str(round(self.mark*100, 1))+"\n"
        else:
            s += "\n\tavg None\n\tta shows None"
        return s

    def add_strand_tuple(self, strand, course_weight):
        self.strands[strand] = Strand(strand, course_weight)

    def add_assessment_obj(self, assessment_obj):
        self.assessments.append(assessment_obj)
        for strand in assessment_obj.marks.keys():
            if assessment_obj.marks[strand] is not None:
                self.strands[strand].add_mark_obj(assessment_obj.marks[strand])

    def calculate_course_mark(self):
        for strand in self.strands.values():
            strand.calculate_strand_mark()
        total_weights = 0
        weighted_sum = 0
        for strand in self.strands.values():
            if strand.is_valid:
                total_weights += strand.weight
                weighted_sum += strand.mark*strand.weight
        if total_weights == 0:
            self.is_valid = False
            self.mark = 1.0
        else:
            self.is_valid = True
            self.mark = float(weighted_sum)/total_weights
