import requests
import re
from .assessment import Assessment
from .course import Course

TIMEOUT = 1
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


def get_from_ta(auth_dict):
    print("logging in... ", end="")
    ta_session = requests.session()
    homepage = ta_session.post(TA_LOGIN_URL, auth_dict).text

    ta_ids = TA_ID_REGEX.findall(homepage)
    if len(ta_ids) < 1:
        print("No open reports found")
        return []

    student_id = ta_ids[0][1]
    subject_ids = [match_tuple[0] for match_tuple in ta_ids]

    print("logged in")
    courses = []
    for subject_id in subject_ids:
        try:
            print("getting "+subject_id+"... ", end="")
            response = ta_session.get(TA_COURSE_BASE_URL,
                                      params={"subject_id": subject_id,
                                              "student_id": student_id},
                                      allow_redirects=False,
                                      timeout=TIMEOUT)
            response.raise_for_status()
            print("got report")

            report = re.sub(r"\s+", r" ", response.text)
            courses.append(Course(_get_name(report),
                                  _get_weights(report),
                                  _get_assessments(report)))
        except requests.HTTPError:
            print("Non-OK response code while getting", subject_id)
        except requests.Timeout:
            print("Timed out while getting", subject_id)
        except requests.ConnectionError:
            print("Could not connect while getting", subject_id)
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
                          "<table").content
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
        rows.append(row.content)
        report = report[row.end:]
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
    # who knew you could have anonymous objects in python
    # maybe i shouldn't do this
    return type("",
                (object,),
                {"content": report[idx-1:idx+next_match.end()],
                 "start": idx-1,
                 "end": idx+next_match.end()})
