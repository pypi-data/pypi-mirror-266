from django.core.exceptions import PermissionDenied
from django.db.models import Q

import graphene
from graphene_django.types import DjangoObjectType
from graphene_django_cud.mutations import (
    DjangoBatchCreateMutation,
    DjangoBatchDeleteMutation,
    DjangoBatchPatchMutation,
)
from guardian.shortcuts import get_objects_for_user

from aleksis.apps.cursus.settings import SCHOOL_CLASS_GROUP_TYPE_NAME, SCHOOL_GRADE_GROUP_TYPE_NAME
from aleksis.apps.cursus.util.group_types import (
    get_school_class_group_type,
    get_school_grade_group_type,
)
from aleksis.core.models import Group, Person
from aleksis.core.schema.base import (
    DjangoFilterMixin,
    FilterOrderList,
    PermissionBatchDeleteMixin,
    PermissionBatchPatchMixin,
    PermissionsTypeMixin,
)
from aleksis.core.schema.group import GroupType as GraphQLGroupType
from aleksis.core.schema.person import PersonType as GraphQLPersonType
from aleksis.core.util.core_helpers import has_person

from .models import Course, Subject


class SubjectType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    class Meta:
        model = Subject
        fields = (
            "id",
            "short_name",
            "name",
            "parent",
            "colour_fg",
            "colour_bg",
            "courses",
            "teachers",
        )
        filter_fields = {
            "id": ["exact"],
            "short_name": ["exact", "icontains"],
            "name": ["exact", "icontains"],
            "parent": ["exact", "in"],
            "colour_fg": ["exact"],
            "colour_bg": ["exact"],
            "courses": ["exact", "in"],
            "teachers": ["exact", "in"],
        }

    @classmethod
    def get_queryset(cls, queryset, info):
        return get_objects_for_user(info.context.user, "cursus.view_subject", Subject)

    @staticmethod
    def resolve_courses(root, info, **kwargs):
        return get_objects_for_user(info.context.user, "cursus.view_course", root.courses.all())


class SubjectBatchCreateMutation(DjangoBatchCreateMutation):
    class Meta:
        model = Subject
        permissions = ("cursus.create_subject_rule",)
        only_fields = (
            "short_name",
            "name",
            "parent",
            "colour_fg",
            "colour_bg",
            "courses",
            "teachers",
        )


class SubjectBatchDeleteMutation(PermissionBatchDeleteMixin, DjangoBatchDeleteMutation):
    class Meta:
        model = Subject
        permissions = ("cursus.delete_subject_rule",)


class SubjectBatchPatchMutation(PermissionBatchPatchMixin, DjangoBatchPatchMutation):
    class Meta:
        model = Subject
        permissions = ("cursus.edit_subject_rule",)
        only_fields = (
            "id",
            "short_name",
            "name",
            "parent",
            "colour_fg",
            "colour_bg",
            "courses",
            "teachers",
        )


class CourseInterface(graphene.Interface):
    id = graphene.ID()  # noqa: A003
    course_id = graphene.ID()
    name = graphene.String()
    subject = graphene.Field(SubjectType)
    teachers = graphene.List(GraphQLPersonType)
    groups = graphene.List(GraphQLGroupType)
    lesson_quota = graphene.Int()


class CourseType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    class Meta:
        model = Course
        interfaces = (CourseInterface,)
        fields = ("id", "name", "subject", "teachers", "groups", "lesson_quota")
        filter_fields = {
            "id": ["exact"],
            "name": ["exact", "icontains"],
            "subject": ["exact", "in"],
            "subject__name": ["icontains"],
            "subject__short_name": ["icontains"],
            "teachers": ["in"],
            "groups": ["in"],
        }

    @staticmethod
    def resolve_teachers(root, info, **kwargs):
        teachers = get_objects_for_user(info.context.user, "core.view_person", root.teachers.all())

        # Fixme: this following code was copied from aleksis/core/schema/group.py so it should work
        #        It does however fail with the message "'Person' object has no attribute 'query'"
        # if has_person(info.context.user) and [
        #     m for m in root.teachers.all() if m.pk == info.context.user.person.pk
        # ]:
        #     teachers = (teachers | Person.objects.get(pk=info.context.user.person.pk)).distinct()
        return teachers

    @staticmethod
    def resolve_groups(root, info, **kwargs):
        by_permission = get_objects_for_user(
            info.context.user, "core.view_group", root.groups.all()
        )
        by_ownership = info.context.user.person.owner_of.all() & root.groups.all()
        return by_permission | by_ownership

    @staticmethod
    def resolve_course_id(root, info, **kwargs):
        return root.id

    @classmethod
    def get_queryset(cls, queryset, info):
        # FIXME: Permissions... this is just a workaround,
        # because cursus.view_course would have to be assigned manually
        if not has_person(info.context.user):
            raise PermissionDenied()
        return queryset
        # return get_objects_for_user(info.context.user, "cursus.view_course", Course)


class CourseBatchCreateMutation(DjangoBatchCreateMutation):
    class Meta:
        model = Course
        permissions = ("cursus.create_course_rule",)
        only_fields = ("name", "subject", "teachers", "groups", "lesson_quota")


class CourseBatchDeleteMutation(PermissionBatchDeleteMixin, DjangoBatchDeleteMutation):
    class Meta:
        model = Course
        permissions = ("cursus.delete_course_rule",)


class CourseBatchPatchMutation(PermissionBatchPatchMixin, DjangoBatchPatchMutation):
    class Meta:
        model = Course
        permissions = ("cursus.edit_course.rule",)
        only_fields = ("id", "name", "subject", "teachers", "groups", "lesson_quota")


class CreateSchoolClassMutation(DjangoBatchCreateMutation):
    class Meta:
        model = Group
        permissions = ("core.add_group",)
        only_fields = ("name", "short_name", "school_term", "parent_groups")

    @classmethod
    def before_mutate(cls, root, info, input):  # noqa
        group_type = get_school_class_group_type()
        for school_class in input:
            school_class["group_type"] = group_type.pk
        return input


class CreateSchoolGradeMutation(DjangoBatchCreateMutation):
    class Meta:
        model = Group
        permissions = ("core.add_group",)
        only_fields = ("name", "short_name", "school_term", "parent_groups")

    @classmethod
    def before_mutate(cls, root, info, input):  # noqa
        group_type = get_school_grade_group_type()
        for school_grade in input:
            school_grade["group_type"] = group_type.pk
        return input


class Query(graphene.ObjectType):
    subjects = FilterOrderList(SubjectType)
    courses = FilterOrderList(CourseType)

    school_classes = FilterOrderList(GraphQLGroupType)
    school_grades = FilterOrderList(GraphQLGroupType)
    school_grades_by_term = FilterOrderList(GraphQLGroupType, school_term=graphene.ID())

    teachers = FilterOrderList(GraphQLPersonType)

    course_by_id = graphene.Field(CourseType, id=graphene.ID())
    courses_of_teacher = FilterOrderList(CourseType, teacher=graphene.ID())

    def resolve_course_by_id(root, info, id):  # noqa
        course = Course.objects.get(pk=id)
        if not info.context.user.has_perm("cursus.view_course_rule", course):
            raise PermissionDenied()
        return course

    @staticmethod
    def resolve_school_classes(root, info, **kwargs):
        return get_objects_for_user(
            info.context.user,
            "core.view_group",
            Group.objects.filter(group_type__name=SCHOOL_CLASS_GROUP_TYPE_NAME),
        )

    @staticmethod
    def resolve_school_grades(root, info, **kwargs):
        return get_objects_for_user(
            info.context.user,
            "core.view_group",
            Group.objects.filter(group_type__name=SCHOOL_GRADE_GROUP_TYPE_NAME),
        )

    @staticmethod
    def resolve_school_grades_by_term(root, info, school_term):
        return get_objects_for_user(
            info.context.user,
            "core.view_group",
            Group.objects.filter(school_term__id=school_term).filter(
                group_type__name=SCHOOL_GRADE_GROUP_TYPE_NAME
            ),
        )

    @staticmethod
    def resolve_teachers(root, info):
        return get_objects_for_user(
            info.context.user,
            "core.view_person",
            Person.objects.filter(
                Q(courses_as_teacher__isnull=False) | Q(subjects_as_teacher__isnull=False)
            ),
        )

    @staticmethod
    def resolve_courses_of_teacher(root, info, teacher=None):
        if not has_person(info.context.user):
            raise PermissionDenied()
        teacher = Person.objects.get(pk=teacher) if teacher else info.context.user.person
        # FIXME: Permission checking. But maybe it's done in get_queryset
        return teacher.courses_as_teacher.all()


class Mutation(graphene.ObjectType):
    create_subjects = SubjectBatchCreateMutation.Field()
    delete_subjects = SubjectBatchDeleteMutation.Field()
    update_subjects = SubjectBatchPatchMutation.Field()

    create_courses = CourseBatchCreateMutation.Field()
    delete_courses = CourseBatchDeleteMutation.Field()
    update_courses = CourseBatchPatchMutation.Field()

    create_grades = CreateSchoolGradeMutation.Field()
    create_classes = CreateSchoolClassMutation.Field()
