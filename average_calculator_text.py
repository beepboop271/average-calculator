from classes.file_reader import unpack_file

# output precision
STRAND_PRECISION = 5
AVERAGE_PRECISION = 10

courses = unpack_file("example_text_data.txt")
for course in courses:
    course.calculate_course_mark()
    print course.get_report_str(STRAND_PRECISION, AVERAGE_PRECISION)
