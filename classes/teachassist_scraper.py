import requests
import re
from .assessment import Assessment
from .course import Course

TIMEOUT = 0.5
TA_LOGIN_URL = "https://ta.yrdsb.ca/yrdsb/"
TA_COURSE_BASE_URL = "https://ta.yrdsb.ca/live/students/viewReport.php"
MARK_REGEX = r"([0-9\.]+) / ([0-9\.]+).+?<br> <font size=\"-2\">weight=([0-9\.]+)</font> </td>"
STRAND_PATTERNS = [
    re.compile(r"<td bgcolor=\"ffffaa\" align=\"center\" id=\"\S+?\">" + MARK_REGEX),
    re.compile(r"<td bgcolor=\"c0fea4\" align=\"center\" id=\"\S+?\">" + MARK_REGEX),
    re.compile(r"<td bgcolor=\"afafff\" align=\"center\" id=\"\S+?\">" + MARK_REGEX),
    re.compile(r"<td bgcolor=\"ffd490\" align=\"center\" id=\"\S+?\">" + MARK_REGEX)
]


def get_from_ta(auth_dict, student_id, subject_ids):
    print "logging in...",
    ta_session = requests.session()
    ta_session.post(TA_LOGIN_URL, auth_dict)
    print "logged in"
    courses = []
    for subject_id in subject_ids:
        try:
            print "getting "+subject_id+"...",
            response = ta_session.get(TA_COURSE_BASE_URL,
                                      params={"subject_id": subject_id,
                                              "student_id": student_id},
                                      allow_redirects=False,
                                      timeout=TIMEOUT)
            response.raise_for_status()
            print "got report"

            report = re.sub(r"\s+", r" ", response.content)
            courses.append(Course(get_name(report),
                                  get_weights(report),
                                  get_assessments(report)))
        except requests.HTTPError:
            print "Non-OK response code while getting", subject_id
            courses.append(None)
        except requests.Timeout:
            print "Timed out while getting", subject_id
            courses.append(None)
        except requests.ConnectionError:
            print "Could not connect while getting", subject_id
            courses.append(None)
    return courses


def get_name(report):
    return re.search(r"<h2>(\S+?)</h2>", report).group(1)


def get_weights(report):
    idx = re.search(r"#ffffaa", report).start()
    report = report[idx:idx+800].split("#")
    report.pop(0)

    weights = []
    for i in range(4):
        weights.append(re.findall(r"[0-9\.]+%", report[i])[1][:-1])
    weights.append(re.findall(r"[0-9\.]+%", report[5])[0][:-1])
    return map(float, weights)


def get_assessments(report):
    # get the big table of all assessments
    report = _get_end_tag(report,
                          r"table border=\"1\" cellpadding=\"3\" cellspacing=\"0\" width=\"100%\"",
                          r"(<table)|(</table>)",
                          "<table").content
    # teachassist, why do you put blank lines between each assessment?
    report = re.sub(r"<tr> <td colspan=\"[0-5]\" bgcolor=\"white\"> &nbsp; </td> </tr>",
                    r"",
                    report)
    rows = []
    while re.search(r"<tr>.+</tr>", report) is not None:
        row = _get_end_tag(report,
                           r"<tr>",
                           r"(<tr>)|(</tr>)",
                           "<tr>")
        rows.append(row.content)
        report = report[row.end:]
    rows.pop(0)

    assessments = []
    name = ""
    for row in rows:
        name = re.sub(r"\s+", r"-",
                      re.search(r"<td rowspan=\"2\">(.+?)</td>", row).group(1).strip())
        marks = []
        for strand_pattern in STRAND_PATTERNS:
            match = re.search(strand_pattern, row)
            if match is not None:
                marks.append(map(float, [match.group(1), match.group(2), match.group(3)]))
            else:
                marks.append(None)
        assessments.append(Assessment(name, marks))

    return assessments


def _get_end_tag(report, start_regex, search_regex, start_tag):
    idx = re.search(start_regex, report).start()

    tags_to_close = 1
    tag_iter = re.finditer(search_regex, report[idx+1:])
    while tags_to_close > 0:
        next_match = tag_iter.next()
        if next_match.group() == start_tag:
            tags_to_close += 1
        else:
            tags_to_close -= 1
    # who knew you could have anonymous objects in python
    # maybe i shouldn't do this
    return type("",
                (object,),
                {"content": report[idx-1:idx+next_match.end()],
                 "start": idx-1,
                 "end": idx+next_match.end()})
