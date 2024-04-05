from django.contrib.auth.models import User

from rules import predicate

from ..models import Course


@predicate
def is_course_teacher(user: User, obj: Course) -> bool:
    """Check if person of user is teacher in a specific course."""
    return user.person in obj.teachers.all()
