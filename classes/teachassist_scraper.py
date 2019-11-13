import requests
import re
TA_LOGIN_URL = "https://ta.yrdsb.ca/yrdsb/"
TA_COURSE_BASE_URL = "https://ta.yrdsb.ca/live/students/viewReport.php"


def get_from_ta(auth_dict, student_id, subject_ids):
    ta_session = requests.session()
    ta_session.post(TA_LOGIN_URL, auth_dict)
    for subject_id in subject_ids:
        response = ta_session.get(TA_COURSE_BASE_URL,
                                  params={"subject_id": subject_id,
                                          "student_id": student_id},
                                  allow_redirects=False)
        if response.status_code != 200:
            print "GET failed. Incorrect code given or teachassist is not open for this course"
        else:
            response = re.sub(r"\s+", r" ", response.content)
            get_name(response)
            get_weights(response)
            print response


def get_name(report):
    name = re.search(r"<h2>(\S+)</h2>", report).group(1)
    print name
    return name


def get_weights(report):
    idx = re.search(r"#ffffaa", report).start()
    report = report[idx:idx+790].split("#")
    report.pop(0)
    
    weights = []
    for i in range(4):
        weights.append(re.findall(r"[0-9\.]+%", report[i])[1][:-1])
    weights.append(re.findall(r"[0-9\.]+%", report[5])[0][:-1])

    print weights
    return weights
