import re
from course import Course
from assessment import Assessment
STRAND_STRINGS = ["k", "t", "c", "a", "f"]


def unpack_file(path):
    data = _parse_to_lists(path)
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
                                                      STRAND_STRINGS[strand])
                    strand += 1
                except(StopIteration):
                    break
            courses[i].add_assessment_obj(assessment_obj)

    return courses


def pack_file(courses, path):
    s = ""
    for course in courses:
        s += "COURSE "+course.name+"\n"

        s += "WEIGHTS"
        for strand_str in STRAND_STRINGS:
            s += " "+str(course.strands.get(strand_str).weight)
        s += "\n"

        for assessment in course.assessments:
            s += assessment.name
            for strand_str in STRAND_STRINGS:
                s += "    "
                strand_mark = assessment.marks.get(strand_str)
                if strand_mark is None:
                    s += "n"
                else:
                    s += str(strand_mark.numerator)
                    s += "/"+str(strand_mark.denominator)
                    s += " "+str(strand_mark.weight)
            s += "\n"

        s += "\n"

    f = open(path, "w")
    f.write(s)
    f.close()


def _parse_to_lists(path):
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
    _remove_empty(courses)
    for i in range(len(courses)):
        _remove_empty(courses[i])
    # split assessments to strands
    for course in courses:
        for i in range(len(course)):
            if " " in course[i]:
                course[i] = course[i].split(" ")

    return courses


def _remove_empty(x):
    for i in range(len(x)-1, -1, -1):
        if type(x[i]) == str:
            if len(x[i]) < 1:
                x.pop(i)
            else:
                x[i] = x[i].strip()
        else:
            if len(x[i]) <= 1:
                x.pop(i)
