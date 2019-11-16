from classes.file_io import pack_file, unpack_file
from classes.teachassist_scraper import get_from_ta

# output precision
STRAND_PRECISION = 5
AVERAGE_PRECISION = 10

with open("auth.txt") as f:
    TA_INFO = f.read().split("\n")

ta_courses = get_from_ta({"username": TA_INFO[0], "password": TA_INFO[1]},
                         TA_INFO[2],
                         TA_INFO[3:])
pack_file(ta_courses, "actual_data.txt")
for course in ta_courses:
    if course is not None:
        course.calculate_course_mark()
        print course.get_report_str(STRAND_PRECISION, AVERAGE_PRECISION)

# todo: find differences between remote and local copy
# and allow the user to resolve differences

print "\n"
local_courses = unpack_file("actual_data.txt")
for course in local_courses:
    course.calculate_course_mark()
    print course.get_report_str(STRAND_PRECISION, AVERAGE_PRECISION)
