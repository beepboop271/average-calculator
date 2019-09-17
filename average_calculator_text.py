from classes.file_io import unpack_file, pack_file
from classes.teachassist_scraper import get_from_ta

# output precision
STRAND_PRECISION = 5
AVERAGE_PRECISION = 10

courses = unpack_file("example_text_data.txt")
for course in courses:
    course.calculate_course_mark()
    print course.get_report_str(STRAND_PRECISION, AVERAGE_PRECISION)
