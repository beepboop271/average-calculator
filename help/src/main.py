import re
import os
import requests

output = []

STRAND_STRINGS = ["k", "t", "c", "a", "f"]

STRAND_PRECISION = 5
AVERAGE_PRECISION = 10

TIMEOUT = 0.5
TA_LOGIN_URL = "https://ta.yrdsb.ca/yrdsb/"
TA_COURSE_BASE_URL = "https://ta.yrdsb.ca/live/students/viewReport.php"
TA_ID_REGEX = re.compile(r"<a href=\"viewReport.php\?subject_id=([0-9]+)&student_id=([0-9]+)\">")
_MARK_REGEX = r"([0-9\.]+) / ([0-9\.]+).+?<br> <font size=\"-2\">weight=([0-9\.]+)</font> </td>"
_STRAND_PATTERNS = [
    re.compile(r"<td bgcolor=\"ffffaa\" align=\"center\" id=\"\S+?\">" + _MARK_REGEX),
    re.compile(r"<td bgcolor=\"c0fea4\" align=\"center\" id=\"\S+?\">" + _MARK_REGEX),
    re.compile(r"<td bgcolor=\"afafff\" align=\"center\" id=\"\S+?\">" + _MARK_REGEX),
    re.compile(r"<td bgcolor=\"ffd490\" align=\"center\" id=\"\S+?\">" + _MARK_REGEX),
    re.compile(r"<td bgcolor=\"#?dedede\" align=\"center\" id=\"\S+?\">" + _MARK_REGEX)
]


class Mark(object):
    def __init__(self, numerator, denominator, weight, strand_str):
        self.numerator = numerator
        self.denominator = denominator
        self.weight = weight
        self.strand_str = strand_str
        self.decimal = float(numerator)/denominator

    def __eq__(self, other):
        if(other is None
           or type(other) != type(self)):
            return False
        return (self.numerator == other.numerator
                and self.denominator == other.denominator
                and self.weight == other.weight
                and self.strand_str == other.strand_str)

    def __ne__(self, other):
        return not(self == other)

    def __str__(self):
        return ("Mark({0} W{1} {2}/{3} {4}%)"
                .format(self.strand_str,
                        self.weight,
                        self.numerator,
                        self.denominator,
                        round(self.decimal*100, 1)))


class Assessment(object):
    def __init__(self, name,
                 mark_list=None):
        self.name = name
        self.marks = {"k": None,
                      "t": None,
                      "c": None,
                      "a": None,
                      "f": None}
        if mark_list is not None:
            for i in range(len(mark_list)):
                if mark_list[i] is not None:
                    self.add_mark_tuple(*mark_list[i],
                                        strand_str=STRAND_STRINGS[i])

    def __eq__(self, other):
        if(other is None
           or type(other) != type(self)
           or other.name != self.name):
            return False
        for strand_str in STRAND_STRINGS:
            if self.marks.get(strand_str) != other.marks.get(strand_str):
                return False
        return True

    def __ne__(self, other):
        return not(self == other)

    def __str__(self):
        return ("Assessment({0}: K:{1} T:{2} C:{3} A:{4} F:{5})"
                .format(self.name,
                        self.marks.get("k"),
                        self.marks.get("t"),
                        self.marks.get("c"),
                        self.marks.get("a"),
                        self.marks.get("f")))

    def add_mark_tuple(self, numerator, denominator, weight, strand_str):
        self.marks[strand_str] = Mark(numerator,
                                      denominator,
                                      weight,
                                      strand_str)

    def copy_from(self, other):
        self.marks = other.marks


class Strand(object):
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


class Course(object):
    NOT_PRESENT = 1
    PRESENT_BUT_DIFFERENT = 2
    PRESENT = 3

    def __init__(self, name,
                 weights=[],
                 assessment_list=None):
        self.name = name
        self._assessments = []
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
        if(other is None
           or type(other) != type(self)
           or self.mark != other.mark):
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

    def get_assessments(self):
        return iter(self._assessments)

    def has_assessment(self, assessment):
        for own_assessment in self._assessments:
            if assessment == own_assessment:
                return (Course.PRESENT,)
            elif assessment.name == own_assessment.name:
                return (Course.PRESENT_BUT_DIFFERENT, own_assessment)
        return (Course.NOT_PRESENT, assessment)

    def remove_assessment(self, i):
        self._assessments.pop(i)

    def add_assessment_obj(self, assessment_obj):
        self._assessments.append(assessment_obj)
        for strand_str in assessment_obj.marks.keys():
            if assessment_obj.marks[strand_str] is not None:
                self.strands[strand_str].add_mark_obj(assessment_obj.marks[strand_str])
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


def merge_courses_into(ta_course, local_course):
    if(ta_course == local_course):
        return
    for ta_assessment in ta_course.get_assessments():
        in_code = local_course.has_assessment(ta_assessment)
        # if it's Course.PRESENT, do nothing because
        # it's already recorded corrrectly
        if in_code[0] == Course.NOT_PRESENT:
            local_course.add_assessment_obj(ta_assessment)
            output.append(f"added {ta_assessment.name} to {local_course.name}")
        elif in_code[0] == Course.PRESENT_BUT_DIFFERENT:
            in_code[1].copy_from(ta_assessment)
            output.append(f"updated {ta_assessment.name}")
    for (i, local_assessment) in enumerate(local_course.get_assessments()):
        in_code = ta_course.has_assessment(local_assessment)
        if in_code[0] == Course.NOT_PRESENT:
            output.append(f"removed {local_assessment.name}")
            local_course.remove_assessment(i)


def merge_course_lists(ta_courses, local_courses):
    ta_courses_dict = {course.name: course for course in ta_courses}
    local_courses_dict = {course.name: course for course in local_courses}

    ta_names = set([course.name for course in ta_courses])
    local_names = set([course.name for course in local_courses])

    for new_course_name in (ta_names-local_names):
        output.append(f"added {new_course_name} to local courses")
        local_courses.append(ta_courses_dict.get(new_course_name))

    for common_course_name in (ta_names & local_names):
        merge_courses_into(ta_courses_dict.get(common_course_name),
                           local_courses_dict.get(common_course_name))


def unpack_file(path):
    data = _parse_to_lists(path)
    # for each course
    courses = []
    for i in range(len(data)):
        courses.append(Course(data[i][0], list(map(float, data[i][1][1:]))))
        # for each assessment in the course
        for assessment in map(iter, data[i][2:]):
            assessment_obj = Assessment(next(assessment))
            strand = 0
            # for each strand in the assessment
            while True:
                try:
                    # either a mark (e.g. 12/13) and a weight (e.g. 4)
                    # or "n" indicating no mark for that strand
                    part = next(assessment)
                    if part != "n":
                        weight = next(assessment)
                        split_mark = list(map(float, part.split("/")))
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
    s = []
    for course in courses:
        if course is None:
            continue
        s.append("COURSE "+course.name+"\n")

        s.append("WEIGHTS")
        for strand_str in STRAND_STRINGS:
            s.append(" "+str(course.strands.get(strand_str).weight))
        s.append("\n")

        for assessment in course.get_assessments():
            s.append(_pad(assessment.name, 32))
            for strand_str in STRAND_STRINGS:
                strand_mark = assessment.marks.get(strand_str)
                if strand_mark is None:
                    s.append(_pad("n", 12))
                else:
                    s.append(_pad((_get_num_str(strand_mark.numerator)
                                   + "/"+_get_num_str(strand_mark.denominator)
                                   + " "+_get_num_str(strand_mark.weight)),
                                  12))
            s.append("\n")
        s.append("\n")

    with open(path, "w") as f:
        f.write("".join(s))


def _pad(s, min_len):
    if len(s) < min_len:
        return s+" "*(min_len-len(s))
    else:
        return s+" "


def _get_num_str(num):
    if int(num) == num:
        return str(int(num))
    else:
        return str(num)


def _parse_to_lists(path):
    with open(path) as f:
        data = f.read()

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


def get_from_ta(auth_dict):
    output.append("logging in...")
    ta_session = requests.session()
    homepage = ta_session.post(TA_LOGIN_URL, auth_dict).text

    ta_ids = TA_ID_REGEX.findall(homepage)
    if len(ta_ids) < 1:
        output.append("No open reports found")
        return []

    student_id = ta_ids[0][1]
    subject_ids = [match_tuple[0] for match_tuple in ta_ids]

    output.append("logged in")
    courses = []
    for subject_id in subject_ids:
        try:
            output.append(f"getting {subject_id}...")
            response = ta_session.get(TA_COURSE_BASE_URL,
                                      params={"subject_id": subject_id,
                                              "student_id": student_id},
                                      allow_redirects=False,
                                      timeout=TIMEOUT)
            response.raise_for_status()
            output.append("got report")

            report = re.sub(r"\s+", r" ", response.text)
            courses.append(Course(_get_name(report),
                                  _get_weights(report),
                                  _get_assessments(report)))
        except requests.HTTPError:
            output.append("Non-OK response code while getting", subject_id)
        except requests.Timeout:
            output.append("Timed out while getting", subject_id)
        except requests.ConnectionError:
            output.append("Could not connect while getting", subject_id)
    return courses


def _get_name(report):
    return re.search(r"<h2>(\S+?)</h2>", report).group(1)


def _get_weights(report):
    idx = re.search(r"#ffffaa", report).start()
    report = report[idx:idx+800].split("#")
    report.pop(0)

    weights = []
    for i in range(4):
        weights.append(re.findall(r"[0-9\.]+%", report[i])[1][:-1])
    weights.append(re.findall(r"[0-9\.]+%", report[5])[0][:-1])
    return list(map(float, weights))


def _get_assessments(report):
    # get the big table of all assessments
    report = _get_end_tag(report,
                          r"table border=\"1\" cellpadding=\"3\" cellspacing=\"0\" width=\"100%\"",
                          r"(<table)|(</table>)",
                          "<table")["content"]
    # remove the feedback box which is usually empty
    report = re.sub(r"<tr> <td colspan=\"[0-5]\" bgcolor=\"white\"> [^&]*&nbsp; </td> </tr>",
                    r"",
                    report)
    rows = []
    while re.search(r"<tr>.+</tr>", report) is not None:
        row = _get_end_tag(report,
                           r"<tr>",
                           r"(<tr>)|(</tr>)",
                           "<tr>")
        rows.append(row["content"])
        report = report[row["end"]:]
    rows.pop(0)

    assessments = []
    name = ""
    for row in rows:
        name = re.sub(r"\s+", r"-",
                      re.search(r"<td rowspan=\"2\">(.+?)</td>", row)
                        .group(1)
                        .strip())
        marks = []
        for strand_pattern in _STRAND_PATTERNS:
            match = re.search(strand_pattern, row)
            if match is not None:
                marks.append(list(map(float, [match.group(1),
                                              match.group(2),
                                              match.group(3)])))
            else:
                marks.append(None)
        assessments.append(Assessment(name, marks))

    return assessments


def _get_end_tag(report, start_regex, search_regex, start_tag):
    idx = re.search(start_regex, report).start()

    tags_to_close = 1
    tag_iter = re.finditer(search_regex, report[idx+1:])
    while tags_to_close > 0:
        next_match = next(tag_iter)
        if next_match.group() == start_tag:
            tags_to_close += 1
        else:
            tags_to_close -= 1
    return {"content": report[idx-1:idx+next_match.end()],
            "start": idx-1,
            "end": idx+next_match.end()}


def main(requestn):
    ta_courses = get_from_ta({"username": os.getenv("USERNAME"),
                              "password": os.getenv("PASSWORD")})

    for course in ta_courses:
        course.calculate_course_mark()
        output.append(course.get_report_str(STRAND_PRECISION, AVERAGE_PRECISION))

    local_courses = unpack_file("actual_data.txt")
    for course in local_courses:
        course.calculate_course_mark()
        output.append(course.get_report_str(STRAND_PRECISION, AVERAGE_PRECISION))

    merge_course_lists(ta_courses, local_courses)
    pack_file(local_courses, "actual_data.txt")

    return "\n".join(output)
