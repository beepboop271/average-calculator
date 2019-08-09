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
        if len(weights) == len(self.strands):
            for i in range(len(self.strands)):
                self.add_strand_tuple(STRANDS[i], weights[i])

    def add_strand_tuple(self, strand, course_weight):
        self.strands[strand] = Strand(strand, course_weight)

    def add_assessment_obj(self, assessment_obj):
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
        self.mark = float(weighted_sum)/total_weights
