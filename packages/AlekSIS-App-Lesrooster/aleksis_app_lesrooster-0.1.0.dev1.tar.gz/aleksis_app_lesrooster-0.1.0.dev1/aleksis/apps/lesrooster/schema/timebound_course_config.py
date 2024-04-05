import graphene
from graphene_django.types import DjangoObjectType
from graphene_django_cud.mutations import (
    DjangoBatchCreateMutation,
    DjangoBatchDeleteMutation,
    DjangoBatchPatchMutation,
)
from guardian.shortcuts import get_objects_for_user

from aleksis.apps.cursus.models import Course, Subject
from aleksis.apps.cursus.schema import CourseInterface, CourseType, SubjectType
from aleksis.core.schema.base import (
    DjangoFilterMixin,
    PermissionBatchPatchMixin,
    PermissionsTypeMixin,
)

from ..models import TimeboundCourseConfig

timebound_course_config_filters = {"course": ["in"], "validity_range": ["in"], "teachers": [""]}


class TimeboundCourseConfigType(PermissionsTypeMixin, DjangoFilterMixin, DjangoObjectType):
    class Meta:
        model = TimeboundCourseConfig
        interfaces = (CourseInterface,)
        fields = ("id", "course", "validity_range", "lesson_quota", "teachers")
        filter_fields = timebound_course_config_filters

    @classmethod
    def get_queryset(cls, queryset, info):
        if not info.context.user.has_perm("lesrostter.view_timeboundcourseconfig_rule"):
            return get_objects_for_user(
                info.context.user,
                "lesrooster.view_timeboundcourseconfig",
                queryset,
            )
        return queryset

    @staticmethod
    def resolve_name(root, info, **kwargs):
        return root.course.name

    @staticmethod
    def resolve_subject(root, info, **kwargs):
        return root.course.subject

    @staticmethod
    def resolve_groups(root, info, **kwargs):
        return root.course.groups.all()

    @staticmethod
    def resolve_lesson_quota(root, info, **kwargs):
        return root.lesson_quota

    @staticmethod
    def resolve_teachers(root, info, **kwargs):
        return root.teachers.all()

    @staticmethod
    def resolve_course_id(root, info, **kwargs):
        return root.course.id


class LesroosterExtendedCourseType(CourseType):
    class Meta:
        model = Course

    lr_timebound_course_configs = graphene.List(TimeboundCourseConfigType)

    @staticmethod
    def resolve_lr_timebound_course_configs(root, info, **kwargs):
        if not info.context.user.has_perm("lesrooster.view_timeboundcourseconfig_rule"):
            return get_objects_for_user(
                info.context.user,
                "lesrooster.view_timeboundcourseconfig",
                root.lr_timebound_course_configs.all(),
            )
        return root.lr_timebound_course_configs.all()


class LesroosterExtendedSubjectType(SubjectType):
    class Meta:
        model = Subject

    courses = graphene.List(LesroosterExtendedCourseType)


class TimeboundCourseConfigBatchCreateMutation(DjangoBatchCreateMutation):
    class Meta:
        model = TimeboundCourseConfig
        fields = ("id", "course", "validity_range", "lesson_quota", "teachers")
        permissions = ("lesrooster.create_timeboundcourseconfig_rule",)


class TimeboundCourseConfigBatchDeleteMutation(DjangoBatchDeleteMutation):
    class Meta:
        model = TimeboundCourseConfig
        permission_required = "lesrooster.delete_timeboundcourseconfig_rule"


class TimeboundCourseConfigBatchPatchMutation(PermissionBatchPatchMixin, DjangoBatchPatchMutation):
    class Meta:
        model = TimeboundCourseConfig
        fields = ("id", "course", "validity_range", "lesson_quota", "teachers")
        permissions = ("lesrooster.change_timeboundcourseconfig_rule",)
