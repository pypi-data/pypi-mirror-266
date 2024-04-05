from datetime import date, datetime
from typing import Optional, Union

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Q, QuerySet
from django.utils import timezone
from django.utils.formats import date_format, time_format
from django.utils.functional import classproperty
from django.utils.translation import gettext_lazy as _

import recurrence
from calendarweek import CalendarWeek
from calendarweek.django import i18n_day_abbr_choices_lazy, i18n_day_name_choices_lazy
from recurrence.fields import RecurrenceField

from aleksis.apps.chronos.managers import RoomPropertiesMixin, TeacherPropertiesMixin
from aleksis.apps.chronos.models import LessonEvent, SupervisionEvent
from aleksis.apps.cursus.models import Course, Subject
from aleksis.core.mixins import ExtensibleModel, ExtensiblePolymorphicModel, GlobalPermissionModel
from aleksis.core.models import Group, Holiday, Person, Room, SchoolTerm

from .managers import ValidityRangeManager, ValidityRangeQuerySet


class ValidityRangeStatus(models.TextChoices):
    """Validity range status."""

    DRAFT = "draft", _("Draft")
    PUBLISHED = "published", _("Published")


class ValidityRange(ExtensibleModel):
    """A validity range is a date range in which certain data are valid."""

    objects = ValidityRangeManager.from_queryset(ValidityRangeQuerySet)()

    school_term = models.ForeignKey(
        SchoolTerm,
        on_delete=models.CASCADE,
        verbose_name=_("School term"),
        related_name="lr_validity_ranges",
    )
    name = models.CharField(verbose_name=_("Name"), max_length=255, blank=True)

    date_start = models.DateField(verbose_name=_("Start date"))
    date_end = models.DateField(verbose_name=_("End date"))

    status = models.CharField(
        verbose_name=_("Status"),
        max_length=255,
        choices=ValidityRangeStatus.choices,
        default=ValidityRangeStatus.DRAFT,
    )

    @property
    def published(self):
        return self.status == ValidityRangeStatus.PUBLISHED.value

    @classmethod
    def get_current(cls, day: Optional[date] = None) -> Optional["ValidityRange"]:
        """Get the currently active validity range."""
        if not day:
            day = timezone.now().date()
        try:
            return cls.objects.on_day(day).first()
        except ValidityRange.DoesNotExist:
            return None

    @classproperty
    def current(cls) -> Optional["ValidityRange"]:
        """Get the currently active validity range."""
        return cls.get_current()

    @property
    def is_current(self) -> bool:
        return self.date_start <= (today := timezone.now().date()) and self.date_end >= today

    def clean(self):
        """Ensure that there is only one validity range at each point of time."""
        if self.date_end < self.date_start:
            raise ValidationError(_("The start date must be earlier than the end date."))

        if self.school_term and (
            self.date_end > self.school_term.date_end
            or self.date_start < self.school_term.date_start
        ):
            raise ValidationError(_("The validity range must be within the school term."))

        if self.status == ValidityRangeStatus.PUBLISHED.value:
            qs = ValidityRange.objects.within_dates(self.date_start, self.date_end).filter(
                status=ValidityRangeStatus.PUBLISHED
            )
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    _(
                        "There is already a published validity range "
                        "for this time or a part of this time."
                    )
                )

    def __str__(self) -> str:
        return self.name or f"{date_format(self.date_start)}–{date_format(self.date_end)}"

    class Meta:
        verbose_name = _("Validity range")
        verbose_name_plural = _("Validity ranges")
        constraints = [
            models.UniqueConstraint(
                fields=["school_term", "date_start", "date_end"],
                condition=Q(status=ValidityRangeStatus.PUBLISHED),
                name="lr_unique_dates_per_term",
            ),
            models.CheckConstraint(
                check=Q(date_start__lte=F("date_end")), name="date_start_lte_date_end"
            ),
        ]
        indexes = [
            models.Index(fields=["date_start", "date_end"], name="lr_validity_date_start_end")
        ]


class TimeGrid(ExtensibleModel):
    validity_range = models.ForeignKey(
        ValidityRange,
        on_delete=models.CASCADE,
        related_name="time_grids",
        verbose_name=_("Linked validity range"),
    )

    group = models.ForeignKey(
        Group,
        verbose_name=_("Group"),
        on_delete=models.SET_NULL,
        related_name="time_grids",
        blank=True,
        null=True,
    )

    def __str__(self):
        if self.group:
            return f"{self.validity_range}: {self.group}"
        return str(self.validity_range)

    class Meta:
        verbose_name = _("Time Grid")
        verbose_name_plural = _("Time Grids")
        constraints = [
            models.UniqueConstraint(
                fields=["validity_range", "group"], name="lr_unique_validity_range_group_time_grid"
            ),
            models.UniqueConstraint(
                fields=["validity_range"], condition=Q(group=None), name="lr_one_default_time_grid"
            ),
        ]


class Slot(ExtensiblePolymorphicModel):
    """A slot is a time period in which a lesson can take place."""

    WEEKDAY_CHOICES = i18n_day_name_choices_lazy()
    WEEKDAY_CHOICES_SHORT = i18n_day_abbr_choices_lazy()

    time_grid = models.ForeignKey(
        TimeGrid,
        on_delete=models.CASCADE,
        related_name="slots",
        verbose_name=_("Time Grid"),
    )

    name = models.CharField(verbose_name=_("Name"), max_length=255, blank=True)

    weekday = models.PositiveSmallIntegerField(
        verbose_name=_("Week day"), choices=i18n_day_name_choices_lazy()
    )
    period = models.PositiveSmallIntegerField(
        verbose_name=_("Number of period"), blank=True, null=True
    )

    time_start = models.TimeField(verbose_name=_("Start time"))
    time_end = models.TimeField(verbose_name=_("End time"))

    def __str__(self) -> str:
        if self.name:
            suffix = self.name
        elif self.period:
            suffix = f"{self.period}."
        else:
            suffix = f"{time_format(self.time_start)}–{time_format(self.time_end)}"
        return f"{self.weekday}, {suffix}"

    def get_date(self, week: CalendarWeek) -> date:
        """Get date of lesson in a specific week."""
        return week[self.weekday]

    def get_datetime_start(self, date_ref: Union[CalendarWeek, date]) -> datetime:
        """Get datetime of lesson start in a specific week or on a specific day."""
        day = date_ref if isinstance(date_ref, date) else self.get_date(date_ref)
        return timezone.make_aware(datetime.combine(day, self.time_start))

    def get_first_datetime(self) -> datetime:
        return self.get_datetime_start(self.time_grid.validity_range.date_start)

    def get_datetime_end(self, date_ref: Union[CalendarWeek, int, date]) -> datetime:
        """Get datetime of lesson end in a specific week or on a specific day."""
        day = date_ref if isinstance(date_ref, date) else self.get_date(date_ref)
        return timezone.make_aware(datetime.combine(day, self.time_end))

    def get_last_datetime(self) -> datetime:
        return self.get_datetime_end(self.time_grid.validity_range.date_end)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["weekday", "period", "time_grid"], name="lr_unique_period_per_range"
            ),
            models.CheckConstraint(
                check=Q(time_start__lte=F("time_end")), name="time_start_lte_time_end"
            ),
        ]
        ordering = ["weekday", "period"]
        indexes = [models.Index(fields=["time_start", "time_end"])]
        verbose_name = _("Slot")
        verbose_name_plural = _("Slots")


class Lesson(TeacherPropertiesMixin, RoomPropertiesMixin, ExtensibleModel):
    """A lesson represents a single teaching event."""

    lesson_event = models.OneToOneField(
        LessonEvent,
        on_delete=models.SET_NULL,
        related_name="lesson",
        verbose_name=_("Linked lesson event"),
        blank=True,
        null=True,
    )

    # A Course is the base of each lesson, it is its planing base

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, verbose_name=_("Course"), null=True, blank=True
    )

    # Allow lessons to go over multiple slots to ensure
    # that they are later tracked as single event
    slot_start = models.ForeignKey(
        Slot,
        on_delete=models.CASCADE,
        verbose_name=_("Start slot"),
        related_name="+",
    )
    slot_end = models.ForeignKey(
        Slot,
        on_delete=models.CASCADE,
        verbose_name=_("End slot"),
        related_name="+",
    )

    # Recurrence rules allow to define a series of lessons
    # Common examples are weekly or every second week
    recurrence = RecurrenceField(
        verbose_name=_("Recurrence"),
        blank=True,
        null=True,
        help_text=_("Leave empty for a single lesson."),
    )

    # None of the following attributes is required
    # as practice has shown that all possible combinations can occur
    rooms = models.ManyToManyField(
        Room,
        verbose_name=_("Rooms"),
        related_name="lr_lessons",
        blank=True,
    )
    teachers = models.ManyToManyField(
        Person,
        verbose_name=_("Teachers"),
        related_name="lr_lessons_as_teacher",
        blank=True,
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        verbose_name=_("Subject"),
        related_name="lr_lessons",
        blank=True,
        null=True,
    )

    def get_teachers(self) -> QuerySet[Person]:
        return self.teachers.all()

    def get_rooms(self) -> QuerySet[Room]:
        return self.rooms.all()

    def get_groups(self) -> QuerySet[Group]:
        return self.course.groups.all()

    def clean(self):
        """Ensure that the slots are in the same validity range."""
        if self.slot_start.time_grid != self.slot_end.time_grid:
            raise ValidationError(_("The slots must be in the same time grid."))

    @property
    def real_recurrence(self) -> "recurrence.Recurrence":
        """Get the real recurrence adjusted to the validity range and including holidays."""
        if not self.recurrence:
            return
        rrules = self.recurrence.rrules
        for rrule in rrules:
            rrule.until = self.slot_end.get_last_datetime()
        pattern = recurrence.Recurrence(
            dtstart=self.slot_start.get_first_datetime(),
            rrules=rrules,
        )
        pattern.exdates = Holiday.get_ex_dates(
            self.slot_start.get_first_datetime(), self.slot_end.get_last_datetime(), pattern
        )
        return pattern

    def sync(self) -> LessonEvent:
        """Sync the lesson with its lesson event."""
        week_start = CalendarWeek.from_date(self.slot_start.time_grid.validity_range.date_start)
        datetime_start = self.slot_start.get_datetime_start(week_start)
        datetime_end = self.slot_end.get_datetime_end(week_start)

        lesson_event = LessonEvent() if not self.lesson_event else self.lesson_event

        lesson_event.course = self.course
        lesson_event.subject = self.subject
        lesson_event.datetime_start = datetime_start
        lesson_event.datetime_end = datetime_end

        lesson_event.recurrences = self.real_recurrence

        lesson_event.save()

        lesson_event.groups.set(self.course.groups.all())
        lesson_event.teachers.set(self.teachers.all())
        lesson_event.rooms.set(self.rooms.all())

        if self.lesson_event != lesson_event:
            self.lesson_event = lesson_event
            self.save()

        return lesson_event

    class Meta:
        ordering = [
            "slot_start__time_grid__validity_range__date_start",
            "slot_start__weekday",
            "slot_start__time_start",
            "subject",
        ]
        verbose_name = _("Lesson")
        verbose_name_plural = _("Lessons")


class BreakSlot(Slot):
    """A break is a time period that can supervised and in which no lessons take place."""

    def __str__(self) -> str:
        return f"{time_format(self.time_start)} - {time_format(self.time_end)}"

    class Meta:
        verbose_name = _("Break")
        verbose_name_plural = _("Breaks")


class Supervision(TeacherPropertiesMixin, RoomPropertiesMixin, ExtensibleModel):
    """A supervision is a time period in which a teacher supervises a room."""

    supervision_event = models.OneToOneField(
        SupervisionEvent,
        on_delete=models.SET_NULL,
        related_name="supervision",
        verbose_name=_("Linked supervision event"),
        blank=True,
        null=True,
    )

    rooms = models.ManyToManyField(
        Room,
        verbose_name=_("Rooms"),
        related_name="lr_supervisions",
    )
    teachers = models.ManyToManyField(
        Person,
        verbose_name=_("Teachers"),
        related_name="lr_supervisions",
    )
    break_slot = models.ForeignKey(
        BreakSlot,
        on_delete=models.CASCADE,
        verbose_name=_("Break Slot"),
        related_name="lr_supervisions",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        verbose_name=_("Subject"),
        related_name="lr_supervisions",
        blank=True,
        null=True,
    )

    # Recurrence rules allow to define a series of supervisions
    # Common examples are weekly or every second week
    recurrence = RecurrenceField(
        verbose_name=_("Recurrence"),
        blank=True,
        null=True,
        help_text=_("Leave empty for a single supervision."),
    )

    def get_teachers(self) -> QuerySet[Person]:
        return self.teachers.all()

    def get_rooms(self) -> QuerySet[Room]:
        return self.rooms.all()

    def __str__(self):
        return f"{self.break_slot}, {self.room_names} ({self.teacher_names}))"

    class Meta:
        verbose_name = _("Supervision")
        verbose_name_plural = _("Supervisions")

    @property
    def real_recurrence(self) -> "recurrence.Recurrence":
        """Get the real recurrence adjusted to the validity range and including holidays."""
        if not self.recurrence:
            return
        rrules = self.recurrence.rrules
        for rrule in rrules:
            rrule.until = self.break_slot.get_last_datetime()
        pattern = recurrence.Recurrence(
            dtstart=self.break_slot.get_first_datetime(),
            rrules=rrules,
        )
        pattern.exdates = Holiday.get_ex_dates(
            self.break_slot.get_first_datetime(), self.break_slot.get_last_datetime(), pattern
        )
        return pattern

    def sync(self) -> SupervisionEvent:
        """Sync the supervision with its supervision event."""
        week_start = CalendarWeek.from_date(self.break_slot.time_grid.validity_range.date_start)
        datetime_start = self.break_slot.get_datetime_start(week_start)
        datetime_end = self.break_slot.get_datetime_end(week_start)

        supervision_event = self.supervision_event if self.supervision_event else SupervisionEvent()

        supervision_event.datetime_start = datetime_start
        supervision_event.datetime_end = datetime_end
        supervision_event.subject = self.subject

        supervision_event.recurrences = self.real_recurrence

        supervision_event.save()

        supervision_event.teachers.set(self.teachers.all())
        supervision_event.rooms.set(self.rooms.all())

        if self.supervision_event != supervision_event:
            self.supervision_event = supervision_event
            self.save()

        return supervision_event


class TimeboundCourseConfig(ExtensibleModel):
    """A timebound course config is the specific configuration of a course.

    It consists of a course and a validity range.
    """

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name=_("Course"),
        related_name="lr_timebound_course_configs",
    )
    validity_range = models.ForeignKey(
        ValidityRange,
        on_delete=models.CASCADE,
        verbose_name=_("Linked validity range"),
        related_name="lr_timebound_course_configs",
    )

    lesson_quota = models.PositiveSmallIntegerField(
        verbose_name=_("Lesson quota"),
        help_text=_("Number of slots this course is scheduled to fill per week"),
        blank=True,
        null=True,
    )
    teachers = models.ManyToManyField(
        Person,
        verbose_name=_("Teachers"),
        related_name="lr_timebound_course_configs",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["course", "validity_range"], name="lr_unique_course_config_per_range"
            ),
        ]
        verbose_name = _("Timebound course config")
        verbose_name_plural = _("Timebound course configs")


class LesroosterGlobalPermissions(GlobalPermissionModel):
    class Meta:
        managed = False
        permissions = (
            ("manage_lesson_raster", _("Can manage lesson raster")),
            ("plan_timetables", _("Can plan timetables")),
        )
