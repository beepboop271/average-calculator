# from classes.file_io import pack_file, unpack_file
from classes.teachassist_scraper import get_from_ta

# output precision
STRAND_PRECISION = 5
AVERAGE_PRECISION = 10

TA_INFO = []
TA_INFO.append(raw_input("enter username: ").strip())
TA_INFO.append(raw_input("enter password: ").strip())
TA_INFO.append(raw_input("enter TA student id: ").strip())
TA_INFO.append([raw_input("enter TA course id: ").strip()])

ta_courses = get_from_ta({"username": TA_INFO[0], "password": TA_INFO[1]},
                         TA_INFO[2],
                         TA_INFO[3])
for course in ta_courses:
    if course is not None:
        course.calculate_course_mark()
        print course.get_report_str(STRAND_PRECISION, AVERAGE_PRECISION)
