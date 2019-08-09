import re
from classes.course import Course
from classes.assessment import Assessment

STRANDS = ["k", "t", "c", "a", "f"]
# output not internal precision
STRAND_PRECISION = 5
AVERAGE_PRECISION = 10


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
    courses = data.strip().split("COURSE ")
    # split each course to assessments
    courses = [course.split("\n") for course in courses]
    # remove duplicate whitespace
    pattern = re.compile(r"\s+")
    courses = [[re.sub(pattern, r" ", assessment) for assessment in course] for course in courses]
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
            assessment_obj = Assessment(assessment.next())
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
                        assessment_obj.add_mark_tuple(split_mark[0],
                                                      split_mark[1],
                                                      float(weight),
                                                      STRANDS[strand])
                        courses[i].add_assessment_obj(assessment_obj)
                    strand += 1
                except(StopIteration):
                    break
    return courses


def calculate_and_print(courses):
    # calculating the marks
    for course in courses:
        print course.course, "\n\t",
        for strand in course.strands.values():
            strand.calculate_strand_mark()
            print strand.strand,
            if strand.is_valid:
                print round(strand.mark*100, STRAND_PRECISION), "\t",
            else:
                print "None\t",
        course.calculate_course_mark()
        print "\n\tavg", round(course.mark*100, AVERAGE_PRECISION)
        print "\tta shows", round(course.mark*100, 1), "\n"


courses = unpack_file("average_calculator_data.txt", [])
calculate_and_print(courses)
