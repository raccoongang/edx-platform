from course_category.models import CourseCategory


def add_categories_for_course(category_names, course_id):
    for category_name in category_names:
        category = CourseCategory.objects.filter(name=category_name).first()
        if category:
            category.courses.add(course_id)
