from .courses import courses

def total_time():
    return sum(course.duration for course in courses)

