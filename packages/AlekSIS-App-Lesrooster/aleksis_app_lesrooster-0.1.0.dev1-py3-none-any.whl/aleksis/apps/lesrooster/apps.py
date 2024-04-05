from django.db.models import signals

from aleksis.core.util.apps import AppConfig

from .util.signal_handlers import (
    create_time_grid_for_new_validity_range,
    m2m_changed_handler,
    post_save_handler,
    pre_delete_handler,
    publish_validity_range,
)


class DefaultConfig(AppConfig):
    name = "aleksis.apps.lesrooster"
    verbose_name = "AlekSIS — Lesrooster"
    dist_name = "AlekSIS-App-Lesrooster"

    urls = {
        "Repository": "https://edugit.org/AlekSIS/onboarding//AlekSIS-App-Lesrooster",
    }
    licence = "EUPL-1.2+"
    copyright_info = (([2023], "Jonathan Weth", "dev@jonathanweth.de"),)

    def ready(self):
        # Configure change tracking for models to sync changes with LessonEvent in Chronos
        from .models import (
            Lesson,
            Supervision,
            ValidityRange,
        )

        models = [Lesson, Supervision]

        for model in models:
            signals.post_save.connect(
                post_save_handler,
                sender=model,
            )
            signals.m2m_changed.connect(
                m2m_changed_handler,
                sender=model.teachers.through,
            )
            signals.pre_delete.connect(pre_delete_handler, sender=model)

        signals.m2m_changed.connect(
            m2m_changed_handler,
            sender=Lesson.rooms.through,
        )
        signals.m2m_changed.connect(
            m2m_changed_handler,
            sender=Supervision.rooms.through,
        )

        signals.post_save.connect(create_time_grid_for_new_validity_range, sender=ValidityRange)

        signals.post_save.connect(publish_validity_range, sender=ValidityRange)
