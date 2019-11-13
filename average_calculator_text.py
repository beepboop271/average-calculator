from classes.file_io import unpack_file
from classes.teachassist_scraper import get_from_ta

# output precision
STRAND_PRECISION = 5
AVERAGE_PRECISION = 10

with open("auth.txt") as f:
    TA_INFO = f.read().split("\n")

AUTH_DICT = {"username": TA_INFO[0],
             "password": TA_INFO[1]}
TA_STUDENT_ID = TA_INFO[2]
TA_SUBJECT_IDS = TA_INFO[3:]

# program currently prints html of course report pages,
# extracting useful data to come
get_from_ta(AUTH_DICT, TA_STUDENT_ID, TA_SUBJECT_IDS)
courses = unpack_file("example_text_data.txt")
for course in courses:
    course.calculate_course_mark()
    print course.get_report_str(STRAND_PRECISION, AVERAGE_PRECISION)
