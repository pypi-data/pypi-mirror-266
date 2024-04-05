from aleksis.core.models import GroupType

from ..settings import SCHOOL_CLASS_GROUP_TYPE_NAME, SCHOOL_GRADE_GROUP_TYPE_NAME


def get_school_grade_group_type():
    group_type, __ = GroupType.objects.managed_by_app("cursus").get_or_create(
        name=SCHOOL_GRADE_GROUP_TYPE_NAME, managed_by_app_label="cursus"
    )
    return group_type


def get_school_class_group_type():
    group_type, __ = GroupType.objects.managed_by_app("cursus").get_or_create(
        name=SCHOOL_CLASS_GROUP_TYPE_NAME, managed_by_app_label="cursus"
    )
    return group_type
