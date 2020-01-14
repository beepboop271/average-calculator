from classes.file_io import pack_file, unpack_file
from classes.teachassist_scraper import get_from_ta
from classes.course_merger import merge_course_lists

# output precision
STRAND_PRECISION = 5
AVERAGE_PRECISION = 10

with open("auth.txt") as f:
    TA_INFO = f.read().split("\n")

ta_courses = get_from_ta({"username": TA_INFO[0], "password": TA_INFO[1]})
for course in ta_courses:
    course.calculate_course_mark()
    print(course.get_report_str(STRAND_PRECISION, AVERAGE_PRECISION))

print("\n")
local_courses = unpack_file("actual_data.txt")
for course in local_courses:
    course.calculate_course_mark()
    print(course.get_report_str(STRAND_PRECISION, AVERAGE_PRECISION))

merge_course_lists(ta_courses, local_courses)
pack_file(local_courses, "actual_data.txt")
