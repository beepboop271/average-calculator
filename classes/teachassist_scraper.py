import requests
import re
TA_LOGIN_URL = "https://ta.yrdsb.ca/yrdsb/"
TA_COURSE_BASE_URL = "https://ta.yrdsb.ca/live/students/viewReport.php"


def get_from_ta(auth_dict, student_id, subject_ids):
    ta_session = requests.session()
    ta_session.post(TA_LOGIN_URL, auth_dict)
    for subject_id in subject_ids:
        # print "getting", subject_id
        response = ta_session.get(TA_COURSE_BASE_URL,
                                  params={"subject_id": subject_id,
                                          "student_id": student_id},
                                  allow_redirects=False)
        if response.status_code != 200:
            print "GET failed"
        else:
            report = re.sub(r"\s+", r" ", response.content)
            get_name(report)
            get_weights(report)
            get_assessments(report)


def get_name(report):
    print re.search(r"<h2>(\S+)</h2>", report).group(1)


def get_weights(report):
    idx = re.search(r"#ffffaa", report).start()
    report = report[idx:idx+800].split("#")
    report.pop(0)
    
    weights = []
    for i in range(4):
        weights.append(re.findall(r"[0-9\.]+%", report[i])[1][:-1])
    weights.append(re.findall(r"[0-9\.]+%", report[5])[0][:-1])
    print weights


def get_assessments(report):
    # idx = re.search(r"table border=\"1\" cellpadding=\"3\" cellspacing=\"0\" width=\"100%\"",
    #                 report).start()
    # report = _get_whole_table(report, idx)
    # report = _get_end_tag(report, idx, r"(<table)|(</table>)", "<table")
    report = _get_next_tag_pair(report,
                                r"table border=\"1\" cellpadding=\"3\" cellspacing=\"0\" width=\"100%\"",
                                r"(<table)|(</table>)",
                                "<table")[0]
    report = re.sub(r"<tr> <td colspan=\"4\" bgcolor=\"white\"> &nbsp; </td> </tr>",
                    r"",
                    report)
    rows = []
    while _has_pair(report, r"<tr>.+</tr>"):
        tag = _get_next_tag_pair(report,
                                 r"<tr>",
                                 r"(<tr>)|(</tr>)",
                                 "<tr>")
        rows.append(tag[0])
        report = report[tag[2]:]

    print rows

def _has_pair(report, regex):
    return re.search(regex, report) is not None


def _get_next_tag_pair(report, start_regex, search_regex, start_tag):
    idx = re.search(start_regex, report).start()

    tags_to_close = 1
    tag_iter = re.finditer(search_regex, report[idx+1:])
    while tags_to_close > 0:
        next_match = tag_iter.next()
        if next_match.group() == start_tag:
            tags_to_close += 1
        else:
            tags_to_close -= 1
    return (report[idx-1:idx+next_match.end()], idx-1, idx+next_match.end())
