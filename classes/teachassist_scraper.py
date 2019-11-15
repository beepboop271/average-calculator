import requests
import re
TA_LOGIN_URL = "https://ta.yrdsb.ca/yrdsb/"
TA_COURSE_BASE_URL = "https://ta.yrdsb.ca/live/students/viewReport.php"
STRAND_PATTERNS = [
    re.compile(r"<td bgcolor=\"ffffaa\" align=\"center\" id=\"\S+?\">([0-9\.]+) / ([0-9\.]+).+?<br> <font size=\"-2\">weight=([0-9\.]+)</font> </td>"),
    re.compile(r"<td bgcolor=\"c0fea4\" align=\"center\" id=\"\S+?\">([0-9\.]+) / ([0-9\.]+).+?<br> <font size=\"-2\">weight=([0-9\.]+)</font> </td>"),
    re.compile(r"<td bgcolor=\"afafff\" align=\"center\" id=\"\S+?\">([0-9\.]+) / ([0-9\.]+).+?<br> <font size=\"-2\">weight=([0-9\.]+)</font> </td>"),
    re.compile(r"<td bgcolor=\"ffd490\" align=\"center\" id=\"\S+?\">([0-9\.]+) / ([0-9\.]+).+?<br> <font size=\"-2\">weight=([0-9\.]+)</font> </td>")
]


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
    print re.search(r"<h2>(\S+?)</h2>", report).group(1)


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
    report = _get_next_tag_pair(report,
                                r"table border=\"1\" cellpadding=\"3\" cellspacing=\"0\" width=\"100%\"",
                                r"(<table)|(</table>)",
                                "<table")[0]
    report = re.sub(r"<tr> <td colspan=\"4\" bgcolor=\"white\"> &nbsp; </td> </tr>",
                    r"",
                    report)
    rows = []
    while _has_match(report, r"<tr>.+</tr>"):
        tag = _get_next_tag_pair(report,
                                 r"<tr>",
                                 r"(<tr>)|(</tr>)",
                                 "<tr>")
        rows.append(tag[0])
        report = report[tag[2]:]

    rows.pop(0)
    
    names = []
    strand_marks = []
    for row in rows:
        # print row
        names.append(re.search(r"<td rowspan=\"2\">(.+?)</td>", row).group(1))
        this_assessment = []
        for strand_pattern in STRAND_PATTERNS:
            match = re.search(strand_pattern, row)
            if match is not None:
                this_assessment.append([match.group(1), match.group(2), match.group(3)])
            else:
                this_assessment.append(None)
        strand_marks.append(this_assessment)
        
    print names
    print strand_marks


def _has_match(report, regex):
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
