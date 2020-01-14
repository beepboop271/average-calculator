from classes.teachassist_scraper import get_from_ta

# output precision
STRAND_PRECISION = 5
AVERAGE_PRECISION = 10

TA_INFO = [
    input("enter username: ").strip(),
    input("enter password: ").strip()
]

ta_courses = get_from_ta({"username": TA_INFO[0], "password": TA_INFO[1]})
for course in ta_courses:
    course.calculate_course_mark()
    print(course.get_report_str(STRAND_PRECISION, AVERAGE_PRECISION))
