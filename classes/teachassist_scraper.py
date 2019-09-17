import requests
TA_LOGIN_URL = "https://ta.yrdsb.ca/yrdsb/"
TA_COURSE_BASE_URL = "https://ta.yrdsb.ca/live/students/viewReport.php"


def get_from_ta(auth_dict, student_id, subject_ids):
    ta_session = requests.session()
    ta_session.post(TA_LOGIN_URL, auth_dict)
    for subject_id in subject_ids:
        print ta_session.get(get_httpGET_url(student_id, subject_id)).content


def get_httpGET_url(student_id, subject_id):
    return (TA_COURSE_BASE_URL
            + "?subject_id="
            + str(subject_id)
            + "&student_id="
            + str(student_id))
