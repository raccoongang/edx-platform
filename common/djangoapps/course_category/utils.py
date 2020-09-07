from course_category.models import CourseCategory


def add_categories_for_course(category_names, course_id):
    for category in CourseCategory.objects.filter(name__in=category_names):
        category.courses.add(course_id)
