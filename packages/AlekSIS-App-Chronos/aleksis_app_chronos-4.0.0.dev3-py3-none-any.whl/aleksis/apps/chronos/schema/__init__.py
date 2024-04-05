from datetime import timezone

import graphene
from graphene_django import DjangoObjectType
from graphene_django_cud.mutations import (
    DjangoBatchCreateMutation,
    DjangoBatchDeleteMutation,
    DjangoBatchPatchMutation,
)

from aleksis.core.models import Group, Person, Room

from ..models import LessonEvent
from ..util.chronos_helpers import get_classes, get_rooms, get_teachers


class TimetablePersonType(DjangoObjectType):
    class Meta:
        model = Person
        fields = ("id", "first_name", "last_name", "short_name")
        skip_registry = True


class TimetableGroupType(DjangoObjectType):
    class Meta:
        model = Group
        fields = ("id", "name", "short_name")
        skip_registry = True


class TimetableRoomType(DjangoObjectType):
    class Meta:
        model = Room
        fields = ("id", "name", "short_name")
        skip_registry = True


class LessonEventType(DjangoObjectType):
    class Meta:
        model = LessonEvent
        fields = (
            "id",
            "amends",
            "datetime_start",
            "datetime_end",
            "subject",
            "teachers",
            "groups",
            "rooms",
            "cancelled",
            "comment",
        )
        filter_fields = {
            "id": ["exact", "lte", "gte"],
        }

    amends = graphene.Field(lambda: LessonEventType, required=False)


class DatetimeTimezoneMixin:
    """Handle datetimes for mutations with CalendarEvent objects.

    This is necessary because the client sends timezone information as
    ISO string which only includes an offset (+00:00 UTC) and an
    offset is not a valid timezone. Instead we set UTC as timezone
    here directly.
    """

    @classmethod
    def handle_datetime_start(cls, value, name, info) -> int:
        value = value.replace(tzinfo=timezone.utc)
        return value

    @classmethod
    def handle_datetime_end(cls, value, name, info) -> int:
        value = value.replace(tzinfo=timezone.utc)
        return value


class AmendLessonBatchCreateMutation(DatetimeTimezoneMixin, DjangoBatchCreateMutation):
    class Meta:
        model = LessonEvent
        permissions = ("chronos.edit_substitution_rule",)
        only_fields = (
            "amends",
            "datetime_start",
            "datetime_end",
            "subject",
            "teachers",
            "groups",
            "rooms",
            "cancelled",
            "comment",
        )

    @classmethod
    def before_save(cls, root, info, input, created_objects):  # noqa: A002
        for obj in created_objects:
            obj.timezone = obj.amends.timezone
        return created_objects


class AmendLessonBatchPatchMutation(DatetimeTimezoneMixin, DjangoBatchPatchMutation):
    class Meta:
        model = LessonEvent
        permissions = ("chronos.edit_substitution_rule",)
        only_fields = ("subject", "teachers", "groups", "rooms", "cancelled", "comment")

    @classmethod
    def before_save(cls, root, info, input, updated_objects):  # noqa: A002
        for obj in updated_objects:
            obj.timezone = obj.amends.timezone
        return updated_objects


class AmendLessonBatchDeleteMutation(DjangoBatchDeleteMutation):
    class Meta:
        model = LessonEvent
        permissions = ("chronos.delete_substitution_rule",)


class TimetableType(graphene.Enum):
    TEACHER = "teacher"
    GROUP = "group"
    ROOM = "room"


class TimetableObjectType(graphene.ObjectType):
    id = graphene.String()  # noqa
    obj_id = graphene.String()
    name = graphene.String()
    short_name = graphene.String()
    type = graphene.Field(TimetableType)  # noqa

    def resolve_obj_id(root, info, **kwargs):
        return root.id

    def resolve_id(root, info, **kwargs):
        return f"{root.type.value}-{root.id}"


class Query(graphene.ObjectType):
    timetable_teachers = graphene.List(TimetablePersonType)
    timetable_groups = graphene.List(TimetableGroupType)
    timetable_rooms = graphene.List(TimetableRoomType)
    available_timetables = graphene.List(TimetableObjectType)

    def resolve_timetable_teachers(self, info, **kwargs):
        return get_teachers(info.context.user)

    def resolve_timetable_groups(self, info, **kwargs):
        return get_classes(info.context.user)

    def resolve_timetable_rooms(self, info, **kwargs):
        return get_rooms(info.context.user)

    def resolve_available_timetables(self, info, **kwargs):
        all_timetables = []
        for group in get_classes(info.context.user):
            all_timetables.append(
                TimetableObjectType(
                    id=group.id,
                    name=group.name,
                    short_name=group.short_name,
                    type=TimetableType.GROUP,
                )
            )

        for teacher in get_teachers(info.context.user):
            print(teacher.full_name)
            all_timetables.append(
                TimetableObjectType(
                    id=teacher.id,
                    name=teacher.full_name,
                    short_name=teacher.short_name,
                    type=TimetableType.TEACHER,
                )
            )

        for room in get_rooms(info.context.user):
            all_timetables.append(
                TimetableObjectType(
                    id=room.id, name=room.name, short_name=room.short_name, type=TimetableType.ROOM
                )
            )

        return all_timetables


class Mutation(graphene.ObjectType):
    create_amend_lessons = AmendLessonBatchCreateMutation.Field()
    patch_amend_lessons = AmendLessonBatchPatchMutation.Field()
    delete_amend_lessons = AmendLessonBatchDeleteMutation.Field()
