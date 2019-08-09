import re
STRANDS = ["K&U", "T&I", "COM", "APP", "FIN"]
# output not internal precision
STRAND_PRECISION = 5
AVERAGE_PRECISION = 10


class Assessment():
    def __init__(self, name, strand, strand_weight, mark_numerator, mark_denominator):
        self.name = name
        self.strand = strand
        self.weight = strand_weight
        self.numerator = mark_numerator
        self.denominator = mark_denominator
        self.approx_value = round(self.numerator/self.denominator, 2)


class Strand():
    def __init__(self, strand, course_weight):
        self.strand = strand
        self.weight = course_weight
        self.marks = []
        self.value = 100
        self.valid = True

    def add_mark_o(self, mark_o):
        self.marks.append(mark_o)

    def add_mark_tuple(self, numerator, denominator, weight, name):
        mark_o = Assessment(self.strand, name, weight, numerator, denominator)
        self.add_mark_o(mark_o)

    def calculate_strand_mark(self):
        total_weights = 0
        weighted_sum = 0
        for mark in self.marks:
            total_weights += mark.weight
            weighted_sum += (float(mark.numerator)/mark.denominator)*mark.weight
        if total_weights == 0:
            self.valid = False
            self.value = 1.0
        else:
            self.value = float(weighted_sum)/total_weights


class Course():
    def __init__(self, course, weights=[]):
        self.course = course
        self.strands = []
        self.value = 100
        if len(weights) == len(STRANDS):
            for i in range(len(STRANDS)):
                self.add_strand_tuple(STRANDS[i], weights[i])

    def add_strand_o(self, strand_o):
        self.strands.append(strand_o)

    def add_strand_tuple(self, strand, course_weight):
        self.strands.append(Strand(strand, course_weight))

    def calculate_course_mark(self):
        total_weights = 0
        weighted_sum = 0
        for strand in self.strands:
            if strand.valid:
                total_weights += strand.weight
                weighted_sum += strand.value*strand.weight
        self.value = float(weighted_sum)/total_weights


def remove_empty(x):
    for i in range(len(x)-1, -1, -1):
        if type(x[i]) == str:
            if len(x[i]) < 1:
                x.pop(i)
            else:
                x[i] = x[i].strip()
        else:
            if len(x[i]) <= 1:
                x.pop(i)


def parse_to_lists(path):
    f = open(path)
    data = f.read()
    f.close()
    # split to courses
    courses = data.strip().split("COURSE")

    # split each course to assessments
    courses = map(lambda x: x.split("\n"), courses)

    # remove duplicate whitespace
    pattern = re.compile(r"\s+")
    courses = map(lambda x: map(lambda y: re.sub(pattern, r" ", y), x), courses)

    # remove empty lists and strings
    remove_empty(courses)
    for i in range(len(courses)):
        remove_empty(courses[i])

    # split assessments to strands
    for course in courses:
        for i in range(len(course)):
            if " " in course[i]:
                course[i] = course[i].split(" ")

    return courses


def unpack_file(path, courses):
    data = parse_to_lists(path)
    # for each course
    courses = []
    for i in range(len(data)):
        courses.append(Course(data[i][0], map(float, data[i][1][1:])))
        # for each assessment in the course
        for assessment in map(iter, data[i][2:]):
            assessment_name = assessment.next()
            strand = 0
            # for each strand in the assessment
            while True:
                try:
                    # either a mark (e.g. 12/13) and a weight (e.g. 4)
                    # or "n" indicating no mark for that strand
                    part = assessment.next()
                    if part != "n":
                        weight = assessment.next()
                        split_mark = map(float, part.split("/"))
                        # finally add the mark
                        courses[i].strands[strand].add_mark_tuple(split_mark[0],
                                                                  split_mark[1],
                                                                  float(weight),
                                                                  assessment_name)
                    strand += 1
                except(StopIteration):
                    break
    return courses


def calculate_and_print(courses):
    # calculating the marks
    for course in courses:
        print course.course, "\n\t",
        for strand in course.strands:
            strand.calculate_strand_mark()
            print strand.strand, round(strand.value*100, STRAND_PRECISION), "\t",
        course.calculate_course_mark()
        print "\n\tavg", round(course.value*100, AVERAGE_PRECISION), "\n"


print "master"
courses = unpack_file("average_calculator_data_master.txt", [])
calculate_and_print(courses)
print "other"
courses = unpack_file("average_calculator_data.txt", [])
calculate_and_print(courses)
