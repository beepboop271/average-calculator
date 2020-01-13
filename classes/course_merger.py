from .course import Course


def merge_courses_into(ta_course, local_course):
    if(ta_course == local_course):
        return
    for ta_assessment in ta_course.get_assessments():
        in_code = local_course.has_assessment(ta_assessment)
        # if it's Course.PRESENT, do nothing because
        # it's already recorded corrrectly
        if in_code[0] == Course.NOT_PRESENT:
            local_course.add_assessment_obj(ta_assessment)
            print("added", ta_assessment.name, "to", local_course.name)
        elif in_code[0] == Course.PRESENT_BUT_DIFFERENT:
            print("conflict:")
            print("local  (enter '1'):", in_code[1])
            print("remote (enter '2'):", ta_assessment)
            course_to_choose = int(input("enter choice: "))
            # if it's 1, do nothing because the correct
            # course is already recorded
            if course_to_choose == 2:
                in_code[1].copy_from(ta_assessment)
    for (i, local_assessment) in enumerate(local_course.get_assessments()):
        in_code = ta_course.has_assessment(local_assessment)
        if in_code[0] == Course.NOT_PRESENT:
            print("local assessment not present in remote course:")
            print(in_code[1])
            print("keep local: enter '1'")
            print("remove    : enter '2'")
            course_to_choose = int(input("enter choice: "))
            if course_to_choose == 2:
                local_course.remove_assessment(i)


def merge_course_lists(ta_courses, local_courses):
    ta_courses_dict = {course.name: course for course in ta_courses}
    local_courses_dict = {course.name: course for course in local_courses}

    ta_names = set([course.name for course in ta_courses])
    local_names = set([course.name for course in local_courses])
    
    for new_course_name in (ta_names-local_names):
        print("added", new_course_name, "to local courses")
        local_courses.append(ta_courses_dict.get(new_course_name))

    for common_course_name in (ta_names & local_names):
        merge_courses_into(ta_courses_dict.get(common_course_name),
                           local_courses_dict.get(common_course_name))
