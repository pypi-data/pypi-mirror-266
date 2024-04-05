import logging


def post_save_handler(sender, instance, created, **kwargs):
    """Sync the instance with Chronos after it has been saved."""
    if hasattr(instance, "sync"):
        logging.debug(f"Syncing {instance} (of type {sender}) after post_save signal")
        instance.sync()


def m2m_changed_handler(sender, instance, action, **kwargs):
    """Sync the instance with Chronos after a m2m relationship has been changed."""
    if hasattr(instance, "sync"):
        logging.debug(f"Syncing {instance} (of type {sender}) after m2m_changed signal")
        instance.sync()


def pre_delete_handler(sender, instance, **kwargs):
    """Sync the instance with Chronos after it has been deleted."""
    if hasattr(instance, "lesson_event"):
        logging.debug(
            f"Delete lesson event {instance.lesson_event} after deletion of lesson {instance}"
        )
        instance.lesson_event.delete()
    elif hasattr(instance, "supervision_event"):
        logging.debug(
            f"Delete supervision event {instance.supervision_event} "
            f"after deletion of lesson {instance}"
        )
        instance.supervision_event.delete()


def create_time_grid_for_new_validity_range(sender, instance, created, **kwargs):
    from ..models import TimeGrid  # noqa

    if created:
        TimeGrid.objects.create(validity_range=instance)


def publish_validity_range(sender, instance, created, **kwargs):
    from ..models import Lesson, Supervision

    # FIXME Move this to a background job
    objs_to_update = list(
        Lesson.objects.filter(slot_start__time_grid__validity_range=instance)
    ) + list(Supervision.objects.filter(break_slot__time_grid__validity_range=instance))
    for obj in objs_to_update:
        logging.info(f"Syncing object {obj} ({type(obj)}, {obj.pk})")
        obj.sync()
